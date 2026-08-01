"""Contagem de tokens e estimativa de custo.

IMPORTANTE: a API do Claude não informa saldo nem quanto falta para um
limite de gasto — isso não existe na resposta. O que vem em cada chamada é
quantos tokens ELA consumiu. Portanto o número aqui é uma **estimativa
calculada localmente** contra um orçamento que VOCÊ declara no .env, não um
valor oficial da Anthropic.

Os quatro baldes de token têm preços diferentes, e tratar tudo a preço
cheio superestimaria bastante (o texto do documento vai cacheado):

  - input normal ......... 1,00x o preço de input
  - escrita de cache ..... 1,25x
  - leitura de cache ..... 0,10x
  - output ............... preço de output (inclui os tokens de thinking)
"""

from __future__ import annotations

from dataclasses import dataclass

CACHE_WRITE_MULTIPLIER = 1.25
CACHE_READ_MULTIPLIER = 0.10


@dataclass
class UsageTracker:
    """Acumula o uso de todas as chamadas ao modelo durante o run."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    calls: int = 0

    def record(self, usage) -> None:
        """Soma o `response.usage` de uma chamada. Tolera campos ausentes."""
        if usage is None:
            return
        self.calls += 1
        self.input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
        self.output_tokens += int(getattr(usage, "output_tokens", 0) or 0)
        self.cache_creation_tokens += int(
            getattr(usage, "cache_creation_input_tokens", 0) or 0
        )
        self.cache_read_tokens += int(
            getattr(usage, "cache_read_input_tokens", 0) or 0
        )

    @property
    def total_input_tokens(self) -> int:
        return self.input_tokens + self.cache_creation_tokens + self.cache_read_tokens

    def cost_usd(self, price_input_per_mtok: float, price_output_per_mtok: float) -> float:
        """Custo estimado em dólares, com os quatro baldes precificados."""
        billable_input = (
            self.input_tokens
            + self.cache_creation_tokens * CACHE_WRITE_MULTIPLIER
            + self.cache_read_tokens * CACHE_READ_MULTIPLIER
        )
        return (
            billable_input * price_input_per_mtok
            + self.output_tokens * price_output_per_mtok
        ) / 1_000_000


def format_tokens(count: int) -> str:
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.0f}K"
    return str(count)
