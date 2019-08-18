using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace MedalOverlayUpdater {
	static class Program {
		/// <summary>
		/// The main entry point for the application.
		/// </summary>
		[STAThread]
		static void Main ( string[] args ) {
			Application.EnableVisualStyles ( );
			Application.SetCompatibleTextRenderingDefault ( false );
			var mainForm = new MainForm ( );
			Application.Run ( mainForm );
		}
	}
}
