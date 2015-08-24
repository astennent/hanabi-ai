from copy import deepcopy

class GameState:
   def __init__(self, game):
      self.hands = []
      for player in game._players:
         self.hands.append(player._hand)

      self.deck = deepcopy(game._deck)
      self.progress = deepcopy(game._progress)
      self.hintTokens = game.hintTokens()
      self.deathTokens = game.deathTokens()
      self.currentPlayerIndex = game.currentPlayerIndex()