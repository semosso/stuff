"""Leitura de configuração a partir de variáveis de ambiente.

Nenhuma credencial é hardcoded neste projeto. Todas as chaves vêm do
ambiente (ou de um arquivo .env carregado via python-dotenv). Veja
.env.example para a lista de variáveis necessárias.
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Variável de ambiente obrigatória ausente ou inválida."""


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(
            f"Variável de ambiente obrigatória não definida: {name}. "
            "Veja .env.example para a lista completa."
        )
    return value


def _int_env(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} deve ser um número inteiro; recebido: {raw!r}") from exc
    if value < minimum:
        raise ConfigError(f"{name} deve ser >= {minimum}; recebido: {value}")
    return value


@dataclass(frozen=True)
class Config:
    # API do Claude
    anthropic_api_key: str
    claude_model: str

    # Google Workspace
    # Credencial de LEITURA: Drive (readonly) + Sheets (readonly).
    google_reader_credentials_file: str
    # Credencial de ESCRITA: separada da leitura, com permissão de edição
    # restrita à aba `Pendente` (configurada na própria planilha — ver README).
    google_writer_credentials_file: str
    spreadsheet_id: str

    # Quantas categorias de termo vão em cada chamada ao modelo. Valores
    # maiores reduzem custo e tempo; valores menores dão mais atenção do
    # modelo a cada termo. Ver README, seção "Processamento em lote".
    category_batch_size: int = 5

    # Nomes das colunas na aba `Deals`. Se não bater, o código ainda tenta
    # aliases conhecidos e, para a pasta, qualquer coluna com link do Drive.
    deals_company_column: str = "Empresa"
    deals_folder_column: str = "Pasta_Documentos_Assinados"

    reader_scopes: tuple = field(
        default=(
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        )
    )
    writer_scopes: tuple = field(
        default=("https://www.googleapis.com/auth/spreadsheets",)
    )


def load_config() -> Config:
    return Config(
        anthropic_api_key=_required("ANTHROPIC_API_KEY"),
        claude_model=os.environ.get("CLAUDE_MODEL", "claude-opus-4-8").strip(),
        google_reader_credentials_file=_required("GOOGLE_READER_CREDENTIALS_FILE"),
        google_writer_credentials_file=_required("GOOGLE_WRITER_CREDENTIALS_FILE"),
        spreadsheet_id=_required("SPREADSHEET_ID"),
        category_batch_size=_int_env("CATEGORY_BATCH_SIZE", 5),
        deals_company_column=os.environ.get("DEALS_COMPANY_COLUMN", "Empresa").strip(),
        deals_folder_column=os.environ.get(
            "DEALS_FOLDER_COLUMN", "Pasta_Documentos_Assinados"
        ).strip(),
    )
