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
      self.removePossibility(cardFact.card()) # You can look at it now.


   def removePossibility(self, card):
      for cardFact in self._hand:
         cardFact.removePossibility(card)


   def GetActionForTurn(self, simulationMetadata):
      #TODO: Reconsider Plays and Burns if hints are better.
      safePlayFact = self.getSafePlay()
      if safePlayFact:
         return Play(safePlayFact, self)
      
      safeBurnFact = self.getSafeBurn()
      if safeBurnFact:
         return Burn(safeBurnFact, self)

      if self._game.hintTokens() > 0:
         return self.calculateBestHint(simulationMetadata)

      # No more Hint tokens. Guessing time!
      return self.Yolo()


   def getSafePlay(self):
      for cardFact in self._hand:
         if cardFact.shouldPlay():
            if cardFact.verifyPlayable(self._game.allProgress()):
               return cardFact
            else:
               cardFact.setShouldBurn()

      return None


   def getSafeBurn(self):
      for cardFact in self._hand:
         if cardFact.shouldBurn():
            return cardFact # should double check this?

      return None


   def getCards(self):
      cards = []
      for cardFact in self._hand:
         cards.append(cardFact.card())
      return cards


   def calculateBestHint(self, simulationMetadata):
      bestScore = 0
      bestHint = None
      for otherPlayer in self._game.players():
         if otherPlayer == self or otherPlayer == simulationMetadata.initialPlayer:
            continue

         validHints = otherPlayer.getValidHints()
         for hint in validHints:

            if simulationMetadata.depth <= 0:
               print str.format("{}Player {} At depth {}. \t Considering {} \t for player{}", \
                  "  "*simulationMetadata.depth, self._id, simulationMetadata.depth, hint, otherPlayer._id)
            score = self._game.simulate(hint, simulationMetadata)
            if simulationMetadata.depth <= 0:
               print str.format("{}Score: {}", "  "*simulationMetadata.depth, score)

            if score > bestScore:
               bestScore = score
               bestHint = hint
      return bestHint


   def getValidHints(self):
      #TODO: Make sure you don't double-hint.

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
      playableSlots = 0
      futureSlots = 0
      for suit in SUITS:
         currentProgress = self._game.progress(suit)
         if currentProgress == number - 1:
            playableSlots += 1
         elif currentProgress < number:
            futureSlots += 1

      if playableSlots >= len(relevantCardFacts):
         for cardFact in relevantCardFacts:
            cardFact.setShouldPlay()

      elif futureSlots <= len(relevantCardFacts):
         for cardFact in relevantCardFacts:
            cardFact.setShouldBurn()


   # Add context clues that cannot be determined from the game state on the player's turn.
   def contemplateSuitHint(self, suit, relevantCardFacts):
      remainingCardsForSuit = len(NUMBERS) - self._game.progress(suit)
      if remainingCardsForSuit < len(relevantCardFacts):
         for cardFact in relevantCardFacts:
            cardFact.setShouldBurn()

      elif len(relevantCardFacts) == 1:
         relevantCardFacts[0].setShouldPlay()


   def Yolo(self):
      print "I don't know how to yolo"
      exit(0)

