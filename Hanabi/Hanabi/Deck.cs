using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Hanabi
{
   public class Deck : Versioned
   {
      private readonly int[] cardCounts = {3, 2, 2, 2, 1};
      private static readonly Random Rng = new Random(20);

      private readonly Card[] cards;
      private int currentCardIndex;

      public Deck(IVersionSource versionSource)
      {
         VersionSource = versionSource;
         var cardList = new List<Card>();
         foreach (var suit in Card.GetSuits())
         {
            foreach (var number in Card.GetNumbers())
            {
               for (var i = 0 ; i < cardCounts[number-1] ; i++)
               {
                  cardList.Add(new Card(suit, number, versionSource));
               }
            }
         }
         cards = cardList.ToArray();
         Shuffle(cards);
      }

      public static void Shuffle(Card[] list)
      {
         var n = list.Length;
         while (n > 1)
         {
            n--;
            var k = Rng.Next(n + 1);
            var value = list[k];
            list[k] = list[n];
            list[n] = value;
         }
      }

      public Card Draw()
      {
         var nextCard = cards[currentCardIndex++];
         PushUndoable(delegate()
         {
            currentCardIndex--;
         });
         return nextCard;
      }

      public IEnumerable<Card> GetRemainingCards()
      {
         var output = new Card[cards.Length-currentCardIndex];
         Array.Copy(cards, currentCardIndex, output, 0, output.Length);
         return output;
      }

      public int CountRemainingCards()
      {
         return cards.Length - currentCardIndex;
      }

      public void PrintCardsInOrder()
      {
         var output = "[\n";
         for (var i = 0 ; i < cards.Length ; i++)
         {
            output += string.Format(" {0} {1}", cards[i], (i%7 == 6) ? "\n" : "");
         }
         Console.WriteLine(output + "]");
      }

   }
}
