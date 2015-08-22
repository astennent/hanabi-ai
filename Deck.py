import random
from CardFact import *
from Card import *
import copy

class Deck():
   def GenerateFreshMap(self):
      deck = dict([])
      for suit in SUITS:
         deck[suit] = dict([])
         for number in NUMBERS:
            count = CARD_COUNTS[number-1]
            deck[suit][number] = count

      return deck

   def GenerateFreshList(self):
      cards = []

      for suit in SUITS:
         for number in NUMBERS:
            count = CARD_COUNTS[number-1]
            for i in range(count):
               c = Card(suit, number)
               cards.append(c)
      return cards

   def __init__(self):
      cards = self.GenerateFreshList()
      random.shuffle(cards)
      self._cards = cards

      self._remainingCards = self.GenerateFreshMap()

   def draw(self):
      nextCard = self._cards.pop()
      self._remainingCards[nextCard.suit()][nextCard.number()] -= 1
      return nextCard

   def remainingCards(self):
      return copy.deepcopy(self._remainingCards)
