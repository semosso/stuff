"""Testes do processamento em lote: aba `Deals`, idempotência, cobertura de
categorias e escrita em lote."""

import dataclasses

import pytest

from agent import tools
from agent.loop import (
    STATUS_FAILED,
    STATUS_INVALID,
    STATUS_PROCESSED,
    STATUS_SKIPPED,
    DealResult,
    ExtractionLoop,
)
from agent.tools import EmptyDictionaryError, GoogleClients, TermRow
from tests.conftest import FakeSheetsService
from tests.test_permissions import make_row


def clients_with(config, tabs, forbidden=("Publicado",)):
    sheets = FakeSheetsService(tabs=tabs, forbidden_tabs=forbidden)
    return GoogleClients(config, drive=None, sheets_reader=sheets, sheets_writer=sheets), sheets


DEALS_HEADER = ["Empresa", "Pasta_Documentos_Assinados", "Status"]
LINK_A = "https://drive.google.com/drive/folders/1AAAAAAAAAA"
LINK_B = "https://drive.google.com/drive/folders/1BBBBBBBBBB"


class TestListDeals:
    def test_reads_company_and_folder(self, config):
        clients, _ = clients_with(config, {"Deals": [
            DEALS_HEADER,
            ["Acme Ltda", LINK_A, "assinado"],
            ["Beta S.A.", LINK_B, "assinado"],
        ]})
        deals = tools.list_deals(clients, config)
        assert [d.company for d in deals] == ["Acme Ltda", "Beta S.A."]
        assert deals[0].folder_link == LINK_A
        assert all(d.processable for d in deals)

    def test_missing_link_is_reported_not_dropped(self, config):
        clients, _ = clients_with(config, {"Deals": [
            DEALS_HEADER,
            ["Acme Ltda", "", "assinado"],
        ]})
        deals = tools.list_deals(clients, config)
        assert len(deals) == 1  # continua no relatório
        assert not deals[0].processable
        assert "link da pasta" in deals[0].issue.lower()

    def test_invalid_link_is_reported(self, config):
        clients, _ = clients_with(config, {"Deals": [
            DEALS_HEADER,
            ["Acme Ltda", "pasta do drive do fulano", "assinado"],
        ]})
        deals = tools.list_deals(clients, config)
        assert not deals[0].processable

    def test_falls_back_to_any_column_with_a_drive_link(self, config):
        """Coluna com nome inesperado ainda é encontrada pelo conteúdo."""
        clients, _ = clients_with(config, {"Deals": [
            ["Empresa", "Coluna Com Nome Esquisito"],
            ["Acme Ltda", LINK_A],
        ]})
        deals = tools.list_deals(clients, config)
        assert deals[0].folder_link == LINK_A
        assert deals[0].processable

    def test_company_column_alias(self, config):
        clients, _ = clients_with(config, {"Deals": [
            ["Company", "Pasta"],
            ["Acme Ltda", LINK_A],
        ]})
        deals = tools.list_deals(clients, config)
        assert deals[0].company == "Acme Ltda"

    def test_blank_rows_are_ignored(self, config):
        clients, _ = clients_with(config, {"Deals": [
            DEALS_HEADER,
            ["Acme Ltda", LINK_A, "assinado"],
            ["", "", ""],
        ]})
        assert len(tools.list_deals(clients, config)) == 1


class TestIdempotency:
    def _loop(self, config, tabs):
        clients, sheets = clients_with(config, tabs)
        loop = ExtractionLoop(config, clients=clients, claude=object())
        return loop, sheets

    def test_deal_already_in_pendente_is_skipped(self, config):
        loop, _ = self._loop(config, {
            "Deals": [DEALS_HEADER, ["Acme Ltda", LINK_A, "assinado"]],
            "Pendente": [["empresa", "categoria"], ["Acme Ltda", "MFN"]],
            "Publicado": [],
        })
        summary = loop.run_batch()
        assert summary.deals[0].status == STATUS_SKIPPED
        assert "Pendente" in summary.deals[0].detail

    def test_deal_already_in_publicado_is_skipped(self, config):
        loop, _ = self._loop(config, {
            "Deals": [DEALS_HEADER, ["Acme Ltda", LINK_A, "assinado"]],
            "Pendente": [],
            "Publicado": [["Empresa", "Termo"], ["Acme Ltda", "MFN"]],
        })
        summary = loop.run_batch()
        assert summary.deals[0].status == STATUS_SKIPPED
        assert "aprovado" in summary.deals[0].detail.lower()

    def test_company_match_ignores_case_and_accents(self, config):
        loop, _ = self._loop(config, {
            "Deals": [DEALS_HEADER, ["Aurélio Participações", LINK_A, "x"]],
            "Pendente": [["empresa"], ["aurelio participacoes"]],
            "Publicado": [],
        })
        assert loop.run_batch().deals[0].status == STATUS_SKIPPED

    def test_force_reprocesses(self, config):
        loop, _ = self._loop(config, {
            "Deals": [DEALS_HEADER, ["Acme Ltda", LINK_A, "assinado"]],
            "Pendente": [["empresa"], ["Acme Ltda"]],
            "Publicado": [],
        })
        calls = []
        loop.run_deal = lambda c, f: calls.append(c) or DealResult(c, STATUS_PROCESSED)
        summary = loop.run_batch(force=True)
        assert calls == ["Acme Ltda"]
        assert summary.deals[0].status == STATUS_PROCESSED

    def test_invalid_deal_row_never_disappears(self, config):
        loop, _ = self._loop(config, {
            "Deals": [DEALS_HEADER, ["Acme Ltda", "", "assinado"]],
            "Pendente": [], "Publicado": [],
        })
        summary = loop.run_batch()
        assert summary.deals[0].status == STATUS_INVALID

    def test_one_failing_deal_does_not_stop_the_batch(self, config):
        loop, _ = self._loop(config, {
            "Deals": [
                DEALS_HEADER,
                ["Acme Ltda", LINK_A, "x"],
                ["Beta S.A.", LINK_B, "x"],
            ],
            "Pendente": [], "Publicado": [],
        })

        def run_deal(company, folder):
            if company == "Acme Ltda":
                raise RuntimeError("PDF corrompido")
            return DealResult(company, STATUS_PROCESSED)

        loop.run_deal = run_deal
        summary = loop.run_batch()
        assert summary.deals[0].status == STATUS_FAILED
        assert "PDF corrompido" in summary.deals[0].detail
        assert summary.deals[1].status == STATUS_PROCESSED

    def test_permission_error_aborts_whole_batch(self, config):
        """Erro sistêmico de escrita falharia igual nos 50 deals — aborta."""
        loop, _ = self._loop(config, {
            "Deals": [
                DEALS_HEADER,
                ["Acme Ltda", LINK_A, "x"],
                ["Beta S.A.", LINK_B, "x"],
            ],
            "Pendente": [], "Publicado": [],
        })

        def run_deal(company, folder):
            raise tools.SheetsWritePermissionError("403 na aba Pendente")

        loop.run_deal = run_deal
        summary = loop.run_batch()
        assert summary.aborted
        assert "403" in summary.aborted
        assert len(summary.deals) == 0

    def test_only_filters_to_one_deal(self, config):
        loop, _ = self._loop(config, {
            "Deals": [
                DEALS_HEADER,
                ["Acme Ltda", LINK_A, "x"],
                ["Beta S.A.", LINK_B, "x"],
            ],
            "Pendente": [], "Publicado": [],
        })
        loop.run_deal = lambda c, f: DealResult(c, STATUS_PROCESSED)
        summary = loop.run_batch(only="Beta S.A.")
        assert [d.company for d in summary.deals] == ["Beta S.A."]


class TestCategoryCoverage:
    CATEGORIES = ["MFN", "Liquidation Preference", "Indemnification"]

    def test_missing_category_becomes_explicit_not_found(self):
        model_items = [
            {"category": "MFN", "found": True, "term": "mfn", "value": "incluído",
             "summary": "s", "source_section": "§3", "confidence": "high_confidence",
             "flag_reason": "", "comparison_note": "n", "precedent_used": False},
        ]
        covered = ExtractionLoop._ensure_coverage(model_items, self.CATEGORIES)
        assert [c["category"] for c in covered] == self.CATEGORIES
        omitted = covered[1]
        assert omitted["value"] == tools.NOT_FOUND
        assert omitted["confidence"] == "review"
        assert omitted["flag_reason"]  # motivo obrigatório

    def test_omitted_category_row_passes_validation(self):
        covered = ExtractionLoop._ensure_coverage([], ["MFN"])
        row = TermRow(
            categoria=covered[0]["category"],
            termo=covered[0]["term"],
            resumo=covered[0]["summary"],
            valor=covered[0]["value"],
            documento_fonte="spa.pdf",
            secao_fonte=covered[0]["source_section"],
            confianca=covered[0]["confidence"],
            motivo_flag=covered[0]["flag_reason"],
            empresa="Acme",
            versao_documento="spa.pdf — ok",
        )
        tools.validate_term_row(row)  # não levanta

    def test_extra_category_from_model_is_discarded(self):
        items = [
            {"category": "MFN", "found": True, "term": "t", "value": "v", "summary": "s",
             "source_section": "§1", "confidence": "high_confidence", "flag_reason": "",
             "comparison_note": "", "precedent_used": False},
            {"category": "Categoria Inventada", "found": True, "term": "t", "value": "v",
             "summary": "s", "source_section": "§9", "confidence": "high_confidence",
             "flag_reason": "", "comparison_note": "", "precedent_used": False},
        ]
        covered = ExtractionLoop._ensure_coverage(items, ["MFN"])
        assert [c["category"] for c in covered] == ["MFN"]

    def test_category_name_is_normalized_to_canonical(self):
        items = [
            {"category": "mfn", "found": True, "term": "t", "value": "v", "summary": "s",
             "source_section": "§1", "confidence": "high_confidence", "flag_reason": "",
             "comparison_note": "", "precedent_used": False},
        ]
        covered = ExtractionLoop._ensure_coverage(items, ["MFN"])
        assert covered[0]["category"] == "MFN"


class TestBatchWrite:
    def test_all_rows_written_in_a_single_api_call(self, clients, config, sheets):
        rows = [make_row(termo=f"termo_{i}") for i in range(5)]
        tools.write_drafts(rows, clients, config)
        assert len(sheets.append_calls) == 1
        assert len(sheets.append_calls[0]["body"]["values"]) == 5

    def test_one_invalid_row_blocks_the_whole_batch(self, clients, config, sheets):
        """Validação de todas antes de escrever qualquer uma: nada de meio
        documento gravado."""
        rows = [make_row(), make_row(valor=""), make_row()]
        with pytest.raises(tools.DraftValidationError):
            tools.write_drafts(rows, clients, config)
        assert sheets.append_calls == []

    def test_empty_batch_is_a_noop(self, clients, config, sheets):
        assert tools.write_drafts([], clients, config) == {}
        assert sheets.append_calls == []

    def test_batch_write_still_refuses_publicado(self, clients, config):
        with pytest.raises(tools.TabWriteNotAllowedError):
            tools._append_rows(tools.PUBLICADO_TAB, [["x"], ["y"]], clients, config)


class TestEmptyDictionaryFailsLoudly:
    def test_empty_tab_raises(self, config):
        clients, _ = clients_with(config, {"Dicionario_Termos": []})
        with pytest.raises(EmptyDictionaryError, match="vazia"):
            tools.list_term_categories("SPA", clients, config)

    def test_no_category_matches_document_type_raises(self, config):
        clients, _ = clients_with(config, {"Dicionario_Termos": [
            ["Categoria", "Tipos_Documento"],
            ["Indemnification", "SPA"],
        ]})
        with pytest.raises(EmptyDictionaryError, match="Nenhuma categoria"):
            tools.list_term_categories("Certificate of Incorporation", clients, config)


class TestReadableTabsDoNotWeakenWriteGuard:
    def test_pendente_and_publicado_are_readable(self):
        assert tools.PENDENTE_TAB in tools.READABLE_TABS
        assert tools.PUBLICADO_TAB in tools.READABLE_TABS

    def test_but_publicado_is_still_not_writable(self, clients, config):
        with pytest.raises(tools.TabWriteNotAllowedError):
            tools._append_rows(tools.PUBLICADO_TAB, [["x"]], clients, config)

    def test_deals_tab_is_not_writable(self, clients, config):
        with pytest.raises(tools.TabWriteNotAllowedError):
            tools._append_rows(tools.DEALS_TAB, [["x"]], clients, config)


class TestChunking:
    def test_categories_are_split_by_configured_size(self, config):
        from agent.loop import _chunks

        sized = dataclasses.replace(config, category_batch_size=2)
        blocks = _chunks(["a", "b", "c", "d", "e"], sized.category_batch_size)
        assert blocks == [["a", "b"], ["c", "d"], ["e"]]
