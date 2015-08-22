from Card import *

class CardFact:

   def __init__(self, card, possibilities):
      self._card = card

      # Hints can be given that don't necessarily make sense with the current board state.
      # shouldBurn and shouldPlay are used for tracking these. If a hint is given which indicates
      # a certain number of possible plays
      self._shouldBurn = False
      self._shouldPlay = False
      self._possibilities = possibilities

   def __str__(self):
      delimiter = "" # TODO: Switch on knowledge
      return str.format("{}{}{}", delimiter, self._card, delimiter)

   def printPossibilities(self):
      for suit in SUITS:
         suitString = suit + ": "
         for number in NUMBERS:
            suitString += str(self._possibilities[suit][number]) + " "
         print suitString 

   def shouldPlay(self):
      return self._shouldPlay

   def shouldBurn(self):
      return self._shouldBurn

   def card(self):
      return self._card

   def processHint(self, hint):
      hintApplies = hint.appliesToCard(self._card)

      for suit in SUITS:
         for number in NUMBERS:
            hintMatchesCombo = hint.appliesToNumberOrSuit(number, suit)
            if hintApplies is not hintMatchesCombo:
               self._possibilities[suit][number] = 0

   def removePossibility(self, card):
      self._possibilities[card.suit()][card.number()] -= 1
