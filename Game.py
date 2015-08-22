from Player import *
from Deck import *
from CardDrawManager import *

InitialDrawCount = 4
InitialHintTokens = 7
InitialDeathTokens = 3

progressValues = [0, 50, 95, 130, 155, 170]
hintTokenValue = 10
deathTokenValues = [-1000, 10, 15, 20]

class Game():
   def __init__(self, numPlayers):
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
         print len(player.getValidHints())
         player.hand()[0].printPossibilities()
         print "============="

      self._progress = {}
      for suit in SUITS:
         self._progress[suit] = 0

      self._hintTokens = InitialHintTokens
      self._deathTokens = InitialDeathTokens

   def deck(self):
      return self._deck

   def play(self):
      self._players[0].GetActionForTurn()
      #Do Action

   def progress(self, suite):
      return self._progress[suit]

   def currentPlayer(self):
      return self._players[self._currentPlayerIndex]

   def players(self):
      return self._players

   def score(self):
      score = 0
      for suitProgress in self._progress:
         score += progressValues[suitProgress]

      score += self._hintTokens * hintTokenValue
      score += deathTokenValues[self._deathTokens]

      return score
