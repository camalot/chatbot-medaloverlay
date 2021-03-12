using System;
using System.Collections.Generic;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;

namespace MedalHotkeyListener {
	static class Program {
		/// <summary>
		/// The main entry point for the application.
		/// </summary>
		static void Main ( string[] args ) {
			var arguments = new Arguments ( args );

			if ( arguments.ContainsKey ( "console", "c" ) ) {
				var ls = new ListenerServer ( );
				ls.Start ( );
				Console.WriteLine ( "PRESS {ENTER} TO EXIT..." );
				Console.ReadLine ( );

				ls.Stop ( );

			} else {
				ServiceBase[] ServicesToRun;
				ServicesToRun = new ServiceBase[]
				{
					new MedalHotKeyListenerService()
				};
				ServiceBase.Run ( ServicesToRun );
			}
		}
	}
}
