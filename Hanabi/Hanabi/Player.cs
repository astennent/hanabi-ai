using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Hanabi
{
   public class Player : Versioned
   {
      private readonly Game game;
      private readonly int id;
      private readonly List<Card> cards = new List<Card>();

      private List<Hint> validHintCache;

      public bool WillPlayAgain { get; set; }

      public Player(Game game, int id)
      {
         this.game = game;
         this.id = id;
         VersionSource = game;
         validHintCache = new List<Hint>();
         WillPlayAgain = true;
      }

      public void ReceiveCard(Card card)
      {
         cards.Add(card);
         validHintCache.Clear();
         PushUndoable(delegate()
         {
            cards.Remove(card);
            validHintCache.Clear();
         });
      }

      public void DropCard(Card card)
      {
         cards.Remove(card);
         validHintCache.Clear();
         PushUndoable(delegate()
         {
            cards.Add(card);
            validHintCache.Clear();
         });
      }

      public IEnumerable<Card> GetHand()
      {
         return cards;
      }

      public IEnumerable<Move> GetPossibleActions(Player initialPlayer)
      {
         var actions = new List<Move>();
         
         AddGainToPossibleActions(actions);

         if (game.CanBurn()) 
            AddBurnToPossibleActions(actions);

         if (game.CanHint())
            AddOtherPlayersHintsToActions(actions, initialPlayer);

         actions.Add(Yolo());
         
         return actions;
      }

      public void ProcessHint(Hint hint)
      {
         var relevantCards = cards.Where(card => card.ProcessHint(hint));
         if (hint is NumberHint)
         {
            ContemplateNumberHint( ((NumberHint) hint).Number, relevantCards);
         }
         else
         {
            ContemplateSuitHint( ((SuitHint) hint).Suit, relevantCards);
         }
      }

      private void ContemplateNumberHint(int number, IEnumerable<Card> relevantCards)
      {
         var playableSlots = 0;
         var futureSlots = 0;
         foreach (var currentProgress in Card.GetSuits().Select(suit => game.Progress[suit]))
         {
            if (currentProgress == number - 1)
            {
               playableSlots += 1;
            }
            else if (currentProgress < number)
            {
               futureSlots += 1;
            }
         }

         if (playableSlots >= relevantCards.Count())
         {
            foreach (var card in relevantCards)
            {
               card.ShouldGain = true;
            }
         }
         else if (futureSlots <= relevantCards.Count())
         {
            foreach (var card in relevantCards)
            {
               card.ShouldBurn = true;
            }
         }
      }

      private void ContemplateSuitHint(Card.Suit suit, IEnumerable<Card> relevantCards)
      {    
         var remainingCardsForSuit = Card.GetNumbers().Count() - game.Progress[suit];
         if (remainingCardsForSuit < relevantCards.Count())
         {
            foreach (var card in relevantCards)
            {
               card.ShouldBurn = true;
            }
         }
         else if (relevantCards.Count() == 1)
         {
            relevantCards.First().ShouldGain = true;
         }
      }

      public void AddBurnToPossibleActions(List<Move> actions)
      {
         var knownRemainingCards = KnownRemainingCards();
         foreach (var card in cards
            .Where(card => card.ShouldBurn)
            .Where(card => card.VerifyBurnable(knownRemainingCards, game.Progress)))
         {
            actions.Add(new Burn(card));
            return;
         }
      }

      public void AddGainToPossibleActions(List<Move> actions)
      {
         var lowestExpectedNumber = double.MaxValue;
         Card bestGain = null;
         var knownRemainingCards = KnownRemainingCards();

         foreach (var card in cards)
         {
            var expectedNumber = 0.0;
            var isSafe = false;

            if (card.IsFullyRevealed())
            {
               expectedNumber = card.GetNumber();
               isSafe = true;
            }
            else if (card.ShouldGain)
            {
               expectedNumber = card.CalculateExpectedNumberGivenRemainingCards(knownRemainingCards, game.Progress);
               if (expectedNumber > 0)
               {
                  isSafe = true;
               }
            }

            if (isSafe && expectedNumber < lowestExpectedNumber)
            {
               lowestExpectedNumber = expectedNumber;
               bestGain = card;
            }
         }
         if (bestGain != null)
         {
            actions.Add(new Gain(bestGain));
         }
      }

      private IEnumerable<Card> KnownRemainingCards()
      {
         var myCards = GetHand();
         var knownRemainingCards = game.Deck.GetRemainingCards().Concat(myCards);
         return knownRemainingCards;
      }

      public void AddOtherPlayersHintsToActions(List<Move> actions, Player initialPlayer)
      {
         foreach (var player in game.Players.Where(player => player != this && player != initialPlayer && player.WillPlayAgain))
         {
            player.AddHintsToPossibleActions(actions);
         }
      }

      public void AddHintsToPossibleActions(List<Move> actions)
      {
         if (validHintCache.Count == 0)
         {
            var suits = new HashSet<Card.Suit>();
            var numbers = new HashSet<int>();

            foreach (var card in cards)
            {
               suits.Add(card.GetSuit());
               numbers.Add(card.GetNumber());
            }

            foreach (var suit in suits)
            {
               validHintCache.Add(new SuitHint(this, suit));
            }
            foreach (var number in numbers)
            {
               validHintCache.Add(new NumberHint(this, number));
            }
         }

         actions.AddRange(validHintCache);
      }

      public Move Yolo()
      {
         var canBurn = game.CanBurn();
         var knownRemainingCards = KnownRemainingCards();
         const int goodGainValue = 30;
         var badGainValue = game.GetNextDeathTokenValue();
         var goodBurnValue = canBurn ? game.GetNextHintTokenValue() : 0;
         const int badBurnValue = -10;

         var bestUtility = double.MinValue;
         Move bestMove = null;

         foreach (var card in cards)
         {
            var probabilities = card.CalculateProbabilityOfSafePlays(knownRemainingCards, game.Progress);
            var safeGainProbability = probabilities.Item1;
            var safeBurnProbability = probabilities.Item2;

            var gainUtility = (goodGainValue * safeGainProbability) + (badGainValue * (1 - safeGainProbability));
            var burnUtility = canBurn ? (goodBurnValue * safeBurnProbability) + (badBurnValue * (1 - safeGainProbability)) : int.MinValue;

            if (gainUtility > bestUtility)
            {
               bestMove = new Gain(card);
               bestUtility = gainUtility;
            }

            if (burnUtility > bestUtility)
            {
               bestMove = new Burn(card);
               bestUtility = burnUtility;
            }
         }

         return bestMove;
      }

      public new void RevertToVersion(int version)
      {
         base.RevertToVersion(version);
         foreach (var card in cards)
         {
            card.RevertToVersion(version);
         }
      }

      public override string ToString()
      {
         var output = id + "[";
         foreach (var card in cards)
         {
            output += string.Format("{0}", card);
         }
         output += "]";
         return output;
      }
   }
}
