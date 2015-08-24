class Action:
   def __init__(self, cardFact, player):
      self._cardFact = cardFact
      self._player = player

   def player(self):
      return self._player

   def cardFact(self):
      return self._cardFact


class Burn(Action):
   def actionName(self):
      return "Burn"


class Play(Action):
   def actionName(self):
      return "Play"


class Hint(Action):
   def __init__(self, isNumber, value, player):
      self._isNumber = isNumber
      self._value = value
      self._player = player

   def __str__(self):
      return str.format("#{}", self._value)

   def __unicode__(self):
      return str(self)

   def actionName(self):
      return "Hint"

   def isNumber(self):
      return self._isNumber

   def value(self):
      return self._value

   def player(self):
      return self._player

   def appliesToCard(self, card):
      if self._isNumber:
         return card.number() == self._value
      else:
         return card.suit() == self._value

   def appliesToNumberOrSuit(self, number, suit):
      return self._value == number or self._value == suit