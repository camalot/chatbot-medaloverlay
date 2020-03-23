using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using MedalRunner;
using Newtonsoft.Json;

namespace Test {
	public partial class Form1 : Form {
		private MedalRunner.Watcher watcher;
		public Form1 ( ) {
			InitializeComponent ( );

			watcher = new MedalRunner.Watcher ( @"d:\Users\rconr\Videos\medal" );
			watcher.ClipStarted += Watcher_ClipStarted;
			watcher.ClipReady += Watcher_ClipReady;
			watcher.MonitorStart += Watcher_MonitorStart;
			watcher.MonitorStop += Watcher_MonitorStop;
			watcher.MonitorPause += Watcher_MonitorPause;

			watcher.Start ( );
		}

		private void Watcher_MonitorPause ( object sender, EventArgs e ) {
			Console.WriteLine ( $"PAUSE MONITOR: {watcher.Path}" );
		}

		private void Watcher_MonitorStop ( object sender, EventArgs e ) {
			Console.WriteLine ( $"STOP MONITOR: {watcher.Path}" );
		}

		private void Watcher_MonitorStart ( object sender, EventArgs e ) {
			Console.WriteLine ( $"START MONITOR: {watcher.Path}" );
		}

		private void Watcher_ClipStarted ( object sender, MedalRunner.MedalClipWatcherEventData e ) {
			Console.WriteLine ( $"CLIP STARTED: {e.ClipId}" );
		}

		private void Watcher_ClipReady ( object sender, MedalRunner.MedalClipWatcherEventData e ) {
			Console.WriteLine ( $"CLIP READY: {e.ClipId}" );
		}

		private void trigger_Click ( object sender, EventArgs e ) {
			//SendKeys.Send ( "{F8}" );
			MedalRunner.Keys.SendKeys ( "{F8}" );
		}

		private void start_Click ( object sender, EventArgs e ) {
			watcher.Start ( );
		}

		private void pause_Click ( object sender, EventArgs e ) {
			watcher.Pause ( );
		}

		private void stop_Click ( object sender, EventArgs e ) {
			watcher.Stop ( );
		}

		private void Killmohttpd_Click ( object sender, EventArgs e ) {
			new MedalRunner.Process ( ).Stop ( "mohttpd" );
		}

		private void ImportTest_Click ( object sender, EventArgs e ) {

			var appData = Environment.GetFolderPath ( Environment.SpecialFolder.ApplicationData );
			var path = Path.Combine ( appData, "Medal/store/user.json" );
			MedalUserSettings settings = null;
			if ( System.IO.File.Exists ( path ) ) {
				using ( var sr = File.OpenText ( path ) ) {
					settings = JsonConvert.DeserializeObject<MedalUserSettings> ( sr.ReadToEnd ( ) );
				}
				var importer = new Importer ( settings.UserId, settings.Key );
				var result = importer.Import ( "https://www.twitch.tv/darthminos/clip/ObeseSparklingAxeArsonNoSexy", "empty", "Long? Tom Clancy's Rainbow Six: Siege", "Test Clip Import");
				Console.WriteLine ( result );
			} else {
				Console.WriteLine ( "User Settings File Not Found." );
			}
		}
	}

	public class MedalUserSettings {
		[JsonProperty ( "userId" )]
		public int UserId { get; set; }
		[JsonProperty ( "key" )]
		public string Key { get; set; }
	}
}
