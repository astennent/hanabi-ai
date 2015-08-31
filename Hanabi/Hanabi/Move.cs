using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Hanabi
{
   public interface Move
   {
   }

   public abstract class Hint : Move
   {
      public Player TargetPlayer { get; protected set; }
   }

   class NumberHint : Hint
   {
      public int Number { get; private set; }

      public NumberHint(Player targetPlayer, int number)
      {
         TargetPlayer = targetPlayer;
         Number = number;
      }

      public override string ToString()
      {
         return string.Format("<NumberHint:{0} for {1}>", Number, TargetPlayer);
      }
   }

   class SuitHint : Hint
   {
      public Card.Suit Suit { get; private set; }

      public SuitHint(Player targetPlayer, Card.Suit suit)
      {
         TargetPlayer = targetPlayer;
         Suit = suit;
      }

      public override string ToString()
      {
         return string.Format("<SuitHint:{0} for {1}>", Suit, TargetPlayer);
      }
   }

   public abstract class Play : Move
   {
      public Card Card { get; protected set; }

      protected Play(Card card)
      {
         Card = card;
      }
   }

   public class Gain : Play
   {
      public Gain(Card card) 
         : base(card)
      {
      }

      public override string ToString()
      {
         return string.Format("<Gain:{0}>", Card);
      }
   }

   public class Burn : Play
   {
      public Burn(Card card)
         : base(card)
      {
      }

      public override string ToString()
      {
         return string.Format("<Burn:{0}>", Card);
      }
   }


}
