from Player import *
from Deck import *
from CardDrawManager import *
from Simulation import *

InitialDrawCount = 4
InitialHintTokens = 8
InitialDeathTokens = 3

progressValues = [0, 50, 95, 130, 155, 170]
hintTokenValue = 10
deathTokenValues = [-1000, -40, -20, 0]

class Game():
   def __init__(self, numPlayers, maxSimulationDepth):
      self._players = []
      self._currentPlayerIndex = 0
      self._deck = Deck()
      self._cardDrawManager = CardDrawManager(self)

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
         print str.format("Score at depth: {}, Action Performed: {}", score, action)
         print self.allProgress()
      self.processAction(action, simulation.isSimulating())
      if canPrint:
         print str.format("Score after play: {}", self.score())
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

   def nextDeathTokenValue(self):
      return self.getDeathTokenValue(self._deathTokens-1)

   def nextHintTokenValue(self):
      return hintTokenValue

   def score(self):
      score = 0
      for suit in SUITS:
         suitProgress = self._progress[suit]
         score += progressValues[suitProgress]

      score += (self._hintTokens -InitialHintTokens) * hintTokenValue
      score += self.getDeathTokenValue(self._deathTokens)

      # Scoring for unplayed cards. Needs A/B Testing.
      for player in self._players:
         for cardFact in player.hand():
            if cardFact.shouldPlay():
               score += 3
            elif cardFact.shouldBurn():
               score += 1

      return score

