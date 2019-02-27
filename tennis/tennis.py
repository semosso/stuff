from textwrap import dedent
from random import randint

class Player(object):

     # consider adding a mental component
     # i.e., if player is down by X and mental > Y, higher chances of scoring
     # i.e., if it's a match point and mental < X, lower chances of scoring
    pool = {
        "roger": ["Roger Federer", 3, 5, 4],
        "rafa": ["Rafael Nadal", 4, 3, 5],
        "djoko": ["Novak Djokovic", 4, 5, 3],
        "andy": ["Andy Murray", 4, 4, 4]
    }

    def __init__(self, nome):
        self.name = Player.pool[f"{nome}"][0]
        self.stamina = Player.pool[f"{nome}"][1]
        self.technique = Player.pool[f"{nome}"][2]
        self.spin = Player.pool[f"{nome}"][3]

    def court_impact(self, court):
        self.stamina += court.impact_stamina
        self.technique += court.impact_technique
        self.spin += court.impact_spin

class Court(object):

    pool = {
        "au": ["Australian Open", -1, 0, 0],
        "fr": ["Roland Garros", 0, 0, -2],
        "uk": ["Wimbledon", -1, -1, 0],
        "us": ["U.S. Open", 0, -2, 0],
    }

    def __init__(self, quadra):
        self.name = Court.pool[f"{quadra}"][0]
        self.impact_stamina = Court.pool[f"{quadra}"][1]
        self.impact_technique = Court.pool[f"{quadra}"][2]
        self.impact_spin = Court.pool[f"{quadra}"][3]

# complexity to be added: full scoring system, game by game, set by set
# class Match(object):
# class Set(Match):
# class Game(Set):

class Engine(object):

    def __init__(self, player1, player2, court):
        self.player1 = player1
        self.player2 = player2
        self.court = court
        self.p1_wins = 0 # where should this be defined? inside each function?
        self.p2_wins = 0 # inside function might be the best scope... figure it out later

    def fifty_match(self):
        for i in range(1, 10001):
            simul = randint(1, 2)
            
            if simul == 1:
                self.p1_wins += 1
            elif simul == 2:
                self.p2_wins += 1
            else:
                exit(0)

        self.log = "log.txt"
        with open(self.log, "a+") as f:
            f.write(dedent(f"""\n50-50 simul results:\n
            {self.player1.name} won {self.p1_wins}, {self.player2.name} won {self.p2_wins}"""))

    def actual_match(self):
        self.player1.court_impact(self.court)
        self.player2.court_impact(self.court)

        # standard of comparison is 2, * 3 attributes
        self.p1_delta = self.player1.stamina + self.player1.technique + self.player1.spin - 6
        self.p2_delta = self.player2.stamina + self.player2.technique + self.player2.spin - 6
        self.delta = self.p1_delta - self.p2_delta # this renders court_impact useless

        if self.p1_delta == self.p2_delta:
            simul.fifty_match()

        for i in range(1, 10001):
            self.win_prob = randint(1, 100)

            if self.win_prob == range(1, (51+self.delta)):
                    self.p1_wins += 1
            elif self.win_prob == range((51+self.delta), 101):
                    self.p2_wins += 1
            else:
                exit(0)

        self.log = "log.txt"
        with open(self.log, "a+") as f:
            f.write(dedent(f"""\n50-50 simul results:\n
            {self.player1.name} won {self.p1_wins}, {self.player2.name} won {self.p2_wins}"""))


name1, name2, court = Player("rafa"), Player("roger"), Court("fra") # hard set values to test my work
simul = Engine(name1, name2, court)
simul.fifty_match()
simul.actual_match()

# to add sometime: player/court input cleanup (similar to NBA game app)
# simular vários campeonatos e salvar todos num txt para teste
# atributos de 1 a 10, que impactam a chance de ter um power ou weak move
# a chance é random, mas os atributos aumentam
# quadras afetam os atributos
# quanto mais sets jogados, maior o efeito
# preciso criar um scoring system

# desenhando função de actual match
# se delta = 0, 50-50; = 1, 53-47; = 2, 55-45; = 3, 58-42; > 4, 60-40
## this doesn't work, it makes court_impact redundant since it affects both players in the same way
## what I can do is to make win% change based on a delta vs. a standard (3), not other player
### i.e., delta = sum of all deviations (+ or -) between player attribute and 3
# 1, recebe os jogadores/court;
# 2, aplica o court_impact;
# 3, compara as pontuações ajustadas;
# 4, "simula partida" com chances delta-dependent