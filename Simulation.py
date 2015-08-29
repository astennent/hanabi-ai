from GameState import *

class Simulation:
   def __init__(self, game, initialPlayer):
      self._game = game
      self._initialPlayer = initialPlayer
      self._depth = 0

   def initialPlayer(self):
      return self._initialPlayer

   def isSimulating(self):
      return self._depth > 0

   def simulate(self, actions):
      bestScore = -9999
      bestAction = 0
      self._depth += 1

      for action in actions:
         score = self.executeTopAction(action)
         if score > bestScore:
            bestScore = score
            bestAction = action

      self._depth -= 1

      return bestAction, bestScore

   def executeTopAction(self, action):
      game = self._game
      gameState = GameState(game)
      game.processAction(action, True)

      atMaxDepth = (self._depth >= game._maxSimulationDepth)
      if game.deathTokens() == 0:
         score = -1000
      elif not atMaxDepth:
         game.iteratePlayerIndex()
         score = game.simulateSingleTurn(self)
      else:
         score = game.score(self.initialPlayer)

      gameState.restoreGame()
      return score

