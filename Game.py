from Player import *
from Deck import *
from CardDrawManager import *
from Simulation import *

InitialDrawCount = 4
InitialHintTokens = 8
InitialDeathTokens = 3

progressValues = [0, 60, 110, 145, 170, 190]
hintTokenValues = [20, 15, 10, 10, 10, 0, 0, 0]
deathTokenValues = [-1000, -80, -20, 0]

class Game():
   def __init__(self, numPlayers, maxSimulationDepth):
      self._players = []
      self._currentPlayerIndex = 0
      self._deck = Deck()
      self._cardDrawManager = CardDrawManager(self)

      print "==========="
      self._deck.printCards()

      for playerIndex in range(numPlayers):
         player = Player(self, playerIndex)
         self._players.append(player)
         for drawIndex in range(InitialDrawCount):
            self._cardDrawManager.handleDrawFor(player)

      for player in self._players:
         print player
         print "============="

      self._progress = {}
      for suit in SUITS:
         self._progress[suit] = 0

      self._hintTokens = InitialHintTokens
      self._deathTokens = InitialDeathTokens
      self._maxSimulationDepth = maxSimulationDepth

   def deck(self):
      return self._deck

   def currentPlayerIndex(self):
      return self._currentPlayerIndex

   def iteratePlayerIndex(self):
      self._currentPlayerIndex += 1
      self._currentPlayerIndex %= len(self._players)

   def play(self):
      while self._deck.hasNext() and self._deathTokens > 0:
         self.doTurn()

      for i in range(len(self._players)):
         if self._deathTokens == 0:
            break
         self.doTurn()        

      if self._deathTokens == 0:
         print "Ended early because we fucked up."

      print self._progress

   def doTurn(self):
      simulation = Simulation(self, self._players[self._currentPlayerIndex])
      self.simulateSingleTurn(simulation)
      self.iteratePlayerIndex()

   def simulateSingleTurn(self, simulation):
      canPrint = simulation._depth == 0
      action, score = self._players[self._currentPlayerIndex].getActionForTurn(simulation)
      if canPrint:
         print "--------"
         print str.format("{} will do: {}. Score at depth: {}", self.currentPlayer(), action, score)
         self.printProgress()
      self.processAction(action, simulation.isSimulating())
      if canPrint:
         print str.format("Score after play: {}. Hint tokens: {}. Death Tokens: {}", self.score(None), self._hintTokens, self._deathTokens)
         print "--------"

      return score # Represents the best score at the deepest sim level.

   def processAction(self, action, isSimulating):
      if action.actionName() == "Hint":
         self.processHint(action)
      else:
         self.processBurnOrPlay(action, isSimulating)

   def processHint(self, hint):
      hint.player().receiveHint(hint)
      self._hintTokens -= 1

   def processBurnOrPlay(self, action, isSimulating):
      player = action.player()
      cardFact = action.cardFact()
      player.dropCard(cardFact)

      if action.actionName() == "Burn":
         self._hintTokens += 1
      else: # Play:
         card = cardFact.card()
         suit = card.suit()
         number = card.number()
         if self.progress(suit) == number - 1:
            self._progress[suit] = number  # :)
         else:
            self._deathTokens -= 1 # :(

      if not isSimulating:
         self._cardDrawManager.handleDrawFor(player)

   def progress(self, suit):
      return self._progress[suit]

   def allProgress(self):
      return self._progress

   def printProgress(self):
      output = "Progress {"
      for suit in SUITS:
         output += str.format(" {}:{} ", suit, self.progress(suit))
      print output + "}"

   def currentPlayer(self):
      return self._players[self._currentPlayerIndex]

   def players(self):
      return self._players

   def hintTokens(self):
      return self._hintTokens

   def deathTokens(self):
      return self._deathTokens

   def getDeathTokenValue(self, numTokens):
      if numTokens < 0:
         numTokens = 0
      return deathTokenValues[numTokens]

   # Returns the value of spending a death token.
   def nextDeathTokenValue(self):
      return self.getDeathTokenValue(self._deathTokens-1)

   # Returns the value of gaining a hint.
   def nextHintTokenValue(self):
      return hintTokenValues[self._hintTokens+1]

   def calculateProgressValue(self, suitProgress):
      return -3.3571 * suitProgress * suitProgress + 75.071 * suitProgress

   def score(self, uninformedPlayer):
      score = 0
      for suit in SUITS:
         suitProgress = self._progress[suit]
         score += self.calculateProgressValue(suitProgress)

      score += sum(hintTokenValues[0:self._hintTokens])
      score += self.getDeathTokenValue(self._deathTokens)

      # Scoring for unplayed cards. Needs A/B Testing. These numbers don't need to be high.
      # They are just used for breaking ties between hints that are too distant to observe.
      for player in self._players:
         for cardFact in player.hand():
            if player is not uninformedPlayer:
               card  = cardFact.card()
               if cardFact.shouldPlay():
                  if self._progress[card.suit()] == card.number() - 1:
                     score += 8
                  else:
                     score -= 2
               elif cardFact.shouldBurn():
                  if self._progress[card.suit()] >= card.number():
                     score += 7
                  else:
                     score -= 7

      return score

