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


def _float_env(name: str, default: float, minimum: float = 0.0) -> float:
    raw = os.environ.get(name, "").strip().replace(",", ".")
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} deve ser um número; recebido: {raw!r}") from exc
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

    # ---- Otimizações de custo (REVERSÍVEIS por uma variável cada) --------
    # Profundidade de raciocínio do modelo. O padrão da API é "high"; aqui
    # usamos "medium" para cortar tokens de output (que custam 5x o input e
    # incluem o thinking). REVERTER: CLAUDE_EFFORT=high no .env.
    effort: str = "medium"

    # Quantos caracteres do documento vão para a etapa de CLASSIFICAÇÃO.
    # O tipo do documento aparece nas primeiras páginas e a assinatura nas
    # últimas, então mandamos início + fim em vez do texto inteiro.
    # REVERTER (mandar documento completo): CLASSIFY_CHAR_LIMIT=0 no .env.
    classify_char_limit: int = 12000

    # ---- Checkpoint interativo -------------------------------------------
    pause_every_deals: int = 0        # 0 = desligado
    budget_usd: float = 0.0           # 0 = sem orçamento
    budget_warn_pct: int = 80
    checkpoint_no_tty: str = "parar"  # "parar" | "continuar"

    # Preços por milhão de tokens, usados só para a ESTIMATIVA de custo.
    # Padrão: claude-opus-4-8. Ajuste se trocar de modelo.
    price_input_per_mtok: float = 5.0
    price_output_per_mtok: float = 25.0

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


VALID_EFFORTS = ("low", "medium", "high", "xhigh", "max")
VALID_NO_TTY = ("parar", "continuar")


def load_config() -> Config:
    effort = os.environ.get("CLAUDE_EFFORT", "medium").strip().lower()
    if effort not in VALID_EFFORTS:
        raise ConfigError(
            f"CLAUDE_EFFORT inválido: {effort!r}. Valores aceitos: {VALID_EFFORTS}."
        )

    no_tty = os.environ.get("CHECKPOINT_SEM_TERMINAL", "parar").strip().lower()
    if no_tty not in VALID_NO_TTY:
        raise ConfigError(
            f"CHECKPOINT_SEM_TERMINAL inválido: {no_tty!r}. "
            f"Valores aceitos: {VALID_NO_TTY}."
        )

    return Config(
        anthropic_api_key=_required("ANTHROPIC_API_KEY"),
        claude_model=os.environ.get("CLAUDE_MODEL", "claude-opus-4-8").strip(),
        google_reader_credentials_file=_required("GOOGLE_READER_CREDENTIALS_FILE"),
        google_writer_credentials_file=_required("GOOGLE_WRITER_CREDENTIALS_FILE"),
        spreadsheet_id=_required("SPREADSHEET_ID"),
        category_batch_size=_int_env("CATEGORY_BATCH_SIZE", 5),
        effort=effort,
        classify_char_limit=_int_env("CLASSIFY_CHAR_LIMIT", 12000, minimum=0),
        pause_every_deals=_int_env("PAUSE_EVERY_DEALS", 0, minimum=0),
        budget_usd=_float_env("BUDGET_USD", 0.0),
        budget_warn_pct=_int_env("BUDGET_WARN_PCT", 80, minimum=1),
        checkpoint_no_tty=no_tty,
        price_input_per_mtok=_float_env("PRICE_INPUT_PER_MTOK", 5.0),
        price_output_per_mtok=_float_env("PRICE_OUTPUT_PER_MTOK", 25.0),
        deals_company_column=os.environ.get("DEALS_COMPANY_COLUMN", "Empresa").strip(),
        deals_folder_column=os.environ.get(
            "DEALS_FOLDER_COLUMN", "Pasta_Documentos_Assinados"
        ).strip(),
    )
