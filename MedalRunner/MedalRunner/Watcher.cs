using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MedalRunner {

	public class MedalClipWatcherEventData {
		public string ClipId { get; set; }
	}

	public class Watcher {

		public event EventHandler<MedalClipWatcherEventData> ClipReady;
		public event EventHandler<MedalClipWatcherEventData> ClipStarted;
		public event EventHandler<EventArgs> MonitorStart;
		public event EventHandler<EventArgs> MonitorStop;
		public event EventHandler<EventArgs> MonitorPause;

		public Watcher ( string path ) {
			Path = path;
		}

		private FileSystemWatcher ThumbnailWatcher { get; set; }
		private FileSystemWatcher MP4Watcher { get; set; }
		public string Path { get; private set; }

		public void Start() {
			if ( ThumbnailWatcher == null) {
				ThumbnailWatcher = new FileSystemWatcher ( Path, "*-thumbnail.jpg" );
				ThumbnailWatcher.IncludeSubdirectories = true;
				ThumbnailWatcher.Created += ThumbnailWatcher_Created;
			}

			if ( MP4Watcher == null) {
				MP4Watcher = new FileSystemWatcher ( Path, "*.mp4" );
				MP4Watcher.IncludeSubdirectories = false;
				MP4Watcher.Created += MP4Watcher_Created;
			}

			ThumbnailWatcher.EnableRaisingEvents = true;
			MP4Watcher.EnableRaisingEvents = true;

			MonitorStart?.Invoke ( this, new EventArgs ( ) );

		}

		private void MP4Watcher_Created ( object sender, FileSystemEventArgs e ) {
			ClipStarted?.Invoke ( sender, new MedalClipWatcherEventData {
				ClipId = System.IO.Path.GetFileNameWithoutExtension ( e.Name )
			} );
		}

		private void ThumbnailWatcher_Created ( object sender, FileSystemEventArgs e ) {
			ClipReady?.Invoke ( sender, new MedalClipWatcherEventData {
				ClipId = System.IO.Path.GetFileNameWithoutExtension ( e.Name ).Replace("-thumbnail", "")
		} );
		}

		public void Pause() {
			ThumbnailWatcher.EnableRaisingEvents = false;
			MP4Watcher.EnableRaisingEvents = false;
			MonitorPause?.Invoke ( this, new EventArgs ( ) );
		}

		public void Stop ( ) {
			ThumbnailWatcher.EnableRaisingEvents = false;
			MP4Watcher.EnableRaisingEvents = false;

			ThumbnailWatcher.Dispose ( );
			MP4Watcher.Dispose ( );

			ThumbnailWatcher = null;
			MP4Watcher = null;
			MonitorStop?.Invoke ( this, new EventArgs ( ) );

		}


	}
}
