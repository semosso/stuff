"""Testes da classificação de erros por origem e natureza."""

import pytest

from agent import errors, tools
from agent.errors import (
    KIND_ACTIONABLE,
    KIND_TRANSIENT,
    ORIGIN_AGENT,
    ORIGIN_CLAUDE,
    ORIGIN_DOCUMENT,
    ORIGIN_DRIVE,
    ORIGIN_SHEETS,
    classify_error,
    group_by_cause,
)


class FakeAnthropicError(Exception):
    """Imita uma exceção do SDK da Anthropic (módulo + status_code)."""

    __module__ = "anthropic"

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class FakeGoogleError(Exception):
    """Imita googleapiclient.errors.HttpError (resp.status + uri)."""

    __module__ = "googleapiclient.errors"

    def __init__(self, status, uri=""):
        super().__init__(f"HTTP {status}")
        self.resp = type("Resp", (), {"status": status})()
        self.uri = uri


class FakePdfError(Exception):
    __module__ = "pypdf.errors"


class TestClaudeErrors:
    def test_rate_limit_is_transient(self):
        info = classify_error(FakeAnthropicError("rate limited", 429))
        assert info.origin == ORIGIN_CLAUDE
        assert info.kind == KIND_TRANSIENT
        assert info.retryable
        assert "rode o lote de novo" in info.hint.lower()

    def test_server_error_is_transient(self):
        assert classify_error(FakeAnthropicError("overloaded", 529)).retryable

    def test_bad_api_key_requires_action(self):
        info = classify_error(FakeAnthropicError("unauthorized", 401))
        assert info.kind == KIND_ACTIONABLE
        assert "ANTHROPIC_API_KEY" in info.hint

    def test_bad_model_requires_action(self):
        info = classify_error(FakeAnthropicError("not found", 404))
        assert info.kind == KIND_ACTIONABLE
        assert "CLAUDE_MODEL" in info.hint

    def test_connection_error_is_transient(self):
        exc = FakeAnthropicError("connection reset")
        exc.__class__.__name__ = "APIConnectionError"
        assert classify_error(exc).retryable


class TestGoogleErrors:
    def test_drive_403_points_at_the_reader_service_account(self):
        info = classify_error(
            FakeGoogleError(403, "https://www.googleapis.com/drive/v3/files")
        )
        assert info.origin == ORIGIN_DRIVE
        assert info.kind == KIND_ACTIONABLE
        assert "reader-sa" in info.hint

    def test_drive_404_points_at_the_deals_tab(self):
        info = classify_error(
            FakeGoogleError(404, "https://www.googleapis.com/drive/v3/files")
        )
        assert info.kind == KIND_ACTIONABLE
        assert "`Deals`" in info.hint

    def test_sheets_quota_is_transient(self):
        info = classify_error(
            FakeGoogleError(429, "https://sheets.googleapis.com/v4/spreadsheets/x")
        )
        assert info.origin == ORIGIN_SHEETS
        assert info.retryable
        assert "cota" in info.hint.lower()

    def test_sheets_surface_detected_from_uri(self):
        info = classify_error(
            FakeGoogleError(403, "https://sheets.googleapis.com/v4/spreadsheets/x")
        )
        assert info.origin == ORIGIN_SHEETS


class TestDocumentAndAgentErrors:
    def test_corrupt_pdf_is_a_document_problem(self):
        info = classify_error(FakePdfError("EOF marker not found"))
        assert info.origin == ORIGIN_DOCUMENT
        assert info.kind == KIND_ACTIONABLE

    def test_unsupported_file_type(self):
        info = classify_error(tools.UnsupportedFileTypeError("arquivo.xyz"))
        assert info.origin == ORIGIN_DOCUMENT

    def test_write_permission_error_is_flagged_systemic(self):
        info = classify_error(tools.SheetsWritePermissionError("403"))
        assert info.origin == ORIGIN_SHEETS
        assert "sistêmico" in info.hint.lower()

    def test_empty_dictionary_points_at_the_readme(self):
        info = classify_error(tools.EmptyDictionaryError("vazia"))
        assert info.origin == ORIGIN_AGENT
        assert "Dicionario_Termos" in info.hint

    def test_unknown_error_defaults_to_actionable(self):
        """Não induzir a re-rodar um lote de horas sem investigar."""
        info = classify_error(ValueError("algo inesperado"))
        assert info.kind == KIND_ACTIONABLE
        assert "não classificado" in info.hint.lower()


class TestFormattingAndGrouping:
    def test_str_includes_origin_status_and_hint(self):
        info = classify_error(FakeAnthropicError("rate limited", 429))
        text = str(info)
        assert "[Claude HTTP 429]" in text
        assert "rate limited" in text

    def test_group_by_cause_buckets_same_origin_and_hint(self):
        infos = [
            classify_error(FakeGoogleError(403, "/drive/v3/files")),
            classify_error(FakeGoogleError(403, "/drive/v3/files")),
            classify_error(FakeAnthropicError("rate", 429)),
        ]
        grouped = group_by_cause(infos)
        assert len(grouped) == 2
        assert sorted(len(v) for v in grouped.values()) == [1, 2]
