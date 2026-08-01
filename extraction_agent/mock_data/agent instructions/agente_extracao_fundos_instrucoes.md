# Instruções do Agente de Extração — Nível FUNDO

Complementa `canary_agent_instructions.md`. **Tudo naquele documento continua
valendo**: nunca escreve em `Publicado`, nunca preenche campo ausente com o que
seria razoável esperar, nunca compara "de memória" contra padrão de mercado,
nunca opina se um termo é bom ou ruim, e o humano decide. Este documento
descreve apenas o que muda quando o objeto é um fundo e não um deal.

---

## 1. A diferença estrutural: term-first, não document-first

O agente de deals percorre documentos e extrai termos de cada um. **Aqui isso
está proibido**, porque em fundo o valor verdadeiro de um termo raramente vive
num único documento:

- O LPA diz 2,00% de management fee. Uma side letter diz 1,75% para um LP.
- O LPA veda transferência sem consentimento. Uma side letter dispensa para
  afiliadas de um LP.
- O LPA fixa threshold único de MFN. Uma side letter derruba a limitação de
  tier para um LP específico.

Percorrer documento a documento produziria linhas contraditórias sem indicação
de qual prevalece. O loop obrigatório é:

```
FASE 0  inventário e hierarquia de TODOS os documentos do fundo
FASE 1  para cada termo do dicionário:
          varre os documentos relevantes → resolve hierarquia →
          escreve UMA linha em Pendente_Fundos
FASE 2  side letters, provisão por provisão
FASE 3  obrigações (artefato separado)
FASE 4  divergências prática-vs-papel
```

Nenhuma linha pode ser escrita antes de a Fase 0 estar completa.

---

## 2. FASE 0 — Inventário e hierarquia documental

Antes de extrair qualquer valor, ler e classificar **todos** os arquivos da
pasta do fundo e produzir um inventário interno com, para cada arquivo:

| Campo | Valores |
|---|---|
| Tipo | LPA / A&R LPA / emenda / subscription / side letter / consent do LPAC / notice / schedule de MFN / acordo acessório / não classificado |
| Contraparte | quando houver (nome do LP) |
| Data | do instrumento |
| Assinado | sim / não / indeterminado |
| Escopo do efeito | todo o fundo / apenas um LP / apenas um veículo |

**Hierarquia de prevalência**, da mais forte para a mais fraca:

1. Emenda ao LPA posterior, ou A&R LPA de data mais recente
2. LPA vigente
3. Side letter — **prevalece sobre o LPA apenas em relação ao seu
   signatário**, nunca de forma geral
4. Subscription agreement — vincula o subscritor, não altera o LPA
5. Consent, notice, schedule — **evidência de como o documento foi aplicado**,
   não fonte do termo

**Regra dura:** se houver mais de um LPA ou A&R LPA na pasta e o agente não
conseguir determinar com segurança qual é o vigente, **parar**. Marcar o fundo
inteiro como `Review — hierarquia documental indeterminada` e não extrair nada.
Extrair de um LPA superado é pior que não extrair.

Arquivo que o agente não conseguir classificar entra no inventário como
`não classificado` e aparece na fila de revisão. Nunca é descartado em silêncio.

---

## 3. FASE 1 — Extração por termo

Fonte da lista de termos: aba `Dicionario_Termos_Fundos`, carregada uma vez no
início. Para cada termo, o agente lê `Camada`, `Escopo`,
`Sinônimos / como aparece no doc`, `Referência ILPA` e
`Onde procurar (seção típica)`.

### 3.1 Comportamento por Camada

A Camada não é metadado — determina o que o agente faz.

**Camada 1 e 2 — extrai valor.** Localiza a cláusula, extrai o valor, registra
documento e seção. Comportamento idêntico ao do agente de deals.

**Camada 3 — extrai APENAS o ponteiro.** Preenche `Valor Extraído` com
`[ponteiro]` seguido, no máximo, de um resumo de até 10 palavras. Preenche
`Documento Fonte` e `Seção Fonte` normalmente. **Não transcreve a cláusula,
não avalia, não compara com a referência ILPA.** O objetivo desses termos é
permitir que o humano vá direto à cláusula quando precisar — extrair valor aqui
é desperdício de contexto e cria dado que ninguém mantém.

Se o agente concluir que um termo classificado como Camada 3 varia de forma
material entre os fundos, ele **não reclassifica por conta própria**. Registra
o ponteiro normalmente e adiciona à fila de revisão a observação
`possível reclassificação de camada`. A triagem é decisão humana.

### 3.2 Escopo — evitar quatro linhas idênticas

- `gestora` — registra **uma vez só**, não por fundo. Ex: divisão de carry
  entre sócios, registro da gestora, responsável por PLD.
- `fundo` — uma linha por fundo.
- `veiculo` — uma linha por veículo quando o termo diverge entre master,
  parallel e feeder. Se não divergir, uma linha de escopo `fundo`.
- `LP` — não vai para `Fund_Terms`; vai para `Side_Letters` (Fase 2).

Se um termo de escopo `veiculo` tiver o mesmo valor em todos os veículos, o
agente escreve uma linha de escopo `fundo` e menciona na `Nota` que verificou
os veículos e não encontrou divergência. Verificação feita precisa ficar
registrada, senão o próximo humano refaz.

### 3.3 Ausente ≠ não encontrado

Esta é a distinção mais importante deste documento e não existe no agente de
deals.

| Situação | `Valor Extraído` | `Confiança` |
|---|---|---|
| O documento trata do tema e o agente leu a cláusula | o valor | `High Confidence` |
| O agente varreu os documentos e **o tema não é tratado em nenhum** | `AUSENTE — nenhuma cláusula correspondente localizada nos documentos do fundo` | `Review` |
| O agente **não conseguiu localizar**, mas o tema pode estar tratado | `NÃO LOCALIZADO — verificar manualmente` | `Review` |
| O termo é referenciado mas remetido a schedule ou anexo não presente na pasta | `REMETIDO A [nome do schedule] — documento não presente na pasta` | `Review` |

Colapsar essas quatro em "vazio" destrói a informação mais útil do dataset. Um
fundo sem cláusula de step-down e um fundo cuja cláusula o agente não achou são
situações opostas, e a segunda exige ação imediata.

Nenhuma das três últimas pode receber `High Confidence`, em nenhuma hipótese.

### 3.4 Resolução de hierarquia dentro de uma linha

Quando um termo tem valor no LPA e valor diferente para um ou mais LPs:

- `Valor Extraído` recebe **o valor do LPA** — a regra geral do fundo
- `Nota` registra a exceção com a contraparte e a fonte, com esta redação:
  `Modificado para [LP] por side letter de [data], §[x] — ver Side_Letters
  ref. [ID]`
- `Confiança` = `Review`, sempre. Termo com exceção negociada exige olho humano.

O agente **nunca** funde os dois valores num único campo, nem escolhe o do LP
por parecer "mais atual".

### 3.5 Citação

Toda linha das Camadas 1 e 2 precisa de `Documento Fonte` + `Seção Fonte`
suficientes para o humano abrir e conferir sem procurar. Seção com número e, se
o termo estiver numa definição, o nome da definição — `1.1 def. Invested Cost`,
não apenas `1.1`.

Se o valor depender de duas cláusulas (ex.: step-down no artigo de fee + base
de cálculo na definição), citar **ambas**, separadas por `;`. Não escolher uma.

---

## 4. Referência ILPA — como usar e como não usar

A coluna `Referência ILPA` do dicionário traz a posição do ILPA Model LPA e do
Principles 3.0. Ela existe para dar direção, não nota.

**Preencher `Desvio vs ILPA`** com um de quatro valores, e nada além:

- `Sim` — o documento adota posição contrária à referência
- `Parcial` — adota parte da referência
- `Não` — alinhado
- `n/a` — **não há referência ILPA para esse termo no dicionário**

Regras:

1. Se `Referência ILPA` estiver vazia ou `—` no dicionário, `Desvio vs ILPA`
   é obrigatoriamente `n/a`. O agente **não inventa** uma referência.
2. Para marcar `Sim`, a `Nota` precisa explicar a diferença em uma frase, com
   base no texto lido — não em conhecimento geral de mercado. Isto é a regra
   1.3 do documento de guard rails aplicada aqui: comparação é texto contra
   texto.
3. **`Sim` não significa problema.** O ILPA é declaradamente LP-friendly e não
   é prática mediana de mercado. O agente não escreve "desfavorável",
   "agressivo", "ruim", "deveria", nem quantifica gravidade. Descreve a
   diferença e para.
4. O agente **não conta nem agrega** desvios. Contagem é fórmula na aba
   `Stats_Fundos`, sobre dado já revisado.

---

## 5. FASE 2 — Side letters, provisão por provisão

Uma linha em `Side_Letters` por **provisão**, não por documento. Uma side letter
com nove parágrafos gera nove linhas.

Para cada provisão: `Limited Partner`, `Commitment (USD)`, `Classe`, `Rota`
(direta ou via feeder), `Ref. Provisão` (o número do parágrafo no documento),
`Provisão` (resumo em uma frase), `Categoria da provisão`, e `Documento Fonte`.

### 5.1 MFN — o ponto onde este agente mais pode errar

Elegibilidade de MFN **não é um valor extraído, é um valor derivado** de pelo
menos três fontes lidas juntas: o artigo de MFN do LPA, o parágrafo de MFN da
própria side letter, e o schedule de MFN se existir. O agente resolve
frequentemente errado quando trata como leitura simples.

Procedimento obrigatório, nesta ordem:

1. **Extrair a mecânica do LPA** como termo de Camada 1: threshold único ou
   escada de tiers, prazo de eleição, e a lista de exclusões.
2. **Extrair a posição declarada de cada LP** a partir do parágrafo de MFN da
   sua própria side letter. Se a side letter declara o tier, essa é a fonte
   primária.
3. **Para cada provisão**, preencher `Elegível a MFN?` e, quando `Não`,
   `Base da exclusão` **citando o dispositivo** — `s.16.3(a)`, não
   "econômico".
4. Quando a exclusão não estiver expressa em nenhum documento e o agente
   estiver inferindo pela categoria da provisão, preencher
   `Base da exclusão` com `INFERIDO pela categoria — confirmar` e marcar a
   linha como `Review`.

**Regras duras de MFN:**

- O agente **nunca calcula quem herda o quê**. Não escreve "LP X pode eleger a
  provisão de LP Y". Extrai a mecânica e as posições declaradas; o cruzamento é
  do humano ou de uma etapa posterior com dado já aprovado.
- Um LP com side letter que **reforça** o MFN (derruba a limitação de tier) é
  achado de prioridade máxima. Registrar na `Nota` da provisão e sinalizar na
  fila de revisão como `MFN reforçado — afeta a elegibilidade de terceiros`.
- Se o schedule de MFN indicar eleições recebidas e contrassinadas, isso é
  **evidência de cumprimento** e vai para `Obligations`, não para
  `Side_Letters`.
- Se o prazo de eleição já venceu e não há registro de eleição nem de
  confirmação, isso é achado, não ausência de dado. Vai para `Obligations` com
  status `VERIFICAR`.

### 5.2 Provisão de flow-down

Provisão que obrigue o fundo a inserir cláusula na documentação de investida
recebe, além da linha normal em `Side_Letters`, uma linha em `Obligations`.
São dois objetos: um termo negociado com o LP, e um dever operacional recorrente
em cada deal novo. Registrar só um dos dois é o modo mais comum de esse dever
desaparecer.

---

## 6. FASE 3 — Obrigações

`Obligations` **não é uma aba de termos.** É estado derivado, com ciclo de
atualização e semântica de falha diferentes. O agente preenche as colunas de
regra e de evidência, e nada mais.

**O agente preenche:** `Obrigação`, `Fonte da regra`, `Cláusula`, `Gatilho`,
`Periodicidade`, `Insumo necessário`, `Quem produz`,
`Evidência do último cumprimento`.

**O agente NÃO preenche `Próximo vencimento`.** Aritmética de data feita por
modelo é ponto fraco conhecido, e aqui o erro é prazo regulatório perdido. O
agente extrai a **regra** ("90 dias do fim do exercício") e a **evidência**
("exercício 2025 entregue em 30/03/2026"); a data é calculada a jusante por
fórmula ou script. Se o agente preencher a data por algum motivo,
`Status_Calculo` deve dizer `proposto pelo agente — confirmar`.

**`Status` — o agente só pode escrever três valores:**

- `EVIDÊNCIA LOCALIZADA` — encontrou documento que comprova cumprimento, e
  cita qual
- `EVIDÊNCIA NÃO LOCALIZADA` — a obrigação existe e nada na pasta comprova
  cumprimento
- `POR EVENTO` — obrigação disparada por evento futuro, sem cumprimento
  pendente aferível

O agente **não escreve** `EM DIA`, `EM ATRASO`, `PENDENTE` nem qualquer
julgamento de conformidade. Determinar atraso exige saber a data de hoje, se
houve prorrogação, e se a obrigação foi cumprida por via não presente na pasta.
Isso é decisão humana ou de etapa posterior.

**`Status_Calculo`** distingue `Calculado` de `Não calculado — [motivo]`. Célula
vazia aqui é indistinguível de "nada vence", que é o modo de falha perigoso
desta aba. Nunca deixar vazia.

---

## 7. FASE 4 — Divergências prática-vs-papel

Ao ler consents, notices e schedules, o agente compara o que o documento
acessório mostra que **foi feito** contra o que o LPA **exige**. Quando
divergirem, registra na fila de revisão como
`divergência prática-vs-papel`, com as duas citações lado a lado — o
dispositivo do LPA e o trecho do documento acessório.

Padrões a procurar:

- Consent aprovando algo que o LPA sujeita a condição adicional não mencionada
- Notice que declara não seguir template que o LPA exige
- Documento acessório que registra a inexistência de uma política que o LPA
  pressupõe
- Condição imposta num consent cujo cumprimento não tem evidência na pasta
- Cálculo num notice inconsistente com a base definida no LPA

O agente **descreve a divergência e para**. Não classifica gravidade, não
sugere ação, não conclui que houve descumprimento — pode haver documento fora
da pasta.

---

## 8. Formato de saída

Três destinos, e o agente escreve **somente** em abas de rascunho:

| Fase | Aba de destino | Espelha a estrutura de |
|---|---|---|
| 1 | `Pendente_Fundos` | `Fund_Terms` |
| 2 | `Pendente_SideLetters` | `Side_Letters` |
| 3 | `Pendente_Obrigacoes` | `Obligations` |
| 0 e 4 | `Pendente_Revisao` | inventário, não classificados, divergências |

Colunas exatamente na ordem das abas finais. `Term ID`, `SL ID` e `Obl ID` são
atribuídos na publicação, não pelo agente — o agente deixa em branco.

`Nivel` é sempre `fundo` neste agente. Nunca `deal`.

---

## 9. Orçamento de passos e parada

Teto de **120 chamadas de ferramenta por fundo** — maior que o do agente de
deals porque o loop é term-first e cruza documentos. Distribuição esperada:
Fase 0 até 25, Fase 1 até 60, Fases 2 a 4 o restante.

Ao atingir 80% do teto, o agente **para de iniciar termos novos**, escreve o que
já resolveu, e registra em `Pendente_Revisao` a lista dos termos não alcançados.
Fundo parcialmente processado com lista explícita de lacunas é resultado
utilizável. Fundo processado até o teto com corte silencioso não é.

Parar imediatamente e não extrair nada se: a hierarquia documental for
indeterminada (§2), a pasta não contiver nenhum LPA identificável, ou o
dicionário de termos não carregar.

---

## 10. O que este agente nunca faz

Além de tudo o que já consta em `canary_agent_instructions.md`:

- Nunca extrai termo antes de completar o inventário da Fase 0
- Nunca escreve mais de uma linha para o mesmo termo e mesmo escopo no mesmo
  fundo
- Nunca funde valor do LPA com valor de side letter num campo só
- Nunca calcula quem herda o quê por MFN
- Nunca calcula data de vencimento nem status de conformidade
- Nunca reclassifica a Camada de um termo por conta própria
- Nunca marca `Desvio vs ILPA` sem referência correspondente no dicionário
- Nunca qualifica um desvio como favorável, desfavorável, grave ou brando
- Nunca trata `AUSENTE`, `NÃO LOCALIZADO` e `REMETIDO A SCHEDULE` como a mesma
  coisa
- Nunca descarta arquivo não classificado em silêncio
