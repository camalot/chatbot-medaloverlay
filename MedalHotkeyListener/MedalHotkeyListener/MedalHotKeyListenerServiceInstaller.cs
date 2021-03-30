using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Configuration.Install;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;

namespace MedalHotkeyListener {
	[RunInstaller(true)]
	public class MedalHotKeyListenerServiceInstaller : Installer{
		public MedalHotKeyListenerServiceInstaller ( ) {
			var installer = new ServiceInstaller ( );
			installer.ServiceName = "MedalHotkeyListener";
			installer.DisplayName = "Medal Hotkey Listener";

			var procInstaller = new ServiceProcessInstaller ( );
			procInstaller.Account = ServiceAccount.LocalSystem;
			installer.StartType = ServiceStartMode.Automatic;
			installer.Description = "A medal hotkey listener for the medaloverlay script for streamlabs chatbot.";
			Installers.Add ( installer );
			Installers.Add ( procInstaller );
		}
		public override void Install ( IDictionary stateSaver ) {
			base.Install ( stateSaver );
		}
	}
}
