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


   def getActionForTurn(self, simulation):
      actions = self.getSafePlays() + self.getSafeBurns()

      # Only consider hints if you don't have something better to do.
      if self._game.hintTokens() > 0:
         actions += self.getValidHintsForOthers(simulation)

      if len(actions) == 0:
         actions = [self.Yolo(simulation)]
      
      return simulation.simulate(actions)

   def getSafePlays(self):
      #TODO: Even if you only return one thing, you can still choose the BEST thing with more info.
      for cardFact in self._hand:
         if cardFact.shouldPlay():
            if cardFact.verifyPlayable(self._game.allProgress()):
               # Is this cheating? This always plays the first card you find...
               return [Play(cardFact, self)]
            else:
               cardFact.setShouldBurn() #Turns out this can't be played. Burn it!

      return []


   def getSafeBurns(self):
      #TODO: Even if you only return one thing, you can still choose the BEST thing with more info.
      for cardFact in self._hand:
         if cardFact.shouldBurn():
            if cardFact.verifyBurnable(self._game.allProgress()):
               return [Burn(cardFact, self)] # should this be verified?
            else:
               cardFact.disableBurn()

      return []

   def getCards(self):
      cards = []
      for cardFact in self._hand:
         cards.append(cardFact.card())
      return cards


   def getValidHintsForOthers(self, simulation):
      hints = []
      for otherPlayer in self._game.players():
         if otherPlayer != self and otherPlayer != simulation.initialPlayer:
            hints += otherPlayer.getValidHintsForSelf()
      
      return hints

   def getValidHintsForSelf(self):
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


   def Yolo(self, simulation):
      # print ""
      # print str(self)
      # print str(self._game._progress)

      highestPlayProbability = 0
      bestPlay = None
      highestBurnProbability = 0
      bestBurn = None

      for cardFact in self.hand():
         playProbability, burnProbability = cardFact.calculateYolo(self._game.allProgress())
         if playProbability > highestPlayProbability:
            highestPlayProbability = playProbability
            bestPlay = cardFact
         if burnProbability > highestBurnProbability:
            highestBurnProbability = burnProbability
            bestBurn = cardFact

      gainOfBadPlay = self._game.nextDeathTokenValue()
      gainOfGoodPlay = 10 # TODO: This should be more sensitive to progress.

      gainOfBadBurn = -30 # TODO: This should also be more senstive to blocking progress.
      gainOfGoodBurn = self._game.nextHintTokenValue()

      playUtility = (gainOfGoodPlay * highestPlayProbability) + (gainOfBadPlay * (1 - highestPlayProbability))
      burnUtility = (gainOfGoodBurn * highestBurnProbability) + (gainOfBadBurn * (1 - highestBurnProbability))

      # print "--------"
      # print str.format("Burn: Utility: {},  Card: {}, Prob: {}", burnUtility, bestBurn, highestBurnProbability)
      # print str.format("Play: Utility: {},  Card: {}, Prob: {}", playUtility, bestPlay, highestPlayProbability)
      # print "--------"

      # exit(0)
      if bestPlay != None and playUtility > burnUtility:
         return Play(bestPlay, self)
      elif bestBurn != None:
         return Burn(bestBurn, self)
      else:
         # Definitely no burns or plays. Just burn the first card. 
         # TODO: Can this selection be smarter? Maybe avoid discards that end suits?
         return Burn(self.hand()[0], self)

