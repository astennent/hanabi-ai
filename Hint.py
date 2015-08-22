class Hint:
   def __init__(self, isNumber, value):
      self._isNumber = isNumber
      self._value = value

   def __str__(self):
      return str.format("#{}", self._value)

   def __unicode__(self):
      return str(self)

   def isNumber(self):
      return self._isNumber

   def value(self):
      return self._value

   def appliesToCard(self, card):
      if self._isNumber:
         return card.number() == self._value
      else:
         return card.suit() == self._value

   def appliesToNumberOrSuit(self, number, suit):
      return self._value == number or self._value == suit
