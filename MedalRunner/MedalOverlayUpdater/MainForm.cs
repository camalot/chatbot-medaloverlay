using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace MedalOverlayUpdater {
	public partial class MainForm : Form {


		// Copy Updater To Temp Directory
		// Create Config File With Data About Chatbot Location
		// Run Updater
		// IF UPDATE:
		//		Close Down Chatbot
		//		Download new Version
		//		Extract Update To Script Directory
		//		Reopen Chatbot
		
		public MainForm ( ) {
			Updater = new MedalRunner.ScriptUpdater ( );
			Updater.BeginUpdateCheck += Updater_BeginUpdateCheck;
			Updater.EndUpdateCheck += Updater_EndUpdateCheck;
			
			this.Version = "1.0.0";
			InitializeComponent ( );
			this.statusLabel.Text = "";
		}

		private void Updater_EndUpdateCheck ( object sender, MedalRunner.ScriptUpdater.UpdateStatusEventArgs e ) {
			if(e.Status.HasUpdate) {
				this.statusLabel.Text = $"Update Available: v{e.Status.LatestVersion}. You are running v{e.Status.UserVersion}";
			} else {
				this.statusLabel.Text = $"You are running the latest version: {e.Status.UserVersion.ToString()}";
			}
		}

		private void Updater_BeginUpdateCheck ( object sender, EventArgs e ) {
			this.statusLabel.Text = "Checking for Update...";
		}

		public MedalRunner.ScriptUpdater Updater { get; set; }

		public string Version { get; set; }

		private async void MainForm_Load ( object sender, EventArgs e ) {
			Version = await Updater.GetScriptVersion ( );
			await Updater.CheckUpdateStatus ( Version );
		}
	}
}
