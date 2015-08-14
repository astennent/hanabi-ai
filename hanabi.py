import random

CARD_COUNTS = [3, 2, 2, 2, 1]
SUITS = ["blue", "green", "red", "yellow", "orange"]
class Card():
   def __init__(self, suit, number):
      self.suit = suit
      self.number = number

   def __str__(self):
      return str.format("{}:{}", self.suit, self.number+1)

   def __unicode__(self):
      return str.format("{}:{}", self.suit, self.number+1)

class Deck():
   def __init__(self):
      cards = []

      for suit in SUITS:
         for number in range(0, 5):
            count = CARD_COUNTS[number]
            for i in range(0, count):
               c = Card(suit, number)
               cards.append(c)

      random.shuffle(cards)
      self.cards = cards

class Game():
   def __init__(self, numPlayers):
      self.players = []
      for i in range(0, numPlayers):
         self.players.append(Player(self))

      self.deck = Deck()



class Player():
   def __init__(self, game):
      self.game = game


def main():
   game = Game(4)
   game.play()

if __name__ == "__main__":
   main()
