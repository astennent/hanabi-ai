from Game import *
from random import seed

NumPlayers = 4
SimulationDepth = 3

def main():
   random.seed(515)
   game = Game(NumPlayers, SimulationDepth)
   score = game.play()

if __name__ == "__main__":
   main()
