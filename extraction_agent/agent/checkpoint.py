"""Checkpoint interativo: pausa o lote e pergunta se continua.

Dispara pelo que vier primeiro:
  - a cada N deals processados (`PAUSE_EVERY_DEALS`);
  - ao cruzar X% do orçamento declarado (`BUDGET_USD` + `BUDGET_WARN_PCT`).

A pergunta é escrita e lida direto em `/dev/tty`, não em stdout/stdin. Com
isso o prompt aparece no seu terminal mesmo com a saída redirecionada
(`> run.log`, `2>&1`, `| tee`), e o log fica limpo, sem a pergunta no meio.
Só quando não existe terminal nenhum (nohup, cron) é que entra o
comportamento não-interativo configurado.
"""

from __future__ import annotations

import sys

from agent.usage import UsageTracker, format_tokens

# O que fazer quando não há terminal para perguntar.
NON_INTERACTIVE_STOP = "parar"
NON_INTERACTIVE_CONTINUE = "continuar"

REASON_DEAL_COUNT = "contagem"
REASON_BUDGET = "orcamento"


class _Terminal:
    """Acesso ao terminal de controle, independente dos redirecionamentos."""

    def __init__(self):
        self._tty = None
        try:
            self._tty = open("/dev/tty", "r+")
        except OSError:
            # Windows, ou sem terminal de controle (nohup/cron/CI).
            if sys.stdin.isatty() and sys.stderr.isatty():
                self._tty = None
                self._fallback = True
            else:
                self._fallback = False
            return
        self._fallback = False

    @property
    def available(self) -> bool:
        return self._tty is not None or getattr(self, "_fallback", False)

    def write(self, text: str) -> None:
        if self._tty is not None:
            self._tty.write(text)
            self._tty.flush()
        else:
            sys.stderr.write(text)
            sys.stderr.flush()

    def readline(self) -> str:
        if self._tty is not None:
            return self._tty.readline()
        return sys.stdin.readline()

    def close(self) -> None:
        if self._tty is not None:
            self._tty.close()
            self._tty = None


class Checkpoint:
    """Decide quando parar para perguntar, e faz a pergunta."""

    def __init__(self, pause_every: int = 0, budget_usd: float = 0.0,
                 warn_pct: int = 80, price_input: float = 5.0,
                 price_output: float = 25.0,
                 non_interactive: str = NON_INTERACTIVE_STOP,
                 terminal=None):
        self.pause_every = max(0, pause_every)
        self.budget_usd = max(0.0, budget_usd)
        self.warn_pct = warn_pct
        self.price_input = price_input
        self.price_output = price_output
        self.non_interactive = non_interactive
        self._terminal = terminal if terminal is not None else _Terminal()
        self._last_pause_at = 0
        # Avisa em warn_pct% e de novo em 100%; depois desarma para não
        # ficar perguntando a cada deal. A contagem de deals continua
        # valendo e segue mostrando o custo.
        self._budget_thresholds = sorted({warn_pct, 100}) if budget_usd > 0 else []

    @property
    def enabled(self) -> bool:
        return self.pause_every > 0 or self.budget_usd > 0

    def cost(self, usage: UsageTracker) -> float:
        return usage.cost_usd(self.price_input, self.price_output)

    def reason_to_pause(self, deals_done: int, usage: UsageTracker) -> str:
        """Motivo da parada, ou string vazia se é para seguir."""
        if self.budget_usd > 0 and self._budget_thresholds:
            pct = self.cost(usage) / self.budget_usd * 100
            if pct >= self._budget_thresholds[0]:
                return REASON_BUDGET
        if self.pause_every > 0 and deals_done - self._last_pause_at >= self.pause_every:
            return REASON_DEAL_COUNT
        return ""

    def _describe(self, reason: str, deals_done: int, deals_total: int,
                  usage: UsageTracker, crossed_pct: int | None = None) -> str:
        cost = self.cost(usage)
        lines = [
            "",
            "=" * 60,
            f"CHECKPOINT — {deals_done} de {deals_total} deals avaliados",
            "=" * 60,
        ]
        lines.append(f"  Chamadas ao modelo    : {usage.calls}")
        lines.append(
            f"  Tokens entrada/saída  : "
            f"{format_tokens(usage.total_input_tokens)} / "
            f"{format_tokens(usage.output_tokens)}"
        )
        lines.append(
            f"    (leitura de cache   : {format_tokens(usage.cache_read_tokens)}, "
            f"cobrada a 10%)"
        )
        lines.append(f"  Custo estimado        : ${cost:,.2f}")
        if self.budget_usd > 0:
            pct = cost / self.budget_usd * 100
            lines.append(
                f"  Orçamento             : ${self.budget_usd:,.2f} "
                f"({pct:.0f}% consumido)"
            )
        remaining = deals_total - deals_done
        if remaining > 0 and deals_done > 0:
            projected = cost / deals_done * deals_total
            lines.append(f"  Faltam                : {remaining} deal(s)")
            lines.append(f"  Projeção até o fim    : ${projected:,.2f}")
        if reason == REASON_BUDGET:
            lines.append("")
            lines.append(
                f"  MOTIVO: o gasto estimado cruzou "
                f"{crossed_pct}% do orçamento declarado."
            )
        else:
            lines.append("")
            lines.append(f"  MOTIVO: {self.pause_every} deal(s) desde o último checkpoint.")
        lines.append("")
        lines.append(
            "  Parar agora é seguro: o que já foi escrito fica em `Pendente` e"
        )
        lines.append(
            "  não será reprocessado quando você rodar de novo (idempotência)."
        )
        lines.append("")
        return "\n".join(lines)

    def review(self, deals_done: int, deals_total: int, usage: UsageTracker,
               reason: str) -> bool:
        """Pergunta se continua. True = seguir, False = parar."""
        self._last_pause_at = deals_done
        crossed_pct = None
        if reason == REASON_BUDGET and self._budget_thresholds:
            # Desarma este limiar ANTES de perguntar, para não repetir o
            # mesmo aviso no próximo deal.
            crossed_pct = self._budget_thresholds.pop(0)

        if not self._terminal.available:
            if self.non_interactive == NON_INTERACTIVE_CONTINUE:
                print(
                    f"[checkpoint] {reason}: sem terminal para perguntar — "
                    "seguindo (CHECKPOINT_SEM_TERMINAL=continuar).",
                    flush=True,
                )
                return True
            print(
                f"[checkpoint] {reason}: sem terminal para perguntar — parando. "
                "Rode de novo para continuar de onde parou "
                "(ou use CHECKPOINT_SEM_TERMINAL=continuar).",
                flush=True,
            )
            return False

        self._terminal.write(
            self._describe(reason, deals_done, deals_total, usage, crossed_pct)
        )
        self._terminal.write("  Continuar? [s/N] ")
        answer = (self._terminal.readline() or "").strip().lower()
        keep_going = answer in ("s", "sim", "y", "yes")
        self._terminal.write(
            "  → continuando...\n\n" if keep_going else "  → parando aqui.\n\n"
        )
        return keep_going

    def close(self) -> None:
        self._terminal.close()
