# Agente de Extração — Canary Deal Terms

Agente Python que roda **localmente, sob demanda** (sem servidor, sem
webhook, sem trigger automático). Dado o nome de uma empresa e o link de
uma pasta do Google Drive com os documentos de um deal assinado, ele:

1. Lista e lê os documentos da pasta (PDF, DOCX, Google Docs).
2. Classifica cada documento por tipo (SPA, IRA, CoI etc.).
3. Extrai os termos-chave com **citação exata** (documento + seção).
4. Compara cada termo com o material de referência da Canary
   (abas `Templates` + `Dicionario_Termos`) e com precedentes (aba `Terms`).
5. Atribui confiança (`high_confidence` / `review`).
6. Escreve o resultado como rascunho na aba **`Pendente`** — nunca em
   `Publicado`.

Os guard rails de comportamento seguem o `canary_agent_instructions.md`:
nunca afirmar sem citar; ausência é `not_found` explícito; comparação
texto-com-texto; incerteza vira `review` com motivo; o agente propõe,
humano decide; arquivos não reconhecidos entram na fila de revisão como
`not_classified` (nunca são descartados em silêncio).

## Estrutura

```
extraction_agent/
  main.py               # ponto de entrada (empresa + link da pasta)
  agent/
    loop.py             # loop principal
    tools.py            # ferramentas (Drive, Sheets, write_draft)
    prompts.py          # prompts + schemas JSON de cada etapa
  config.py             # leitura de variáveis de ambiente
  tests/
    test_permissions.py # escrita restrita à aba Pendente
    test_tools.py       # not_found explícito, citação obrigatória etc.
  requirements.txt
  .env.example
```

## Setup

```bash
cd extraction_agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # e preencha (ver abaixo)
```

### Variáveis de ambiente (`.env`)

| Variável | O que é |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da API do Claude ([console](https://platform.claude.com)) |
| `CLAUDE_MODEL` | Opcional; padrão `claude-opus-4-8` |
| `GOOGLE_READER_CREDENTIALS_FILE` | JSON da service account de **leitura** |
| `GOOGLE_WRITER_CREDENTIALS_FILE` | JSON da service account de **escrita** (separada) |
| `SPREADSHEET_ID` | ID da planilha (trecho entre `/d/` e `/edit` na URL) |

### Credenciais Google (duas service accounts)

No [Google Cloud Console](https://console.cloud.google.com), num projeto com
as APIs **Drive** e **Sheets** habilitadas, crie **duas** service accounts:

1. **Leitora** (`reader-sa`): baixe a chave JSON. Compartilhe a **pasta do
   Drive** dos deals e a **planilha** com o e-mail dela como *Leitor*.
   O código usa apenas escopos readonly com esta conta.
2. **Escritora** (`writer-sa`): baixe a chave JSON. Compartilhe a
   **planilha** com o e-mail dela como *Editor* — e restrinja a edição à
   aba `Pendente` (abaixo).

Salve os dois JSONs em `./credentials/` (a pasta está no `.gitignore`).

### Restringindo a escrita à aba `Pendente` (a nível de planilha)

A restrição é configurada **na permissão do Google Sheets**, não apenas por
convenção no código:

1. Na planilha, para **cada aba exceto `Pendente`** (`Deals`, `Terms`,
   `Publicado`, `Templates`, `Dicionario_Termos`): botão direito na aba →
   **Proteger página** → *Restringir quem pode editar* → apenas você /
   o time de Legal. **Não** inclua o e-mail da `writer-sa`.
2. A aba `Pendente` fica sem proteção (ou protegida permitindo a
   `writer-sa`).

Resultado: mesmo com papel de Editor na planilha, a `writer-sa` recebe
**HTTP 403** ao tentar escrever em qualquer aba protegida — em especial
`Publicado`. O código tem uma segunda guarda (`tools._append_row`) que
recusa qualquer aba diferente de `Pendente` antes mesmo de chamar a API,
com erro explícito. As duas camadas são cobertas por
`tests/test_permissions.py`.

## Rodando

```bash
python main.py \
  --empresa "Acme Ltda" \
  --pasta "https://drive.google.com/drive/folders/<ID_DA_PASTA>"
```

O script processa todos os arquivos da pasta, imprime um resumo
(linhas escritas, flags de `review`, arquivos não classificados) e termina.
A movimentação de `Pendente` → `Publicado` continua sendo uma ação manual
do Legal, fora deste script.

## Testes

```bash
python -m pytest tests/ -v
```

Cobrem, entre outros:

- Escrever em `Publicado` (ou qualquer aba ≠ `Pendente`) **falha com
  exceção explícita**, e um 403 da API nunca é engolido como sucesso.
- Termo não encontrado vira `not_found` explícito; valor em branco é
  **rejeitado** antes da escrita.
- Toda linha escrita em `Pendente` tem citação (documento + seção)
  preenchida; sem citação, a escrita é rejeitada.
- Linha `review` sem motivo do flag é rejeitada; campos de auditoria
  (timestamp, versão do documento) nunca ficam em branco.

Os testes usam fakes locais — não tocam a rede nem exigem credenciais.

## Formato da aba `Pendente`

Colunas escritas (linha 1 da aba deve ter esse cabeçalho, nesta ordem):

```
categoria | termo | resumo | valor | documento_fonte | secao_fonte |
confianca | nota_comparacao | motivo_flag | precedente_consultado |
empresa | timestamp | versao_documento
```

## Fora de escopo (desta versão)

- Agente de consulta (componente separado, em Apps Script).
- Integração com Slack.
- Aprovação/publicação automática — mover `Pendente` → `Publicado` é manual.
