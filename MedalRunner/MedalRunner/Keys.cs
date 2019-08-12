using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Threading;

namespace MedalRunner {
	public class Keys {
		public static void SendKeys(string keys) {
			System.Windows.Forms.SendKeys.SendWait ( keys );
		}
	}
}
