using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Schema;

namespace Hanabi
{
   public class Simulator
   {
      private const int MaxDepth = 3;
      public static int SimulationCount;
      public static int AbortedSimCount;

      public static Tuple<int, Move> CalculateBestAction(Game game)
      {
         return new Simulation(game).Simulate(0);
      }

      class Simulation
      {
         private readonly Player initialPlayer;
         private readonly Game game;
         private readonly int initialScore;
         private const int MaxLossTolerance = 100;

         public Simulation(Game game)
         {
            this.game = game;//.Copy();
            initialScore = game.GetScore();
            initialPlayer = game.GetCurrentPlayer();
         }

         private int Simulate(Move move, int depth)
         {
            SimulationCount++;
            var version = game.HandleMove(move);
            var updatedScore = game.GetScore();
            if (updatedScore < initialScore - MaxLossTolerance)
            {
               AbortedSimCount++;
               game.RevertToVersion(version);
               return -1;
            }

            var score = (depth < MaxDepth && game.TurnsRemaining > 0)
               ? Simulate(depth + 1).Item1
               : updatedScore;
            game.RevertToVersion(version);
            return score;
         }

         public Tuple<int, Move> Simulate(int depth)
         {
            var bestScore = int.MinValue;
            Move bestMove = null;

            foreach (var action in game.GetCurrentPlayer().GetPossibleActions(initialPlayer))
            {
               var score = Simulate(action, depth);
               if (score > bestScore)
               {
                  bestScore = score;
                  bestMove = action;
               }
            }

            return new Tuple<int, Move>(bestScore, bestMove);
         }
      }
   }


}
