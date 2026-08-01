# Agente de Extração — Canary Deal Terms

Agente Python que roda **localmente, sob demanda** (sem servidor, sem
webhook, sem trigger automático). Lê os documentos assinados de um deal no
Google Drive e:

1. Lista e lê os documentos da pasta (PDF, DOCX, Google Docs).
2. Classifica cada documento por tipo (SPA, IRA, CoI etc.).
3. Extrai os termos-chave com **citação exata** (documento + seção).
4. Compara cada termo com o material de referência da Canary
   (abas `Templates` + `Dicionario_Termos`) e com precedentes (aba `Terms`).
5. Atribui confiança (`high_confidence` / `review`).
6. Escreve o resultado como rascunho na aba **`Pendente`** — nunca em
   `Publicado`.

Roda para **um deal** ou para **todos os deals da aba `Deals` de uma vez**.

Os guard rails de comportamento seguem o `canary_agent_instructions.md`:
nunca afirmar sem citar; ausência é `not_found` explícito; comparação
texto-com-texto; incerteza vira `review` com motivo; o agente propõe,
humano decide; arquivos não reconhecidos entram na fila de revisão como
`not_classified` (nunca são descartados em silêncio).

## Estrutura

```
extraction_agent/
  main.py               # ponto de entrada (um deal ou lote)
  agent/
    loop.py             # loop principal, modo lote, idempotência
    tools.py            # ferramentas (Drive, Sheets, Deals, write_drafts)
    prompts.py          # prompts + schemas JSON de cada etapa
    errors.py           # classificação de erros por origem e natureza
    usage.py            # contagem de tokens e estimativa de custo
    checkpoint.py       # pausa interativa via /dev/tty
  config.py             # leitura de variáveis de ambiente
  tests/
    test_permissions.py # escrita restrita à aba Pendente
    test_tools.py       # not_found explícito, citação obrigatória etc.
    test_batch.py       # aba Deals, idempotência, cobertura, escrita em lote
    test_errors.py      # classificação de erros
    test_checkpoint.py  # checkpoint, custo, recorte da classificação
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
| **`CLAUDE_EFFORT`** | **Otimização de custo — ver seção abaixo.** Padrão `medium` |
| **`CLASSIFY_CHAR_LIMIT`** | **Otimização de custo — ver seção abaixo.** Padrão `12000` |
| `CATEGORY_BATCH_SIZE` | Opcional; padrão `5`. Ver "Processamento em lote" |
| `PAUSE_EVERY_DEALS` | Opcional; padrão `0` (desligado). Ver "Checkpoint interativo" |
| `BUDGET_USD` | Opcional; padrão `0` (sem orçamento) |
| `BUDGET_WARN_PCT` | Opcional; padrão `80` |
| `CHECKPOINT_SEM_TERMINAL` | Opcional; `parar` (padrão) ou `continuar` |
| `PRICE_INPUT_PER_MTOK` / `PRICE_OUTPUT_PER_MTOK` | Preços para a estimativa; padrão `5.0` / `25.0` |
| `DEALS_COMPANY_COLUMN` | Opcional; padrão `Empresa` |
| `DEALS_FOLDER_COLUMN` | Opcional; padrão `Pasta_Documentos_Assinados` |

## ⚠️ Otimizações de custo e como revertê-las

Duas escolhas do projeto trocam um pouco de profundidade por bastante
economia. **Cada uma se desfaz mudando UMA variável no `.env`** — nenhuma
alteração de código é necessária. Se no teste real a qualidade não
convencer, reverta e rode de novo.

### [1] `CLAUDE_EFFORT` — profundidade de raciocínio

| | |
|---|---|
| **Padrão da API do Claude** | `high` |
| **Padrão deste projeto** | `medium` |
| **Como reverter** | `CLAUDE_EFFORT=high` no `.env` |
| **Onde age** | `agent/loop.py`, em `_call_claude` → `output_config.effort` |

**Por quê:** os tokens de *output* custam 5x os de *input*, e o raciocínio
(thinking) é cobrado como output. Numa extração típica, o output responde
por mais da metade do custo. Baixar de `high` para `medium` corta uma fatia
significativa da conta e do tempo.

**O risco:** menos deliberação por termo. Em cláusulas de redação incomum,
`medium` pode produzir citações menos precisas ou marcar `review` com mais
frequência. Aceita `low`, `medium`, `high`, `xhigh`, `max`.

**Como avaliar:** rode um deal com cada valor e compare as colunas
`secao_fonte` e `nota_comparacao` das linhas geradas.

### [2] `CLASSIFY_CHAR_LIMIT` — recorte na etapa de classificação

| | |
|---|---|
| **Comportamento original** | documento inteiro na classificação |
| **Padrão deste projeto** | `12000` caracteres (início + fim) |
| **Como reverter** | `CLASSIFY_CHAR_LIMIT=0` no `.env` |
| **Onde age** | `agent/loop.py`, em `classify_excerpt()` |

**Por quê:** a classificação só precisa responder "que documento é este?" e
"parece a versão final assinada?". A primeira resposta está nas primeiras
páginas (título, preâmbulo, definições); a segunda está no fim (bloco de
assinaturas). O miolo não ajuda — e é justamente a parte do prompt que
**não** vai cacheada, então é paga a preço cheio em todo documento.

**Como funciona:** manda os primeiros ~70% do limite e os últimos ~30%,
com um marcador explícito no lugar do miolo. O prompt avisa o modelo que o
corte é intencional, para ele não confundir isso com documento incompleto.

**Importante:** isso afeta **apenas a classificação**. A extração dos
termos sempre recebe o documento completo — nenhuma cláusula deixa de ser
procurada por causa desta variável.

**O risco:** um documento cujo tipo só fica claro no meio seria mal
classificado. Se você vir muitos `not_classified` inesperados no relatório,
suba o limite (ex.: `30000`) ou zere para voltar ao original.

### Credenciais Google (duas service accounts)

No [Google Cloud Console](https://console.cloud.google.com), num projeto com
as APIs **Drive** e **Sheets** habilitadas, crie **duas** service accounts:

1. **Leitora** (`reader-sa`): baixe a chave JSON. Compartilhe as **pastas do
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
`Publicado`. O código tem uma segunda guarda (`tools._append_rows`) que
recusa qualquer aba diferente de `Pendente` antes mesmo de chamar a API,
com erro explícito. As duas camadas são cobertas por
`tests/test_permissions.py`.

O agente **lê** `Pendente` e `Publicado` (com a credencial readonly) para
saber quais deals já foram processados. Isso não afrouxa a restrição de
escrita: leitura e escrita usam credenciais e caminhos de código diferentes.

## Preparando as abas da planilha

### `Deals` — quais deals processar

É a fonte do modo lote. Precisa de duas colunas:

| Empresa | Pasta_Documentos_Assinados |
|---|---|
| Acme Ltda | `https://drive.google.com/drive/folders/1AbC...` |
| Beta S.A. | `https://drive.google.com/drive/folders/1XyZ...` |

O link deve apontar direto para a pasta de **documentos assinados** daquele
deal. Se sua planilha usa outros nomes de coluna, ajuste
`DEALS_COMPANY_COLUMN` / `DEALS_FOLDER_COLUMN` no `.env` — o código também
reconhece aliases comuns (`Company`, `Pasta`, `Link`…) e, em último caso,
procura qualquer coluna cujo valor pareça um link do Drive.

Linha sem empresa ou sem link não é ignorada em silêncio: aparece no
relatório final como `INV` com o motivo.

### `Dicionario_Termos` — o que rastrear

É aqui que se define **quais categorias o agente procura** e **como
reconhecê-las mesmo com redação variável**. Uma linha por categoria:

| Categoria | Termo | Definicao | Exemplos_Redacao | Tipos_Documento |
|---|---|---|---|---|
| Liquidation Preference | liquidation_preference | Ordem e múltiplo de pagamento… | `"liquidation preference of 1x"` \| `"Preferência de Liquidação"` | Certificate of Incorporation |
| MFN | mfn | Cláusula de nação mais favorecida | `"most favored nation"` \| `"MFN"` | SPA, Side Letter |

- **`Categoria`** é obrigatória — é ela que dirige o loop de extração.
- **`Tipos_Documento`** (opcional, mas recomendada) evita procurar termo de
  SPA dentro de um Certificate of Incorporation. Sem ela, toda categoria é
  tentada em todo documento e a `Pendente` enche de `not_found` legítimos
  porém ruidosos.
- Qualquer **outra coluna** que você criar é repassada inteira ao modelo —
  o código não precisa saber que ela existe.

Se o dicionário estiver vazio, ou se nenhuma categoria se aplicar ao tipo
de documento, o agente **falha com erro explícito** em vez de terminar
sem escrever nada.

### `Pendente` — cabeçalho

A linha 1 precisa ter estas colunas, nesta ordem:

```
categoria | termo | resumo | valor | documento_fonte | secao_fonte |
confianca | nota_comparacao | motivo_flag | precedente_consultado |
empresa | timestamp | versao_documento
```

## Rodando

```bash
# Todos os deals da aba `Deals` que ainda não foram processados
python main.py --todos

# Um deal específico, com o link vindo da aba `Deals`
python main.py --empresa "Acme Ltda"

# Um deal com link explícito (não precisa estar na aba `Deals`)
python main.py --empresa "Acme Ltda" --pasta "https://drive.google.com/drive/folders/<ID>"

# Reprocessar mesmo quem já tem linhas em Pendente/Publicado
python main.py --todos --reprocessar

# Parar e perguntar a cada 10 deals, ou ao passar de 80% de US$ 100
python main.py --todos --pausar-a-cada 10 --orcamento-usd 100
```

A saída mostra o progresso deal a deal enquanto roda, e um resumo no fim:

```
32 deal(s) a avaliar. Progresso:
  [OK  ] Acme Ltda [47 linha(s), 9 review]
  [PULA] Beta S.A. — Já aprovado pelo Legal (consta em `Publicado`).
  [ERRO] Gama Participações — 1 arquivo(s) com erro.
  [INV ] Delta Corp — Linha 12: link da pasta de documentos assinados ausente.
```

Código de saída: `0` tudo certo, `1` algum deal com erro/inválido, `2` lote
interrompido ou erro de configuração.

### Checkpoint interativo

Para um lote longo, dá para pedir confirmação de tempos em tempos. Dispara
**pelo que vier primeiro**: a contagem de deals ou a porcentagem do
orçamento.

```bash
python main.py --todos --pausar-a-cada 10 --orcamento-usd 100
```

```
============================================================
CHECKPOINT — 10 de 50 deals avaliados
============================================================
  Chamadas ao modelo    : 210
  Tokens entrada/saída  : 12.5M / 3.4M
    (leitura de cache   : 9.5M, cobrada a 10%)
  Custo estimado        : $31.40
  Orçamento             : $100.00 (31% consumido)
  Faltam                : 40 deal(s)
  Projeção até o fim    : $157.00

  MOTIVO: 10 deal(s) desde o último checkpoint.

  Parar agora é seguro: o que já foi escrito fica em `Pendente` e
  não será reprocessado quando você rodar de novo (idempotência).
  Continuar? [s/N]
```

**Você pode redirecionar a saída e ainda assim responder.** A pergunta é
escrita e lida direto em `/dev/tty`, não em stdout — então ela aparece no
seu terminal enquanto o log fica limpo:

```bash
python main.py --todos --pausar-a-cada 10 > run.log 2>&1
```

Só quando não existe terminal nenhum (`nohup`, cron) é que entra o
comportamento de `CHECKPOINT_SEM_TERMINAL`: `parar` (padrão, seguro — você
retoma depois e a idempotência não reprocessa nada) ou `continuar`.

**Sobre o orçamento:** o número é uma **estimativa calculada localmente**
contra um teto que você declara. A API do Claude não informa saldo nem
limite de gasto — o que ela devolve em cada resposta é quantos tokens
aquela chamada consumiu. O cálculo precifica os quatro baldes
separadamente (input normal, escrita de cache a 1,25x, leitura de cache a
0,1x e output), porque tratar tudo a preço cheio superestimaria bastante.

O aviso de orçamento dispara em `BUDGET_WARN_PCT` e mais uma vez em 100%;
depois desarma, para não perguntar a cada deal. A contagem de deals
continua valendo e segue mostrando o custo acumulado.

### Quando algo falha

As falhas são classificadas por **origem** (Claude, Google Drive, Google
Sheets, Documento, Agente) e por **natureza** — e o resumo final separa o
que adianta re-rodar do que exige uma correção sua:

```
--- Falhas por causa ---

TRANSITÓRIAS (3) — rodar de novo tem chance de resolver, e a idempotência
não reprocessa o que já entrou:
  • Claude (3x)
    Rate limit da API do Claude. O SDK já tentou novamente; rode o lote de
    novo mais tarde — a idempotência não reprocessa o que já entrou.
      - spa_assinado.pdf: rate limited

EXIGEM AÇÃO (1) — rodar de novo dá o mesmo erro:
  • Google Drive (1x)
    → A service account de LEITURA não tem acesso a esta pasta.
      Compartilhe a pasta do deal no Drive com o e-mail da reader-sa
      como Leitor.
      - HTTP 403
```

Erro não reconhecido é tratado como "exige ação" de propósito — para não
induzir você a re-rodar um lote de horas sem investigar.

### Idempotência

Rodar de novo **não duplica** rascunhos. Antes de processar, o agente
verifica se a empresa já tem linhas em:

- **`Pendente`** — rascunho aguardando revisão, pula.
- **`Publicado`** — já aprovado pelo Legal, pula (reextrair aqui
  ressuscitaria como pendente algo que já foi decidido).

Isso torna seguro re-rodar `--todos` depois de uma falha no meio do lote:
só os que faltaram são processados. Use `--reprocessar` para forçar.

Um deal que falha (PDF corrompido, erro de rede) **não derruba o lote** —
é registrado no relatório e o próximo continua. A exceção é erro de
permissão de escrita, que falharia igual em todos os deals e portanto
aborta o lote imediatamente.

### Processamento em lote

O agente extrai as categorias em **blocos** (padrão: 5 por chamada ao
modelo), não uma chamada por categoria. Com 20 categorias, isso é 4
chamadas por documento em vez de 20 — cerca de 5x menos custo e tempo. O
texto do documento vai com cache habilitado, então a partir da segunda
chamada do mesmo arquivo o grosso do prompt é cobrado a ~10%.

Ajuste com `CATEGORY_BATCH_SIZE`:

- **Maior** (ex.: 10) — mais rápido e barato, mas o modelo divide atenção
  entre mais termos numa resposta só.
- **Menor** (ex.: 2-3) — mais atenção por termo, mais caro.

As linhas de um documento são gravadas no Sheets em **uma única chamada**,
em vez de uma por termo — sem isso, milhares de termos estouram a cota de
escrita do Google (~60 escritas/minuto).

Se o modelo omitir uma categoria pedida, o código **preenche a lacuna**
com `not_found` marcado para revisão. Nenhuma categoria solicitada some do
resultado sem explicação.

### Antes de soltar nos 50 deals

Rode 2 ou 3 primeiro e leve o resultado ao Legal:

```bash
python main.py --empresa "Acme Ltda"
```

O `Dicionario_Termos` quase sempre precisa de ajuste no primeiro contato
com documentos reais — categorias faltando, redações alternativas que
ninguém lembrou, `Tipos_Documento` mal calibrado. Descobrir isso depois de
horas de processamento e milhares de linhas escritas custa caro em tempo
de revisão.

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
- Uma linha inválida no meio de um lote impede a gravação do lote inteiro
  (nada de meio documento gravado).
- Deal já em `Pendente`/`Publicado` é pulado; `--reprocessar` força.
- Um deal com erro não interrompe o lote; erro de permissão interrompe.
- Categoria omitida pelo modelo vira `not_found` marcado para revisão.
- Dicionário vazio falha alto em vez de escrever zero linhas em silêncio.
- Erros são classificados por origem e por natureza (transitório vs. exige
  ação); erro desconhecido cai em "exige ação" por segurança.
- Checkpoint dispara pela contagem ou pelo orçamento, o que vier primeiro;
  resposta vazia para o lote; sem terminal, para por padrão.
- Cache é precificado abaixo do input normal na estimativa de custo.
- O recorte da classificação preserva início **e** fim do documento (a
  página de assinaturas está no fim) e some com `CLASSIFY_CHAR_LIMIT=0`.

Os testes usam fakes locais — não tocam a rede nem exigem credenciais.

## Fora de escopo (desta versão)

- Agente de consulta (componente separado, em Apps Script).
- Integração com Slack.
- Aprovação/publicação automática — mover `Pendente` → `Publicado` é manual.
