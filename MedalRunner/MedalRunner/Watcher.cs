using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace MedalRunner
{

	public class MedalClipWatcherEventData
	{
		public string ClipId { get; set; }
	}

	public class Watcher
	{


		public event EventHandler<MedalClipWatcherEventData> ClipReady;
		public event EventHandler<MedalClipWatcherEventData> ClipStarted;
		public event EventHandler<EventArgs> MonitorStart;
		public event EventHandler<EventArgs> MonitorStop;
		public event EventHandler<EventArgs> MonitorPause;

		public Watcher(string path)
		{
			Path = path;
			var asm = Assembly.GetExecutingAssembly();
			var asmDirectory = System.IO.Path.GetDirectoryName(asm.Location);
			var loggerPath = System.IO.Path.Combine(asmDirectory, "../logs");
			var dt = DateTime.Now.ToString("yyyyMMdd");
			var logFile = System.IO.Path.Combine(loggerPath, $"{asm.GetName().Name}-{dt}.log");
			Logger = new Logger(logFile);
		}

		private Logger Logger { get; set; }
		private FileSystemWatcher ThumbnailWatcher { get; set; }
		private FileSystemWatcher DotThumbnailWatcher { get; set; }
		private FileSystemWatcher MP4Watcher { get; set; }
		public string Path { get; private set; }

		public void Start()
		{
			if (ThumbnailWatcher == null)
			{
				Logger.Debug("Watcher", "Initialize ThumbnailWatcher");
				ThumbnailWatcher = new FileSystemWatcher(Path, "*-thumbnail.jpg");
				Logger.Debug("Watcher", $"Watching: {ThumbnailWatcher.Path}::{ThumbnailWatcher.Filter}");
				ThumbnailWatcher.IncludeSubdirectories = true;
				ThumbnailWatcher.Created += ThumbnailWatcher_Created;
				ThumbnailWatcher.Deleted += ThumbnailWatcher_Deleted;
				ThumbnailWatcher.Renamed += ThumbnailWatcher_Renamed;
				ThumbnailWatcher.Changed += ThumbnailWatcher_Changed;
				ThumbnailWatcher.Error += ThumbnailWatcher_Error;
			}
			if (DotThumbnailWatcher == null)
			{
				Logger.Debug("Watcher", "Initialize DotThumbnailWatcher");
				DotThumbnailWatcher = new FileSystemWatcher(System.IO.Path.Combine(Path, ".Thumbnails"), "*.jpg");
				Logger.Debug("Watcher", $"Watching: {DotThumbnailWatcher.Path}::{DotThumbnailWatcher.Filter}");
				DotThumbnailWatcher.IncludeSubdirectories = true;
				DotThumbnailWatcher.Created += ThumbnailWatcher_Created;
				DotThumbnailWatcher.Deleted += ThumbnailWatcher_Deleted;
				DotThumbnailWatcher.Renamed += ThumbnailWatcher_Renamed;
				DotThumbnailWatcher.Changed += ThumbnailWatcher_Changed;
				DotThumbnailWatcher.Error += ThumbnailWatcher_Error;
			}

			if (MP4Watcher == null)
			{
				Logger.Debug("Watcher", "Initialize MP4Watcher");
				MP4Watcher = new FileSystemWatcher(Path, "*.mp4");
				Logger.Debug("Watcher", $"Watching: {MP4Watcher.Path}::{MP4Watcher.Filter}");
				MP4Watcher.IncludeSubdirectories = true;
				MP4Watcher.Created += MP4Watcher_Created;
			}

			ThumbnailWatcher.EnableRaisingEvents = true;
			MP4Watcher.EnableRaisingEvents = true;
			DotThumbnailWatcher.EnableRaisingEvents = true;

			MonitorStart?.Invoke(this, new EventArgs());

		}

		private void ThumbnailWatcher_Error(object sender, ErrorEventArgs e)
		{
			Logger.Error("Watcher", $"{e.GetException().ToString()}");
		}

		private void ThumbnailWatcher_Changed(object sender, FileSystemEventArgs e)
		{
			Logger.Debug("Watcher", $"Changed: {e.Name}::{e.ChangeType}");
		}

		private void ThumbnailWatcher_Renamed(object sender, RenamedEventArgs e)
		{
			Logger.Debug("Watcher", $"Renamed: {e.OldName}->{e.Name}");
		}

		private void ThumbnailWatcher_Deleted(object sender, FileSystemEventArgs e)
		{
			Logger.Debug("Watcher", $"Deleted: {e.Name}");
		}

		private void MP4Watcher_Created(object sender, FileSystemEventArgs e)
		{
			Logger.Debug("Watcher", $"Waiting for: {e.Name}");
			var relativePath = System.IO.Path.GetFileNameWithoutExtension(e.FullPath.Replace(MP4Watcher.Path, ""));
			ClipStarted?.Invoke(sender, new MedalClipWatcherEventData
			{
				ClipId = relativePath
			});
		}

		private void ThumbnailWatcher_Created(object sender, FileSystemEventArgs e)
		{
			Logger.Debug("Watcher", $"Clip Ready: {e.Name}");
			var relativePath = System.IO.Path.GetFileNameWithoutExtension(e.FullPath.Replace(DotThumbnailWatcher.Path, "").Replace("-thumbnail", ""));
			ClipReady?.Invoke(sender, new MedalClipWatcherEventData
			{
				ClipId = relativePath
			});
		}

		public void Pause()
		{
			DotThumbnailWatcher.EnableRaisingEvents = false;
			ThumbnailWatcher.EnableRaisingEvents = false;
			MP4Watcher.EnableRaisingEvents = false;
			MonitorPause?.Invoke(this, new EventArgs());
		}

		public void Stop()
		{
			DotThumbnailWatcher.EnableRaisingEvents = false;
			ThumbnailWatcher.EnableRaisingEvents = false;
			MP4Watcher.EnableRaisingEvents = false;

			DotThumbnailWatcher.Dispose();
			ThumbnailWatcher.Dispose();
			MP4Watcher.Dispose();

			DotThumbnailWatcher = null;
			ThumbnailWatcher = null;
			MP4Watcher = null;
			MonitorStop?.Invoke(this, new EventArgs());

		}


	}
}
