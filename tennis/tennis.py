from textwrap import dedent

# class jogador
class Player(object):

    pool = {
        "Roger Federer": [0, 1, 2],
        "Rafael Nadal": [0, 1, 2],
        "Novak Djokovic": [0, 1, 2],
        "Andy Murray": [0, 1, 2]
    }

    def __init__(self, name):
        self.name = name
        self.strength = Player.pool[f"{name}"][0]
        self.stamina = Player.pool[f"{name}"][1]
        self.speed = Player.pool[f"{name}"][2]

    def power_move(self):
        print("w/e")
    
    def weak_move(self):
        print("w/e")

# class tipo de quadra

# class equipamento

# class condição climática

# class engine
class Engine(object):
        
    def name_input(self, question):
        print(question)
        name = input("> ").lower()
        name = "".join(x for x in Player.pool.keys() if name in x.lower())

        while name not in list(Player.pool.keys()):
            name = self.name_input(dedent(f"""
            That player is not in the tournament, pick one from the following:
            {list(Player.pool.keys())}"""))
        
        return name

name = Engine()
nome = name.name_input("Escolha")
jogador = Player(nome)
print(type(jogador.strength))