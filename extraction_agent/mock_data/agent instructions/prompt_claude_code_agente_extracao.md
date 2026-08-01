# Prompt para Claude Code — Agente de Extração (Python, local)

> Cole isso como primeira mensagem numa sessão nova do Claude Code, dentro da
> pasta onde você quer criar o projeto. Anexe também o arquivo
> `canary_agent_instructions.md` (guard rails já escritos) — referencie ele
> explicitamente pedindo para o Claude Code ler antes de começar.

---

Quero construir um agente de extração em Python que roda localmente na minha
máquina, sob demanda (eu disparo manualmente, sem servidor, sem webhook, sem
trigger automático). Antes de escrever qualquer código, leia o arquivo
`canary_agent_instructions.md` que anexei — ele contém os guard rails de
comportamento que o agente precisa seguir. Depois disso, quero que você
implemente a estrutura abaixo.

## Objetivo

Dado o nome de uma empresa e o link de uma pasta do Google Drive contendo
documentos de um deal assinado, o agente deve:
1. Listar e ler os documentos da pasta.
2. Classificar cada documento por tipo.
3. Extrair os termos-chave de cada documento, com citação exata (documento +
   seção).
4. Comparar cada termo extraído com o material de referência (templates
   Canary + dicionário de termos), também na mesma planilha.
5. Atribuir um nível de confiança a cada termo extraído.
6. Escrever o resultado como rascunho numa aba específica do Google Sheets —
   nunca na aba de dados aprovados.

## Fontes de dados (todas no Google Workspace da empresa)

- **Google Drive**: pasta por deal, contendo os PDFs/DOCX assinados.
- **Google Sheets** (uma única planilha, múltiplas abas):
  - `Deals` e `Terms` — golden dataset já aprovado (leitura apenas, para
    comparação de precedentes).
  - `Pendente` — onde o agente escreve os rascunhos de extração. **Única aba
    com permissão de escrita para este agente.**
  - `Publicado` — dados aprovados por Legal. **O agente nunca deve ter
    permissão de escrita aqui — nem por engano, nem por instrução do
    usuário.**
  - `Templates` — texto dos templates padrão Canary, organizados por tipo de
    documento.
  - `Dicionario_Termos` — categoria, termo, definição, exemplos de redação
    conhecidos (usado para reconhecer o termo no texto, mesmo com redação
    variável).

## Estrutura do código

Organize como um projeto Python normal, não um script único:

```
extraction_agent/
  main.py                # ponto de entrada, recebe empresa + link da pasta
  agent/
    loop.py               # o loop principal (passo a passo abaixo)
    tools.py               # as funções/ferramentas que o loop chama
    prompts.py             # os prompts enviados ao modelo em cada etapa
  config.py                 # leitura de variáveis de ambiente
  tests/
    test_permissions.py    # ver seção "Testes obrigatórios"
    test_tools.py
  requirements.txt
  .env.example              # modelo do que precisa estar no .env real
  .gitignore                 # deve excluir .env e qualquer credencial
  README.md                  # como rodar localmente
```

## Ferramentas (tools) que o loop deve ter disponíveis

- `list_files(folder_link)` — lista arquivos da pasta do Drive.
- `read_document(file_id)` — extrai texto de PDF/DOCX.
- `search_reference(document_type, term_category)` — busca a seção
  relevante em `Templates` e as definições relevantes em
  `Dicionario_Termos`. Read-only.
- `search_precedent(term_category)` — busca como esse termo apareceu em
  deals já aprovados na aba `Terms`, para contexto de comparação adicional.
  Read-only.
- `write_draft(term_row)` — escreve uma linha na aba `Pendente`. Use uma
  credencial de serviço separada das outras ferramentas, com permissão de
  escrita **restrita a essa aba especificamente** — configure isso a nível
  de permissão do Google Sheets/API, não apenas por convenção no código.

## Loop principal (passo a passo)

Para cada documento na pasta:
1. Classificar o tipo de documento. Se não for possível classificar com
   confiança, marcar como `not_classified` e seguir para o próximo arquivo
   sem tentar extrair termos dele.
2. Verificar indícios de que não é a versão final assinada (nome de arquivo
   com "draft"/"v1"/"redline", ausência de assinatura). Se houver
   ambiguidade, sinalizar isso no rascunho antes de prosseguir.
3. Para cada categoria de termo relevante ao tipo de documento:
   a. Localizar o trecho relevante no texto já lido.
   b. Chamar `search_reference` para obter o texto de comparação.
   c. Chamar `search_precedent` para contexto adicional (opcional, mas
      registrar se usado).
   d. Decidir: termo encontrado ou `not_found` — nunca deixar em branco sem
      explicação.
   e. Atribuir confiança (`high_confidence` / `review`) segundo os critérios
      do `canary_agent_instructions.md`.
   f. Chamar `write_draft` com: categoria, termo, resumo em linguagem
      simples, valor, documento fonte, seção fonte, confiança, nota de
      comparação com o padrão, motivo do flag (se `review`).

Sem trigger automático — o `main.py` é executado manualmente por mim, uma
vez por deal, e termina sozinho quando processa todos os arquivos da pasta.

## Autenticação e credenciais

- Usar OAuth ou uma service account do Google, com escopos mínimos
  necessários (Drive leitura, Sheets leitura+escrita restrita).
- Todas as chaves/credenciais (API do Claude, credenciais do Google) devem
  vir de variáveis de ambiente lidas via `config.py`, nunca hardcoded.
- Criar um `.env.example` mostrando quais variáveis são necessárias, sem
  valores reais.
- Confirmar que `.gitignore` exclui `.env` e qualquer arquivo de credencial
  antes do primeiro commit.

## Testes obrigatórios (escrever antes de considerar o projeto pronto)

- Um teste que confirma que a função de escrita **não tem permissão** de
  escrever na aba `Publicado` — tentar escrever lá deve falhar de forma
  explícita, não silenciosa.
- Um teste que confirma que um termo não encontrado no documento resulta em
  `not_found` explícito, nunca num campo vazio sem explicação.
- Um teste que confirma que toda linha escrita em `Pendente` tem uma citação
  (documento + seção) preenchida — rejeitar/sinalizar qualquer escrita sem
  isso.

## Fora de escopo para esta primeira versão

- Não construir o agente de consulta (esse é outro componente, hospedado em
  Apps Script, fora deste projeto).
- Não construir integração com Slack.
- Não implementar aprovação/publicação automática — mover dados de
  `Pendente` para `Publicado` continua sendo uma ação manual feita por mim
  fora deste script, pelo menos por enquanto.

## Ao terminar

Me dê um resumo do que foi criado, como rodar (`README.md`), e quais
variáveis de ambiente eu preciso preencher antes do primeiro teste real com
um deal de verdade.
