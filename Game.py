from Player import *
from Deck import *
from CardDrawManager import *
from GameState import *

InitialDrawCount = 4
InitialHintTokens = 7
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
      self.playSingleTurn(0)

   def playSingleTurn(self, simulationDepth):
      action = self._players[self._currentPlayerIndex].GetActionForTurn(simulationDepth)
      self.processAction(action)

   def processAction(self, action):
      actionName = action.actionName()
      if actionName == "Hint":
         self.processHint(action)
      else:
         self.processBurnOrPlay(action)

   def processHint(self, hint):
      hint.player().receiveHint(hint)
      self._hintTokens -= 1

   def processBurnOrPlay(self, action):
      player = action.player
      card = action.cardFact.card()
      player.dropCard(card)

      if actionName == "Burn":
         self._hintTokens += 1
      else: # Play:
         suit = card.suit()
         number = card.number()
         if self.progress(suit) == number - 1:
            self._progress[suit] = number  # :)
         else:
            self.deathTokens -= 1 # :(

      cardDrawManager.handleDrawFor(player)

   def simulate(self, action, simulationDepth):
      atMaxDepth = (simulationDepth >= self._maxSimulationDepth)
      gameState = GameState(self)
      self.processAction(action)

      if not atMaxDepth:
         self.iteratePlayerIndex()
         self.playSingleTurn(simulationDepth)

      score = self.score()
      self.setState(gameState)
      return score

   def setState(self, state):
      self._players = state.players
      self._deck = state.deck
      self._progress = state.progress
      self._hintTokens = state.hintTokens
      self._deathTokens = state.deathTokens
      self._currentPlayerIndex = state.currentPlayerIndex


   def progress(self, suite):
      return self._progress[suit]

   def currentPlayer(self):
      return self._players[self._currentPlayerIndex]

   def players(self):
      return self._players

   def playersExcept(self, exceptedPlayer):
      players = []
      for player in self._players:
         if player is not exceptedPlayer:
            players.append(player)
      return players

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