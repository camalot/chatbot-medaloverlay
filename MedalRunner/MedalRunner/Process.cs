using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedalRunner {
	public class Process {

		public string Stop(string name) {
			var output = new StringBuilder ( );
			foreach ( var process in System.Diagnostics.Process.GetProcessesByName ( name ) ) {
				Console.WriteLine ( $"{process.ProcessName} : {process.Id}" );
				output.AppendLine ( $"{process.ProcessName} : {process.Id}" );
				process.Kill ( );
			}
			return output.ToString();
		}
	}
}
