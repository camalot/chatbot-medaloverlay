using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;

namespace MedalHotkeyListener {
	public partial class MedalHotKeyListenerService : ServiceBase {
		public MedalHotKeyListenerService ( ) {
			InitializeComponent ( );
			Server = new ListenerServer ( );
		}

		private ListenerServer Server { get; set; }

		protected override void OnStart ( string[] args ) {
			Server.Start ( );
		}

		protected override void OnStop ( ) {
			Server.Stop ( );
		}
	}
}
