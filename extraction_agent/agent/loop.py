"""Loop principal do agente de extração.

Para cada documento da pasta do deal:
  1. Classifica o tipo de documento. Sem confiança => `not_classified`:
     entra na fila de revisão (linha em `Pendente`), nunca é descartado.
  2. Verifica indícios de que não é a versão final assinada (nome do
     arquivo + conteúdo) e propaga o alerta para o rascunho.
  3. Para cada categoria de termo relevante: busca referência e precedente,
     extrai com citação, decide `not_found` quando ausente, atribui
     confiança e escreve o rascunho em `Pendente`.

Sem trigger automático: é executado manualmente via main.py e termina
quando todos os arquivos foram processados.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import anthropic

from config import Config
from agent import prompts, tools
from agent.tools import GoogleClients, TermRow


@dataclass
class ExtractionSummary:
    company: str
    files_processed: list = field(default_factory=list)
    files_not_classified: list = field(default_factory=list)
    rows_written: int = 0
    review_flags: int = 0
    errors: list = field(default_factory=list)


class ExtractionLoop:
    def __init__(self, config: Config, clients: GoogleClients | None = None,
                 claude: anthropic.Anthropic | None = None):
        self.config = config
        self.clients = clients or GoogleClients(config)
        self.claude = claude or anthropic.Anthropic(api_key=config.anthropic_api_key)

    # -- chamadas ao modelo -------------------------------------------------

    def _call_claude(self, content_blocks: list, schema: dict) -> dict:
        response = self.claude.messages.create(
            model=self.config.claude_model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=[{
                "type": "text",
                "text": prompts.SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": content_blocks}],
            output_config={"format": {"type": "json_schema", "schema": schema}},
        )
        if response.stop_reason == "refusal":
            raise tools.ToolError(
                "O modelo recusou a solicitação (stop_reason=refusal). "
                "Marque o documento para revisão manual."
            )
        text = next(b.text for b in response.content if b.type == "text")
        return json.loads(text)

    def _document_block(self, document_text: str) -> dict:
        # O texto do documento é reutilizado em todas as chamadas de extração
        # do mesmo arquivo — cache para reduzir custo/latência.
        return {
            "type": "text",
            "text": f"<document>\n{document_text}\n</document>",
            "cache_control": {"type": "ephemeral"},
        }

    def classify(self, file_name: str, document_text: str) -> dict:
        instructions = prompts.CLASSIFY_INSTRUCTIONS.format(
            file_name=file_name,
            document_text=document_text,
        )
        return self._call_claude(
            [{"type": "text", "text": instructions}],
            prompts.CLASSIFY_SCHEMA,
        )

    def extract_term(self, file_name: str, document_text: str, document_type: str,
                     term_category: str, reference: dict, precedents: list,
                     version_flags: list[str]) -> dict:
        instructions = prompts.EXTRACT_INSTRUCTIONS.format(
            term_category=term_category,
            file_name=file_name,
            document_type=document_type,
            reference=prompts.format_reference(reference),
            precedents=prompts.format_precedents(precedents),
            version_flags="\n".join(f"- {f}" for f in version_flags) or "(nenhum)",
        )
        return self._call_claude(
            [
                self._document_block(document_text),
                {"type": "text", "text": instructions},
            ],
            prompts.EXTRACT_SCHEMA,
        )

    # -- pipeline por documento --------------------------------------------

    def _version_label(self, file_name: str, version_flags: list[str]) -> str:
        if version_flags:
            return f"{file_name} — POSSÍVEL NÃO-FINAL: {'; '.join(version_flags)}"
        return f"{file_name} — sem indícios de rascunho"

    def _write_not_classified(self, company: str, file_name: str, reason: str,
                              version_label: str) -> None:
        """Arquivo não reconhecido entra na fila de revisão — nunca é
        descartado silenciosamente (§2.4)."""
        row = TermRow(
            categoria="documento",
            termo="classificacao",
            resumo="Arquivo não classificado automaticamente; requer revisão humana.",
            valor="not_classified",
            documento_fonte=file_name,
            secao_fonte="documento completo",
            confianca="review",
            motivo_flag=reason,
            empresa=company,
            versao_documento=version_label,
        )
        tools.write_draft(row, self.clients, self.config)

    def process_file(self, company: str, file: dict, summary: ExtractionSummary) -> None:
        file_name = file["name"]
        name_markers = tools.filename_draft_markers(file_name)
        version_flags = [
            f"nome de arquivo contém {m!r}" for m in name_markers
        ]

        try:
            text = tools.read_document(
                file["id"], file_name, file.get("mimeType", ""), self.clients
            )
        except tools.UnsupportedFileTypeError as exc:
            self._write_not_classified(
                company, file_name, str(exc), self._version_label(file_name, version_flags)
            )
            summary.files_not_classified.append(file_name)
            summary.rows_written += 1
            summary.review_flags += 1
            return

        # Passo 1: classificar
        classification = self.classify(file_name, text)
        if not classification["confident"] or classification["document_type"] == "not_classified":
            self._write_not_classified(
                company,
                file_name,
                f"Classificação sem confiança: {classification['reasoning']}",
                self._version_label(file_name, version_flags),
            )
            summary.files_not_classified.append(file_name)
            summary.rows_written += 1
            summary.review_flags += 1
            return

        document_type = classification["document_type"]

        # Passo 2: indícios de versão não-final (nome do arquivo + conteúdo)
        version_flags += classification.get("final_version_concerns", [])
        version_label = self._version_label(file_name, version_flags)

        # Passo 3: extrair cada categoria relevante
        categories = tools.list_term_categories(document_type, self.clients, self.config)
        for category in categories:
            reference = tools.search_reference(document_type, category, self.clients, self.config)
            precedents = tools.search_precedent(category, self.clients, self.config)

            result = self.extract_term(
                file_name, text, document_type, category,
                reference, precedents, version_flags,
            )

            confidence = result["confidence"]
            flag_reason = result["flag_reason"]
            # Guard rail §1.4: documento possivelmente não-final nunca sai
            # como high_confidence, independente do que o modelo respondeu.
            if version_flags and confidence == "high_confidence":
                confidence = "review"
                flag_reason = (
                    "Rebaixado pelo agente: possível versão não-final do documento "
                    f"({'; '.join(version_flags)})."
                )

            value = result["value"].strip() if result["found"] else tools.NOT_FOUND

            row = TermRow(
                categoria=category,
                termo=result["term"] or category,
                resumo=result["summary"],
                valor=value or tools.NOT_FOUND,
                documento_fonte=file_name,
                secao_fonte=result["source_section"],
                confianca=confidence,
                nota_comparacao=result["comparison_note"],
                motivo_flag=flag_reason,
                precedente_consultado=result["precedent_used"],
                empresa=company,
                versao_documento=version_label,
            )
            tools.write_draft(row, self.clients, self.config)
            summary.rows_written += 1
            if confidence == "review":
                summary.review_flags += 1

        summary.files_processed.append(f"{file_name} ({document_type})")

    # -- entrada ------------------------------------------------------------

    def run(self, company: str, folder_link: str) -> ExtractionSummary:
        summary = ExtractionSummary(company=company)
        files = tools.list_files(folder_link, self.clients)
        if not files:
            summary.errors.append("Nenhum arquivo encontrado na pasta informada.")
            return summary
        for file in files:
            try:
                self.process_file(company, file, summary)
            except (tools.TabWriteNotAllowedError, tools.DraftValidationError,
                    tools.SheetsWritePermissionError):
                # Violações de guard rail nunca são engolidas.
                raise
            except Exception as exc:  # noqa: BLE001 — registrado, não silenciado
                summary.errors.append(f"{file.get('name', file.get('id'))}: {exc}")
        return summary
