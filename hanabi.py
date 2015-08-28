from Game import *
from random import seed

NumPlayers = 4
SimulationDepth = 4

def main():
   random.seed(3)
   game = Game(NumPlayers, SimulationDepth)
   score = game.play()

if __name__ == "__main__":
   main()
