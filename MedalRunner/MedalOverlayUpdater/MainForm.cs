using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using MedalRunner;
using MedalRunner.Github;

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
			Updater.Error += Updater_Error;
			Configuration = new ScriptUpdater.Configuration {
				Version = "0.0.0"
			};


			InitializeComponent ( );
			this.statusLabel.Text = "";
		}

		private void Updater_Error ( object sender, System.IO.ErrorEventArgs e ) {
			this.statusLabel.Text = e.GetException ( ).Message;
		}

		private void Updater_EndUpdateCheck ( object sender, MedalRunner.ScriptUpdater.UpdateStatusEventArgs e ) {
			UpdateStatus = e.Status;
			if ( UpdateStatus.HasUpdate ) {
				this.statusLabel.Text = $"Update Available: v{UpdateStatus.LatestVersion}. You are running v{UpdateStatus.UserVersion}";
			} else {
				this.statusLabel.Text = $"You are running the latest version: {UpdateStatus.UserVersion.ToString ( )}";
			}
			updateNow.Enabled = UpdateStatus.HasUpdate;
		}

		private void Updater_BeginUpdateCheck ( object sender, EventArgs e ) {
			this.statusLabel.Text = "Checking for Update...";
			updateNow.Enabled = false;
			progress.Value = 0;

		}

		public MedalRunner.ScriptUpdater Updater { get; set; }
		public UpdateCheck UpdateStatus { get; set; }
		public ScriptUpdater.Configuration Configuration { get; set; }

		private async void MainForm_Load ( object sender, EventArgs e ) {
			Configuration = Updater.GetConfiguration ( );
			if ( !Updater.HasError ) {
				await Updater.CheckUpdateStatus ( Configuration.Version );
			}
		}

		private void DownloadAsset ( ) {

			if ( UpdateStatus == null || UpdateStatus.Asset == null || string.IsNullOrWhiteSpace ( UpdateStatus.Asset.DownloadUrl ) ) {
				return;
			}

			using ( var http = new WebClient ( ) ) {
				var path = Path.GetDirectoryName ( Assembly.GetExecutingAssembly ( ).Location );
				var local = Path.Combine ( path, UpdateStatus.Asset.Name );

				http.DownloadFileCompleted += Http_DownloadFileCompleted;
				http.DownloadProgressChanged += Http_DownloadProgressChanged;
				http.DownloadFile ( new Uri ( UpdateStatus.Asset.DownloadUrl ), local );
			}
		}

		private void MoveDirectory ( string source, string dest ) {
			if ( !Directory.Exists ( dest ) ) {
				Console.WriteLine ( $"Create Directory: {dest}" );
				Directory.CreateDirectory ( dest );
			}
			var files = Directory.GetFiles ( source );
			var directories = Directory.GetDirectories ( source );
			foreach ( string s in files ) {
				Console.WriteLine ( $"Copy File: {s}" );
				File.Copy ( s, Path.Combine ( dest, Path.GetFileName ( s ) ), true );
			}
			foreach ( string d in directories ) {
				MoveDirectory ( Path.Combine ( source, Path.GetFileName ( d ) ), Path.Combine ( dest, Path.GetFileName ( d ) ) );
			}

		}

		private void ExtractAsset ( ) {
			if ( UpdateStatus == null || UpdateStatus.Asset == null || string.IsNullOrWhiteSpace ( UpdateStatus.Asset.DownloadUrl ) ) {
				return;
			}
			var path = Path.GetDirectoryName ( Assembly.GetExecutingAssembly ( ).Location );
			var local = Path.Combine ( path, UpdateStatus.Asset.Name );
			// the path is the path of Medal Overlay. This gets the parent.
			var slcScriptsPath = new DirectoryInfo ( Configuration.Path
				/*@"D:\Development\projects\github\chatbot-medal\MedalRunner\MedalOverlayUpdater\bin\Debug\Scripts\MedalOverlay"*/
			);
			if ( File.Exists ( local ) ) {
				if ( slcScriptsPath.Exists ) {
					var dest = slcScriptsPath.FullName;
					Console.WriteLine ( $"Dest: {dest}" );
					if ( Directory.Exists ( Path.Combine ( path, "temp" ) ) ) {
						Directory.Delete ( Path.Combine ( path, "temp" ), true );
					}
					ZipFile.ExtractToDirectory ( local, Path.Combine ( path, "temp" ) );
					MoveDirectory ( Path.Combine ( path, "temp", "MedalOverlay" ), Path.Combine ( dest, "MedalOverlay" ) );
					if ( Directory.Exists ( Path.Combine ( path, "temp" ) ) ) {
						Directory.Delete ( Path.Combine ( path, "temp" ), true );
					}
				} else {
					throw new DirectoryNotFoundException ( $"Unable to locate directory: {slcScriptsPath}" );
				}
			} else {
				throw new FileNotFoundException ( $"Unable to locate file: {local}" );
			}
		}

		private void ShutdownMoHttpdProcess ( ) {
			var pm = new MedalRunner.Process ( );
			pm.Stop ( "mohttpd" );
		}

		private void ShutdownChatbotProcess ( ) {
			var pm = new MedalRunner.Process ( );
			pm.Stop ( "Streamlabs Chatbot" );
		}

		private void RestartChatbotProcess ( ) {
			var processInfo = new System.Diagnostics.ProcessStartInfo ( Configuration.Chatbot );
			processInfo.WorkingDirectory = System.IO.Path.GetDirectoryName ( Configuration.Chatbot );
			var process = new System.Diagnostics.Process ( );
			process.StartInfo = processInfo;
			process.Start ( );
		}


		private void Http_DownloadProgressChanged ( object sender, DownloadProgressChangedEventArgs e ) {
			double bytesIn = double.Parse ( e.BytesReceived.ToString ( ) );
			double totalBytes = double.Parse ( e.TotalBytesToReceive.ToString ( ) );
			double percentage = bytesIn / totalBytes * 100;
			progressLabel.Text = "Downloaded " + e.BytesReceived + " of " + e.TotalBytesToReceive;
			progress.Value = int.Parse ( Math.Truncate ( percentage ).ToString ( ) );
		}


		private void Http_DownloadFileCompleted ( object sender, AsyncCompletedEventArgs e ) {
			progressLabel.Text = "Download Completed...";
			progress.Value = 20;
		}

		private void UpdateNow_Click ( object sender, EventArgs e ) {
			this.cancel.Enabled = false;
			var result = MessageBox.Show ( "This will shutdown Streamlabs Chatbot, and restart it after update.\n\nDo you want to continue?",
				"Continue?",
				MessageBoxButtons.YesNo,
				MessageBoxIcon.Question );

			if ( result == DialogResult.Yes ) {
				try {
					DownloadAsset ( );

					progressLabel.Text = "Shutting mohttpd";
					ShutdownMoHttpdProcess ( );
					progress.Value = 40;

					progressLabel.Text = "Shutting Down Chatbot";
					ShutdownChatbotProcess ( );
					progress.Value = 60;

					progressLabel.Text = "Waiting for Chatbot to exit ";
					var waitMax = 150;
					var cnt = 0;
					while ( true ) {
						if ( cnt++ > waitMax ) {
							throw new TimeoutException ( "Timeout while waiting for Streamlabs Chatbot to exit" );
						}
						System.Diagnostics.Process[] processList = System.Diagnostics.Process.GetProcessesByName ( "Streamlabs Chatbot" );
						if ( processList.Length > 0 ) {
							progressLabel.Text = $"Waiting for Chatbot to exit {SpinText ( cnt )}";
							Thread.Sleep ( 100 );
						} else {
							break;
						}
					}

					progressLabel.Text = "Extracting Archive";
					ExtractAsset ( );
					progress.Value = 80;

					progressLabel.Text = "Restart Chatbot";
					RestartChatbotProcess ( );
					progress.Value = 100;

					this.statusLabel.Text = $"Update to {this.UpdateStatus.LatestVersion} Completed Successfully";
					this.progressLabel.Text = "";
					this.updateNow.Enabled = false;
					this.cancel.Enabled = true;

				} catch ( Exception err ) {
					this.cancel.Enabled = true;
					progressLabel.Text = err.Message;
					Console.WriteLine ( err.ToString ( ) );
				}
			}
		}

		private void Cancel_Click ( object sender, EventArgs e ) {
			this.Close ( );
		}

		private string SpinText ( int interval ) {

			var items = new string[] {
				"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
			};

			var index = Math.Floor ( (decimal)interval / items.Length );
			return items[(int)index];
		}
	}
}
