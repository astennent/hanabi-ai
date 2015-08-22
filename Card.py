SUITS = ["blue", "green", "red", "yellow", "orange"]
NUMBERS = range(1, 6)
CARD_COUNTS = [3, 2, 2, 2, 1]

class Card():
   def __init__(self, suit, number):
      self._suit = suit
      self._number = number

   def __str__(self):
      return str.format("{}:{}", self._suit, self._number)

   def __unicode__(self):
      return str.format("{}:{}", self._suit, self._number)

   def number(self):
      return self._number

   def suit(self):
      return self._suit

