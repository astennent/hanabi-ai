using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace Hanabi
{
   public class Card : Versioned
   {
      public enum Suit { R, W, Y, G, B };
      private static readonly int[] Numbers = { 1, 2, 3, 4, 5 };
      
      private readonly Suit suit;
      private readonly int number;

      private readonly List<Suit> disprovenSuits = new List<Suit>();
      private readonly List<int> disprovenNumbers = new List<int>();

      private bool shouldBurn;
      public bool ShouldBurn
      {
         get { return shouldBurn; }
         set
         {
            var oldValue = shouldBurn;
            PushUndoable(delegate()
            {
               shouldBurn = oldValue;
            });
            shouldBurn = value;
         }
      }

      private bool shouldGain;
      public bool ShouldGain
      {
         get { return shouldGain; }
         set
         {
            var oldValue = shouldGain;
            PushUndoable(delegate()
            {
               shouldGain = oldValue;
            });
            shouldGain = value;
         }
      }

      public static IEnumerable<Suit> GetSuits()
      {
         return Enum.GetValues(typeof(Suit)).Cast<Suit>();
      }

      public static IEnumerable<int> GetNumbers()
      {
         return Numbers;
      }

      public Card(Suit suit, int number, IVersionSource versionSource)
      {
         this.suit = suit;
         this.number = number;
         this.VersionSource = versionSource;
      }

      public Suit GetSuit()
      {
         return suit;
      }

      public int GetNumber()
      {
         return number;
      }

      public bool IsFullyRevealed()
      {
         return IsNumberRevealed() && IsSuitRevealed();
      }

      public bool IsNumberRevealed()
      {
         return disprovenNumbers.Count() == GetNumbers().Count() - 1;
      }

      public bool IsSuitRevealed()
      {
         return disprovenSuits.Count() == GetSuits().Count() - 1;
      }

      public bool ProcessHint(Hint hint)
      {
         if (hint is NumberHint)
         {
            return ProcessNumberHint((NumberHint) hint);
         }
         return ProcessSuitHint((SuitHint) hint);
      }

      private bool ProcessNumberHint(NumberHint hint)
      {
         var hintApplies = (number == hint.Number);
         foreach (var item in 
            from item in GetNumbers() 
            let isHintedNumber = (item == hint.Number) 
            where hintApplies != isHintedNumber && !disprovenNumbers.Contains(item)
            select item)
         {
            disprovenNumbers.Add(item);
            PushUndoable(delegate()
            {
               disprovenNumbers.Remove(item);
            });
         }
         return hintApplies;
      }

      private bool ProcessSuitHint(SuitHint hint)
      {
         var hintApplies = (suit == hint.Suit);
         foreach (var item in 
            from item in GetSuits() 
            let isHintedSuit = (item == hint.Suit) 
            where hintApplies != isHintedSuit && !disprovenSuits.Contains(item)
            select item)
         {
            disprovenSuits.Add(item);
            PushUndoable(delegate()
            {
               disprovenSuits.Remove(item);
            });
         }
         return hintApplies;
      }

      public double CalculateExpectedNumberGivenRemainingCards(IEnumerable<Card> remainingCards, Dictionary<Suit, int> progress)
      {
         var sum = 0;
         var count = 0;
         foreach (var card in GetNonDisprovenCards(remainingCards)
            .Where(card => progress[card.GetSuit()] == card.GetNumber() - 1))
         {
            count++;
            sum += card.GetNumber();
         }

         if (count == 0)
         {
            return 0; // indicates that this will not be playable.
         }
         return (1.0*sum)/count;
      }

      public bool VerifyBurnable(IEnumerable<Card> remainingCards, Dictionary<Suit, int> progress)
      {
         return GetNonDisprovenCards(remainingCards)
            .Any(card => progress[card.GetSuit()] >= card.GetNumber());
      }

      public IEnumerable<Card> GetNonDisprovenCards(IEnumerable<Card> remainingCards)
      {
         return from card in remainingCards
                let disqualified = disprovenNumbers.Contains(card.GetNumber()) || disprovenSuits.Contains(card.GetSuit()) 
                where !disqualified
                select card;
      }

      public Tuple<double, double> CalculateProbabilityOfSafePlays(IEnumerable<Card> remainingCards, Dictionary<Suit, int> progress)
      {
         var nonDisprovenCards = GetNonDisprovenCards(remainingCards);

         var gainCount = 0.0;
         var burnCount = 0.0;

         if (!nonDisprovenCards.Any())
         {
            Console.WriteLine("foo");
         }

         foreach (var card in nonDisprovenCards)
         {
            var currentProgress = progress[card.GetSuit()];
            if (currentProgress == card.GetNumber() - 1)
            {
               gainCount++;
            }
            else if (currentProgress >= card.GetNumber())
            {
               burnCount++;
            }
         }
         var total = nonDisprovenCards.Count();
         return new Tuple<double, double>(gainCount/total, burnCount/total);
      }

      public override string ToString()
      {
         var isSuitRevealed = (disprovenSuits.Count() == GetSuits().Count() - 1);
         var isNumberRevealed = (disprovenNumbers.Count() == GetNumbers().Count() - 1);
         var delimiter = (isSuitRevealed && isNumberRevealed) ? "*"
                       : (isSuitRevealed) ? "$"
                       : (isNumberRevealed) ? "#"
                       : "-";
         return string.Format("{0}{1}:{2}{3}", delimiter, suit, number, delimiter);
      }
   }
}
