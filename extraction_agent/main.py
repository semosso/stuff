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

Sem servidor, sem webhook, sem trigger automático: o script termina sozinho.
"""

import argparse
import sys

from config import load_config, ConfigError
from agent.loop import (
    STATUS_FAILED,
    STATUS_INVALID,
    STATUS_PROCESSED,
    STATUS_SKIPPED,
    BatchSummary,
    ExtractionLoop,
)


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


def _print_summary(summary: BatchSummary) -> int:
    print("\n=== Resumo do lote ===")
    processed = summary.by_status(STATUS_PROCESSED)
    skipped = summary.by_status(STATUS_SKIPPED)
    failed = summary.by_status(STATUS_FAILED)
    invalid = summary.by_status(STATUS_INVALID)

    print(f"Deals na aba `Deals`: {len(summary.deals)}")
    print(f"  processados: {len(processed)}")
    print(f"  pulados (já em Pendente/Publicado): {len(skipped)}")
    print(f"  com erro: {len(failed)}")
    print(f"  linhas inválidas na aba `Deals`: {len(invalid)}")
    print(f"Linhas escritas em 'Pendente': {summary.rows_written}")
    print(f"Linhas marcadas como 'review': {summary.review_flags}")

    if failed or invalid:
        print("\nPrecisam de atenção:", file=sys.stderr)
        for result in failed + invalid:
            print(f"  - {result.company}: {result.detail}", file=sys.stderr)
            for err in result.errors:
                print(f"      {err}", file=sys.stderr)

    if summary.aborted:
        print(f"\nLOTE INTERROMPIDO: {summary.aborted}", file=sys.stderr)
        return 2
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
        summary = BatchSummary()
        summary.add(result)
        _print_deal_line(result)
        return _print_summary(summary)

    scope = "todos os deals" if args.todos else f"deal {args.empresa!r}"
    reprocess = " (reprocessando)" if args.reprocessar else ""
    print(f"Lendo aba `Deals` — {scope}{reprocess}...")

    try:
        summary = extraction.run_batch(
            force=args.reprocessar,
            only="" if args.todos else args.empresa,
            on_start=lambda deals: print(f"{len(deals)} deal(s) a avaliar. Progresso:"),
            on_result=_print_deal_line,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Não foi possível ler a aba `Deals`: {exc}", file=sys.stderr)
        return 2

    code = _print_summary(summary)
    if code == 0:
        print("\nConcluído. Os rascunhos aguardam revisão do Legal na aba 'Pendente'.")
    return code


if __name__ == "__main__":
    sys.exit(main())
