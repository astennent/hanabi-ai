using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Hanabi
{
   public interface IVersionSource
   {
      int GetVersion();
      void IncrementVersion();
   }

   public abstract class Versioned
   {
      private readonly Stack<Undoable> versionStack = new Stack<Undoable>();
      protected IVersionSource VersionSource; // This needs to be set in the constructor of anything that implements this class.

      protected void PushUndoable(Action action)
      {
         versionStack.Push(new Undoable(VersionSource.GetVersion(), action));
      }

      public void RevertToVersion(int version)
      {
         while (versionStack.Count > 0)
         {
            if (versionStack.Peek().Version <= version)
            {
               break;
            }

            versionStack.Pop().Action();
         }
      }
   }

   public class Undoable
   {
      public int Version;
      public Action Action;

      public Undoable(int version, Action action)
      {
         Version = version;
         Action = action;
      }
   }
}
