from textwrap import dedent
from random import randint

# class jogador
class Player(object):

    pool = {
        "Roger Federer": [3, 5, 4],
        "Rafael Nadal": [4, 3, 5],
        "Novak Djokovic": [4, 5, 3],
        "Andy Murray": [4, 4, 4]
    }

    def __init__(self, name):
        self.name = name
        self.stamina = Player.pool[f"{name}"][0]
        self.technique = Player.pool[f"{name}"][1]
        self.spin = Player.pool[f"{name}"][2]

    def court_impact(self, court):
        self.stamina += court.impact_stamina
        self.technique += court.impact_technique
        self.spin += court.impact_spin

# class tipo de quadra
class Court(object):

    slams = {
        "australian": ["Australian Open", -2, 0, 0],
        "garros": ["Roland Garros", 0, 0, -2],
        "wimbledon": ["Wimbledon", -1, -1, 0],
        "us": ["U.S. Open", 0, -2, 0],
    }

    def __init__(self, tourney):
        self.name = Court.slams[f"{tourney}"][0]
        self.impact_stamina = Court.slams[f"{tourney}"][1]
        self.impact_technique = Court.slams[f"{tourney}"][2]
        self.impact_spin = Court.slams[f"{tourney}"][3]

# complexity to be added: full scoring system, game by game, set by set
# class Match(object):
#     pass

# class Set(Match):
#     pass

# class Game(Set):
#     p1_score = 0
#     p2_score = 0

# class engine
class Engine(object):

    def __init__(self, p1, p2, quadra):
        self.player1 = Player(p1)
        self.player2 = Player(p2)
        self.court = Court(quadra)
        self.log = "log.txt"

    def simple_match(self):
        # I don't think there's a need to assign it to a variable here...
        self.player1.court_impact(self.court)
        self.player2.court_impact(self.court)

        p1_wins = 0
        p2_wins = 0
        
        for i in range(1, 1001):
            simul = randint(1, 2)
            if simul == 1:
                p1_wins += 1
                with open(self.log, "a+") as f:
                    f.write(f"Jogo {i}: {self.player1.name} wins!\n")
            elif simul == 2:
                p2_wins += 1
                with open(self.log, "a+") as f:
                    f.write(f"Jogo {i}: {self.player2.name} wins!\n")
            else:
                with open(self.log, "a+") as f:
                    f.write("Oh oh, erro")
                    exit(0)
        
        with open(self.log, "a+") as f:
            f.write(dedent(f"""
            {self.player1.name} wins: {p1_wins}
            {self.player2.name} wins: {p2_wins}"""))

def player_input(question):
    print(question)
    name = input("> ").lower()
    name = "".join(x for x in Player.pool.keys() if name in x.lower())

    while name not in list(Player.pool.keys()):
        name = player_input(f"Pick one from the following: {list(Player.pool.keys())}")
        
    return name

nome1 = player_input("Escolha o jogador")
nome2 = player_input("Escolha o jogador")
teste = Engine(nome1, nome2, "wimbledon")
teste.simple_match()
## teste inicio
# print(jogador.name)
# print(quadra.name, quadra.impact_stamina, quadra.impact_technique, quadra.impact_spin)
# jogador.court_impact(quadra)
# print(jogador.pool[nome])
# print(jogador.name, jogador.stamina, jogador.technique, jogador.spin)
## teste fim


# simular vários campeonatos e salvar todos num txt para teste
# atributos de 1 a 10, que impactam a chance de ter um power ou weak move
# a chance é random, mas os atributos aumentam
# quadras afetam os atributos
# quanto mais sets jogados, maior o efeito
# preciso criar um scoring system