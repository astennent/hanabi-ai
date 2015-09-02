using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net.Configuration;
using System.Text;
using System.Threading.Tasks;
using System.Xml;

namespace Hanabi
{
   public class Game : Versioned, IVersionSource
   {
      public static int InitialHintTokens = 8;
      public static int InitialDeathTokens = 3;

      readonly int[] hintTokenValues = { 15, 25, 38, 50, 50, 50, 50, 50, 50 };
      readonly int[] progressValues = { 0, 60, 110, 145, 170, 190 };
      readonly int[] deathTokenValues = { -1000, -200, -50, 0 };

      private int currentPlayerIndex;
      public Deck Deck { get; private set; }
      public List<Player> Players { get; private set; }

      public int HintTokens { get; private set; }
      public int DeathTokens { get; private set; }

      private int blockedSuitCount = 0;
      private int badBurnCount = 0;

      public int TurnsRemaining { get; private set; }

      private int currentVersion;
      public Dictionary<Card.Suit, int> Progress { get; private set; }

      public Game(int numPlayers, int handSize)
      {
         VersionSource = this;
         Deck = new Deck(this);
         HintTokens = InitialHintTokens;
         DeathTokens = InitialDeathTokens;
         TurnsRemaining = Deck.CountRemainingCards();

         Progress = new Dictionary<Card.Suit, int>();
         foreach (var suit in Card.GetSuits())
         {
            Progress[suit] = 0;
         }

         Players = new List<Player>();
         for (int id = 0; id < numPlayers; id++)
         {
            var player = new Player(this, id);
            for (int drawIndex = 0; drawIndex < handSize; drawIndex++)
            {
               DrawCardFor(player);
            }
            Players.Add(player);
            Console.WriteLine(player);
         }

         IncrementVersion();
      }

      public void RunToCompletion()
      {
         while (Deck.CountRemainingCards() > 0)
         {
            if (DeathTokens == 0) break;
            PlayTurn();
         }

         TurnsRemaining = Players.Count;

         for (var i = 0; i < Players.Count; i++)
         {
            if (DeathTokens == 0) break;
            var currentPlayer = GetCurrentPlayer();
            PlayTurn();
            currentPlayer.WillPlayAgain = false;
            TurnsRemaining--;
         }
      }

      public void PlayTurn()
      {
         var result = Simulator.CalculateBestAction(this);
         var score = result.Item1;
         var move = result.Item2;
         Console.WriteLine("--------");
         Console.WriteLine("{0} will do: {1}. Score at depth: {2}", GetCurrentPlayer(), move, score);
         PrintProgress();
         HandleMove(move);
         Console.WriteLine("Score after play: {0}. Hint tokens: {1}. Death Tokens: {2}", GetScore(), HintTokens, DeathTokens);
      }

      public void IncrementPlayer()
      {
         var oldPlayerIndex = currentPlayerIndex;
         currentPlayerIndex = (currentPlayerIndex + 1) % Players.Count;
         PushUndoable(delegate()
         {
            currentPlayerIndex = oldPlayerIndex;
         });
      }

      public int HandleMove(Move move)
      {
         var version = GetVersion();
         IncrementVersion();

         if (move is Hint)
         {
            HandleHint((Hint)move);
         }
         else
         {
            var play = (Play) move;
            var player = GetCurrentPlayer();
            var card = play.Card;

            player.DropCard(card);

            if (play is Burn)
            {
               HandleBurn((Burn) play);
            }
            else
            {
               HandleGain((Gain) play);
            }

            DrawCardFor(player);
         }

         IncrementPlayer();
         return version;
      }

      public void HandleHint(Hint hint)
      {
         SpendHintToken();
         hint.TargetPlayer.ProcessHint(hint);
      }

      private void SpendHintToken()
      {
         HintTokens--;
         PushUndoable(delegate()
         {
            HintTokens++;
         });
      }

      private void SpendDeathToken()
      {
         DeathTokens--;
         PushUndoable(delegate()
         {
            DeathTokens++;
         });
      }

      public bool CanBurn()
      {
         bool atMaxHints = (HintTokens >= InitialHintTokens);
         return !atMaxHints && !IsInEndgame();
      }

      public bool CanHint()
      {
         var hasHintTokens = (HintTokens > 0);
         return hasHintTokens && !IsInEndgame();
      }

      public bool IsReadyForGain(Card card)
      {
         return Progress[card.GetSuit()] == card.GetNumber() - 1;
      }

      public bool HasProgressedPast(Card card)
      {
         return Progress[card.GetSuit()] >= card.GetNumber();
      }

      public void HandleBurn(Burn burn)
      {
         HintTokens++;
         PushUndoable(delegate()
         {
            HintTokens--;
         });

         CheckIfBurnBlocksSuit(burn);
      }

      public void CheckIfBurnBlocksSuit(Burn burn)
      {
         var suit = burn.Card.GetSuit();
         var number = burn.Card.GetNumber();
         var currentProgress = Progress[suit];
         if (currentProgress >= number)
         {
            return;
         }
         
         if (currentProgress == number - 1)
         {
            badBurnCount++;
            PushUndoable(delegate()
            {
               badBurnCount--;
            });
         }

         var unplayedCards = Deck.GetRemainingCards();
         unplayedCards = Players.Aggregate(unplayedCards, (current, player) => current.Concat(player.GetHand()));

         if (unplayedCards.Any(card => card.GetSuit() == suit && card.GetNumber() == number))
         {
            return;
         }

         blockedSuitCount++;
         PushUndoable(delegate()
         {
            blockedSuitCount--;
         });

      }

      public void HandleGain(Gain gain)
      {
         var card = gain.Card;
         var suit = card.GetSuit();
         if (Progress[suit] == card.GetNumber() - 1)
         {
            IncrementProgress(suit);
         }
         else
         {
            SpendDeathToken();
         }
      }

      private void IncrementProgress(Card.Suit suit)
      {
         Progress[suit]++;
         PushUndoable(delegate()
         {
            Progress[suit]--;
         });
      }

      private void DrawCardFor(Player player)
      {
         if (Deck.CountRemainingCards() > 0)
         {
            player.ReceiveCard(Deck.Draw());
         }
      }

      public Player GetCurrentPlayer()
      {
         return Players[currentPlayerIndex];
      }

      public int GetScore()
      {
         return ScoreDeathTokens() + ScoreHintTokens() + ScoreProgress() + ScorePlayers() + ScoreBlockedSuits();;
      }

      private int ScoreBlockedSuits()
      {
         return -50*blockedSuitCount - 20*badBurnCount;
      }

      private int ScoreHintTokens()
      {
         return hintTokenValues[HintTokens];
      }

      private int ScoreDeathTokens()
      {
         return deathTokenValues[DeathTokens];
      }

      private int ScoreProgress()
      {
         return Card.GetSuits().Sum(suit => progressValues[Progress[suit]]);
      }

      private int ScorePlayers()
      {
         var score = 0;
         const int readyForGain = 6;
         const int notReadyForGain = -5;
         const int readyForBurn = 3;
         const int notReadyForBurn = -2;
         foreach (var card in Players.SelectMany(player => player.GetHand()))
         {
            if (card.ShouldGain)
            {
               if (Progress[card.GetSuit()] == card.GetNumber() - 1)
               {
                  score += readyForGain;
               }
               else
               {
                  score += notReadyForGain;
               }
            }
            if (card.ShouldBurn)
            {
               if (Progress[card.GetSuit()] >= card.GetNumber())
               {
                  score += readyForBurn;
               }
               else
               {
                  score += notReadyForBurn;
               }
            }
         }
         return score;
      }

      public new void RevertToVersion(int version)
      {
         base.RevertToVersion(version);
         Deck.RevertToVersion(version);
         foreach (var player in Players)
         {
            player.RevertToVersion(version);
         }
         currentVersion = version;
      }

      public void IncrementVersion()
      {
         currentVersion++;
      }

      public int GetVersion()
      {
         return currentVersion;
      }

      public void PrintProgress()
      {
         var output = "{";
         foreach (var suit in Card.GetSuits())
         {
            output += string.Format(" {0}:{1} ", suit, Progress[suit]);
         }
         Console.WriteLine(output + "}");
      }

      public int GetNextDeathTokenValue()
      {
         return deathTokenValues[DeathTokens - 1];
      }

      public int GetNextHintTokenValue()
      {
         return hintTokenValues[HintTokens + 1];
      }

      public int FinalScore()
      {
         return Progress.Values.Sum();
      }

      public bool IsInEndgame()
      {
         return TurnsRemaining <= Players.Count;
      }
   }
}
