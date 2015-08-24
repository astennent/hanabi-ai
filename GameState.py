from copy import deepcopy

class GameState:
   def __init__(self, game):
      self.players = deepcopy(game._players)
      self.deck = deepcopy(game._deck)
      self.progress = deepcopy(game._progress)
      self.hintTokens = game.hintTokens()
      self.deathTokens = game.deathTokens()
      self.currentPlayerIndex = game.currentPlayerIndex()