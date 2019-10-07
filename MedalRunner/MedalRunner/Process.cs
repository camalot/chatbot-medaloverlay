using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedalRunner {
	public class Process {

		public string Stop ( string name ) {
			var output = new StringBuilder ( );
			var procName = System.IO.Path.GetFileNameWithoutExtension ( name );
			foreach ( var process in System.Diagnostics.Process.GetProcessesByName ( procName ) ) {
				Console.WriteLine ( $"{process.ProcessName} : {process.Id}" );
				output.AppendLine ( $"{process.ProcessName} : {process.Id}" );
				process.Kill ( );
			}
			return output.ToString ( );
		}

		public int StartAndWait ( string command, string arguments, bool showWindow = true, string workingDirectory = null ) {
			var psi = new System.Diagnostics.ProcessStartInfo ( command, arguments );
			if ( !string.IsNullOrWhiteSpace ( workingDirectory ) && System.IO.Directory.Exists ( workingDirectory ) ) {
				psi.WorkingDirectory = workingDirectory;
			}
			psi.WindowStyle = showWindow ? System.Diagnostics.ProcessWindowStyle.Normal : System.Diagnostics.ProcessWindowStyle.Hidden;
			var proc = new System.Diagnostics.Process ( );
			proc.StartInfo = psi;
			proc.Start ( );
			proc.WaitForExit ( );
			return proc.ExitCode;
		}

		public void StartUnattached ( string command, string arguments, bool showWindow = true, string workingDirectory = null ) {
			var psi = new System.Diagnostics.ProcessStartInfo ( command, arguments );
			if ( !string.IsNullOrWhiteSpace ( workingDirectory ) && System.IO.Directory.Exists ( workingDirectory ) ) {
				psi.WorkingDirectory = workingDirectory;
			}
			psi.WindowStyle = showWindow ? System.Diagnostics.ProcessWindowStyle.Normal : System.Diagnostics.ProcessWindowStyle.Hidden;
			var proc = new System.Diagnostics.Process ( );
			proc.StartInfo = psi;
			proc.Start ( );
		}

		public void Start ( string command, string arguments, bool wait = false, bool showWindow = true ) {
			if ( wait ) {
				StartAndWait ( command, arguments, showWindow );
			} else {
				StartUnattached ( command, arguments, showWindow );
			}
		}
	}
}
