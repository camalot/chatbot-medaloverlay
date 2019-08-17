using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Semver;

namespace MedalRunner {
	public class ScriptUpdater {
		public class UpdateStatusEventArgs {
			public Github.UpdateCheck Status { get; set; }
		}
		public event EventHandler BeginUpdateCheck;
		public event EventHandler<UpdateStatusEventArgs> EndUpdateCheck;

		public ScriptUpdater ( ) {

		}

		public async Task<string> GetScriptVersion () {
			var pattern = @"^Version\s+=\s+""([^""]+)""";
			var file = "Medal_StreamlabsSystem.py";
			var path = System.IO.Path.GetDirectoryName ( Assembly.GetExecutingAssembly ( ).Location );
			var fullPath = Path.Combine ( path, file );
			using(var fr = new StreamReader(fullPath)) {
				var python = await fr.ReadToEndAsync ( );
				var regex = new Regex ( pattern, RegexOptions.Compiled | RegexOptions.Multiline | RegexOptions.CultureInvariant |RegexOptions.IgnorePatternWhitespace );
				var m = regex.Match ( python );
				if(m.Success) {
					return m.Groups[1].Value;
				} else {
					return "0.0.1";
				}
			}
		}

		public async Task<Github.UpdateCheck> CheckUpdateStatus ( string baseVersion ) {
			BeginUpdateCheck?.Invoke ( this, new EventArgs ( ) );
			var release = await GetLatestRelease ( );
			var userVersion = SemVersion.Parse ( baseVersion );
			var result = new Github.UpdateCheck ( ) {
				HasUpdate = false,
				UserVersion = userVersion,
				LatestVersion = SemVersion.Parse("0.0.0-unknown")
			};
			if ( release != null && release.Assets?.Count ( ) > 0 ) {
				var releaseVersion = SemVersion.Parse ( release.TagName );
				result = new Github.UpdateCheck ( ) {
					HasUpdate = userVersion < releaseVersion,
					LatestVersion = releaseVersion,
					UserVersion = userVersion,
					Asset = release.Assets.First ( )
				};
			}

			EndUpdateCheck?.Invoke ( this, new UpdateStatusEventArgs ( ) { Status = result } );
			return result;

		}

		private async Task<Github.Release> GetLatestRelease ( ) {
			var api = "https://api.github.com/repos/camalot/chatbot-medaloverlay/releases/latest";

			using ( var httpClient = new HttpClient ( ) ) {
				httpClient.DefaultRequestHeaders.Add ( "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36" );
				var json = await httpClient.GetStringAsync ( api );
				using ( var sr = new StringReader ( json ) ) {
					using ( var jr = new JsonTextReader ( sr ) ) {
						var ser = new JsonSerializer ( ) {
							DateFormatHandling = DateFormatHandling.IsoDateFormat
						};
						return ser.Deserialize<Github.Release> ( jr );
					}
				}
			}
		}
	}
}
