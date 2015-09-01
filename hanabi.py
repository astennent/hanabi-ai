from Game import *
from random import seed

import cProfile
import pstats

NumPlayers = 4
SimulationDepth = 3

def main():
   random.seed(6)
   game = Game(NumPlayers, SimulationDepth)
   score = game.play()

if __name__ == "__main__":
   main()
   #cProfile.run("main()", "hanabi-stats")
   #pstats.Stats('hanabi-stats').sort_stats('tottime').print_stats()

