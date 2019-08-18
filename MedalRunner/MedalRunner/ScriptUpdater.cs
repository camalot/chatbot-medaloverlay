using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using MedalRunner.Exceptions;
using Newtonsoft.Json;
using Semver;

namespace MedalRunner {
	public class ScriptUpdater {

		public class Configuration {
			[JsonProperty ( "path" )]
			public string Path { get; set; }
			[JsonProperty ( "version" )]
			public string Version { get; set; }
			[JsonProperty ( "chatbot" )]
			public string Chatbot { get; set; }
		}

		public class UpdateStatusEventArgs {
			public Github.UpdateCheck Status { get; set; }
		}
		public event EventHandler BeginUpdateCheck;
		public event EventHandler<UpdateStatusEventArgs> EndUpdateCheck;
		public event EventHandler<ErrorEventArgs> Error;

		public ScriptUpdater ( ) {

		}

		public bool HasError { get; set; }

		public Configuration GetConfiguration ( ) {
			var path = Path.GetDirectoryName ( Assembly.GetExecutingAssembly ( ).Location );
			var file = "chatbot.json";
			var fullPath = Path.Combine ( path, file );
			if ( File.Exists ( fullPath ) ) {
				using ( var fr = new StreamReader ( fullPath ) ) {
					using ( var jr = new JsonTextReader ( fr ) ) {
						var ser = new JsonSerializer ( );
						return ser.Deserialize<Configuration> ( jr );
					}
				}
			} else {
				HasError = true;
				Error?.Invoke ( this, new ErrorEventArgs ( new FileNotFoundException ( "Unable to locate required chatbot.json config file" ) ) );

				return new Configuration {
					Version = "0.0.0"
				};
			}
		}

		public async Task<Github.UpdateCheck> CheckUpdateStatus ( string baseVersion ) {
			BeginUpdateCheck?.Invoke ( this, new EventArgs ( ) );
			var release = await GetLatestRelease ( );
			var userVersion = SemVersion.Parse ( baseVersion );
			var result = new Github.UpdateCheck ( ) {
				HasUpdate = false,
				UserVersion = userVersion,
				LatestVersion = SemVersion.Parse ( "0.0.0" )
			};
			if ( release != null && release.Assets?.Count ( ) > 0 ) {
				var releaseVersion = SemVersion.Parse ( release.TagName );
				result = new Github.UpdateCheck ( ) {
					HasUpdate = userVersion < releaseVersion,
					LatestVersion = releaseVersion,
					UserVersion = userVersion,
					Asset = release.Assets.First ( )
				};
			} else {
				HasError = true;
				Error?.Invoke ( this, new ErrorEventArgs ( new UnableToLoadReleaseException ( ) ) );
				return result;
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
