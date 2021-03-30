using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedalRunner {
	public class Logger {
		private enum LogLevel {
			DEBUG,
			INFO,
			WARNING,
			ERROR,
			FATAL
		}

		public Logger ( string logFile ) {
			LogFile = logFile;
			var parent = Path.GetDirectoryName ( LogFile );
			if(!Directory.Exists(parent)) {
				Directory.CreateDirectory ( parent );
			}
		}

		public string LogFile { get; set; }
		private void Write ( LogLevel level, string scriptName, string message ) {
			using (var sw = new StreamWriter(LogFile, true, Encoding.UTF8)) {
				var time = DateTime.Now;
				sw.WriteLine ( $"[{time.ToString ( "MM/dd/yyyy HH:mm:ss" )}]\t[{scriptName.ToUpper ( )}]\t[{level.ToString ( )}]\t{message}" );
			}
		}

		public void Debug(string scriptName, string message ) {
			Write ( LogLevel.DEBUG, scriptName, message );
		}
		public void Info ( string scriptName, string message ) {
			Write ( LogLevel.INFO, scriptName, message );
		}
		public void Warning ( string scriptName, string message ) {
			Write ( LogLevel.WARNING, scriptName, message );
		}
		public void Error ( string scriptName, string message ) {
			Write ( LogLevel.ERROR, scriptName, message );
		}
		public void Fatal ( string scriptName, string message ) {
			Write ( LogLevel.FATAL, scriptName, message );
		}
	}
}
