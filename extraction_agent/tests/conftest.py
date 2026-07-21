"""Fakes compartilhados dos testes.

Nenhum teste toca a rede: os serviços do Google são substituídos por fakes
que gravam as chamadas recebidas e podem simular a recusa (HTTP 403) da
proteção a nível de planilha.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config  # noqa: E402
from agent.tools import GoogleClients  # noqa: E402


class FakeHttpError(Exception):
    """Imita googleapiclient.errors.HttpError o suficiente para os testes."""

    def __init__(self, status: int):
        super().__init__(f"HTTP {status}")
        self.resp = type("Resp", (), {"status": status})()


class FakeValues:
    def __init__(self, owner):
        self._owner = owner

    def append(self, spreadsheetId, range, valueInputOption, insertDataOption, body):
        self._owner.append_calls.append({"range": range, "body": body})
        tab = range.split("!")[0]
        if tab in self._owner.forbidden_tabs:
            return FakeRequest(error=FakeHttpError(403))
        return FakeRequest(result={"updates": {"updatedRows": 1}})

    def get(self, spreadsheetId, range):
        tab = range.split("!")[0]
        return FakeRequest(result={"values": self._owner.tabs.get(tab, [])})


class FakeRequest:
    def __init__(self, result=None, error=None):
        self._result = result
        self._error = error

    def execute(self):
        if self._error is not None:
            raise self._error
        return self._result


class FakeSheetsService:
    """Fake do client Sheets. `forbidden_tabs` simula a proteção da planilha:
    escrita nessas abas retorna 403, como a API real faria para a service
    account de escrita restrita à aba Pendente."""

    def __init__(self, tabs=None, forbidden_tabs=("Publicado",)):
        self.tabs = tabs or {}
        self.forbidden_tabs = set(forbidden_tabs)
        self.append_calls = []

    def spreadsheets(self):
        return self

    def values(self):
        return FakeValues(self)


@pytest.fixture
def config():
    return Config(
        anthropic_api_key="test-key",
        claude_model="claude-opus-4-8",
        google_reader_credentials_file="/dev/null",
        google_writer_credentials_file="/dev/null",
        spreadsheet_id="sheet-id",
    )


@pytest.fixture
def sheets():
    return FakeSheetsService()


@pytest.fixture
def clients(config, sheets):
    return GoogleClients(config, drive=None, sheets_reader=sheets, sheets_writer=sheets)
