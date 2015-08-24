from Player import *
from Deck import *
from CardDrawManager import *
from GameState import *

InitialDrawCount = 4
InitialHintTokens = 8
InitialDeathTokens = 3

progressValues = [0, 50, 95, 130, 155, 170]
hintTokenValue = 10
deathTokenValues = [-1000, 10, 15, 20]

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
      #TODO: This should be a loop.
      simulationMetadata = SimulationMetadata(self._players[self._currentPlayerIndex])
      self.playSingleTurn(simulationMetadata)

   def playSingleTurn(self, simulationMetadata):
      action = self._players[self._currentPlayerIndex].GetActionForTurn(simulationMetadata)
      self.processAction(action)

   def processAction(self, action):
      if action.actionName() == "Hint":
         self.processHint(action)
      else:
         self.processBurnOrPlay(action)

   def processHint(self, hint):
      hint.player().receiveHint(hint)
      self._hintTokens -= 1

   def processBurnOrPlay(self, action):
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
            self.deathTokens -= 1 # :(

      self._cardDrawManager.handleDrawFor(player)

   def simulate(self, action, simulationMetadata):
      originalDepth = simulationMetadata.depth
      atMaxDepth = (originalDepth >= self._maxSimulationDepth)
      gameState = GameState(self)
      self.processAction(action)

      if not atMaxDepth:
         self.iteratePlayerIndex()
         self.playSingleTurn(simulationMetadata.increment())

      score = self.score()
      self.setState(gameState)
      simulationMetadata.depth = originalDepth
      return score

   def setState(self, state):
      self._deck = state.deck
      self._progress = state.progress
      self._hintTokens = state.hintTokens
      self._deathTokens = state.deathTokens
      self._currentPlayerIndex = state.currentPlayerIndex
      for i, player in enumerate(self._players):
         player._hand = state.hands[i]


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

   def score(self):
      score = 0
      for suit in SUITS:
         suitProgress = self._progress[suit]
         score += progressValues[suitProgress]

      score += self._hintTokens * hintTokenValue
      score += deathTokenValues[self._deathTokens]

      return score

class SimulationMetadata:
   def __init__(self, initialPlayer):
      self.initialPlayer = initialPlayer
      self.depth = 0

   def increment(self):
      self.depth += 1
      return self