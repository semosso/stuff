"""Ponto de entrada do agente de extração (execução manual, sob demanda).

Uso:
    python main.py --empresa "Acme Ltda" --pasta "https://drive.google.com/drive/folders/<ID>"

Processa todos os arquivos da pasta, escreve os rascunhos na aba `Pendente`
e termina. Sem servidor, sem webhook, sem trigger automático.
"""

import argparse
import sys

from config import load_config, ConfigError
from agent.loop import ExtractionLoop


def main() -> int:
    parser = argparse.ArgumentParser(description="Agente de extração — Canary Deal Terms")
    parser.add_argument("--empresa", required=True, help="Nome da empresa do deal")
    parser.add_argument("--pasta", required=True, help="Link da pasta do Google Drive do deal")
    args = parser.parse_args()

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Erro de configuração: {exc}", file=sys.stderr)
        return 2

    loop = ExtractionLoop(config)
    print(f"Processando deal de {args.empresa!r}...")
    summary = loop.run(args.empresa, args.pasta)

    print("\n=== Resumo da extração ===")
    print(f"Empresa: {summary.company}")
    print(f"Linhas escritas em 'Pendente': {summary.rows_written}")
    print(f"Linhas marcadas como 'review': {summary.review_flags}")
    print(f"Documentos processados ({len(summary.files_processed)}):")
    for name in summary.files_processed:
        print(f"  - {name}")
    if summary.files_not_classified:
        print(f"Arquivos NÃO classificados — na fila de revisão ({len(summary.files_not_classified)}):")
        for name in summary.files_not_classified:
            print(f"  - {name}")
    if summary.errors:
        print(f"Erros ({len(summary.errors)}):", file=sys.stderr)
        for err in summary.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("\nConcluído. Os rascunhos aguardam revisão do Legal na aba 'Pendente'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
