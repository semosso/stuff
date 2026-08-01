"""Classificação de erros por ORIGEM e por NATUREZA.

Num lote de 50 deals que roda de madrugada, o relatório da manhã precisa
responder duas perguntas antes de qualquer outra:

  - De quem foi a falha? (Claude, Google Drive, Google Sheets, o documento)
  - Adianta rodar de novo, ou preciso arrumar alguma coisa antes?

A detecção é por "duck typing" (atributos e módulo da exceção), não por
`isinstance`: assim este módulo não precisa importar `anthropic` nem
`googleapiclient`, e continua funcionando se uma dessas bibliotecas mudar
a hierarquia de exceções.
"""

from __future__ import annotations

from dataclasses import dataclass

ORIGIN_CLAUDE = "Claude"
ORIGIN_DRIVE = "Google Drive"
ORIGIN_SHEETS = "Google Sheets"
ORIGIN_DOCUMENT = "Documento"
ORIGIN_AGENT = "Agente"

# Transitório: rodar de novo tem chance de funcionar (rate limit, 5xx, rede).
KIND_TRANSIENT = "transitorio"
# Exige ação: rodar de novo dá exatamente o mesmo erro (permissão, 404, PDF ruim).
KIND_ACTIONABLE = "exige_acao"


@dataclass
class ErrorInfo:
    origin: str
    kind: str
    message: str
    hint: str = ""
    status: int | None = None

    @property
    def retryable(self) -> bool:
        return self.kind == KIND_TRANSIENT

    def __str__(self) -> str:
        status = f" HTTP {self.status}" if self.status else ""
        hint = f" — {self.hint}" if self.hint else ""
        return f"[{self.origin}{status}] {self.message}{hint}"


def _module_of(exc: Exception) -> str:
    return (type(exc).__module__ or "").lower()


def _http_status(exc: Exception) -> int | None:
    """Status HTTP, venha ele da Anthropic (`status_code`) ou do Google (`resp.status`)."""
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return status
    resp = getattr(exc, "resp", None)
    status = getattr(resp, "status", None)
    if isinstance(status, int):
        return status
    return None


def _google_surface(exc: Exception) -> str:
    """Drive ou Sheets, a partir da URI da requisição que falhou."""
    uri = str(getattr(exc, "uri", "") or "").lower()
    if "sheets.googleapis" in uri or "spreadsheets" in uri:
        return ORIGIN_SHEETS
    if "drive.googleapis" in uri or "/drive/" in uri:
        return ORIGIN_DRIVE
    return ORIGIN_DRIVE  # a maior parte do tráfego do agente é leitura do Drive


def _classify_claude(exc: Exception, status: int | None) -> ErrorInfo:
    name = type(exc).__name__
    message = str(exc) or name

    if status == 429:
        return ErrorInfo(
            ORIGIN_CLAUDE, KIND_TRANSIENT, message,
            "Rate limit da API do Claude. O SDK já tentou novamente; "
            "rode o lote de novo mais tarde — a idempotência não reprocessa "
            "o que já entrou.",
            status,
        )
    if status is not None and status >= 500:
        return ErrorInfo(
            ORIGIN_CLAUDE, KIND_TRANSIENT, message,
            "Instabilidade da API do Claude. Rode de novo mais tarde.", status,
        )
    if status in (401, 403):
        return ErrorInfo(
            ORIGIN_CLAUDE, KIND_ACTIONABLE, message,
            "Chave da API rejeitada. Confira ANTHROPIC_API_KEY no .env.", status,
        )
    if status == 404:
        return ErrorInfo(
            ORIGIN_CLAUDE, KIND_ACTIONABLE, message,
            "Modelo inexistente. Confira CLAUDE_MODEL no .env.", status,
        )
    if status == 400:
        return ErrorInfo(
            ORIGIN_CLAUDE, KIND_ACTIONABLE, message,
            "Requisição inválida — provavelmente documento longo demais para "
            "o contexto, ou parâmetro não suportado pelo modelo escolhido.",
            status,
        )
    if "connection" in name.lower() or "timeout" in name.lower():
        return ErrorInfo(
            ORIGIN_CLAUDE, KIND_TRANSIENT, message,
            "Falha de rede ao falar com a API do Claude. Rode de novo.",
        )
    return ErrorInfo(ORIGIN_CLAUDE, KIND_TRANSIENT, message, "", status)


def _classify_google(exc: Exception, status: int | None) -> ErrorInfo:
    surface = _google_surface(exc)
    message = str(exc) or type(exc).__name__

    if status in (401, 403):
        if surface == ORIGIN_DRIVE:
            hint = (
                "A service account de LEITURA não tem acesso a esta pasta. "
                "Compartilhe a pasta do deal no Drive com o e-mail da "
                "reader-sa como Leitor."
            )
        else:
            hint = (
                "A service account não tem permissão nesta aba. Se for "
                "escrita, confira a proteção de páginas da planilha "
                "(ver README)."
            )
        return ErrorInfo(surface, KIND_ACTIONABLE, message, hint, status)
    if status == 404:
        return ErrorInfo(
            surface, KIND_ACTIONABLE, message,
            "Pasta ou arquivo não existe mais (movido, renomeado ou apagado). "
            "Confira o link na aba `Deals`.",
            status,
        )
    if status == 429:
        return ErrorInfo(
            surface, KIND_TRANSIENT, message,
            "Cota do Google estourada (o Sheets aceita ~60 escritas/minuto). "
            "Espere um minuto e rode de novo.",
            status,
        )
    if status is not None and status >= 500:
        return ErrorInfo(
            surface, KIND_TRANSIENT, message,
            "Instabilidade do Google. Rode de novo mais tarde.", status,
        )
    return ErrorInfo(surface, KIND_TRANSIENT, message, "", status)


def classify_error(exc: Exception) -> ErrorInfo:
    """Devolve origem, natureza e dica de correção para qualquer exceção."""
    # Importa aqui para evitar ciclo (tools importa config, não errors).
    from agent import tools

    if isinstance(exc, tools.SheetsWritePermissionError):
        return ErrorInfo(
            ORIGIN_SHEETS, KIND_ACTIONABLE, str(exc),
            "Erro sistêmico: falharia em todos os deals. O lote foi abortado "
            "de propósito.",
        )
    if isinstance(exc, tools.TabWriteNotAllowedError):
        return ErrorInfo(
            ORIGIN_AGENT, KIND_ACTIONABLE, str(exc),
            "Guarda de código: o agente só escreve na aba `Pendente`.",
        )
    if isinstance(exc, tools.UnsupportedFileTypeError):
        return ErrorInfo(
            ORIGIN_DOCUMENT, KIND_ACTIONABLE, str(exc),
            "Converta para PDF/DOCX ou remova o arquivo da pasta.",
        )
    if isinstance(exc, tools.EmptyDictionaryError):
        return ErrorInfo(
            ORIGIN_AGENT, KIND_ACTIONABLE, str(exc),
            "Preencha a aba `Dicionario_Termos` (ver README).",
        )
    if isinstance(exc, tools.DraftValidationError):
        return ErrorInfo(
            ORIGIN_AGENT, KIND_ACTIONABLE, str(exc),
            "Guard rail barrou a linha antes da escrita — nada foi gravado.",
        )

    module = _module_of(exc)
    status = _http_status(exc)

    if module.startswith("anthropic"):
        return _classify_claude(exc, status)
    if module.startswith("googleapiclient") or module.startswith("google"):
        return _classify_google(exc, status)
    if module.startswith("pypdf") or "docx" in module:
        return ErrorInfo(
            ORIGIN_DOCUMENT, KIND_ACTIONABLE, str(exc) or type(exc).__name__,
            "Arquivo ilegível ou corrompido. Abra manualmente para conferir.",
        )
    if isinstance(exc, tools.ToolError):
        return ErrorInfo(ORIGIN_AGENT, KIND_ACTIONABLE, str(exc))

    # Não reconhecido: trata como exige ação para não induzir a re-rodar
    # um lote de horas à toa.
    return ErrorInfo(
        ORIGIN_AGENT, KIND_ACTIONABLE,
        f"{type(exc).__name__}: {exc}",
        "Erro não classificado — vale investigar antes de rodar de novo.",
    )


def group_by_cause(infos: list) -> dict:
    """Agrupa erros por (origem, natureza) para o resumo final."""
    grouped: dict = {}
    for info in infos:
        grouped.setdefault((info.origin, info.kind, info.hint), []).append(info)
    return grouped
