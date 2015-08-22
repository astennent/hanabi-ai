from Game import *
from random import seed
def main():
   random.seed(514)
   game = Game(4)
   game.play()

if __name__ == "__main__":
   main()
