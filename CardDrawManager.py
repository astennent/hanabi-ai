from CardFact import *

class CardDrawManager:
   def __init__(self, game):
      self._game = game

   def handleDrawFor(self, player):
      if not self._game.deck().hasNext():
         return
         
      possibilities = self.getKnownRemainingCardsForPlayer(player)
      
      card = self._game.deck().draw()

      for otherPlayer in self._game.players():
         if otherPlayer is not player:
            otherPlayer.removePossibility(card)

      cardFact = CardFact(card, possibilities)
      player.receiveCard(cardFact)

   def getKnownRemainingCardsForPlayer(self, player):
      actualRemainingCards = self._game.deck().remainingCards()

      for cardFact in player.hand():
         card = cardFact.card()
         actualRemainingCards[card.suit()][card.number()] += 1

      return actualRemainingCards