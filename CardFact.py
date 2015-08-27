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
      possibleSuits = set([])
      possibleNumbers = set([])
      for suit in SUITS:
         for number in NUMBERS:
            if self._possibilities[suit][number] > 0:
               possibleSuits.add(suit)
               possibleNumbers.add(number)

      suitCount = len(possibleSuits)
      numberCount = len(possibleNumbers)

      if suitCount == 1 and numberCount == 1:
         delimiter = "*"
      elif suitCount == 1:
         delimiter = "$"
      elif numberCount == 1:
         delimiter = "#"
      else:
         delimiter = "-"

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

   def setShouldPlay(self):
      self._shouldPlay = True
      self._shouldBurn = False

   def setShouldBurn(self):
      self._shouldBurn = True
      self._shouldPlay = False

   def disableBurn(self):
      self._shouldBurn = False

   def possibilities(self):
      return self._possibilities

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
      currentValue = self._possibilities[card.suit()][card.number()]

      # It is common to receive an indirect hint that sets a possibility to 0 before you see the 
      # card that's causing this to be removed.
      if currentValue > 0:
         self._possibilities[card.suit()][card.number()] -= 1


   # Returns True if there is at least ONE possibility that would be playable.
   def verifyPlayable(self, progress):
      for suit in progress:
         nextRequiredNumber = progress[suit] + 1
         if nextRequiredNumber <= 5 and self.hasPossibility(suit, nextRequiredNumber):
            return True

      return False

   # If there is even one possibility that would be a reasonable burn, this will be True.
   def verifyBurnable(self, progress):
      for suit in progress:
         suitProgress= progress[suit]
         for number in NUMBERS:
            possibilities = self._possibilities[suit][number]
            if possibilities > 1: # Definitely won't block this.
               return True
            elif possibilities == 1 and number <= suitProgress: #
               return True

      return False

   def hasPossibility(self, suit, number):
      return self._possibilities[suit][number] > 0


   def calculateYolo(self, progress):
      totalPossibilities = 0.0
      totalPlayable = 0
      totalBurnable = 0
      for suit in SUITS:
         suitProgress = progress[suit]
         for number in NUMBERS:
            remainingMatches = self._possibilities[suit][number]
            totalPossibilities += remainingMatches
            if number == suitProgress+1:
               totalPlayable += remainingMatches
            elif number <= suitProgress:
               totalBurnable += remainingMatches

      return totalPlayable / totalPossibilities, totalBurnable / totalPossibilities
