from CardFact import *
from Action import *

import copy

class Player():

   def __init__(self, game, id):
      self._game = game
      self._hand = []
      self._id = id

   def __str__(self):
      output = str.format("Player{} [", self._id)
      for card in self._hand:
         output += str(card) + ", "
      output= output[0:-2] + "]"
      return output

   def hand(self):
      return self._hand

   def receiveCard(self, cardFact):
      self._hand.append(cardFact)

   def dropCard(self, cardFact):
      self._hand.remove(cardFact)
      removePossibility(cardFact.card())

   def removePossibility(self, card):
      for cardFact in self._hand:
         cardFact.removePossibility(card)


   def GetActionForTurn(self, simulationDepth):

      #TODO: Reconsider Plays and Burns if hints are better.
      safePlayFact = self.getSafePlay()
      if safePlayFact:
         return Play(safePlayFact)
      
      safeBurnFact = self.getSafeBurn()
      if safeBurnFact:
         return Burn(safeBurnFact)

      if self._game.hintTokens() > 0:
         return self.calculateBestHint(simulationDepth)

      # No more Hint tokens. Guessing time!
      return self.Yolo()


   def getSafePlay(self):
      for cardFact in self._hand:
         if cardFact.shouldPlay():
            # TODO: Double check, someone might have finished the suit or number.
            return cardFact

      return None


   def getSafeBurn(self):
      for cardFact in self._hand:
         if cardFact.shouldBurn():
            return cardFact

      return None


   def getCards(self):
      if self._game.currentPlayer() == self:
         return []
      cards = []
      for cardFact in self._hand:
         cards.append(cardFact.card())
      return cards


   def calculateBestHint(self, simulationDepth):
      bestScore = 0
      bestHint = None
      for otherPlayer in self._game.playersExcept(self):
         validHints = otherPlayer.getValidHints()
         for hint in validHints:
            score = self._game.simulate(hint, simulationDepth)
            if score > bestScore:
               bestScore = score
               bestHint = hint
      return bestHint


   def getValidHints(self):
      numbers = set([])
      suits = set([])
      hints = []
      for card in self.getCards():
         number = card.number()
         if number not in numbers:
            numbers.add(number)
            hints.append(Hint(True, number, self))

         suit = card.suit()
         if suit not in suits:
            suits.add(suit)
            hints.append(Hint(False, suit, self))
      return hints


   def receiveHint(self, hint):
      print "Receving " + str(hint)

      relevantCardFacts = []
      for cardFact in self._hand:
         # We let the cardFact determine if it applies. This is a little weird since in real life
         # the hinting player would point out which cards it applies to, but this is cleaner.
         cardFact.processHint(hint)

         if hint.appliesToCard(cardFact.card()):
            relevantCardFacts.append(cardFact)

      if hint.isNumber():
         self.contemplateNumberHint(hint.value(), relevantCardFacts)
      else:
         self.contemplateSuitHint(hint.value(), relevantCardFacts)

   # Add context clues that cannot be determined from the game state on the player's turn.
   def contemplateNumberHint(self, number, relevantCardFacts):
      pass

   # Add context clues that cannot be determined from the game state on the player's turn.
   def contemplateSuitHint(self, suit, relevantCardFacts):
      pass

   def Yolo(self):
      print "I don't know how to yolo"
      exit(0)

