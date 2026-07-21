"""Testes de permissão de escrita (exigência do prompt).

Confirma que a função de escrita NÃO consegue escrever na aba `Publicado`:
a tentativa falha de forma explícita (exceção), nunca silenciosa — tanto
pela guarda no código quanto pela recusa simulada da API do Google.
"""

import pytest

from agent import tools
from agent.tools import (
    PENDENTE_TAB,
    PUBLICADO_TAB,
    SheetsWritePermissionError,
    TabWriteNotAllowedError,
    TermRow,
)


def make_row(**overrides):
    defaults = dict(
        categoria="Liquidation Preference",
        termo="liquidation_preference",
        resumo="Preferência de liquidação de 1x, não participante.",
        valor="1x non-participating",
        documento_fonte="certificate_of_incorporation_signed.pdf",
        secao_fonte="§2.1",
        confianca="high_confidence",
        empresa="Acme Ltda",
        versao_documento="certificate_of_incorporation_signed.pdf — sem indícios de rascunho",
    )
    defaults.update(overrides)
    return TermRow(**defaults)


class TestWriteRestrictedToPendente:
    def test_writing_to_publicado_fails_explicitly(self, clients, config):
        """A guarda de código recusa `Publicado` antes de tocar a API."""
        with pytest.raises(TabWriteNotAllowedError, match="Pendente"):
            tools._append_row(PUBLICADO_TAB, ["x"], clients, config)
        # Falha explícita E sem efeito colateral: a API nunca foi chamada.
        assert clients.sheets_writer.append_calls == []

    def test_writing_to_any_other_tab_fails(self, clients, config):
        for tab in ("Deals", "Terms", "Templates", "Dicionario_Termos", "Publicado "):
            with pytest.raises(TabWriteNotAllowedError):
                tools._append_row(tab, ["x"], clients, config)

    def test_google_403_is_raised_not_swallowed(self, clients, config, sheets):
        """Se a proteção da planilha recusar (403), o erro sobe com contexto
        claro — nunca é engolido como sucesso silencioso."""
        sheets.forbidden_tabs = {PENDENTE_TAB}  # simula proteção mal configurada
        with pytest.raises(SheetsWritePermissionError, match="403"):
            tools.write_draft(make_row(), clients, config)

    def test_write_draft_targets_pendente_only(self, clients, config, sheets):
        tools.write_draft(make_row(), clients, config)
        assert len(sheets.append_calls) == 1
        assert sheets.append_calls[0]["range"].startswith(f"{PENDENTE_TAB}!")

    def test_write_draft_has_no_tab_parameter(self):
        """A API pública de escrita não aceita escolher a aba de destino —
        nem por engano, nem por instrução do usuário."""
        import inspect

        params = inspect.signature(tools.write_draft).parameters
        assert "tab" not in params
        assert "range" not in params
