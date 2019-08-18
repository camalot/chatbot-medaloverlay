using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedalRunner.Exceptions {
	public class UnableToLoadReleaseException : Exception {
		public UnableToLoadReleaseException ( ) : base("Unable to load latest release information") {
		}
	}
}
