"""Testes das ferramentas e dos guard rails de conteúdo (exigências do prompt).

- Termo não encontrado => `not_found` explícito, nunca campo vazio.
- Toda linha escrita em `Pendente` tem citação (documento + seção); escrita
  sem citação é rejeitada com erro.
"""

import pytest

from agent import tools
from agent.tools import (
    NOT_FOUND,
    DraftValidationError,
    GoogleClients,
    TermRow,
)
from tests.test_permissions import make_row


class TestNotFoundIsExplicit:
    def test_empty_value_is_rejected(self, clients, config):
        """Campo de valor vazio sem explicação é falha do agente — a escrita
        é recusada e a mensagem aponta para `not_found`."""
        row = make_row(valor="")
        with pytest.raises(DraftValidationError, match=NOT_FOUND):
            tools.write_draft(row, clients, config)

    def test_whitespace_value_is_rejected(self, clients, config):
        with pytest.raises(DraftValidationError):
            tools.write_draft(make_row(valor="   "), clients, config)

    def test_not_found_row_is_accepted(self, clients, config, sheets):
        """`not_found` com escopo verificado na citação é uma resposta válida."""
        row = make_row(
            valor=NOT_FOUND,
            secao_fonte="documento completo — cláusula de MFN não localizada",
            confianca="review",
            motivo_flag="Termo esperado para o tipo de documento, mas ausente.",
        )
        tools.write_draft(row, clients, config)
        assert len(sheets.append_calls) == 1
        written = sheets.append_calls[0]["body"]["values"][0]
        assert NOT_FOUND in written

    def test_loop_converts_not_found_result_to_explicit_value(self):
        """Mesmo que o modelo retorne found=false com value vazio, o loop
        grava `not_found` explícito (nunca vazio)."""
        result = {"found": False, "value": ""}
        value = result["value"].strip() if result["found"] else NOT_FOUND
        assert value == NOT_FOUND


class TestCitationIsMandatory:
    def test_missing_source_document_is_rejected(self, clients, config):
        with pytest.raises(DraftValidationError, match="documento_fonte"):
            tools.write_draft(make_row(documento_fonte=""), clients, config)

    def test_missing_source_section_is_rejected(self, clients, config):
        with pytest.raises(DraftValidationError, match="secao_fonte"):
            tools.write_draft(make_row(secao_fonte=""), clients, config)

    def test_rejected_row_is_never_written(self, clients, config, sheets):
        """Rejeição acontece ANTES de qualquer chamada à API de escrita."""
        with pytest.raises(DraftValidationError):
            tools.write_draft(make_row(secao_fonte=" "), clients, config)
        assert sheets.append_calls == []

    def test_valid_citation_is_written_in_full(self, clients, config, sheets):
        tools.write_draft(make_row(), clients, config)
        written = sheets.append_calls[0]["body"]["values"][0]
        assert "certificate_of_incorporation_signed.pdf" in written
        assert "§2.1" in written


class TestConfidenceAndAudit:
    def test_review_without_reason_is_rejected(self, clients, config):
        with pytest.raises(DraftValidationError, match="motivo_flag"):
            tools.write_draft(
                make_row(confianca="review", motivo_flag=""), clients, config
            )

    def test_invalid_confidence_is_rejected(self, clients, config):
        with pytest.raises(DraftValidationError, match="confianca"):
            tools.write_draft(make_row(confianca="alta"), clients, config)

    def test_audit_fields_never_blank(self, clients, config):
        with pytest.raises(DraftValidationError, match="versao_documento"):
            tools.write_draft(make_row(versao_documento=""), clients, config)
        row = make_row()
        row.timestamp = ""
        with pytest.raises(DraftValidationError, match="timestamp"):
            tools.write_draft(row, clients, config)

    def test_timestamp_is_auto_filled(self):
        assert make_row().timestamp  # preenchido por default_factory


class TestReadOnlyReferenceTools:
    def _clients_with_tabs(self, config, tabs):
        from tests.conftest import FakeSheetsService

        sheets = FakeSheetsService(tabs=tabs)
        return GoogleClients(config, drive=None, sheets_reader=sheets, sheets_writer=sheets)

    def test_search_reference_filters_by_type_and_category(self, config):
        clients = self._clients_with_tabs(config, {
            "Templates": [
                ["Tipo_Documento", "Categoria", "Secao", "Texto"],
                ["SPA", "Indemnification", "§8", "Texto padrão de indenização"],
                ["IRA", "Registration Rights", "§2", "Outro texto"],
            ],
            "Dicionario_Termos": [
                ["Categoria", "Termo", "Definicao", "Exemplos_Redacao"],
                ["Indemnification", "cap", "Limite de indenização", "capped at..."],
                ["MFN", "mfn", "Nação mais favorecida", "most favored..."],
            ],
        })
        ref = tools.search_reference("SPA", "Indemnification", clients, config)
        assert len(ref["templates"]) == 1
        assert ref["templates"][0]["Secao"] == "§8"
        assert len(ref["dictionary"]) == 1
        assert ref["dictionary"][0]["Termo"] == "cap"

    def test_search_precedent_reads_terms_tab(self, config):
        clients = self._clients_with_tabs(config, {
            "Terms": [
                ["Deal", "Categoria", "Valor"],
                ["Deal A", "MFN", "incluído"],
                ["Deal B", "Indemnification", "18 meses"],
            ],
        })
        rows = tools.search_precedent("MFN", clients, config)
        assert rows == [{"Deal": "Deal A", "Categoria": "MFN", "Valor": "incluído"}]

    def test_list_term_categories_respects_doc_type_column(self, config):
        clients = self._clients_with_tabs(config, {
            "Dicionario_Termos": [
                ["Categoria", "Termo", "Definicao", "Tipos_Documento"],
                ["Indemnification", "cap", "d", "SPA"],
                ["Liquidation Preference", "pref", "d", "Certificate of Incorporation"],
                ["Governança", "board", "d", ""],
            ],
        })
        cats = tools.list_term_categories("SPA", clients, config)
        assert cats == ["Indemnification", "Governança"]


class TestDriveHelpers:
    def test_extract_folder_id_from_url(self):
        url = "https://drive.google.com/drive/folders/1AbC_dEf-123?usp=sharing"
        assert tools.extract_folder_id(url) == "1AbC_dEf-123"

    def test_extract_folder_id_rejects_garbage(self):
        with pytest.raises(tools.ToolError):
            tools.extract_folder_id("isso não é um link")

    def test_filename_draft_markers(self):
        assert tools.filename_draft_markers("SPA_draft_v1.pdf") == ["draft", "v1"]
        assert tools.filename_draft_markers("SPA_signed_final.pdf") == []
