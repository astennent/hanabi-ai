from copy import deepcopy

class GameState:
   def __init__(self, game):
      self._game = game
      self.deck = deepcopy(game._deck)
      self.progress = deepcopy(game._progress)
      self.hintTokens = game.hintTokens()
      self.deathTokens = game.deathTokens()
      self.currentPlayerIndex = game.currentPlayerIndex()
      self.cardFactStates = dict([])
      for player in game._players:
         cardFactStates = []
         for cardFact in player._hand:
            cardFactStates.append(CardFactState(cardFact))
         self.cardFactStates[player] = cardFactStates

   def restoreGame(self):
      self._game._deck = self.deck
      self._game._progress = self.progress
      self._game._hintTokens = self.hintTokens
      self._game._deathTokens = self.deathTokens
      self._game._currentPlayerIndex = self.currentPlayerIndex
      for player in self.cardFactStates.keys():
         cardFactStates = self.cardFactStates[player]
         cardFacts = []
         for cardFactState in cardFactStates:
            cardFacts.append(cardFactState.restore())
         player._hand = cardFacts

class CardFactState():
   def __init__(self, cardFact):
      self._cardFact = cardFact
      self.possibilities = deepcopy(cardFact._possibilities)
      self.shouldBurn = deepcopy(cardFact._shouldBurn)
      self.shouldPlay = deepcopy(cardFact._shouldPlay)

   def restore(self):
      self._cardFact._possibilities = self.possibilities
      self._cardFact._shouldBurn = self.shouldBurn
      self._cardFact._shouldPlay = self.shouldPlay
      return self._cardFact

