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
    pass

def name_input(question):
    print(question)
    name = input("> ").lower()
    name = "".join(x for x in Player.pool.keys() if name in x.lower())

    while name not in list(Player.pool.keys()):
        name = name_input(f"Pick one from the following: {list(Player.pool.keys())}")
        
    return name

nome = name_input("Escolha")
jogador1 = Player(nome)
quadra = Court("wimbledon")
# teste inicio
print(jogador1.name)
print(quadra.name, quadra.impact_stamina, quadra.impact_technique, quadra.impact_spin)
jogador1.court_impact(quadra)
print(jogador1.pool[nome])
print(jogador1.name, jogador1.stamina, jogador1.technique, jogador1.spin)
# teste fim

# simular vários campeonatos e salvar todos num txt para teste
# atributos de 1 a 10, que impactam a chance de ter um power ou weak move
# a chance é random, mas os atributos aumentam
# quadras afetam os atributos
# quanto mais sets jogados, maior o efeito
# preciso criar um scoring system