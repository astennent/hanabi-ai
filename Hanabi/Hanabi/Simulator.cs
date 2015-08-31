using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Schema;

namespace Hanabi
{
   public class Simulator
   {
      private const int MaxDepth = 4;

      public static Tuple<int, Move> CalculateBestAction(Game game)
      {
         // This is weird because it's prepared to be converted to Multithreading.
         var bestScore = int.MinValue;
         Move bestMove = null;

         foreach (var action in game.GetCurrentPlayer().GetPossibleActions())
         {
            var simulation = new Simulation(game);
            var score = simulation.Simulate(action, 0);
            if (score > bestScore)
            {
               bestScore = score;
               bestMove = action;
            }
         }

         return new Tuple<int, Move>(bestScore, bestMove);
      }

      class Simulation
      {
         private readonly Player initialPlayer;
         private readonly Game game;

         public Simulation(Game game)
         {
            this.game = game;
            initialPlayer = game.GetCurrentPlayer();
         }

         public int Simulate(Move move, int depth)
         {
            var version = game.HandleMove(move);
            var score = (depth < MaxDepth)
               ? Simulate(depth + 1) 
               : game.GetScore();
            game.RevertToVersion(version);
            return score;
         }

         private int Simulate(int depth)
         {
            var bestScore = Int32.MinValue;

            foreach (var action in game.GetCurrentPlayer().GetPossibleActions())
            {
               var score = Simulate(action, depth);
               if (score > bestScore)
               {
                  bestScore = score;
               }
            }

            return bestScore;
         }
      }
   }


}
