# ESTRELA CADENTE — simulador de carreira em Hollywood (com filmes e pessoas reais)
### Documento de brainstorm v2 — panorama do mercado, sistemas, conteúdo, caminhos e finais

> Jogo web curto (3–6 min por run), sem cadastro, sem instalação. Você cria um ator ou atriz,
> distribui pontos entre atributos e, ao longo de 30 anos de carreira, escolhe **às cegas** entre
> ofertas reais descritas sem nome ("um diretor que faz 99 takes da cena de abertura").
> Só depois de escolher o jogo revela: **A Rede Social (2010), David Fincher, no papel que foi
> de Jesse Eisenberg.** No fim, um card compartilhável diz como sua carreira terminou:
> da lenda EGOT ao "pelado na Sunset Boulevard gritando com um hidrante".

---

## 0. Já existe algo assim?

Resposta curta: **não exatamente**. Existe muita coisa *perto*, mas ninguém juntou as três peças
(run curta compartilhável + filmes e pessoas reais com revelação + finais satíricos).

| Jogo | Ano / plataforma | O que é | Por que não é a mesma coisa |
|---|---|---|---|
| **BitLife** (caminho de ator) | 2018– / mobile | Life sim de texto. Carreira de ator vira "movie star", libera barra de fama, talk shows, livros, comerciais. | Genérico, sem narrativa de Hollywood, tudo fictício, run longa, sem card de final. |
| **Kim Kardashian: Hollywood** | 2014–2024 / mobile (Glu) | Suba de desconhecido a lista A fazendo jobs, eventos e dates. Faturou US$ 156 mi em 2 anos. Fechou em abril de 2024. | Grind com compras in-app; sem escolhas com consequência; tudo fictício. Mostra que o **tema vende**. |
| **Stardom: Hollywood** / *Hollywood Movie Star Life Sim* / *Starlight Actor Life Sim* / *ActorLife* | 2013– / mobile | Simuladores "de pequeno papel a estrela" com testes, escândalos, paparazzi, RP. | Mesma família do anterior: grind, não história. Fictícios. |
| **Hollywood Visionary** (Choice of Games, Aaron Reed) | 2015 / texto (Steam, mobile) | Você comanda um estúdio na Hollywood dos anos 50. Vários finais. | Chefe de estúdio, não ator. Texto longo (horas). Nomes fictícios. |
| **Hollywood Hustle** | 2008 / celular Java | Aventura de texto com a atriz Lucy Starling; 9 finais; sem "certo ou errado". | Linear, antigo, fictício. Mas prova o formato "escolhas → final" no tema. |
| **The Fame Game: Welcome to Hollywood** | set/2025 / Steam (US$ 8,99) | Dating sim em FMV num reality de TV, vários finais. | Romance em vídeo, não carreira. |
| **Where We Lay Our Scene** | visual novel | Ator envelhecendo decide o próximo passo da carreira. Finais "nem bons nem ruins". | Visual novel longa; um recorte da ideia (nosso Ato IV). |
| **Hollywood Animal** (Weappy) | abr/2025 / Steam early access, US$ 19,99 | Tycoon de estúdio a partir de 1929, com máfia e métodos sujos. "Mostly Positive" com ~3,8 mil reviews. | Gestão profunda, horas de jogo, nomes alterados. |
| **The Movies** (Lionhead) | 2005 / PC | Tycoon de estúdio com editor de filmes. | Idem. |
| **Actor Tycoon 2** | itch.io / Steam (beta) | Você é o **agente**, escolhe papéis para seus atores. | Perspectiva do agente. |
| **Rockstar!** | anos 80 / texto | Paródia da indústria da música: banda, drogas, turnês, saúde. | Música, não cinema. Mas é o ancestral espiritual do tom. |
| **Reaching For The Star** | previsto Q4/2027 / Steam | Life sim de atriz/idol (testes, música, variedades). | Ainda não existe; fictício; coreano. |
| **I Want To Be Famous** (Twine) | itch.io | Escolha seu caminho para a fama; 5 caminhos + 1 final secreto. | Protótipo pequeno, fictício. |
| **Copero / El Ídolo** | 2026 / web | Carreira de jogador de futebol, 16→38 anos, swipe, card final. | **Estruturalmente é o que queremos, mas em futebol.** |
| **82-0 / 7-0** | 2026 / web | Draft de jogadores reais (um por década), simulação, card. | Dados reais + reconhecimento, mas sem narrativa. |
| **Jogos diários de cinema** (Framed, Box Office Game, Cine2Nerdle, Spotle Movies, Critical) | web | Adivinhe o filme por frames / bilheteria / review do Letterboxd. | Provam que **o público de cinema adora "adivinhe por descrição"** e já vive de dados do TMDB. |

**O buraco no mercado**: ninguém fez o "82-0 do cinema" em formato de carreira. Nenhum é em
português. Nenhum usa filmografia real como material de escolha. E nenhum trata o fracasso
(OD, culto, esquecimento, pornô) como final tão desejável quanto o sucesso.

**Riscos de alguém chegar antes**: baixo-médio. A onda 82-0 → 7-0 → Copero mostra que o formato
está sendo copiado para outros esportes a cada mês; cinema é o próximo tema óbvio. Vale correr.

---

## 1. O que aprender com as referências

| Jogo | O que copiar | O que fazer diferente |
|---|---|---|
| **82-0 / 7-0** | Loop de 2 minutos. Um "sorteio" te empurra para escolhas imperfeitas. Resultado com categoria. Card para print. **Material real: o prazer é reconhecer.** | Eles não têm narrativa; aqui a narrativa É o produto. |
| **Copero** | Estrutura por idade. Swipe esquerda/direita estilo *Reigns*. Probabilidade mostrada. Efeitos imediatos, diferidos e permanentes. Conquistas com nome engraçado. Evento absurdo que vira conversa (a tatuagem de águia gigante). | Em Hollywood o "troféu" é plural: prêmio, bilheteria, culto, meme. |
| **Volante de Ouro** | Escolha de era muda tudo. Toggle "realismo" permite morte. Modo cenário (assuma uma pessoa real num momento). Disclaimer "fan-made, não afiliado". | Volante é longo; aqui a run cabe numa fila de banco. |

**Regras de ouro do formato viral**
1. Run curta, final forte, card bonito. O jogo de verdade acontece no grupo comparando finais.
2. **Decidir no escuro, reconhecer depois.** A descrição é o enigma; a revelação é a recompensa.
3. Toda escolha tem um lado óbvio e um lado tentador.
4. Aleatoriedade visível: perder com "72% de chance" é melhor que perder sem saber por quê.
5. Finais ruins têm que ser tão desejáveis quanto os bons.

---

## 2. A grande mudança: tudo real

### 2.1 O loop de um card de projeto
```
[1998 • 27 anos • Fama ▮▮▯▯▯ • Contatos 3]

◀ "Um diretor que mora na Inglaterra e        "Um produtor cuja campanha de Oscar é    ▶
   não entra em avião quer você num hotel      mais agressiva que o filme quer você numa
   vazio no inverno. Uma cena vai ter 127       comédia romântica de época sobre um
   takes. Seu marido na tela é mais famoso      dramaturgo com bloqueio criativo.
   que você."                                   Figurino lindo. Rival de bilheteria: um
   💵 $      🏆 5%     🔮 60%    🧨 30%           filme de guerra de um diretor barbudo."
   estreia em 2 anos                            💵 $$     🏆 45%    🔮 5%     🧨 10%
                                                estreia em 1 ano
```
Você escolhe. O card vira:

> **O ILUMINADO (1980)** — dir. Stanley Kubrick. Você ficou com o papel que foi de **Shelley Duvall**.
> Contracenou com Jack Nicholson. Filmagem: 13 meses. A cena do taco de beisebol: 127 takes (recorde).
>
> **O que aconteceu com o filme:** bilheteria OK (US$ 47 mi), crítica dividida na época,
> hoje considerado um dos maiores filmes de terror da história.
> **O que aconteceu com você:** [rolagem: Talento 3 vs. exigência do papel 4] *indicada ao Razzie
> de Pior Atriz.* Estabilidade −3. Prestígio +0 (por enquanto).
>
> ⏳ **Revisão histórica (card no Ato V):** "Em 2022 a Razzie Foundation retira sua indicação e pede
> desculpas. Você diz que não se lembra do filme. É mentira."

A outra opção também é revelada, menor, embaixo: *"Você recusou: Shakespeare Apaixonado (1998) —
Gwyneth Paltrow ganhou o Oscar de Melhor Atriz. O filme bateu O Resgate do Soldado Ryan."*
Esse "o que você recusou" é o combustível do compartilhamento.

(Exemplo propositalmente anacrônico para mostrar os dois cards; no jogo, as duas ofertas são do mesmo ano.)

### 2.2 Por que isso funciona melhor que ficção
- **Reconhecimento** é o mesmo prazer do 82-0: "era o Fincher!", "eu recusei Titanic!!".
- **Trívia de graça**: cada revelação ensina algo ("Will Smith recusou Neo para fazer *As Loucas
  Aventuras de James West*"). Um card de trívia opcional: *"Quem recusou este papel na vida real"*.
- **Card final imbatível**: *"Em 1996 recusei Jerry Maguire para fazer Striptease. Em 2003 trabalhei
  com Scorsese. Terminei: Rei do Filme de Natal."* Isso é um tweet pronto.
- **Conteúdo quase infinito**: o TMDB tem 1 milhão de filmes; a curadoria é o trabalho, não a invenção.
- **Debate**: "o jogo diz que Hereditary dava 60% de chance de prêmio e a Toni Collette foi esnobada" vira
  discussão de Letterboxd.

### 2.3 Informação é atributo (o point buy ganha sentido)
Antes de escolher, quanto você enxerga da oferta depende de quem você é:

| Atributo | O que ele revela antes da escolha |
|---|---|
| **Contatos 1** | Gênero, orçamento aproximado, tempo de filmagem. |
| **Contatos 3** | Descrição do diretor com um "tell" a mais (filmes anteriores descritos). |
| **Contatos 5** | **O nome do diretor.** Você sabe que é o Nolan. Os outros não. |
| **Juízo ≥ 3** | 🚩 "Sinal de alerta": produção documentadamente problemática (reshoots, diretor demitido, orçamento estourado). |
| **Talento ≥ 3** | Faixa de qualidade do roteiro (proxy: crítica real, mostrada como "o texto é bom / é um pretexto para explosões"). |
| **Carisma ≥ 3** | Descrição dos co-stars ("você vai contracenar com o ator mais bem pago do mundo"). |
| **Beleza** | Não revela nada. Mas abre ofertas: papéis de galã/musa só aparecem com Beleza ≥ 3. |

Quem gasta tudo em Beleza joga literalmente no escuro. Isso é tema e mecânica ao mesmo tempo.

### 2.4 Linha do tempo real
- Na criação você escolhe o **ano de estreia** (MVP: 1975–1995, para a carreira de 30 anos fechar
  antes de 2026). Depois: 1950–2020, com "futuro especulativo" claramente marcado após 2026.
- Cada ato = 6 anos. Cada ato tem 3 cards de projeto (um a cada 2 anos), e as ofertas vêm de filmes
  lançados nos 1–2 anos seguintes ao ano atual (o **pipeline**: você assina em 1996, estreia em 1997).
- Eventos do mundo real entram como cards de contexto quando o ano chega: greve de roteiristas
  (1988, 2007, 2023), #MeToo (2017), pandemia (2020), chegada do streaming, "a noite do tapa" (2022).
- Modo Cenário (v2): "É 1997. Você é a atriz que acabou de recusar Titanic. O telefone toca."

### 2.5 Como as ofertas são geradas (algoritmo)
1. **Pool**: filmes lançados em [ano+1, ano+2] no TMDB com um ator/atriz do seu gênero nas 4 primeiras
   posições do elenco; excluir animação (exceto como "papel de voz"), documentário, filmes sem orçamento
   nem bilheteria conhecidos.
2. **Faixa**: sua Fama define a faixa de orçamento/popularidade. Sempre 1 oferta "do seu tamanho",
   1 "acima" (reach) e, às vezes, 1 "abaixo" (indie/prestígio).
3. **Contraste garantido**: quando possível, uma "armadilha" (orçamento alto, crítica baixa) e uma
   "pérola" (orçamento baixo, crítica alta) com descrições de dificuldade parecida. Nunca duas do mesmo gênero.
4. **Ganchos narrativos**: se você já trabalhou com um diretor, ele pode voltar ("o diretor dos 127
   takes te quer de novo. Diz que mudou."). Se tem flag de franquia, a sequência aparece como obrigação.
5. **Semente determinística**: mesma seed → mesmas ofertas (desafio diário, link "jogue a mesma vida").

### 2.6 Como o resultado é calculado
O **filme** já aconteceu; a história não muda. O que muda é **você dentro dele**.

```
filme (fixo, da base):  crítica (RT/Metacritic), bilheteria/orçamento, prêmios do filme, reputação hoje
papel (fixo, da base):  posição no elenco, o ator original foi indicado/ganhou?, exigência (drama 4, ação 1)
você (variável):        Talento vs exigência, Heat, Estabilidade, sorte

resultado pessoal (rolagem):
  "Indicado(a)" / "Ganhou"      se o papel original foi premiado E Talento passa no teste
  "Roubou a cena"                papel pequeno, Talento alto, roll
  "Fez o trabalho"               neutro
  "Passou batido"                filme flopou e você junto
  "Miscast"                      papel exigente, Talento baixo: "a crítica te escolheu como o problema"
  "Razzie"                       Talento ≤ 2 em papel que já era alvo (dados reais de Razzies)
```
- Fama += f(bilheteria, posição no elenco). Prestígio += f(crítica, prêmios). Dinheiro += cachê
  estimado pela faixa e época (corrigido pela inflação, mostrado em dólares da época e de hoje).
- 10% de variância deliberada: às vezes você é indicado por um filme ruim. Hollywood é assim.
- **Revisão histórica**: ~50 filmes curados cuja reputação virou (O Iluminado, Blade Runner, Clube
  da Luta, Crash ao contrário). Eles geram um card tardio que recalcula Prestígio. É a mecânica mais
  cinéfila do jogo.

### 2.7 Pessoas reais: fato é fato, rumor é rumor
Decisão de produto: **sem medo de processo**. O jogo é sátira sobre figuras públicas, usa fatos de
obra e fatos públicos, e tudo que circulou como rumor entra **marcado como rumor**. Essa marcação
é fácil, é honesta e, de quebra, é engraçada: Hollywood funciona a rumor.

| Tipo de informação | Como entra no jogo | Exemplo de texto |
|---|---|---|
| **Fato de obra** (filme, papel, bilheteria, crítica, prêmio, takes, duração de set, quem recusou) | Direto, sem ressalva | "A cena de abertura teve 99 takes." |
| **Fato público sobre a pessoa** (condenação, feudo público, declaração, o tapa, falência) | Direto, com data | "Em 2020 e 2022 o produtor foi condenado." |
| **Rumor / fofoca / 'fontes'** (set problemático, briga de bastidor, romance, hábito) | Sempre com etiqueta: *"dizem que"*, *"segundo o tabloide"*, *"rumor nunca confirmado"*, ou uma tag visual 🗞️ RUMOR | "🗞️ Dizem que ele chegou 4 horas atrasado todos os dias. Ele nega." |
| **Vício, sexo e crime que acontecem com VOCÊ** | Com personagens fictícios de **nome caricato**, em circunstâncias que **remetem a um caso real famoso**. O jogo **não nomeia** o caso: a circunstância faz lembrar, e quem reconhece, reconhece. | "No bangalô 3 de um hotel na Sunset, Chip Marmont te oferece uma mistura que ele chama de speedball." |

Regras práticas:
- Co-stars reais são colegas de cena, com fatos e rumores etiquetados. Romance, casamento e vício dentro do jogo são com personagens fictícios, porque romance real inventado não é rumor, é invenção.
- A tag 🗞️ RUMOR vira elemento de interface: Carisma alto "ouve mais rumores" antes de escolher (mais informação, de qualidade duvidosa). Rumor pode estar errado: 20% dos rumores do jogo são falsos e a revelação diz "o rumor era mentira".
- Disclaimer curto na home e no card: fan-made, sátira, não afiliado, dados do TMDB/OMDb.
- Pôsteres: uso dentro do jogo com atribuição ao TMDB; no card compartilhável, só texto e tipografia própria, porque pôster é do estúdio e o card vai circular fora do jogo.

#### 2.7.1 Eventos fictícios que ecoam casos reais
O que dispara a memória do jogador não é o nome, é a **circunstância**: a fita que some da casa, a loja de luxo em Beverly Hills, o bangalô do hotel. Então todo evento de vício, sexo, crime ou surto segue três regras:

1. **A circunstância é copiada de um caso real famoso**, com detalhes reconhecíveis (lugar, valor, objeto, frase).
2. **Os personagens envolvidos são fictícios com nome caricato**: ou trocadilho com o original (*Keith Brilhante*, *Heidi Flash*, *Dr. Bem-Estar*), ou nome "de Hollywood" com cheiro de época (*Chip Marmont*, *Candy Vermont*, *Sal Tubarão*, *Tommy Lixo*).
3. **O jogo não nomeia o caso.** Nada de "aconteceu de verdade com X". A referência fica implícita, no máximo com uma etiqueta genérica *"inspirado em fatos reais"* no rodapé do card, sem nome. O reconhecimento é o prêmio do jogador, e explicar a piada mata a piada. (A coluna "Caso real" da tabela abaixo é referência interna para quem escreve, não texto de jogo.)

Banco inicial de casos para os escritores (todos públicos e amplamente documentados; expandir para ~80). A coluna "Caso real" nunca aparece no jogo:

| Caso real | Evento no jogo (circunstância copiada) | Personagem fictício | Medidor |
|---|---|---|---|
| Pamela Anderson e Tommy Lee: fita roubada do cofre da casa durante uma reforma (1995) | "Durante a reforma, um eletricista leva o cofre. Dentro, uma fita." Opções: processar / ignorar / "lançar você mesmo" | *Tommy Lixo*, baterista de metal; *Rand, o eletricista* | Heat +5, Estabilidade −3, Bagagem |
| Winona Ryder: furto de US$ 5,5 mil em roupas na Saks de Beverly Hills (2001) | "Você sai de uma loja de luxo em Beverly Hills com US$ 5 mil em roupas e etiquetas cortadas na bolsa." | *Seguranças da Sacks* | Fama +, Prestígio −, pausa de 2 anos nas ofertas |
| John Belushi: speedball no bangalô 3 do Chateau Marmont (1982) | "Bangalô 3. Chip Marmont te oferece uma mistura." [Juízo] | *Chip Marmont*, anfitrião eterno | Vício +3; Modo Realista: 15% OD |
| River Phoenix: overdose na calçada do Viper Room (1993) | "Na porta de um clube na Sunset, de madrugada, com um amigo músico." | *Johnny Víbora*, dono do clube | Modo Realista: OD |
| Robert Downey Jr.: preso em 1996 e encontrado dormindo na cama de um vizinho (1996) | "Você acorda na cama de uma casa que não é sua. A família está olhando." | *Os Vizinhos de Malibu* | Vício +2, Heat +3, flag `preso_1` |
| Hugh Grant: preso com uma profissional do sexo num carro na Sunset Blvd (1995) | "Carro estacionado na Sunset, 1h da manhã. Luz azul no retrovisor." | *Divina Marrom* | Heat +5; [Carisma 4] vira piada no late show e Fama ++ |
| Heidi Fleiss: a agenda da "madame de Hollywood" (1993) | "Uma agenda com nomes vaza. O seu está nela." | *Heidi Flash* | Bagagem; 🗞️ RUMOR para os outros nomes |
| Rob Lowe: fita com uma menor durante a convenção democrata em Atlanta (1988) | "Uma fita gravada num hotel durante uma convenção política." | *Festa da Convenção* | Bagagem forte, Prestígio −−; comeback só via comédia de TV |
| Charlie Sheen: "tiger blood", demitido da sitcom mais paga da TV (2011) | "Você dá uma entrevista de 40 minutos sobre o seu sangue. É demitido(a) da série mais bem paga da TV." | *Dr. Bem-Estar* (médico das celebridades) | Vício +3, Fama +10, Dinheiro −−, flag `demitido_sitcom` |
| Lindsay Lohan: tornozeleira, tribunal, reabilitações (2007–2013) | "Sua terceira audiência do ano. A juíza conhece seu nome." | *Juíza Sauer-Mente* | Vício, Bagagem, caminho da Espiral |
| Mel Gibson: DUI e discurso antissemita gravado pela polícia (2006) | "Parado(a) por dirigir bêbado(a), você diz coisas que a gravação registra." | *Policial de Malibu* | Cancelado por 10 anos, comeback via direção |
| Wesley Snipes: prisão por sonegação (2010) | "Seu guru fiscal explica que imposto de renda é 'voluntário'." [Juízo] | *Eddie Isento*, consultor | Dinheiro −−, 3 anos preso, flag `preso_fiscal` |
| Nicolas Cage: crânio de dinossauro, castelos, dívida com o fisco | "Um leilão. Um crânio de dinossauro. Você levanta a mão." | *Leiloeiro Sotheby Falso* | Dinheiro −−, flag `filmografia_de_cage` (aceita tudo para pagar) |
| Kim Basinger: comprou uma cidade na Geórgia e faliu (1989/1993) | "Uma cidade inteira está à venda por US$ 20 milhões." | *Prefeito de Braselton* | Dinheiro −− |
| Martin Lawrence: surto no meio da Ventura Blvd com uma arma, gritando (1996) | "Você está no meio da avenida, gritando. Há uma arma. Há um helicóptero." | *Helicóptero do Canal 7* | Estabilidade 0 → caminho "pelado na rua" |
| Anne Heche: bateu na porta de uma casa em Fresno dizendo que ia para a nave (2000) | "Você bate na porta de uma casa no interior e pede para esperar a nave." | *Família de Fresno* | Estabilidade −−, Heat + |
| Randy Quaid: fugiu para o Canadá fugindo dos "star whackers" (2010) | "Você conclui que há um grupo matando astros e foge para o Canadá." | *Os Star Whackers* | Final secreto "Refúgio no Canadá" |
| Shia LaBeouf: saco de papel "I AM NOT FAMOUS ANYMORE" no tapete vermelho (2014) | "Você vai à première com um saco de papel na cabeça." | — | Heat +3, Prestígio ±, flag `performance_art` |
| Joaquin Phoenix: carreira falsa de rapper e documentário (2009–2010) | "Você anuncia que largou o cinema para ser rapper. É sério? Nem você sabe." | *Casey, o cunhado com a câmera* | Fama +, Prestígio − por 2 anos, depois ++ |
| Christian Bale: áudio gritando com o diretor de fotografia no set (2009) | "Alguém mexe na luz durante sua cena. Você grita por 4 minutos. Há áudio." | *Shane, o iluminador* | Reputação na indústria −2, Heat + |
| Russell Crowe: telefone arremessado no funcionário do hotel (2005) | "O telefone do hotel não liga para sua casa. Você arremessa o telefone." | *Nestor, da recepção* | Reputação −1, Heat +2 |
| Zsa Zsa Gabor: tapa num policial de Beverly Hills (1989) | "O policial pede a carteira. Você dá um tapa." | *Policial Kramer* | Fama +, 3 dias de cadeia, flag meme |
| Reese Witherspoon: "você sabe quem eu sou?" na blitz (2013) | "Seu marido é parado na blitz. Você sai do carro e pergunta se o policial sabe quem você é." | *Policial de Atlanta* | Heat +, [Carisma 4] vira piada e Fama + |
| Lori Loughlin e Felicity Huffman: suborno para filhos entrarem na universidade (2019) | "Um consultor garante vaga para sua filha como remadora. Ela nunca remou." [Juízo] | *Rick Cantor*, consultor | Preso(a) 2 meses, Cancelado |
| Allison Mack e NXIVM: grupo de autoajuda que marcava mulheres a ferro (2018) | "O grupo de autoconhecimento tem um nível secreto. Há uma cerimônia." | *Keith Brilhante*, guru | Caminho do Culto, final "Presa pelo culto" |
| Tom Cruise: pulo no sofá da Oprah (2005) | "Num talk show, você está tão apaixonado(a) que sobe no sofá." | *Apresentadora de Chicago* | Fama +5, Prestígio −2, meme eterno |
| Dustin Diamond (o Screech): fita íntima lançada pelo próprio ex-astro de sitcom (2006) | "Seu dinheiro acabou. Um empresário sugere 'lançar uma fita'." | *Sal Tubarão*, empresário | Caminho da indústria adulta |
| Drew Barrymore: reabilitação aos 13 (1989) | Origem *ex-criança estrela*: "Você tem 13 anos e já conhece a clínica." | *Clínica de Malibu* | Vício inicial 2, Estabilidade inicial −1 |
| Macaulay Culkin / Gary Coleman: pais gastaram o dinheiro; processo (1990s) | "Você descobre que a conta está vazia. Seus pais explicam." | *Papai Empresário* | Dinheiro −−, Estabilidade −2 |
| Jared Leto: "presentes" de método para o elenco (2016) | "Um co-star 'de método' manda um rato morto para o seu trailer." | *Jordan Catalano Jr.* | Estabilidade −1, 🗞️ RUMOR |
| Nick Nolte: a foto da prisão por dirigir sob efeito de GHB (2002) | "Sua foto de prisão vira a mais famosa da década." | — | Heat +4, meme eterno |
| Brendan Fraser: anos sumido, volta e ganha o Oscar (2023) | Ato V: "Você passou 10 anos fora. Um diretor te quer num papel de 270 kg." | — | Final "Comeback aos 50" |

Esquema do evento fictício ganha um campo **interno**, nunca renderizado:
```yaml
inspirado_em:   # metadado editorial; não aparece no jogo
  - { quem: "Winona Ryder", ano: 2001, o_que: "Furto de US$ 5.500 em roupas na Saks de Beverly Hills" }
```
Serve para os escritores não repetirem caso, para checar que a circunstância está fiel, e para uma eventual página "créditos" fora do jogo.

### 2.8 Mais exemplos de descrição → revelação (para calibrar o tom)

| Descrição às cegas | Revelação | Dado real que o jogo usa |
|---|---|---|
| "Um diretor britânico que não tem celular nem e-mail quer você num filme sobre sonhos dentro de sonhos. Você vai lutar num corredor que gira. Orçamento de US$ 160 mi." | **A Origem (2010)**, Christopher Nolan, papel de Joseph Gordon-Levitt | US$ 836 mi de bilheteria; 4 Oscars técnicos; nenhum de atuação → "Fez o trabalho, Fama +++, Prestígio +" |
| "O quinto filme de um universo compartilhado de heróis. Seu papel: a estagiária de ciência que faz piadas. Contrato de mais aparições." | **Thor (2011)**, Kenneth Branagh, papel de Kat Dennings | Franquia: Fama +, Dinheiro ++, Prestígio −, flag `franquia` |
| "Um estúdio com logo em serifa quer você num terror sobre luto, filmado em Utah, cheio de casinhas em miniatura. Sem dinheiro. Você vai gritar muito." | **Hereditary (2018)**, Ari Aster, papel de Toni Collette | US$ 10 mi → US$ 80 mi; crítica 89%; Collette **não** foi indicada → "A crítica diz que você foi roubada". Prestígio ++, Estabilidade −2 |
| "Um diretor de 80 anos vai fazer 'o último filme dele' (de novo). Três horas e meia sobre um crime esquecido em Oklahoma. Set cheio de gente que você quer conhecer." | **Assassinos da Lua das Flores (2023)**, Martin Scorsese, papel de Lily Gladstone | 10 indicações, 0 vitórias → "Indicada. Perdeu na noite. Todo mundo achou injusto." Prestígio +++ |
| "Um comediante leva os amigos para filmar no Havaí. Ninguém sabe se é filme ou férias. Você tem perda de memória." | **Como Se Fosse a Primeira Vez (2004)**, Adam Sandler, papel de Drew Barrymore | US$ 196 mi; crítica 45% → Fama ++, Prestígio −1, flag `turma_do_sandler` (ofertas garantidas para sempre) |
| "Um diretor dinamarquês que faz as atrizes chorarem de verdade quer você como operária que está ficando cega. É um musical. Você não é cantora. Ela é." | **Dançando no Escuro (2000)**, Lars von Trier, papel de Björk | Palma de Ouro + Melhor Atriz em Cannes; a atriz original jurou nunca mais atuar → Prestígio +++, Estabilidade −4 |
| "Remake de um remake de um terror japonês. O estúdio chama de 'reimaginação'." | **O Grito (2020)**, papel de Andrea Riseborough | Crítica 20%; US$ 49 mi em US$ 10 mi → "Passou batido" |
| "Biopic de um cantor morto. Dentes falsos. O diretor vai ser demitido no meio e o filme vai ganhar Oscar mesmo assim." | **Bohemian Rhapsody (2018)**, papel de Rami Malek | Crítica 60%, US$ 910 mi, 4 Oscars incl. Melhor Ator → "Ganhou. A crítica odiou o filme. Você não liga." |
| "Um filme de ação cujo astro faz as próprias acrobacias e quebrou o tornozelo pulando entre prédios. Você só precisa de um bigode. O bigode vai causar problemas em OUTRO filme." | **Missão: Impossível — Efeito Fallout (2018)**, papel de Henry Cavill | Fama ++, Dinheiro ++, meme eterno (`bigode_digital`) |
| "Um diretor coreano quer você num trem que nunca para, dividido em classes sociais. Você come barras de proteína." | **Expresso do Amanhã (2013)**, Bong Joon-ho, papel de Chris Evans | Cult: Prestígio ++, Fama +0, flag `cinéfilo` |
| "Um produtor cuja campanha de Oscar é mais agressiva que o filme quer você numa comédia romântica de época sobre um dramaturgo." | **Shakespeare Apaixonado (1998)**, produção Miramax, papel de Gwyneth Paltrow | Oscar de Melhor Atriz e Melhor Filme → Prestígio +++; flag `trabalhou_com_o_produtor` que explode como card em 2017 ("A reportagem sai. Jornalistas perguntam o que você sabia.") |

**Pessoas recorrentes reais**: diretores-autores com múltiplos filmes na janela de anos
(Scorsese, Spielberg, Nolan, Fincher, Tarantino, Coppola, Allen — este com card de contexto 2014+,
Kubrick, Cameron, Bigelow, Campion, Greta Gerwig, Jordan Peele, Villeneuve, Lanthimos, Almodóvar…).
Cada um tem **3 níveis de descrição** (difícil → óbvio) e uma personalidade mecânica
(takes, duração de set, chance de prêmio, efeito em Estabilidade).

**Pessoas fictícias**: agente, empresário, co-star caótica, guru do culto, anfitrião da festa, o amor
da sua vida. O veterano generoso que te apadrinha pode ser real (Paul Newman te chamando de "garoto" é melhor que qualquer invenção).

---

## 3. Criação de personagem

### 3.1 Point buy — 5 atributos, 12 pontos, cada um de 1 a 5

| Atributo | O que faz | Exemplo de "porta" que abre |
|---|---|---|
| **Beleza** | Ofertas de galã/musa, comerciais, capa. Decai aos 35/45/55 (compensável). | "[Beleza 4] O diretor te escala sem teste." |
| **Talento** | Chance de crítica boa, prêmios, sobreviver a roteiro ruim. Cresce com teatro, indie, professores. | "[Talento 4] Improvisa e o diretor mantém." |
| **Contatos** | Quantidade/qualidade de ofertas e **quanto você enxerga antes de escolher** (2.3). Salva em escândalos. | "[Contatos 5] Você sabe quem é o diretor." |
| **Carisma** | Entrevistas, fãs, talk shows. Transforma flop em "divertido". Revela co-stars. | "[Carisma 4] Vira o escândalo em piada no late show." |
| **Juízo** | Resistência a vício, golpe, culto e tweet às 3h. Revela sinais de alerta de produção. | "[Juízo 2] Você não percebeu que era uma pirâmide." |

Opcional: **Sorte** oculta (1–3), sorteada, revelada só no card final.

### 3.2 Origem (define o primeiro ato)

| Origem | Bônus | Ônus | Evento exclusivo |
|---|---|---|---|
| **Nepo baby** | Contatos +2, agente desde o início | Prestígio começa negativo; o sobrenome vira meme | "Jornalista pergunta se você teria chegado aqui sem o sobrenome" |
| **Teatro de Nova York** | Talento +1, Prestígio inicial | Sem dinheiro, chega em LA aos 28 | "Um amigo do off-Broadway virou showrunner" |
| **Ex-criança estrela** | Fama e dinheiro iniciais | Vício começa em 1; os pais gastaram seu dinheiro | "Seu ex-colega de sitcom morreu. A imprensa quer declaração." |
| **Modelo** | Beleza +1 | Ninguém te leva a sério por 10 anos | "Um diretor europeu quer você num filme sem falas" |
| **Influencer** (só estreia ≥ 2012) | Fama instantânea | Zero Prestígio; tweets de 2012 | "Um streaming quer um filme de Natal com você" |
| **Garçom/garçonete em LA** | +1 ponto no point buy | Começa aos 22 lavando prato | "Um cliente deixa um cartão e uma gorjeta de 3 dólares" |
| **Stand-up** | Carisma +1 | Só comédia até provar o contrário | "Uma piada antiga sua ressurge" |
| **Ex-atleta** | Físico, fama de nicho | Talento 1 | "Uma franquia de carros precisa de um músculo novo" |
| **Imigrante com sotaque** | Talento +1 | Só vilão/terrorista/empregada até virar o jogo | "O estúdio quer que você 'suavize' o sotaque" |

### 3.3 Ano de estreia
Ver 2.4. A era muda as ofertas, os eventos de contexto e os finais possíveis (não existe "podcast de
4 horas" em 1985; existe "programa de rádio de madrugada").

---

## 4. Medidores ocultos

| Medidor | Escala | Sobe com | Desce com |
|---|---|---|---|
| **Fama** | 0–100 | Bilheteria, escândalo, talk show | Anos sem lançar; idade (o jogo deixa explícito o duplo padrão de gênero, de propósito) |
| **Prestígio** | −20 a 100 | Crítica, festival, autor, teatro, revisão histórica | Franquia nº 7, filme de Natal, propaganda |
| **Dinheiro** | $ | Cachê, franquia, publi, tequila | Divórcio, impostos, empresário ladrão, cavalos |
| **Heat** | 0–10 | Qualquer notícia; decai 1/ano | Tempo |
| **Estabilidade** | 0–10 | Família, terapia, amigos fora da indústria | Flop, tabloide, diretor tirano, 4 filmes num ano |
| **Vício** | 0–10 | Balada, dor crônica de set de ação | Reabilitação, sobriedade |
| **Reputação na indústria** | −5 a +5 | Ser fácil de trabalhar | Abandonar set, processar estúdio |
| **Rede** | lista | Cada pessoa real com quem trabalhou (reaparece) | Pontes queimadas |
| **Pipeline** | lista | Filmes assinados, ainda não estreados | Cada estreia resolve um |
| **Bagagem** | flags | Tweet antigo, processo, foto, culto, `trabalhou_com_o_produtor` | Nunca desce. Explode ou não. |

Idade avança a cada card. Beleza efetiva −1 aos 35, 45, 55.

---

## 5. Estrutura temporal

~25 cards em 5 atos de 6 anos. Cada ato: 3 projetos (reais), 1–2 pessoas, 1–2 vida, 1 imprensa/prêmios,
mais cards de contexto histórico quando o ano chega.

| Ato | Idade | Tema | Pergunta dramática |
|---|---|---|---|
| **I. A Chegada** | 20–25 | Testes, agente, primeiro papel, aluguel | Você vai entrar? |
| **II. A Ascensão** | 26–31 | Primeiro hit ou flop; franquia vs. indie; primeiro escândalo | Que tipo de estrela você é? |
| **III. O Auge** | 32–37 | Prêmios, poder, produção própria, casamento, vício no pico | O que você faz com o poder? |
| **IV. A Virada** | 38–43 | Ofertas secam; TV, direção, reinvenção | Você aceita envelhecer? |
| **V. O Legado** | 44–50+ | Comeback, prêmio honorário, memórias, revisão histórica | Como vão te lembrar? |

**Morte súbita** (OD, acidente, voo particular) só com **Modo Realista** ligado, como no Volante.

---

## 6. Tipos de card

### 6.1 Projetos (reais — ver seção 2)
Sempre 2 ou 3 ofertas às cegas, com cachê, risco, tempo até estrear e ícones de potencial
(💰 bilheteria, 🏆 prêmio, 🔮 cult, 🧨 escândalo). Os ícones são calculados dos dados reais com ruído
(nunca exatos, senão vira planilha). Ofertas não cinematográficas também são reais quando possível:
"apresentar o programa de humor de sábado à noite", "jurado(a) de um reality de dança", "voz do
guaxinim numa franquia espacial" (Guardiões da Galáxia, 2014, papel de Bradley Cooper).

### 6.2 Pessoas
- **Reais**: diretores, produtores, co-stars, apresentadores. Fatos diretos, rumores etiquetados (2.7). Têm efeitos persistentes
  (Talento +1 permanente depois de sobreviver a Kubrick; `turma_do_sandler`; `trabalhou_com_o_produtor`).
- **Fictícias**: agente do porão (20%), agente-tubarão, empresário que também é sua mãe,
  co-star caótica, guru, o veterano generoso, o amor da sua vida. Instanciadas com variações e nome
  descritivo persistente ("o agente da lavanderia").

### 6.3 Vida pessoal (personagens fictícios de nome caricato, circunstâncias copiadas de casos reais; ver 2.7.1)
- **A balada**: "Depois da festa de Oscar de uma revista, alguém te chama para a continuação nas colinas."
  Ir / não ir / ir e sair cedo [Juízo 3]. Rolagem: conhece produtor (Contatos +), conhece o amor da sua
  vida, conhece cocaína (Vício +2), conhece um guru, foto vaza, nada acontece e você segura um copo 2h.
- **Relacionamentos** (sempre fictícios): civil (Estabilidade ++), músico (casamento em Vegas, 55 horas),
  alguém 25 anos mais novo (tabloide). Divórcio = Dinheiro −50%.
- **Filhos**: Estabilidade +2; ofertas −1 por 3 anos para mulheres, 0 para homens (sátira explícita).
- **Família**: pais pedem dinheiro; irmão quer ser seu empresário; pai escreve livro.
- **Culto**: "Uma amiga te convida para um centro com cursos de 'autoconhecimento'. Metade do elenco
  de uma franquia frequenta." (A igreja pode ser nomeada na revelação: a filiação dos famosos é fato público. O guru que te recruta é fictício.)
- **Dinheiro**: tequila, skincare, cripto (só ≥ 2017), restaurante, time de futebol galês (≥ 2020), vinícola.
- **Saúde**: lesão em set de ação → opioides; cirurgia (Beleza +1 agora, −2 aos 50, Heat +); burnout.

### 6.4 Imprensa & premiações
- **Temporada de prêmios**: se você tem filme com 🏆 no ano, rola indicação com Prestígio + Campanha ($).
  Os concorrentes são os **indicados reais daquele ano** ("você perdeu para Meryl Streep. De novo.").
- **O discurso**: agradecer / político / esquecer o cônjuge / chorar demais (meme: Fama +, Prestígio −).
- **A entrevista**: sobre co-star problemático, sobre o sobrenome. "[Carisma 4] fazer piada".
- **Tabloide**: templates com slots (ver 11).
- **Cards de contexto real**: greve de 2007 ("sua série para"), #MeToo 2017 ("o que você sabia?"),
  pandemia 2020 ("seu filme vai direto para streaming"), IA 2023 ("o estúdio quer escanear seu rosto").

### 6.5 Cards de destino (raros, 1 por run)
Vazamento, acusação (o jogo decide pelo seu histórico de Bagagem), herança, acidente de avião
(Realista), convite para dirigir, gravidez, diagnóstico, "um diretor coreano te quer".

---

## 7. Sistema de resolução

- **2 opções principais (swipe) + 1 opção de atributo** que só aparece com requisito
  ("[Contatos 4] Fazer os dois. Seu agente vai fazer caber.").
- **Probabilidades mostradas** em projetos (com ruído); **ocultas** em vida pessoal.
- **Tipos de efeito**: imediato, diferido ("quando estrear"), permanente, multiplicador, flag, troca de papel
  (galã → "ator de caráter" → "o pai da protagonista").
- **Decaimento** por rodada: Heat −1; Fama −3 se não lançou; Vício +1 se Vício ≥ 5 e Estabilidade ≤ 3.
- **Cálculo de estreia**: seção 2.6.

---

## 8. Caminhos emergentes

Detectados pelo estado, não escolhidos. Cada um precisa de uma "espinha" de 4–6 eventos.

1. **A Lenda** — Talento alto, recusou franquia 2x, trabalhou com 3 autores, sobreviveu a um flop.
2. **O Rei da Franquia** — contrato de 6 filmes; "fãs te odeiam pelo filme 4"; "rejuvenescer digitalmente".
3. **A Espiral** — Vício ≥ 7: atraso, demissão, tabloide, reabilitação, recaída, intervenção.
4. **O Culto** — níveis, recrutar co-star, cônjuge quer sair, documentário.
5. **O Cancelado** — vídeo de desculpas com fundo cinza / "não vou me desculpar" / sumir 3 anos.
6. **A Reinvenção** — Ato IV sem ofertas: TV de prestígio, dirigir, Broadway, Natal, política.
7. **O Esquecido** — Fama 0 sem escândalo. "Numa fila de farmácia: 'você não era…?' Você diz que não."
8. **A indústria adulta** — Dinheiro < 0, Beleza ≥ 3, Juízo baixo. A piada é Hollywood, não a pessoa.
9. **O Civil** — largou tudo. "Hoje dá aula em Ohio e é feliz. Sério." Achievement *Saiu enquanto podia*.

---

## 9. Finais (40+)

| Categoria | Finais |
|---|---|
| **Glória** | EGOT · Oscar honorário · "O(a) maior da geração" · Estátua de cera (que não parece com você) · Estrela na calçada ao lado de um cachorro famoso |
| **Dinheiro** | Bilionário(a) da tequila · Rei/Rainha da franquia · Produtor(a) poderoso(a) · Dono(a) de time galês |
| **Reinvenção** | Diretor(a) premiado(a) · Governador(a) · Broadway · A voz do guaxinim · Rei/Rainha do Natal (47 filmes) · Showrunner · Jurado(a) de reality · Podcast de 4h |
| **Queda** | OD (Realista) · Pelado(a) na Sunset · Preso(a) (fraude fiscal / "o incidente do iate") · Processo bilionário com ex · Esquecido(a) · "Ex-estrela de sitcom" (título do documentário) · Infomercial de travesseiro · Curso de atuação online · Cameo por $40 |
| **Culto** | Porta-voz em cruzeiro · Fugiu e escreveu livro · Nível máximo |
| **Humano** | Professor(a) em Ohio · Fazenda de alpacas, sóbrio(a) · Avô/avó que "fez uns filmes" · Morreu de velhice numa casa cheia de gente |
| **Meme** | O tapa · O discurso de 11 minutos · A foto do tapete vermelho que virou reação · "Aquele ator do GIF" |
| **Secretos** | Comeback aos 70 · Nunca lançou nada e ficou famoso · Morreu no Ato I e virou lenda · Substituído(a) por IA e processou · **Carreira idêntica a uma real** ("você fez exatamente a filmografia de Nicolas Cage. Parabéns?") |

Seleção: cada final declara um vetor-alvo + flags; menor distância vence; raros têm peso extra quando elegíveis.

---

## 10. O card final

Formatos (MVP: o primeiro):
1. **Pôster de biopic** — "*ESTRELA CADENTE: a história de [nome]*", tagline do final, críticas falsas.
2. **Página de obituário/Wikipedia** — "foi um(a) ator(atriz) conhecido(a) por…", filmografia real alternativa.
3. **Grade de emojis estilo Wordle** — 🟩 hit 🟥 flop 🟪 prêmio 🟨 escândalo ⬛ reabilitação 💀.

Obrigatório no card:
- Nome do final + manchete estilo *Variety*.
- **Filmografia alternativa**: `1997 · Titanic · no papel de Kate Winslet · indicada` — texto, sem pôster.
- **Os 3 "recusei X para fazer Y"** mais dolorosos da run (o jogo escolhe pela diferença de resultado).
- Os 5 atributos iniciais ("claro que deu errado, você botou 1 em Juízo").
- Conquistas; raridade do final; seed para "jogue a mesma vida".
- Rodapé: "Dados: TMDB. Fan-made. Não afiliado."

---

## 11. Geradores

- **Nome artístico**: primeiros nomes por década de nascimento + sobrenomes "de Hollywood"; na era 50, "o estúdio troca seu nome".
- **Descrições às cegas**: escritas à mão por filme/pessoa, em 3 níveis. Guia: 2 frases; 1 fato verificável
  (Wikipedia, não trivia de IMDb); 1 piada; nunca o título; nunca inventar. Rascunho com LLM, revisão
  humana obrigatória, checagem de fonte.
- **Manchetes de tabloide**: `"[NOME] VISTO(A) SAINDO DE [LUGAR] COM [PESSOA FICTÍCIA]"`,
  `"O QUE ACONTECEU COM O ROSTO DE [NOME]?"`, `"FONTES: [NOME] É 'IMPOSSÍVEL' NO SET"`.
- **Trívia de revelação**: base de "quem recusou este papel" (Will Smith/Neo, Matt Damon/Avatar,
  Sean Connery/Gandalf, Michelle Pfeiffer/Clarice, John Travolta/Forrest Gump, Tom Selleck/Indiana
  Jones, Emily Blunt/Viúva Negra, Molly Ringwald/Uma Linda Mulher). ~200 entradas curadas.

---

## 12. Viralidade e replay

- **Desafio diário**: mesma seed (mesmo ano de estreia, atributos pré-definidos, mesmas ofertas).
  "Hoje: nepo baby de 1989 com Juízo 1."
- **Modo Destino**: arquétipo pronto ("Ex-criança estrela, 1994, $4M, Vício 3. Boa sorte.").
- **Modo Cenário** (v2): momento real, pessoa real ("É 2022. Alguém fez piada com sua
  esposa no palco. Você tem 4 segundos.").
- **Seed compartilhável**; **estatísticas globais** ("73% de quem aceitou Thor nunca foi indicado");
  **conquistas** (*Sem anel*, *Nômade* (7 agentes), *Disse não ao centro*, *A voz*, *Saiu enquanto podia*,
  *Zero Juízo* (Juízo 1 e ganhou Oscar), *Brendanaissance*, *Nepo e daí*, *Filmografia de Cage*).
- **"Carreira de exemplo"** na home (roda uma vida em 10 s).
- **Camada trívia**: cada revelação tem botão "sabia que…" → compartilhável sozinho.

---

## 13. Tom, escrita e limites

- **Voz**: narrador de documentário cansado + manchete de *Variety* + amigo fofoqueiro.
- **Fato é fato, rumor é rumor (🗞️).** Ver 2.7. A piada é sempre sobre Hollywood e sobre o ego, nunca sobre a vítima.
- **OD e suicídio**: só no Modo Realista; texto seco; linha de apoio discreta no card (CVV 188).
- **Gênero e idade**: duplo padrão explícito porque é sátira; escolha de gênero muda as ofertas (dados
  reais já fazem isso sozinhos: há menos protagonistas mulheres de 45+ no TMDB, e o jogo mostra).
- **Idiomas**: PT-BR primeiro; EN logo depois (o material é americano, o alcance é global); ES (público do Copero).

---

## 14. Lista de eventos para começar (amostra)

**Ato I** — agente do porão (20%) · comercial de sanduíche · figuração num filme de prestígio real do ano
· o teste com o diretor que pede "mais pequeno" · colega de quarto pega o papel · a balada · "sorria mais"
· primeiro papel em série adolescente real do ano (6 anos preso) · professor de teatro de 80 anos · convite
para o "centro" · pirâmide de suplementos · pai/mãe se muda para LA.

**Ato II** — a capa ou o sofá (duas ofertas reais) · co-star caótica (fictícia) · o diretor dos 127 takes
(real) · o produtor do "café" (real; o convite e o que foi documentado depois são fatos, o resto é 🗞️) · primeiro flop
· tabloide inventa romance com músico (fictício) · a franquia renova · o diretor dinamarquês · Vegas 55 h
· agente some com $2M · tweet antigo · apresentar o programa de sábado · lesão → opioides · o indie que
você fez por nada ganha em festival francês · o diretor coreano · colega de sitcom morre.

**Ato III** — temporada de prêmios contra indicados reais · o discurso · a noite do tapa (card de
contexto 2022) · o produtor cai (2017) · produzir o próprio filme · filhos · divórcio público · tequila
· culto nível 3 · intervenção · reabilitação em Malibu · "rejuvenescer digitalmente" · dirigir
· o veterano morre · jurado(a) de reality · processo de ex-assistente · time galês.

**Ato IV** — 18 meses sem oferta · a série de prestígio de domingo · filme de Natal nº 1 · "papel de
mãe/pai do protagonista" · cirurgia · Broadway · o jovem diretor da internet te quer "ironicamente"
· governador · memórias · documentário sobre o culto.

**Ato V** — o comeback (um diretor de prestígio real do ano) · prêmio honorário · cameo por $40
· revisão histórica (o filme que te deu Razzie virou culto) · neto(a) quer ser ator · fila da farmácia.

---

## 15. Dados e arquitetura

### 15.1 Fontes
| Dado | Fonte | Observação |
|---|---|---|
| Filmes, elenco (ordem), equipe, orçamento, bilheteria, gêneros, imagens | **TMDB API** | Grátis para uso não comercial com atribuição (logo + "This product uses the TMDB API but is not endorsed or certified by TMDB"). Comercial exige licença. |
| Rotten Tomatoes, Metacritic, IMDb rating | **OMDb API** | Free tier ~1.000 req/dia. Baixar e congelar em JSON; não consultar em runtime. |
| Oscars (indicados e vencedores por ano) | Dataset público do Academy Awards (Kaggle/GitHub) ou **Wikidata** | Também Globo de Ouro, Cannes, Razzies via Wikidata/Wikipedia. |
| "Quem recusou o papel", takes, duração de set, produções problemáticas | Curadoria manual (Wikipedia como fonte mínima) | É o conteúdo editorial. ~600 filmes × 3 descrições. |
| Inflação | CPI anual | Para mostrar cachê "na época / hoje". |

**Pipeline offline**: script Python baixa e normaliza tudo para um `films.json` (~600 filmes curados,
1975–2025) + `people.json` (~150 diretores, ~100 co-stars) + `awards.json` + `trivia.json`.
O jogo roda 100% estático, sem chamadas de API em runtime.

### 15.2 Stack
- SPA estático (Vite + React ou Svelte), Cloudflare Pages (como o Volante). Worker + KV depois para
  estatísticas globais e desafio diário.
- RNG com seed (`seedrandom`). Estado: máquina `criação → ato → card → revelação → resolução` + reducer; `localStorage`.
- Card: `html-to-image` → PNG; Web Share API; fallback de copiar texto.

### 15.3 Esquema de dados (exemplo)
```yaml
# films.json (um item)
tmdb_id: 37799
title: { original: "The Social Network", pt: "A Rede Social" }
year: 2010
director: { tmdb_id: 7467, name: "David Fincher" }
roles:
  - { actor: "Jesse Eisenberg", order: 0, gender: m, demand: 4, oscar: nominated }
  - { actor: "Andrew Garfield", order: 1, gender: m, demand: 3, oscar: none }
  - { actor: "Rooney Mara",     order: 4, gender: f, demand: 2, oscar: none }
budget: 40000000
revenue: 224900000
rt: 96
metacritic: 95
film_oscars: { nominations: 8, wins: 3, best_picture: nominated }
shoot_days: 70
blind:
  hard:   { pt: "Um diretor que não faz menos de 50 takes quer você num filme sobre um site. Duas horas de gente digitando e falando rápido." }
  medium: { pt: "O diretor de um filme sobre um serial killer que nunca é pego, e de outro em que o protagonista envelhece ao contrário, quer você num filme sobre a criação de um site. A cena de abertura vai ter 99 takes." }
  easy:   { pt: "O Fincher quer você no filme do Facebook. Roteiro do cara que escreve andando." }
flags: [ roteirista_estrela, filme_de_processo ]
trivia:
  - "A cena de abertura foi filmada 99 vezes."
  - "O roteiro de Aaron Sorkin tem 162 páginas; o filme tem 2 horas."
revision: null   # ou { year: 2022, text: "...", prestige_delta: +3 }
```

```yaml
# evento fictício (personagens inventados)
id: balada_nas_colinas
ato: [1, 2]
peso: 8
requer: { heat: ">=2" }
texto: { pt: "Depois da festa de Oscar de uma revista, Chip Marmont te chama para a continuação no bangalô 3." }
inspirado_em:   # interno, não renderizado
  - { quem: "John Belushi", ano: 1982, o_que: "Overdose no bangalô 3 do Chateau Marmont" }
opcoes:
  - rotulo: { pt: "Ir" }
    rolagem:
      - { p: 0.25, efeito: { contatos_evento: +1 }, texto: "Você conhece um produtor que lembra de você." }
      - { p: 0.20, efeito: { flag: amor_da_vida }, texto: "Você conhece alguém que não é da indústria." }
      - { p: 0.20, efeito: { vicio: +2 },           texto: "Você conhece outra coisa." }
      - { p: 0.10, efeito: { flag: culto_1 },        texto: "Alguém te fala de um 'centro'." }
      - { p: 0.10, efeito: { heat: +2, flag: foto },  texto: "Uma foto vaza." }
      - { p: 0.15, efeito: {},                       texto: "Você segura um copo por 2 horas." }
  - rotulo: { pt: "Não ir" }
    efeito: { estabilidade: +1 }
  - rotulo: { pt: "Ir e sair cedo" }
    requer: { juizo: 3 }
    efeito: { contatos_evento: +1 }
```

### 15.4 MVP (escopo)
- 1 janela de estreia (1990–1995), 5 atributos, 3 origens.
- **200 filmes curados** (1991–2025) com 3 descrições cada; 40 diretores; 100 eventos fictícios; 15 finais.
- Card pôster + share. Sem backend.
- Depois: 600 filmes, 1975–2025, desafio diário, estatísticas globais, revisão histórica, EN/ES, modo cenário.

---

## 16. Decisões em aberto

As perguntas abertas (interação, ruído nas probabilidades, pôsteres, nome, janela de anos do MVP,
idiomas, stack, duração da run, features da v1, divisão de trabalho) estão num questionário
editável fora deste arquivo. As respostas serão consolidadas aqui numa seção **17. Decisões tomadas**.

Decidido até agora:
- **Pessoas reais**: fato direto, rumor etiquetado (2.7). Sem medo de processo.
- **Vício, sexo e crime**: personagens fictícios de nome caricato, circunstâncias que remetem a casos reais, **sem nomear** o caso (2.7.1).
- **Atributos revelam informação** e atravessam áreas (Contatos → nome do diretor; Juízo → sinais de alerta; Carisma → rumores; Talento → roteiro).
- **Filmes e pessoas reais**, revelados depois da escolha, com "o que você recusou" no card.
