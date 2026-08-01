"""Loop principal do agente de extração.

Dois modos, ambos disparados manualmente (sem servidor, sem webhook, sem
trigger automático):

  - `run_deal(empresa, link)` — um deal.
  - `run_batch()` — todos os deals listados na aba `Deals`, pulando os que
    já têm linhas em `Pendente` ou `Publicado`.

Para cada documento:
  1. Classifica o tipo. Sem confiança => `not_classified`: entra na fila de
     revisão (linha em `Pendente`), nunca é descartado.
  2. Verifica indícios de que não é a versão final assinada (nome do
     arquivo + conteúdo) e propaga o alerta para o rascunho.
  3. Extrai as categorias relevantes em BLOCOS (uma chamada por bloco, não
     uma por categoria), confere a cobertura, atribui confiança e acumula
     as linhas.
  4. Escreve todas as linhas do documento numa única chamada ao Sheets.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import anthropic

from config import Config
from agent import prompts, tools
from agent.tools import DealEntry, GoogleClients, TermRow

# Status possíveis de um deal no relatório final.
STATUS_PROCESSED = "processado"
STATUS_SKIPPED = "pulado"
STATUS_FAILED = "falhou"
STATUS_INVALID = "invalido"


@dataclass
class DealResult:
    """Resultado de um deal. Nenhum deal some do relatório, qualquer que
    seja o desfecho."""

    company: str
    status: str
    detail: str = ""
    rows_written: int = 0
    review_flags: int = 0
    files_processed: list = field(default_factory=list)
    files_not_classified: list = field(default_factory=list)
    errors: list = field(default_factory=list)


@dataclass
class BatchSummary:
    deals: list = field(default_factory=list)
    aborted: str = ""

    def add(self, result: DealResult) -> DealResult:
        self.deals.append(result)
        return result

    def by_status(self, status: str) -> list:
        return [d for d in self.deals if d.status == status]

    @property
    def rows_written(self) -> int:
        return sum(d.rows_written for d in self.deals)

    @property
    def review_flags(self) -> int:
        return sum(d.review_flags for d in self.deals)


def _chunks(items: list, size: int) -> list:
    return [items[i:i + size] for i in range(0, len(items), size)]


class ExtractionLoop:
    def __init__(self, config: Config, clients: GoogleClients | None = None,
                 claude: anthropic.Anthropic | None = None):
        self.config = config
        self.clients = clients or GoogleClients(config)
        # max_retries acima do padrão: um lote de 50 deals roda por horas e
        # vai encostar em rate limit; o SDK faz o backoff sozinho.
        self.claude = claude or anthropic.Anthropic(
            api_key=config.anthropic_api_key, max_retries=8
        )

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
        text = next((b.text for b in response.content if b.type == "text"), None)
        if text is None:
            raise tools.ToolError(
                f"Resposta do modelo sem bloco de texto (stop_reason="
                f"{response.stop_reason!r})."
            )
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

    def extract_terms(self, file_name: str, document_text: str, document_type: str,
                      categories: list[str], version_flags: list[str]) -> list[dict]:
        """Extrai um bloco de categorias numa única chamada ao modelo.

        Garante cobertura: toda categoria pedida volta na lista, mesmo que o
        modelo a tenha omitido — nesse caso como `not_found` sinalizado para
        revisão, nunca como silêncio.
        """
        blocks = []
        for category in categories:
            reference = tools.search_reference(
                document_type, category, self.clients, self.config
            )
            precedents = tools.search_precedent(category, self.clients, self.config)
            blocks.append(prompts.format_category_block(category, reference, precedents))

        instructions = prompts.EXTRACT_BATCH_INSTRUCTIONS.format(
            file_name=file_name,
            document_type=document_type,
            version_flags="\n".join(f"- {f}" for f in version_flags) or "(nenhum)",
            category_blocks="\n\n".join(blocks),
        )
        response = self._call_claude(
            [
                self._document_block(document_text),
                {"type": "text", "text": instructions},
            ],
            prompts.EXTRACT_BATCH_SCHEMA,
        )
        return self._ensure_coverage(response.get("terms", []), categories)

    @staticmethod
    def _ensure_coverage(items: list, categories: list[str]) -> list[dict]:
        """Casa a resposta do modelo com as categorias pedidas.

        Categoria omitida vira `not_found` explícito marcado para revisão.
        Categoria devolvida que não foi pedida é descartada (o item seria
        um termo sem referência pedida — não confiável).
        """
        by_category = {}
        for item in items:
            key = tools._norm(item.get("category", ""))
            if key and key not in by_category:
                by_category[key] = item

        covered = []
        for category in categories:
            item = by_category.get(tools._norm(category))
            if item is None:
                covered.append({
                    "category": category,
                    "found": False,
                    "term": category,
                    "value": tools.NOT_FOUND,
                    "summary": (
                        "O modelo não retornou resposta para esta categoria; "
                        "nenhuma conclusão foi tirada sobre ela."
                    ),
                    "source_section": (
                        "não verificado — categoria omitida na resposta do modelo"
                    ),
                    "confidence": "review",
                    "flag_reason": (
                        "Categoria solicitada mas ausente na resposta do modelo — "
                        "requer verificação manual no documento."
                    ),
                    "comparison_note": "",
                    "precedent_used": False,
                })
            else:
                item["category"] = category  # normaliza para o nome canônico
                covered.append(item)
        return covered

    # -- pipeline por documento --------------------------------------------

    def _version_label(self, file_name: str, version_flags: list[str]) -> str:
        if version_flags:
            return f"{file_name} — POSSÍVEL NÃO-FINAL: {'; '.join(version_flags)}"
        return f"{file_name} — sem indícios de rascunho"

    def _not_classified_row(self, company: str, file_name: str, reason: str,
                            version_label: str) -> TermRow:
        """Arquivo não reconhecido entra na fila de revisão — nunca é
        descartado silenciosamente (§2.4)."""
        return TermRow(
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

    def process_file(self, company: str, file: dict, result: DealResult) -> None:
        file_name = file["name"]
        version_flags = [
            f"nome de arquivo contém {m!r}"
            for m in tools.filename_draft_markers(file_name)
        ]

        try:
            text = tools.read_document(
                file["id"], file_name, file.get("mimeType", ""), self.clients
            )
        except tools.UnsupportedFileTypeError as exc:
            self._write_rows(
                [self._not_classified_row(
                    company, file_name, str(exc),
                    self._version_label(file_name, version_flags),
                )],
                result,
            )
            result.files_not_classified.append(file_name)
            return

        # Passo 1: classificar
        classification = self.classify(file_name, text)
        if not classification["confident"] or classification["document_type"] == "not_classified":
            self._write_rows(
                [self._not_classified_row(
                    company, file_name,
                    f"Classificação sem confiança: {classification['reasoning']}",
                    self._version_label(file_name, version_flags),
                )],
                result,
            )
            result.files_not_classified.append(file_name)
            return

        document_type = classification["document_type"]

        # Passo 2: indícios de versão não-final (nome do arquivo + conteúdo)
        version_flags += classification.get("final_version_concerns", [])
        version_label = self._version_label(file_name, version_flags)

        # Passo 3: extrair em blocos de categorias
        categories = tools.list_term_categories(document_type, self.clients, self.config)
        rows: list[TermRow] = []
        for block in _chunks(categories, self.config.category_batch_size):
            for item in self.extract_terms(
                file_name, text, document_type, block, version_flags
            ):
                rows.append(self._row_from_item(item, company, file_name, version_label,
                                                version_flags))

        # Passo 4: uma única escrita no Sheets por documento
        self._write_rows(rows, result)
        result.files_processed.append(f"{file_name} ({document_type})")

    def _row_from_item(self, item: dict, company: str, file_name: str,
                       version_label: str, version_flags: list[str]) -> TermRow:
        confidence = item["confidence"]
        flag_reason = item["flag_reason"]
        # Guard rail §1.4: documento possivelmente não-final nunca sai como
        # high_confidence, independente do que o modelo respondeu.
        if version_flags and confidence == "high_confidence":
            confidence = "review"
            flag_reason = (
                "Rebaixado pelo agente: possível versão não-final do documento "
                f"({'; '.join(version_flags)})."
            )

        value = item["value"].strip() if item["found"] else tools.NOT_FOUND
        return TermRow(
            categoria=item["category"],
            termo=item["term"] or item["category"],
            resumo=item["summary"],
            valor=value or tools.NOT_FOUND,
            documento_fonte=file_name,
            secao_fonte=item["source_section"],
            confianca=confidence,
            nota_comparacao=item["comparison_note"],
            motivo_flag=flag_reason,
            precedente_consultado=item["precedent_used"],
            empresa=company,
            versao_documento=version_label,
        )

    def _write_rows(self, rows: list[TermRow], result: DealResult) -> None:
        if not rows:
            return
        tools.write_drafts(rows, self.clients, self.config)
        result.rows_written += len(rows)
        result.review_flags += sum(1 for r in rows if r.confianca == "review")

    # -- um deal ------------------------------------------------------------

    def run_deal(self, company: str, folder_link: str) -> DealResult:
        result = DealResult(company=company, status=STATUS_PROCESSED)
        files = tools.list_files(folder_link, self.clients)
        if not files:
            result.status = STATUS_FAILED
            result.detail = "Nenhum arquivo encontrado na pasta informada."
            return result

        for file in files:
            try:
                self.process_file(company, file, result)
            except (tools.TabWriteNotAllowedError, tools.SheetsWritePermissionError):
                # Erro sistêmico de permissão: falharia em todo deal.
                raise
            except Exception as exc:  # noqa: BLE001 — registrado, não silenciado
                result.errors.append(f"{file.get('name', file.get('id'))}: {exc}")

        if result.errors:
            result.status = STATUS_FAILED
            result.detail = f"{len(result.errors)} arquivo(s) com erro."
        return result

    # -- lote ---------------------------------------------------------------

    def run_batch(self, force: bool = False, only: str = "",
                  on_start=None, on_result=None) -> BatchSummary:
        """Processa os deals da aba `Deals`.

        `force=True` ignora a idempotência e reprocessa tudo.
        `only` restringe a um deal pelo nome da empresa.
        `on_start(deals)` e `on_result(result)` recebem o progresso — um lote
        grande roda por horas e precisa dar sinal de vida enquanto trabalha.
        """
        summary = BatchSummary()
        deals = tools.list_deals(self.clients, self.config)
        if only:
            deals = [d for d in deals if tools._norm(d.company) == tools._norm(only)]
            if not deals:
                summary.aborted = f"Nenhum deal chamado {only!r} na aba `Deals`."
                return summary

        if on_start:
            on_start(deals)

        processed = (
            {tools.PENDENTE_TAB: set(), tools.PUBLICADO_TAB: set()}
            if force
            else tools.list_processed_companies(self.clients, self.config)
        )

        for deal in deals:
            try:
                result = summary.add(self._run_one(deal, processed))
            except (tools.TabWriteNotAllowedError, tools.SheetsWritePermissionError) as exc:
                # Sistêmico: abortar o lote inteiro em vez de repetir o erro
                # 50 vezes.
                summary.aborted = (
                    f"Lote interrompido em {deal.company!r} por erro de permissão "
                    f"de escrita: {exc}"
                )
                return summary
            if on_result:
                on_result(result)
        return summary

    def _run_one(self, deal: DealEntry, processed: dict) -> DealResult:
        if not deal.processable:
            return DealResult(
                company=deal.company, status=STATUS_INVALID, detail=deal.issue
            )

        key = tools._norm(deal.company)
        if key in processed.get(tools.PUBLICADO_TAB, set()):
            return DealResult(
                company=deal.company,
                status=STATUS_SKIPPED,
                detail="Já aprovado pelo Legal (consta em `Publicado`).",
            )
        if key in processed.get(tools.PENDENTE_TAB, set()):
            return DealResult(
                company=deal.company,
                status=STATUS_SKIPPED,
                detail="Rascunho já aguardando revisão em `Pendente`.",
            )

        try:
            return self.run_deal(deal.company, deal.folder_link)
        except (tools.TabWriteNotAllowedError, tools.SheetsWritePermissionError):
            raise
        except Exception as exc:  # noqa: BLE001 — o lote continua, o deal é reportado
            return DealResult(
                company=deal.company, status=STATUS_FAILED, detail=str(exc)
            )
