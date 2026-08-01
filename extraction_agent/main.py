"""Ponto de entrada do agente de extração (execução manual, sob demanda).

Modos:

    # Todos os deals da aba `Deals` que ainda não foram processados
    python main.py --todos

    # Um deal específico, resolvendo o link pela aba `Deals`
    python main.py --empresa "Acme Ltda"

    # Um deal com link explícito (não precisa estar na aba `Deals`)
    python main.py --empresa "Acme Ltda" --pasta "https://drive.google.com/drive/folders/<ID>"

    # Reprocessar mesmo quem já tem linhas em Pendente/Publicado
    python main.py --todos --reprocessar

    # Parar e perguntar a cada 10 deals, ou ao passar de 80% de US$ 100
    python main.py --todos --pausar-a-cada 10 --orcamento-usd 100

A saída pode ser redirecionada sem perder a interação — a pergunta do
checkpoint vai para o terminal, não para o log:

    python main.py --todos --pausar-a-cada 10 > run.log 2>&1

Sem servidor, sem webhook, sem trigger automático: o script termina sozinho.
"""

import argparse
import sys

from config import load_config, ConfigError
from agent.checkpoint import Checkpoint
from agent.errors import KIND_TRANSIENT, group_by_cause
from agent.loop import (
    STATUS_FAILED,
    STATUS_INVALID,
    STATUS_PROCESSED,
    STATUS_SKIPPED,
    BatchSummary,
    ExtractionLoop,
)
from agent.usage import format_tokens


def _print_deal_line(result) -> None:
    marks = {
        STATUS_PROCESSED: "OK  ",
        STATUS_SKIPPED: "PULA",
        STATUS_FAILED: "ERRO",
        STATUS_INVALID: "INV ",
    }
    mark = marks.get(result.status, "?   ")
    extra = f" — {result.detail}" if result.detail else ""
    counts = (
        f" [{result.rows_written} linha(s), {result.review_flags} review]"
        if result.rows_written
        else ""
    )
    # flush: um lote grande roda por horas e a saída não pode ficar presa
    # no buffer quando redirecionada para um arquivo de log.
    print(f"  [{mark}] {result.company}{counts}{extra}", flush=True)


def _print_errors_by_cause(summary: BatchSummary) -> None:
    """Agrupa as falhas por origem e natureza, com a dica de correção.

    Depois de um lote noturno, a pergunta é sempre a mesma: rodar de novo
    resolve, ou preciso arrumar alguma coisa antes?
    """
    infos = summary.all_errors()
    if not infos:
        return

    transient = [i for i in infos if i.retryable]
    actionable = [i for i in infos if not i.retryable]

    print("\n--- Falhas por causa ---", file=sys.stderr)

    if transient:
        print(
            f"\nTRANSITÓRIAS ({len(transient)}) — rodar de novo tem chance de "
            "resolver, e a idempotência não reprocessa o que já entrou:",
            file=sys.stderr,
        )
        for (origin, _, hint), group in group_by_cause(transient).items():
            print(f"  • {origin} ({len(group)}x)", file=sys.stderr)
            if hint:
                print(f"    {hint}", file=sys.stderr)
            for info in group[:3]:
                print(f"      - {info.message}", file=sys.stderr)
            if len(group) > 3:
                print(f"      … e mais {len(group) - 3}", file=sys.stderr)

    if actionable:
        print(
            f"\nEXIGEM AÇÃO ({len(actionable)}) — rodar de novo dá o mesmo erro:",
            file=sys.stderr,
        )
        for (origin, _, hint), group in group_by_cause(actionable).items():
            print(f"  • {origin} ({len(group)}x)", file=sys.stderr)
            if hint:
                print(f"    → {hint}", file=sys.stderr)
            for info in group[:3]:
                print(f"      - {info.message}", file=sys.stderr)
            if len(group) > 3:
                print(f"      … e mais {len(group) - 3}", file=sys.stderr)


def _print_summary(summary: BatchSummary, config) -> int:
    print("\n=== Resumo do lote ===")
    processed = summary.by_status(STATUS_PROCESSED)
    skipped = summary.by_status(STATUS_SKIPPED)
    failed = summary.by_status(STATUS_FAILED)
    invalid = summary.by_status(STATUS_INVALID)

    print(f"Deals avaliados: {len(summary.deals)}")
    print(f"  processados: {len(processed)}")
    print(f"  pulados (já em Pendente/Publicado): {len(skipped)}")
    print(f"  com erro: {len(failed)}")
    print(f"  linhas inválidas na aba `Deals`: {len(invalid)}")
    print(f"Linhas escritas em 'Pendente': {summary.rows_written}")
    print(f"Linhas marcadas como 'review': {summary.review_flags}")

    usage = summary.usage
    if usage.calls:
        cost = usage.cost_usd(config.price_input_per_mtok, config.price_output_per_mtok)
        print(
            f"\nUso do modelo ({config.claude_model}, effort={config.effort}):"
        )
        print(f"  chamadas: {usage.calls}")
        print(
            f"  tokens entrada/saída: "
            f"{format_tokens(usage.total_input_tokens)} / "
            f"{format_tokens(usage.output_tokens)}"
        )
        print(f"  leitura de cache: {format_tokens(usage.cache_read_tokens)}")
        print(f"  custo estimado: ${cost:,.2f}")
        if processed:
            print(f"  custo médio por deal processado: ${cost / len(processed):,.2f}")
        print("  (estimativa local — a API não informa saldo nem limite de gasto)")

    _print_errors_by_cause(summary)

    if summary.aborted:
        print(f"\nLOTE INTERROMPIDO: {summary.aborted}", file=sys.stderr)
        return 2
    if summary.stopped:
        print(f"\n{summary.stopped}")
        return 0
    return 1 if (failed or invalid) else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Agente de extração — Canary Deal Terms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--todos", action="store_true",
                        help="Processa todos os deals da aba `Deals`")
    parser.add_argument("--empresa", help="Nome da empresa do deal")
    parser.add_argument("--pasta", help="Link da pasta de documentos assinados no Drive")
    parser.add_argument("--reprocessar", action="store_true",
                        help="Ignora a idempotência e reprocessa mesmo quem já tem linhas")
    parser.add_argument("--pausar-a-cada", type=int, metavar="N",
                        help="Pergunta se continua a cada N deals "
                             "(sobrepõe PAUSE_EVERY_DEALS do .env)")
    parser.add_argument("--orcamento-usd", type=float, metavar="X",
                        help="Pergunta se continua ao cruzar a porcentagem de "
                             "gasto deste orçamento (sobrepõe BUDGET_USD)")
    args = parser.parse_args()

    if not args.todos and not args.empresa:
        parser.error("informe --todos ou --empresa")
    if args.pasta and not args.empresa:
        parser.error("--pasta exige --empresa")

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Erro de configuração: {exc}", file=sys.stderr)
        return 2

    extraction = ExtractionLoop(config)

    # Deal único com link explícito: não passa pela aba `Deals`.
    if args.pasta:
        print(f"Processando deal de {args.empresa!r}...")
        result = extraction.run_deal(args.empresa, args.pasta)
        summary = BatchSummary(usage=extraction.usage)
        summary.add(result)
        _print_deal_line(result)
        return _print_summary(summary, config)

    checkpoint = Checkpoint(
        pause_every=(
            args.pausar_a_cada
            if args.pausar_a_cada is not None
            else config.pause_every_deals
        ),
        budget_usd=(
            args.orcamento_usd
            if args.orcamento_usd is not None
            else config.budget_usd
        ),
        warn_pct=config.budget_warn_pct,
        price_input=config.price_input_per_mtok,
        price_output=config.price_output_per_mtok,
        non_interactive=config.checkpoint_no_tty,
    )

    scope = "todos os deals" if args.todos else f"deal {args.empresa!r}"
    reprocess = " (reprocessando)" if args.reprocessar else ""
    print(f"Lendo aba `Deals` — {scope}{reprocess}...")
    if checkpoint.enabled:
        gates = []
        if checkpoint.pause_every:
            gates.append(f"a cada {checkpoint.pause_every} deal(s)")
        if checkpoint.budget_usd:
            gates.append(
                f"em {config.budget_warn_pct}% de ${checkpoint.budget_usd:,.2f}"
            )
        print(f"Checkpoint ativo: {' ou '.join(gates)} — o que vier primeiro.")

    try:
        summary = extraction.run_batch(
            force=args.reprocessar,
            only="" if args.todos else args.empresa,
            on_start=lambda deals: print(f"{len(deals)} deal(s) a avaliar. Progresso:"),
            on_result=_print_deal_line,
            checkpoint=checkpoint,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Não foi possível ler a aba `Deals`: {exc}", file=sys.stderr)
        return 2
    finally:
        checkpoint.close()

    summary.usage = extraction.usage
    code = _print_summary(summary, config)
    if code == 0 and not summary.stopped:
        print("\nConcluído. Os rascunhos aguardam revisão do Legal na aba 'Pendente'.")
    return code


if __name__ == "__main__":
    sys.exit(main())
