from Card import *

class CardFact:

   def __init__(self, card, possibilities, owner):
      self._card = card

      # Hints can be given that don't necessarily make sense with the current board state.
      # shouldBurn and shouldPlay are used for tracking these. If a hint is given which indicates
      # a certain number of possible plays
      self._shouldBurn = False
      self._shouldPlay = False
      self._possibilities = possibilities
      self._receivedNumberHint = False
      self._receivedSuitHint = False
      self._owner = owner

   def countSuitsAndNumbers(self, uninformedSimPlayer):
      possibleSuits = set([])
      possibleNumbers = set([])
      for suit in SUITS:
         for number in NUMBERS:
            if self._possibilities[suit][number] > 0:
               possibleSuits.add(suit)
               possibleNumbers.add(number)

      if uninformedSimPlayer is not None and uninformedSimPlayer is not self._owner:
         for cardFact in uninformedSimPlayer.hand():
            card = cardFact.card()
            suit = card.suit()
            number = card.number()
            if self._possibilities[suit][number] > 0: #ick duplicated code.
               possibleSuits.add(suit)
               possibleNumbers.add(number)

      suitCount = len(possibleSuits)
      numberCount = len(possibleNumbers)
      return suitCount, numberCount

   def __str__(self):
      suitCount, numberCount = self.countSuitsAndNumbers(None)
      if suitCount == 1 and numberCount == 1:
         delimiter = "*"
      elif suitCount == 1:
         delimiter = "$"
      elif numberCount == 1:
         delimiter = "#"
      else:
         delimiter = "-"

      return str.format("{}{}{}", delimiter, self._card, delimiter)

   def isFullyRevealed(self, uninformedSimPlayer):
      suitCount, numberCount = self.countSuitsAndNumbers(uninformedSimPlayer)
      return (suitCount == 1 and numberCount == 1)

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

      if hint.isNumber():
         self._receivedNumberHint = True
      else:
         self._receivedSuitHint = True

   def removePossibility(self, card):
      currentValue = self._possibilities[card.suit()][card.number()]

      # It is common to receive an indirect hint that sets a possibility to 0 before you see the 
      # card that's causing this to be removed.
      if currentValue > 0:
         self._possibilities[card.suit()][card.number()] -= 1


   def calculateExpectedNumber(self, progress, uninformedSimPlayer):
      expectedSum = 0
      expectedCount = 0
      
      # To avoid cheating, we add back possibilities of the player counting these options. This
      # makes the expected number for each card slightly higher (and less accurate), but the 
      # net effect of counting instead of guessing randomly is still positive.
      extraPossibilities = dict([]) 
      if uninformedSimPlayer is not None and uninformedSimPlayer is not self._owner:
         for cardFact in uninformedSimPlayer.hand():
            key = cardFact.card().suit() + str(cardFact.card().number())
            if key in extraPossibilities:
               extraPossibilities[key] += 1
            else:
               extraPossibilities[key] = 1

      for suit in progress:
         nextRequiredNumber = progress[suit] + 1
         if nextRequiredNumber <= 5:
            numPossibilities = self._possibilities[suit][nextRequiredNumber]

            extraPossibilitiesKey = suit + str(nextRequiredNumber)
            if extraPossibilitiesKey in extraPossibilities :
               numPossibilities -= max(numPossibilities-extraPossibilities[extraPossibilitiesKey], 0)

            expectedSum += numPossibilities * nextRequiredNumber
            expectedCount += numPossibilities

      if expectedCount == 0:
         return None # The card is not playable right now!


      return (1.0 * expectedSum) / expectedCount
      

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
