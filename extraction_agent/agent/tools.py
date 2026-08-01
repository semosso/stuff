"""Ferramentas do agente de extração.

Acesso a dados:
  - Google Drive (leitura): lista e lê os documentos do deal.
  - Google Sheets (leitura): `Deals`, `Terms`, `Templates`, `Dicionario_Termos`
    e, para controle de idempotência, `Pendente` e `Publicado`.
  - Google Sheets (escrita): APENAS a aba `Pendente`.

Ler `Pendente`/`Publicado` NÃO afrouxa a restrição de escrita: leitura usa a
credencial readonly, escrita passa obrigatoriamente por `_append_rows`, que
recusa qualquer aba != `Pendente`.

A restrição de escrita é aplicada em DUAS camadas:
  1. Nível de permissão do Google Sheets: a service account de escrita só
     tem edição liberada na aba `Pendente` (as demais abas são protegidas
     na planilha — ver README). Uma tentativa de escrita fora dela falha
     com HTTP 403 vindo da API do Google.
  2. Nível de código: `_append_rows` recusa qualquer aba diferente de
     `Pendente` antes mesmo de chamar a API, com erro explícito.

Nenhuma das duas camadas é silenciosa: ambas levantam exceção.
"""

from __future__ import annotations

import datetime
import io
import re
import unicodedata
from dataclasses import dataclass, field, asdict

from config import Config

PENDENTE_TAB = "Pendente"
PUBLICADO_TAB = "Publicado"
DEALS_TAB = "Deals"

# Abas que o agente pode LER. A escrita continua restrita a `Pendente`
# independentemente desta lista (ver `_append_rows`).
READABLE_TABS = (
    DEALS_TAB,
    "Terms",
    "Templates",
    "Dicionario_Termos",
    PENDENTE_TAB,
    PUBLICADO_TAB,
)

NOT_FOUND = "not_found"
CONFIDENCE_LEVELS = ("high_confidence", "review")

DRAFT_FILENAME_MARKERS = ("draft", "rascunho", "redline", "v1", "v2", "wip")

COMPANY_COLUMN_ALIASES = ("Empresa", "Company", "Nome", "Deal", "Startup")
FOLDER_COLUMN_ALIASES = (
    "Pasta_Documentos_Assinados",
    "Pasta",
    "Pasta_Drive",
    "Documentos_Assinados",
    "Drive",
    "Link",
    "Folder",
)


class ToolError(Exception):
    """Erro genérico de ferramenta."""


class TabWriteNotAllowedError(ToolError):
    """Tentativa de escrita fora da aba `Pendente`."""


class DraftValidationError(ToolError):
    """Linha de rascunho inválida (campo obrigatório ausente)."""


class SheetsWritePermissionError(ToolError):
    """A API do Google recusou a escrita (proteção a nível de planilha)."""


class UnsupportedFileTypeError(ToolError):
    """Tipo de arquivo que o agente não sabe ler."""


class EmptyDictionaryError(ToolError):
    """`Dicionario_Termos` não tem categoria aplicável — falha explícita.

    Sem categorias o agente escreveria zero linhas e o run "passaria" sem
    nada extraído. Vazio silencioso é falha do agente (§1.2).
    """


# ---------------------------------------------------------------------------
# Serviços Google (construídos sob demanda; injetáveis nos testes)
# ---------------------------------------------------------------------------

def _build_service(api: str, version: str, credentials_file: str, scopes: tuple):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=list(scopes)
    )
    return build(api, version, credentials=creds, cache_discovery=False)


class GoogleClients:
    """Constrói e guarda os três clientes: Drive (ro), Sheets (ro), Sheets (rw).

    A credencial de escrita é SEPARADA da de leitura (exigência do prompt):
    mesmo que o código tivesse um bug, a credencial de leitura não consegue
    escrever em lugar nenhum, e a de escrita só edita `Pendente`.
    """

    def __init__(self, config: Config, drive=None, sheets_reader=None, sheets_writer=None):
        self._config = config
        self._drive = drive
        self._sheets_reader = sheets_reader
        self._sheets_writer = sheets_writer

    @property
    def drive(self):
        if self._drive is None:
            self._drive = _build_service(
                "drive", "v3",
                self._config.google_reader_credentials_file,
                self._config.reader_scopes,
            )
        return self._drive

    @property
    def sheets_reader(self):
        if self._sheets_reader is None:
            self._sheets_reader = _build_service(
                "sheets", "v4",
                self._config.google_reader_credentials_file,
                self._config.reader_scopes,
            )
        return self._sheets_reader

    @property
    def sheets_writer(self):
        if self._sheets_writer is None:
            self._sheets_writer = _build_service(
                "sheets", "v4",
                self._config.google_writer_credentials_file,
                self._config.writer_scopes,
            )
        return self._sheets_writer


# ---------------------------------------------------------------------------
# Helpers de normalização
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    """Minúsculas, sem acento, sem espaços nas pontas."""
    text = (text or "").strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def _get_field(row: dict, *candidates: str) -> str:
    """Valor da primeira coluna existente entre os candidatos (case/acento-insensível)."""
    normalized = {_norm(k): v for k, v in row.items()}
    for candidate in candidates:
        if not candidate:
            continue
        value = normalized.get(_norm(candidate))
        if value and str(value).strip():
            return str(value).strip()
    return ""


# ---------------------------------------------------------------------------
# Drive: listar e ler documentos
# ---------------------------------------------------------------------------

def extract_folder_id(folder_link: str) -> str:
    """Extrai o ID de uma URL de pasta do Drive (ou aceita o ID puro)."""
    match = re.search(r"/folders/([A-Za-z0-9_-]+)", folder_link)
    if match:
        return match.group(1)
    match = re.search(r"[?&]id=([A-Za-z0-9_-]+)", folder_link)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}", folder_link):
        return folder_link
    raise ToolError(f"Não foi possível extrair o ID da pasta de: {folder_link!r}")


def list_files(folder_link: str, clients: GoogleClients) -> list[dict]:
    """Lista os arquivos da pasta do Drive do deal.

    Retorna [{"id", "name", "mimeType"}], sem descartar nada exceto
    subpastas: arquivos de tipo desconhecido também são retornados, para
    que o loop os registre como `not_classified` em vez de ignorá-los
    silenciosamente.
    """
    folder_id = extract_folder_id(folder_link)
    files: list[dict] = []
    page_token = None
    while True:
        response = (
            clients.drive.files()
            .list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        for item in response.get("files", []):
            # Subpastas não são documentos; entrariam como `not_classified`
            # e poluiriam a fila de revisão.
            if item.get("mimeType") == "application/vnd.google-apps.folder":
                continue
            files.append(item)
        page_token = response.get("nextPageToken")
        if not page_token:
            return files


def read_document(file_id: str, file_name: str, mime_type: str, clients: GoogleClients) -> str:
    """Extrai o texto de um PDF, DOCX ou Google Doc."""
    if mime_type == "application/vnd.google-apps.document":
        data = (
            clients.drive.files()
            .export(fileId=file_id, mimeType="text/plain")
            .execute()
        )
        return data.decode("utf-8") if isinstance(data, bytes) else data

    data = clients.drive.files().get_media(fileId=file_id).execute()

    if mime_type == "application/pdf" or file_name.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            pages.append(f"[página {i}]\n{page.extract_text() or ''}")
        return "\n\n".join(pages)

    if mime_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ) or file_name.lower().endswith(".docx"):
        import docx

        document = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in document.paragraphs)

    raise UnsupportedFileTypeError(
        f"Tipo de arquivo não suportado: {file_name!r} ({mime_type}). "
        "O arquivo deve entrar na fila de revisão como 'not_classified'."
    )


def filename_draft_markers(file_name: str) -> list[str]:
    """Indícios, no nome do arquivo, de que não é a versão final assinada."""
    lowered = file_name.lower()
    return [m for m in DRAFT_FILENAME_MARKERS if m in lowered]


# ---------------------------------------------------------------------------
# Sheets: leitura (read-only)
# ---------------------------------------------------------------------------

def _read_tab(tab: str, clients: GoogleClients, config: Config) -> list[dict]:
    """Lê uma aba e retorna as linhas como dicts (header na linha 1)."""
    if tab not in READABLE_TABS:
        raise ToolError(f"Leitura não prevista para a aba {tab!r}.")
    result = (
        clients.sheets_reader.spreadsheets()
        .values()
        .get(spreadsheetId=config.spreadsheet_id, range=f"{tab}!A:Z")
        .execute()
    )
    values = result.get("values", [])
    if not values:
        return []
    header = [h.strip() for h in values[0]]
    rows = []
    for raw in values[1:]:
        row = {header[i]: (raw[i] if i < len(raw) else "") for i in range(len(header))}
        rows.append(row)
    return rows


def search_reference(
    document_type: str, term_category: str, clients: GoogleClients, config: Config
) -> dict:
    """Busca o texto de comparação nas abas `Templates` e `Dicionario_Termos`.

    Read-only. Retorna {"templates": [...], "dictionary": [...]}, cada item
    com as colunas originais da planilha, para citação lado a lado.
    """
    templates = [
        row
        for row in _read_tab("Templates", clients, config)
        if _norm(row.get("Tipo_Documento")) in ("", _norm(document_type))
        and (
            not row.get("Categoria")
            or _norm(row.get("Categoria")) == _norm(term_category)
        )
    ]
    dictionary = [
        row
        for row in _read_tab("Dicionario_Termos", clients, config)
        if _norm(row.get("Categoria")) == _norm(term_category)
    ]
    return {"templates": templates, "dictionary": dictionary}


def search_precedent(
    term_category: str, clients: GoogleClients, config: Config, limit: int = 10
) -> list[dict]:
    """Busca como o termo apareceu em deals já aprovados (aba `Terms`).

    Read-only; usado apenas como contexto de comparação adicional.
    """
    rows = [
        row
        for row in _read_tab("Terms", clients, config)
        if _norm(row.get("Categoria")) == _norm(term_category)
    ]
    return rows[:limit]


def list_term_categories(document_type: str, clients: GoogleClients, config: Config) -> list[str]:
    """Categorias de termo relevantes ao tipo de documento, via `Dicionario_Termos`.

    Se o dicionário tiver a coluna opcional `Tipos_Documento` (lista separada
    por vírgula), filtra por ela; sem a coluna, todas as categorias são
    consideradas relevantes — e termos ausentes sairão como `not_found`
    explícito, nunca omitidos.

    Levanta `EmptyDictionaryError` se não sobrar nenhuma categoria: um run
    que não extrai nada precisa falhar alto, não passar em silêncio.
    """
    rows = _read_tab("Dicionario_Termos", clients, config)
    if not rows:
        raise EmptyDictionaryError(
            "A aba `Dicionario_Termos` está vazia. Sem categorias o agente não "
            "extrairia nada e o run terminaria sem escrever linha alguma. "
            "Preencha o dicionário antes de rodar (ver README)."
        )

    categories: list[str] = []
    for row in rows:
        category = (row.get("Categoria") or "").strip()
        if not category or category in categories:
            continue
        doc_types = (row.get("Tipos_Documento") or "").strip()
        if doc_types:
            allowed = [_norm(t) for t in doc_types.split(",")]
            if _norm(document_type) not in allowed:
                continue
        categories.append(category)

    if not categories:
        raise EmptyDictionaryError(
            f"Nenhuma categoria do `Dicionario_Termos` se aplica ao tipo de "
            f"documento {document_type!r}. Verifique a coluna `Tipos_Documento` "
            "— se ela não previr este tipo, nada será extraído."
        )
    return categories


# ---------------------------------------------------------------------------
# Sheets: aba `Deals` (fonte dos deals a processar) e idempotência
# ---------------------------------------------------------------------------

@dataclass
class DealEntry:
    """Uma linha da aba `Deals`.

    `issue` preenchido significa que o deal não pode ser processado — ele
    ainda assim aparece no relatório final, nunca é descartado em silêncio.
    """

    company: str
    folder_link: str
    row_number: int
    issue: str = ""

    @property
    def processable(self) -> bool:
        return not self.issue


def _find_folder_link(row: dict) -> str:
    """Fallback: qualquer coluna cujo valor pareça um link de pasta do Drive."""
    for value in row.values():
        text = str(value or "").strip()
        if "drive.google.com" in text or "/folders/" in text:
            return text
    return ""


def list_deals(clients: GoogleClients, config: Config) -> list[DealEntry]:
    """Lê a aba `Deals` e devolve os deals a processar, na ordem da planilha.

    Resolve as colunas de empresa e pasta pelo nome configurado, depois por
    aliases conhecidos e, para a pasta, por qualquer coluna com um link do
    Drive. Linhas sem empresa ou sem link voltam com `issue` preenchido.
    """
    entries: list[DealEntry] = []
    for index, row in enumerate(_read_tab(DEALS_TAB, clients, config), start=2):
        if not any(str(v or "").strip() for v in row.values()):
            continue  # linha totalmente em branco

        company = _get_field(row, config.deals_company_column, *COMPANY_COLUMN_ALIASES)
        folder = _get_field(row, config.deals_folder_column, *FOLDER_COLUMN_ALIASES)
        if not folder:
            folder = _find_folder_link(row)

        issue = ""
        if not company:
            issue = (
                f"Linha {index}: coluna de empresa não encontrada ou vazia "
                f"(esperada {config.deals_company_column!r})."
            )
        elif not folder:
            issue = (
                f"Linha {index}: link da pasta de documentos assinados ausente "
                f"(esperada coluna {config.deals_folder_column!r})."
            )
        else:
            try:
                extract_folder_id(folder)
            except ToolError as exc:
                issue = f"Linha {index}: {exc}"

        entries.append(
            DealEntry(
                company=company or f"(sem empresa — linha {index})",
                folder_link=folder,
                row_number=index,
                issue=issue,
            )
        )
    return entries


def list_processed_companies(clients: GoogleClients, config: Config) -> dict[str, set[str]]:
    """Empresas que já têm linhas em `Pendente` e/ou `Publicado`.

    Usado para idempotência: re-rodar o lote não pode duplicar rascunhos,
    nem ressuscitar como pendente um deal que o Legal já aprovou.
    """
    processed: dict[str, set[str]] = {PENDENTE_TAB: set(), PUBLICADO_TAB: set()}
    for tab in (PENDENTE_TAB, PUBLICADO_TAB):
        for row in _read_tab(tab, clients, config):
            company = _get_field(row, config.deals_company_column, *COMPANY_COLUMN_ALIASES)
            if company:
                processed[tab].add(_norm(company))
    return processed


# ---------------------------------------------------------------------------
# Sheets: escrita de rascunho (APENAS aba Pendente)
# ---------------------------------------------------------------------------

DRAFT_COLUMNS = (
    "categoria",
    "termo",
    "resumo",
    "valor",
    "documento_fonte",
    "secao_fonte",
    "confianca",
    "nota_comparacao",
    "motivo_flag",
    "precedente_consultado",
    "empresa",
    "timestamp",
    "versao_documento",
)


@dataclass
class TermRow:
    """Uma linha de rascunho para a aba `Pendente` (formato da Seção 2.3
    do canary_agent_instructions.md + campos de auditoria da Seção 5)."""

    categoria: str
    termo: str
    resumo: str
    valor: str
    documento_fonte: str
    secao_fonte: str
    confianca: str
    empresa: str
    versao_documento: str
    nota_comparacao: str = ""
    motivo_flag: str = ""
    precedente_consultado: bool = False
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def to_values(self) -> list:
        data = asdict(self)
        data["precedente_consultado"] = "sim" if self.precedente_consultado else "nao"
        return [data[col] for col in DRAFT_COLUMNS]


def validate_term_row(row: TermRow) -> None:
    """Aplica os guard rails antes de qualquer escrita. Falha explícita.

    - Valor nunca em branco: ausência é `not_found`, não campo vazio (§1.2).
    - Citação obrigatória: documento fonte + seção fonte (§1.1).
    - Confiança restrita a high_confidence/review; `review` exige motivo (§1.4).
    - Timestamp e versão do documento nunca em branco (§5).
    """
    def missing(field_name: str, why: str) -> DraftValidationError:
        return DraftValidationError(
            f"Rascunho rejeitado — campo obrigatório ausente/inválido: "
            f"{field_name!r}. {why} Linha: {row.categoria!r}/{row.termo!r}"
        )

    if not row.categoria.strip():
        raise missing("categoria", "Toda linha precisa de categoria.")
    if not row.termo.strip():
        raise missing("termo", "Toda linha precisa do nome do termo.")
    if not row.valor.strip():
        raise missing(
            "valor",
            f"Um campo vazio sem explicação é falha do agente; use {NOT_FOUND!r} "
            "quando o termo não existir no documento.",
        )
    if not row.documento_fonte.strip():
        raise missing("documento_fonte", "Nenhuma afirmação sem citação rastreável.")
    if not row.secao_fonte.strip():
        raise missing(
            "secao_fonte",
            "Nenhuma afirmação sem citação rastreável (documento + seção). "
            f"Para {NOT_FOUND!r}, registre o escopo verificado "
            "(ex.: 'documento completo — termo não localizado').",
        )
    if row.confianca not in CONFIDENCE_LEVELS:
        raise missing("confianca", f"Valores aceitos: {CONFIDENCE_LEVELS}.")
    if row.confianca == "review" and not row.motivo_flag.strip():
        raise missing("motivo_flag", "Toda linha `review` precisa do motivo do flag (§1.4).")
    if not row.timestamp.strip():
        raise missing("timestamp", "Campo de auditoria nunca fica em branco (§5).")
    if not row.versao_documento.strip():
        raise missing("versao_documento", "Campo de auditoria nunca fica em branco (§5).")
    if not row.empresa.strip():
        raise missing("empresa", "Sem empresa a linha não é rastreável nem idempotente.")


def _append_rows(tab: str, values_list: list[list], clients: GoogleClients, config: Config) -> dict:
    """Única função que toca a API de escrita do Sheets.

    Recusa qualquer aba != Pendente ANTES de chamar a API. A proteção a
    nível de planilha (README) é a segunda camada, caso este código seja
    contornado. Escreve todas as linhas numa chamada só — com milhares de
    termos, uma chamada por linha estoura a cota de escrita do Google.
    """
    if tab != PENDENTE_TAB:
        raise TabWriteNotAllowedError(
            f"Escrita recusada: este agente só escreve na aba {PENDENTE_TAB!r}. "
            f"Aba solicitada: {tab!r}. Isso vale mesmo por instrução do usuário."
        )
    if not values_list:
        return {}
    try:
        return (
            clients.sheets_writer.spreadsheets()
            .values()
            .append(
                spreadsheetId=config.spreadsheet_id,
                range=f"{tab}!A:{chr(ord('A') + len(DRAFT_COLUMNS) - 1)}",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": values_list},
            )
            .execute()
        )
    except Exception as exc:  # noqa: BLE001 — re-levantado com contexto, nunca engolido
        status = getattr(getattr(exc, "resp", None), "status", None)
        if status in (401, 403):
            raise SheetsWritePermissionError(
                f"A API do Google recusou a escrita na aba {tab!r} "
                f"(HTTP {status}). A proteção a nível de planilha está ativa; "
                "verifique se a credencial de escrita tem edição liberada "
                f"apenas em {PENDENTE_TAB!r}."
            ) from exc
        raise


def _append_row(tab: str, values: list, clients: GoogleClients, config: Config) -> dict:
    """Atalho de uma linha só (mantido para chamadas pontuais e testes)."""
    return _append_rows(tab, [values], clients, config)


def write_draft(term_row: TermRow, clients: GoogleClients, config: Config) -> dict:
    """Escreve uma linha de rascunho na aba `Pendente`. Nunca em `Publicado`."""
    return write_drafts([term_row], clients, config)


def write_drafts(term_rows: list[TermRow], clients: GoogleClients, config: Config) -> dict:
    """Escreve várias linhas de rascunho numa única chamada.

    Valida TODAS as linhas antes de escrever qualquer uma: uma linha
    inválida no meio do lote não pode deixar metade do documento gravado.
    """
    if not term_rows:
        return {}
    for row in term_rows:
        validate_term_row(row)
    return _append_rows(
        PENDENTE_TAB, [r.to_values() for r in term_rows], clients, config
    )
