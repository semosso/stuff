# ESTRELA CADENTE — simulador de carreira em Hollywood
### Documento de brainstorm (sistemas, conteúdo, caminhos e finais)

> Jogo web curto (3–6 min por run), sem cadastro, sem instalação. Você cria um ator ou atriz,
> distribui pontos entre atributos, e toma ~25 decisões ao longo de uma carreira de 40 anos.
> No fim, recebe um **card compartilhável** dizendo como sua carreira terminou:
> da lenda EGOT ao "pelado na Sunset Boulevard gritando com um hidrante".

---

## 0. O que aprender com as referências

| Jogo | O que fazer igual | O que fazer diferente |
|---|---|---|
| **82-0 / 7-0** | Loop de 2 minutos. Um "sorteio" te empurra para decisões imperfeitas. Resultado com nota/categoria (loteria → dinastia). Card final pensado para print. | Eles não têm narrativa; aqui a narrativa É o produto. |
| **Copero (simulador de carrera)** | Estrutura por idade (16→38). Swipe esquerda/direita estilo *Reigns*. Eventos com resultado positivo/neutro/negativo e **probabilidade mostrada**. Efeitos imediatos, diferidos e permanentes. Conquistas com nomes engraçados ("one_club_legend", "ringless", "nomad"). Evento absurdo que vira conversa (a tatuagem de águia gigante). | Em Hollywood o "troféu" é mais plural: prêmio, bilheteria, culto, meme. E o fracasso é mais interessante que no futebol. |
| **Volante de Ouro** | Escolha de era muda o elenco de rivais e as regras. "Realismo histórico" como toggle (acidente pode acabar a carreira). Modo cenário (assuma uma pessoa real num momento). | Volante é longo (temporadas inteiras). Aqui a run tem que caber numa fila de banco. |

**Regras de ouro do formato viral**
1. Run curta, final forte, card bonito. O jogo "de verdade" acontece no grupo de WhatsApp comparando finais.
2. Zero nomes reais. Tudo por descrição, e o prazer do jogador é **reconhecer** ("é o Nolan!", "é o Weinstein!!"). Isso também é a blindagem jurídica.
3. Toda escolha tem um lado óbvio e um lado tentador. Se não houver tentação, não é decisão.
4. Aleatoriedade visível. Mostrar "72% de chance" e perder é mais divertido (e mais compartilhável) do que perder sem saber por quê.
5. Finais ruins têm que ser **tão desejáveis quanto os bons**. Gente vai jogar de propósito para terminar na indústria pornô. Isso é feature.

---

## 1. Criação de personagem

### 1.1 Point buy — 5 atributos, 12 pontos, cada um de 1 a 5

| Atributo | O que faz | Exemplo de "porta" que abre |
|---|---|---|
| **Beleza** | Testes de elenco para galã/musa, comerciais, capa de revista. Decai com a idade a menos que você "invista" (cirurgia, personal, pacto). | "[Beleza 4] O diretor te escala sem teste." |
| **Talento** | Chance de crítica boa, prêmios, sobreviver a um roteiro ruim. Cresce com trabalho em teatro, indie e professores. | "[Talento 4] Improvisa a cena e o diretor mantém." |
| **Contatos** | Quantidade e qualidade das ofertas. Salva você em escândalos. Nepo babies começam alto. | "[Contatos 3] Ligar para o padrinho produtor." |
| **Carisma** | Entrevistas, talk shows, fãs, redes. Transforma fama em dinheiro e flop em "divertido". | "[Carisma 4] Vira o escândalo em piada no late show." |
| **Juízo** | Resistência a vício, golpe, culto e tweet às 3h da manhã. O atributo que todo mundo zera e se arrepende. | "[Juízo 2] Você não percebeu que era uma pirâmide." |

Opcional: um sexto atributo oculto **Sorte** (1–3), sorteado, que o jogador só descobre no card final ("Sorte: 1 — você nunca teve chance").

### 1.2 Origem (escolha 1 — define o primeiro ato)

| Origem | Bônus | Ônus | Eventos exclusivos |
|---|---|---|---|
| **Nepo baby** | Contatos +2, começa com agente | Crítica desconfia (Prestígio começa negativo), "sobrenome" vira meme | "Jornalista pergunta se você teria chegado aqui sem o sobrenome" |
| **Teatro de Nova York** | Talento +1, Prestígio inicial | Sem dinheiro, 28 anos ao chegar em LA | "Um amigo do off-Broadway virou showrunner" |
| **Ex-criança estrela** | Fama inicial alta, dinheiro | Vício começa em 1, pais gastaram seu dinheiro | "Seu ex-colega de sitcom morreu. A imprensa quer declaração." |
| **Modelo** | Beleza +1, contatos de moda | Ninguém te leva a sério por 10 anos | "Um diretor europeu quer você num filme sem falas" |
| **Influencer** | Fama instantânea, dinheiro de publi | Zero Prestígio, cancelamentos retroativos (tweets de 2012) | "Uma plataforma de streaming quer um filme de Natal com você" |
| **Garçom/garçonete em LA** | O clássico. Nada de bônus, mas +1 ponto extra no point buy | Começa a carreira aos 22 lavando prato | "Um cliente deixa um cartão de visita e uma gorjeta de 3 dólares" |
| **Comediante de stand-up** | Carisma +1 | Pigeonhole: só ofertas de comédia até provar o contrário | "Uma piada antiga sua ressurge" |
| **Ex-atleta / lutador** | Beleza (físico), fama de nicho | Talento começa em 1 | "Uma franquia de ação com carros precisa de um músculo novo" |
| **Imigrante com sotaque** | Talento +1 (teatro no país de origem) | Só papéis de vilão/terrorista/empregada até virar o jogo | "O estúdio quer que você 'suavize' o sotaque" |

### 1.3 Era (toggle avançado, v2)
Começar nos anos 50 (sistema de estúdio, contratos de 7 anos, casamentos arranjados pelo estúdio), 70 (Nova Hollywood, cocaína), 90 (indie boom, Miramax), 2010 (franquias, streaming, #MeToo), 2020 (TikTok, greve, IA). Cada era muda os eventos, os arquétipos e os finais possíveis. **Para o MVP, só a era 2000–2040.**

---

## 2. Recursos ocultos (a "máquina" por trás)

O jogador vê só os 5 atributos. Por baixo, o jogo acompanha ~10 medidores que decidem o final:

| Medidor | Escala | Sobe com | Desce com |
|---|---|---|---|
| **Fama** | 0–100 | Blockbuster, escândalo, talk show, relacionamento famoso | Anos sem lançar, idade (para mulheres o jogo deixa isso explícito: é sátira) |
| **Prestígio** | −20 a 100 | Crítica, festival, indie, teatro, diretor-autor | Franquia nº 7, filme de Natal, propaganda de cassino online |
| **Dinheiro** | $ | Cachê, franquia, publi, marca de tequila | Divórcio, impostos, empresário ladrão, mansão, cavalos |
| **Heat** (momento) | 0–10 | Qualquer notícia. Decai sozinho a cada ano | Tempo. É o recurso mais volátil. |
| **Estabilidade** (saúde mental) | 0–10 | Família, terapia, amigos fora da indústria, hobby | Flop, tabloide, solidão, 4 filmes num ano |
| **Vício** | 0–10 | Balada, co-star "divertido", dor crônica de filme de ação | Reabilitação, sobriedade, religião |
| **Reputação na indústria** | −5 a +5 | Ser fácil de trabalhar, não atrasar | Gritar com assistente, abandonar set, processar estúdio |
| **Rede** | lista | Cada pessoa com quem você trabalhou vira um "contato" com humor | Pontes queimadas |
| **Pipeline** | lista | Projetos assinados que ainda não estrearam | Cada estreia resolve um |
| **Bagagem** | flags | Tweet antigo, processo, ex vingativo, foto comprometedora, culto | Nunca desce. Só explode ou não. |

**Idade** avança a cada rodada. Beleza perde 1 ponto efetivo aos 35, 45, 55 (compensável).

---

## 3. Estrutura temporal (a run)

~25 cards, divididos em 5 atos. Cada ato tem 1 card de "projeto", 1–2 de "pessoa", 1–2 de "vida", 1 de "imprensa/temporada de prêmios" e cards aleatórios da fila de eventos.

| Ato | Idade | Tema | Pergunta dramática |
|---|---|---|---|
| **I. A Chegada** | 20–25 | Testes, agente, primeiro papel, aluguel | Você vai entrar? |
| **II. A Ascensão** | 26–32 | Primeiro hit ou primeiro flop, franquia vs. indie, primeiro escândalo | Que tipo de estrela você é? |
| **III. O Auge** | 33–42 | Prêmios, poder, produção própria, casamento, filhos, vício no pico | O que você faz com o poder? |
| **IV. A Virada** | 43–55 | Ofertas secam, reinvenção, TV, diretor, "e aí, lembra de mim?" | Você aceita envelhecer? |
| **V. O Legado** | 56+ | Comeback tardio, prêmio honorário, memórias, saída de cena | Como vão te lembrar? |

**Morte súbita**: eventos de OD, acidente de set, voo particular e "pelado na rua" podem encerrar a run em qualquer ato. Como no Volante de Ouro, há um toggle **"Modo Realista"** que liga as mortes; desligado, o pior que acontece é reabilitação.

**Pipeline (a mecânica mais importante do jogo)**: um projeto escolhido no Ato II estreia no Ato III. O resultado (hit / flop / cult / "sumiu do streaming") é rolado na estreia, com base no que você escolheu + Talento + diretor + sorte. Isso cria o drama de "eu recusei o filme de super-herói para fazer o drama sobre um faroleiro... e o faroleiro ganhou 4 Oscars" ou "e o faroleiro foi direto pro catálogo de avião".

---

## 4. Tipos de card

### 4.1 Projetos (o coração)
Sempre 2 ou 3 ofertas, descritas sem nome e sem título. Cada uma tem **cachê**, **risco**, **tempo até estrear** e **ícones de potencial** (💰 bilheteria, 🏆 prêmio, 🔮 cult, 🧨 escândalo).

Exemplos de descrição (reconhecíveis, nunca nomeados):
- "Um diretor britânico obcecado por tempo não-linear quer você num filme de 3 horas que ninguém vai entender e todo mundo vai dizer que entendeu. Você vai filmar pendurado de cabeça para baixo. De verdade."
- "O quinto filme de uma franquia sobre um grupo de heróis com capa. Seu personagem: 'Cientista nº 2'. Mas é um contrato de 6 filmes."
- "Um estúdio independente com logo em serifa quer você num terror sobre luto, filmado numa casa em Vermont. Sem dinheiro, mas o pôster vai ser lindo."
- "Um diretor italiano-americano de 80 anos vai fazer 'o último filme dele' (de novo). Papel pequeno. Set cheio de gente que você quer conhecer."
- "Um filme de Natal para um canal a cabo. Você vai se apaixonar por um dono de fazenda de árvores de Natal. Grava em 11 dias. Paga o aluguel de 2 anos."
- "Uma comédia de um ex-humorista de TV que leva os amigos para filmar no Havaí. Ninguém sabe se é filme ou férias."
- "Um diretor dinamarquês que faz as atrizes chorarem de verdade. Festival garantido. Terapia garantida."
- "Remake de um filme japonês que já teve remake. O estúdio chama de 'reimaginação'."
- "Um biopic de um músico morto. Prótese de nariz, 30 kg a mais, 14 meses de preparação. É isca de Oscar e todo mundo sabe."
- "Um filme de ação que exige que você faça as próprias acrobacias porque o astro do filme anterior fez. Ele tem uma igreja. Você não."
- "Um reality de competição de dança como jurado(a)."
- "Papel de voz num filme de animação sobre um guaxinim. Três dias de gravação. Royalties eternos."
- "Um filme de IA onde você vende sua imagem e não precisa aparecer no set." *(evento 2030+)*

### 4.2 Pessoas (com quem trabalhar / conviver)
Arquétipos com personalidade e efeitos persistentes. Trabalhar com alguém adiciona a pessoa à sua **Rede**, e ela reaparece.

| Arquétipo (descrição no jogo) | Efeito ao trabalhar | Risco oculto |
|---|---|---|
| **O gênio tirano** — "Faz 97 takes da mesma cena. Chama isso de respeito pelo cinema." | Prestígio +, Talento +1 permanente, Estabilidade −2 | 15% de você sair do set e queimar ponte |
| **O produtor dos abraços longos** — "Marca reuniões em suítes de hotel. Todo mundo sabe. Ninguém fala." | Ofertas melhoram muito | Flag Bagagem. Quando o escândalo dele estourar (Ato III), você é perguntado(a) sobre o que sabia |
| **O astro da igreja** — "Sorri o tempo todo. Corre em todas as cenas. Te convida para um 'centro' em Hollywood Blvd." | Franquia garantida, Dinheiro +++ | Caminho do culto (ver 6.4) |
| **A co-star caótica** — "Linda, talentosa, chegou 4 horas atrasada e trouxe um lêmure." | Heat ++, Fama + | Vício +2, 20% de romance |
| **O diretor-autor sombrio** — "Cada filme dele é sobre uma mulher sofrendo. A crítica ama. As atrizes, menos." | Prestígio ++, chance de prêmio | Estabilidade −3 |
| **O agente-tubarão** — "Fecha contratos antes de você ler. 'Confia.'" | Dinheiro ++, ofertas ++ | 10%/ano de ele roubar tudo |
| **O ex-colega de teatro que virou showrunner** | Oferta de série garantida | Ciúme: se você ficar mais famoso, ele te mata na 2ª temporada |
| **O humorista com o grupo de amigos** | Trabalho garantido pelo resto da vida | Prestígio congela |
| **O veterano generoso** — "Ganhou tudo. Te chama de 'garoto(a)'. Te apresenta a todo mundo." | Contatos +1 permanente | Nenhum. É o único. Morre no Ato IV e você fala no funeral (evento) |
| **O diretor que só filma em película e grita 'filme é morrer'** | Cult garantido | Bilheteria zero |
| **O jovem diretor da internet** | Heat ++ | 50% de ser genial, 50% de o filme ser um TikTok de 2h |
| **O empresário que também cuida dos seus pais** | Dinheiro organizado (+) | Ele é a mãe. Ela gasta tudo. (origem: ex-criança estrela) |

### 4.3 Vida pessoal
- **A balada**: "Um astro de uma franquia de carros te chama para uma festa nas colinas." Opções: ir / não ir / ir e sair cedo [Juízo 3]. Resultados na festa (roll): conhece produtor (Contatos +), conhece o amor da sua vida (flag Relacionamento), conhece cocaína (Vício +2), conhece um guru (Culto), foto vaza (Heat +, Bagagem), nada acontece e você fica 2h segurando um copo.
- **Relacionamentos**: com co-star (Heat ++, Estabilidade variável), com civil (Estabilidade ++, Fama 0), com alguém 25 anos mais novo (tabloide), com músico (casamento em Las Vegas, 55 horas). Casamento → divórcio é um evento com cálculo de Dinheiro −50%.
- **Filhos**: Estabilidade +2, ofertas −1 por 3 anos (mulheres), 0 (homens — sátira explícita). Desbloqueia o final "Mãe/pai que largou tudo" e o evento "seu filho(a) quer ser ator".
- **Família de origem**: pais pedem dinheiro; irmão quer ser seu empresário; pai escreve livro.
- **Religião/culto**: "Uma amiga te convida para um centro com cursos de 'autoconhecimento'. Metade do elenco de uma franquia frequenta."
- **Política**: discurso em premiação (Prestígio ou cancelamento), campanha, candidatura a governador (final).
- **Dinheiro**: marca de tequila, skincare, cripto, restaurante, time de futebol galês, vinícola.
- **Saúde**: lesão em set de ação (dor crônica → opioides), cirurgia plástica (Beleza +1 agora, −2 aos 50 e Heat + por "o que ela fez no rosto"), burnout.

### 4.4 Imprensa & premiações
- **Temporada de prêmios** (1 card por ato a partir do II): se você tem filme com 🏆 no ano, rola indicação com base em Prestígio + Campanha ($). Pode "fazer campanha" (Dinheiro −, chance +) ou "ficar acima disso" (Prestígio +1, chance −).
- **O discurso**: agradecer a família / fazer discurso político / esquecer o cônjuge / chorar demais (meme eterno: Fama +, Prestígio −).
- **A entrevista**: pergunta sobre co-star problemático, sobre o sobrenome, sobre o passado. Opções honestas, evasivas, ou "[Carisma 4] fazer piada".
- **O tabloide**: romance inventado, briga em restaurante, foto de biquíni "o corpo de X aos 50".
- **A noite do tapa**: evento do Ato III: alguém faz piada com seu cônjuge na premiação. Reagir (Fama ++, Prestígio −−, banido 10 anos) / rir (nada) / chorar no banheiro [Estabilidade].

### 4.5 Cards de "destino" (raros, 1 por run)
Eventos que alteram a direção toda: vazamento de fotos, acusação (verdadeira ou falsa — o jogo decide pelo seu histórico de Bagagem), herança, acidente de avião (sobreviveu? toggle Realista), convite para dirigir, gravidez, diagnóstico, "um diretor coreano quer você num filme sobre classes sociais".

---

## 5. Sistema de resolução

### 5.1 Formato do card
```
[Ato II • 29 anos • Heat ▮▮▮▯▯]

"Uma diretora que você admira quer você num filme de orçamento
de um sofá. Ao mesmo tempo, seu agente ligou: a franquia dos
heróis com capa quer um 'Cientista nº 2'. Contrato de 6 filmes."

◀ O sofá                            A capa ▶
   💵 nada  🏆 40%  🔮 25%            💵 $$$$  🏆 2%  🧨 15%
   estreia em 2 anos                  estreia em 1 ano
                                      (preso por 9 anos)

   [Contatos 4] ▲ Fazer os dois. Seu agente vai fazer caber.
```
- 2 opções principais (swipe) + 1 opção "de atributo" que só aparece se você tem o requisito. Isso faz o point buy importar visivelmente.
- Probabilidades **mostradas** para projetos; **ocultas** para vida pessoal (ninguém sabe a chance de o relacionamento dar certo).

### 5.2 Tipos de efeito (roubado do Copero, estendido)
- **Imediato**: Fama +10, Dinheiro +$2M.
- **Diferido**: "quando este filme estrear".
- **Permanente**: Talento +1, "Beleza não decai aos 45".
- **Multiplicador**: "chance de indicação ×2 nos próximos 3 anos".
- **Flag**: Bagagem, Rede, Relacionamento, Culto, Sobriedade.
- **Troca de papel**: de galã para "ator de caráter"; de protagonista para "o pai da protagonista"; de atriz para diretora.

### 5.3 Cálculo de estreia
```
qualidade = talento*0.3 + diretor.qualidade*0.4 + roteiro(roll)*0.3
bilheteria = heat*0.3 + franquia*0.4 + beleza*0.1 + marketing(roll)*0.2
→ HIT (ambas altas) | ISCA DE OSCAR (qualidade) | PIPOCA (bilheteria)
  | CULT (qualidade alta, bilheteria zero, roll 20%) | FLOP | DIRETO PRO CATÁLOGO
```
Com uma **variância alta de propósito**: 10% de todo projeto virar o oposto do esperado. É o que gera as histórias.

### 5.4 Decaimento
A cada rodada: Heat −1; Fama −3 se não lançou nada; Vício +1 se Vício ≥ 5 e Estabilidade ≤ 3 (a espiral); Beleza efetiva por idade.

---

## 6. Caminhos (os arcos que emergem)

Não são escolhidos; o jogo detecta pelo estado. Mas o conteúdo deve garantir que cada um tenha uma "espinha" de 4–6 eventos.

### 6.1 A Lenda
Talento alto, recusou franquia 2x, trabalhou com 3 autores, sobreviveu a 1 flop. Final: **EGOT / Prêmio honorário / Estátua no AFI**.

### 6.2 O Rei da Franquia
Aceitou contrato de 6 filmes. Dinheiro infinito, Prestígio zero. Eventos: "fãs te odeiam pelo filme 4", "o estúdio quer te rejuvenescer digitalmente", "você tenta fazer indie e a crítica diz 'tentou'". Finais: **Bilionário aposentado em Malibu**, **Comeback tardio (ganha o Oscar aos 55 num filme sobre um lutador decadente)**, **Preso ao contrato até morrer**.

### 6.3 A Espiral
Vício ≥ 7. Eventos: atraso em set, demissão, foto do tabloide, reabilitação ("sai 30 dias depois dizendo que mudou"), recaída, amigo morre, intervenção de um ator de comédia que virou sério. Finais: **OD** (Modo Realista), **Sóbrio e dono de uma fazenda de alpacas**, **O da rua** (pelado, Sunset Blvd, gritando que o filme de 2009 era sobre você), **Reality de celebridades em reabilitação**.

### 6.4 O Culto
Aceitou o convite do "centro". Eventos: subir de nível, recrutar co-star, cônjuge quer sair, documentário expõe. Finais: **Porta-voz da igreja em cruzeiro**, **Fugiu e escreveu livro (best-seller + processo)**, **Nível máximo — ninguém mais te vê**.

### 6.5 O Cancelado
Bagagem explodiu. Opções: pedido de desculpas em vídeo com fundo cinza, "não vou me desculpar", sumir 3 anos. Finais: **Especial de comédia 'não posso dizer mais nada'**, **Podcast de 4 horas**, **Comeback com diretor de prestígio ("a redenção")**, **Esquecido**.

### 6.6 A Reinvenção
Ato IV sem ofertas. Opções: TV ("a série de prestígio de domingo"), dirigir, produzir, Broadway, dublagem, filme de Natal, política, negócios. Finais: **Diretor(a) premiado(a)**, **Dona do estúdio**, **Governador(a)**, **Rei(rainha) do filme de Natal (47 filmes)**, **A voz do guaxinim (3 gerações de crianças)**.

### 6.7 O Esquecido
Fama caiu a 0 sem escândalo. É o final mais comum e precisa ser escrito com carinho: "Um dia, numa fila de farmácia, alguém diz: 'você não era…?' Você diz que não. É mais fácil."

### 6.8 A indústria adulta
Dinheiro < 0, Fama residual, Beleza ≥ 3, Juízo ≤ 2 em algum momento. Caminho de 3 eventos (a oferta "artística", a oferta não-artística, a entrevista 10 anos depois). Final: **"Ex-estrela de sitcom" (título de documentário)**. Tratar com humor, nunca com desprezo pelo trabalho sexual em si: a piada é Hollywood, não a pessoa.

### 6.9 O Civil
Largou tudo no Ato III para criar filhos / virar professor de teatro / casar com dentista. Final: **"Hoje dá aula em Ohio e é feliz. Sério."** — o final secretamente mais raro e um achievement ("Saiu enquanto podia").

---

## 7. Finais (lista mestra, 40+)

Cada final tem: nome, manchete estilo *Variety*, ícone, condição, raridade (%) e uma frase para o card.

| Categoria | Finais |
|---|---|
| **Glória** | EGOT · Oscar honorário · "O(a) maior da geração" · Estátua de cera (versão que não parece com você) · Estrela na calçada (ao lado de um cachorro famoso) |
| **Dinheiro** | Bilionário(a) da tequila · Rei/Rainha da franquia · Produtor(a) poderoso(a) · Dono(a) de time de futebol galês |
| **Reinvenção** | Diretor(a) premiado(a) · Governador(a) · Broadway · Voz do guaxinim · Rei/Rainha do Natal · Showrunner · Dublador(a) de videogame · Jurado(a) de reality · Podcast de 4h |
| **Queda** | OD (Realista) · Pelado(a) na Sunset · Preso(a) (fraude fiscal / dirigir bêbado / "o incidente do iate") · Processo bilionário com ex · Esquecido(a) · Ex-estrela de sitcom (indústria adulta) · Infomercial de travesseiro · Vende curso de atuação online · Cameo por $40 |
| **Culto** | Porta-voz em cruzeiro · Fugiu e escreveu livro · Nível máximo |
| **Humano** | Professor(a) em Ohio · Fazenda de alpacas sóbrio(a) · Avô/avó que "fez uns filmes" · Morreu de velhice numa casa cheia de gente (o final bom de verdade) |
| **Meme** | O tapa · O discurso de 11 minutos · A foto do tapete vermelho que virou reação · "Aquele ator do GIF" |
| **Secretos** | Comeback aos 70 ("a Brendanaissance") · Nunca lançou nada e ficou famoso mesmo assim · Morreu no Ato I e virou lenda ("o que teria sido") · Foi substituído(a) por IA e processou (venceu/perdeu) |

**Como escolher o final**: cada final declara um vetor-alvo nos medidores + flags obrigatórias. No fim da run, calcule a distância; o mais próximo vence; empates decididos por flags e sorte. Finais raros têm peso para aparecer quando elegíveis (todo mundo quer destravar os secretos).

---

## 8. O card final (o produto compartilhável)

Opções de formato (fazer os 3 no longo prazo; MVP: o primeiro):

1. **Pôster de filme biográfico** — título gerado ("*ESTRELA CADENTE: A história de [nome]*"), tagline do final, "baseado em fatos reais", críticas falsas ("★★★★ — 'Doloroso.' Variety"), tarja de classificação com os seus vícios.
2. **Página de obituário/Wikipedia** — "foi um(a) ator(atriz) americano(a) conhecido(a) por…", filmografia gerada, prêmios, casamentos (com durações), patrimônio, causa da saída de cena.
3. **Grade de emojis estilo Wordle** — 25 quadradinhos, um por decisão: 🟩 hit 🟥 flop 🟪 prêmio 🟨 escândalo ⬛ reabilitação 💀 — para colar no Twitter sem imagem.

Elementos obrigatórios:
- Nome do final em letras grandes + manchete.
- **Filmografia procedural** (ver 9.2) com nota tipo "tomate".
- Os 5 atributos iniciais (para o amigo dizer "claro que deu errado, você botou 1 em Juízo").
- 3 "momentos-chave" escolhidos pelo jogo (as decisões de maior impacto).
- Conquistas (badges).
- Raridade: "4,1% dos jogadores terminaram assim".
- Seed/código para "jogar a mesma vida" (desafio: "consegue salvar essa carreira?").

---

## 9. Geradores procedurais

### 9.1 Nome artístico
Lista de primeiros nomes por década de nascimento + sobrenomes "de Hollywood". Opção de "o estúdio troca seu nome" (era 50).

### 9.2 Títulos de filme (por gênero)
- Drama indie: `O [Último|Primeiro] [Verão|Inverno] em [Montauk|Marfa|Duluth]`, `[Substantivo abstrato] para [Nome próprio]`
- Franquia: `[Nome de herói]: [A Era|O Legado|A Ascensão] de [Substantivo]` + numeral romano
- Terror elevado: palavra única: `Herança`, `Ninho`, `Sal`
- Natal: `Um Natal em [cidade pequena]`, `O Noivo do Natal`
- Isca de Oscar: `[Sobrenome do biografado]` ou `A Teoria de [Coisa]`
- Ação: `Velocidade [Adjetivo]`, `[Verbo no imperativo] ou Morra`
- Comédia do humorista: `[Nome]: O [Profissão]` filmado no Havaí

### 9.3 Manchetes de tabloide
Templates com slots: `"[NOME] VISTO(A) SAINDO DE [LUGAR] COM [PESSOA]"`, `"O QUE ACONTECEU COM O ROSTO DE [NOME]?"`, `"FONTES: [NOME] É 'IMPOSSÍVEL' NO SET"`.

### 9.4 Rede de pessoas
Arquétipos são instanciados com variações (gênero, nacionalidade, década) e **nome descritivo persistente** ("o diretor dos 97 takes"). Reaparecem em eventos posteriores: "O diretor dos 97 takes te quer de novo. Ele diz que mudou."

---

## 10. Mecânicas de viralidade e replay

- **Desafio diário**: mesma seed para todo mundo (mesmos atributos pré-definidos, mesma fila de eventos). Compare finais com amigos. "Hoje: nepo baby com Juízo 1."
- **Modo Destino**: comece já num arquétipo pronto ("Ex-criança estrela, 19 anos, $4M, Vício 3. Boa sorte.").
- **Modo Cenário** (do Volante): "Você é um astro de franquia em 2022 e alguém acabou de fazer piada com sua esposa no palco. Você tem 4 segundos."
- **Seed compartilhável**: link que reproduz a mesma vida para o amigo tentar "salvar".
- **Estatísticas globais** no card: "73% de quem aceitou a capa nunca ganhou um prêmio".
- **Conquistas** (nomes à la Copero): *Sem anel* (nunca indicado), *Um estúdio só*, *Nômade* (7 agentes), *Sobreviveu ao produtor*, *Disse não ao centro*, *A voz*, *Saiu enquanto podia*, *Zero Juízo* (terminou com Juízo 1 e ganhou Oscar), *Brendanaissance*, *Nepo e daí*.
- **Streak**: dias seguidos jogando o diário.
- **"Carreira de exemplo"** (do Copero): botão na home que roda uma vida aleatória em 10 segundos, para mostrar o formato antes de o jogador investir.

---

## 11. Tom e guia de escrita

- **Voz**: narrador de documentário cansado + manchete de *Variety* + amigo fofoqueiro. Frases curtas. Sempre uma observação cínica no fim.
- **Nunca nomear** pessoas reais, estúdios, filmes, igrejas. Descrever até o jogador reconhecer, mas com uma pitada de exagero que torna a descrição "ficção".
- **Humor negro sim, crueldade não**: a piada é sempre sobre Hollywood, o sistema, o ego; nunca sobre a vítima. O produtor dos abraços é vilão; quem trabalhou com ele é personagem com dilema.
- **OD e suicídio**: só com Modo Realista ligado; texto seco, sem glamour, sem detalhes de método; o card final mostra uma linha discreta de apoio (CVV 188 no Brasil / equivalente por idioma). Não é "fim de jogo engraçado", é "fim de jogo" com um silêncio.
- **Gênero e idade**: o jogo deixa explícito o duplo padrão (atrizes perdem ofertas aos 40, atores viram "charmoso grisalho") porque é sátira; o jogador pode escolher gênero e sente a diferença.
- **Idiomas**: PT-BR primeiro, EN logo depois (o formato vive de alcance), ES (o público de Copero).

---

## 12. Lista de eventos para começar (uma amostra de 60)

### Ato I (20–25)
1. O agente do porão: "Um agente com escritório em cima de uma lavanderia quer te representar. Cobra 20%." → aceitar / esperar um melhor [Contatos 3].
2. Comercial de sanduíche: $12k, Fama +2, Prestígio −1 (vira meme em 15 anos).
3. Figuração num filme de prestígio: 0 dinheiro, chance de ser notado(a) [Beleza/Talento].
4. O teste com o diretor que pede "mais pequeno": Talento rola.
5. O colega de quarto que também é ator e consegue o papel que você queria.
6. A balada nas colinas (ver 4.3).
7. "Sorria mais": a executiva sugere mudar seu nome / sotaque / dentes.
8. Primeiro papel em série adolescente: Fama ++, 6 anos preso(a).
9. O professor de teatro de 80 anos que só aceita 5 alunos.
10. Convite para um "centro" (Culto, nível 1).
11. O amigo que te chama para uma pirâmide de suplementos [Juízo].
12. Seu pai/mãe se muda para LA "para ajudar".

### Ato II (26–32)
13. A capa ou o sofá (projeto, ver 5.1).
14. Co-star caótica: romance?
15. O diretor dos 97 takes.
16. O produtor dos abraços te chama para um "café".
17. Primeiro flop: culpar o diretor na imprensa / assumir / sumir.
18. Tabloide inventa romance com um músico. Confirmar (Heat ++) / negar / "não comento".
19. A franquia quer renovar por mais 3 filmes e um parque temático.
20. O diretor dinamarquês. Festival. Terapia.
21. Casamento em Vegas (55 horas).
22. Seu agente some com $2M.
23. Tweet de 2011 ressurge.
24. Oferta para apresentar o programa de humor de sábado à noite.
25. Lesão em set de ação → opioides [Vício].
26. O filme indie que você fez por nada ganhou em um festival francês.
27. Convite para um filme de um diretor coreano sobre classes sociais.
28. Seu colega de sitcom morre.

### Ato III (33–42)
29. Temporada de prêmios: campanha ou dignidade.
30. O discurso.
31. A noite do tapa.
32. O produtor dos abraços cai. A jornalista liga.
33. Produzir o próprio filme: hipotecar a casa.
34. Filhos (ver 4.3).
35. Divórcio público. Cartas vazam.
36. Marca de tequila / skincare / cripto.
37. Culto nível 3: recrutar co-star.
38. Intervenção dos amigos (se Vício ≥ 6).
39. Reabilitação em Malibu, 30 dias, $120k.
40. "O estúdio quer rejuvenescer você digitalmente para o filme 7."
41. Dirigir o primeiro filme: pequeno drama sobre o seu pai.
42. O veterano generoso morre. Discurso no funeral.
43. Convite para ser jurado(a) de reality.
44. Processo de uma ex-assistente.
45. Comprar um time de futebol galês com um amigo.

### Ato IV (43–55)
46. O silêncio: 18 meses sem oferta.
47. A série de prestígio de domingo à noite.
48. Filme de Natal nº 1.
49. "Papel de mãe/pai do protagonista". Aceitar é admitir.
50. Cirurgia: "o que aconteceu com o rosto de…".
51. Convite para Broadway: 8 shows por semana, $0, Prestígio +++.
52. O jovem diretor da internet te quer "ironicamente".
53. Candidatura a governador.
54. Memórias: contar tudo (Dinheiro ++, pontes queimadas) / contar nada.
55. Documentário sobre o culto. Você aparece.

### Ato V (56+)
56. O comeback: um diretor de prestígio quer você como um lutador decadente / uma professora de piano / um pai moribundo.
57. Prêmio honorário. Alguém jovem apresenta e erra seu nome.
58. Cameo por $40 num app.
59. Seu neto(a) quer ser ator(atriz). Você diz…
60. Fila da farmácia: "você não era…?"

---

## 13. Arquitetura técnica sugerida (para quando sair do papel)

- **Stack**: SPA estático (Vite + React ou Svelte), deploy em Cloudflare Pages (como o Volante de Ouro). Zero backend no MVP; estatísticas globais e desafio diário com um Worker + KV depois.
- **Conteúdo em dados, não em código**: eventos em YAML/JSON com `condições` (ato, idade, atributos, flags, medidores), `peso`, `opções` com `efeitos` (imediato/diferido/permanente/multiplicador/flag) e `texto` por idioma. Escritores mexem no YAML, não no JS.
- **RNG com seed** (ex.: `seedrandom`) para desafio diário e link de "jogue a mesma vida".
- **Estado**: máquina simples `criação → ato → card → resolução → próximo` + reducer; salvar em `localStorage`.
- **Card**: render em `<canvas>` ou `html-to-image` → PNG; share via Web Share API; fallback de copiar texto (grade de emojis).
- **Esquema de evento (exemplo)**:
```yaml
id: a_capa_ou_o_sofa
ato: 2
peso: 10
requer: { nao_tem_flag: [contrato_franquia] }
texto:
  pt: "Uma diretora que você admira quer você num filme com orçamento de um sofá. ..."
opcoes:
  - rotulo: { pt: "O sofá" }
    efeitos:
      imediato: { dinheiro: 0, prestigio: +3 }
      pipeline: { tipo: indie, estreia_em: 2, chance_premio: 0.40, chance_cult: 0.25 }
  - rotulo: { pt: "A capa" }
    efeitos:
      imediato: { dinheiro: +8000000, fama: +15 }
      flag: [contrato_franquia]
      pipeline: { tipo: franquia, estreia_em: 1, chance_premio: 0.02, chance_escandalo: 0.15 }
  - rotulo: { pt: "Fazer os dois" }
    requer: { contatos: 4 }
    efeitos:
      imediato: { estabilidade: -2 }
      pipeline: [ ... ambos ... ]
```
- **MVP (2–3 semanas de conteúdo)**: 1 era, 5 atributos, 3 origens, ~120 eventos, 15 finais, card pôster, share. Depois: desafio diário, eras, modo cenário, EN/ES.

---

## 14. Perguntas em aberto (decidir antes de codar)

1. **Swipe binário (Reigns) ou 2–3 botões?** Swipe é mais viral no celular; botões permitem a 3ª opção de atributo. Proposta: swipe + a 3ª opção como "puxar para cima".
2. **Probabilidade visível em tudo ou só em projetos?** Proposta acima: projetos sim, vida não.
3. **Morte no padrão ou só no Modo Realista?** Proposta: Realista desligado por padrão, mas o card final mostra "você jogou no modo seguro" para provocar.
4. **Quão explícito ser nos arquétipos?** Quanto mais reconhecível, mais viral e mais risco. Regra: descrever traços públicos e notórios, exagerar um grau, nunca nomear, nunca inventar crime novo para alguém identificável.
5. **Nome do jogo**: *Estrela Cadente* · *Tapete Vermelho* · *Agradeço à Academia* · *Sunset* · *Baseado em Fatos Reais* · *Ex-Estrela*.
