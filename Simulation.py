from GameState import *

class Simulation:
   def __init__(self, game, initialPlayer):
      self._game = game
      self.initialPlayer = initialPlayer
      self._depth = 0

   def isSimulating(self):
      return self._depth == 0

   def simulate(self, actions):

      bestScore = -9999
      bestAction = 0
      self._depth += 1

      MAX_PRINT_DEPTH = 0
      for action in actions:
         if self._depth <= MAX_PRINT_DEPTH:   print str.format("{}action: {}", "  " * self._depth, action)
         score = self.executeTopAction(action)
         if self._depth <= MAX_PRINT_DEPTH:   print str.format("{}action: {}, score: {}", "  " * self._depth, action, score)
         if score > bestScore:
            bestScore = score
            bestAction = action

      self._depth -= 1
      if self._depth == 0:   print str.format("{}bestScore: {}, action: {}", "  " * self._depth, bestScore, bestAction)

      return bestAction, bestScore

   def executeTopAction(self, action):
      game = self._game
      gameState = GameState(game)
      game.processAction(action, True)

      atMaxDepth = (self._depth >= game._maxSimulationDepth)
      if not atMaxDepth:
         game.iteratePlayerIndex()
         score = game.playSingleTurn(self)
      else:
         score = game.score()

      gameState.restoreGame()
      return score

