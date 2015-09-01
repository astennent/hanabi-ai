using System;

namespace Hanabi
{

   class Program
   {
      private const int NumPlayers = 4;
      private const int HandSize = 4;

      static void Main(string[] args)
      {
         Game game = new Game(NumPlayers, HandSize);
         game.RunToCompletion();
         Console.WriteLine("\n\nDone! Final Score: {0}", game.FinalScore());
         game.PrintProgress();
         Console.WriteLine("Total Move Simulations: {0}, Aborted: {1}", Simulator.SimulationCount, Simulator.AbortedSimCount);
         Console.Write("Original Deck: ");
         game.Deck.PrintCardsInOrder();
         Console.ReadLine(); // Stop to see results.
      }
   }
}
