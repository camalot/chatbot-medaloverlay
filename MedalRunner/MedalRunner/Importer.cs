using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Cache;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace MedalRunner {
	public class Importer {
		public Importer ( int userId, string authKey ) {
			UserId = userId;
			AuthKey = authKey;
		}

		public int UserId { get; private set; }
		public string AuthKey { get; private set; }
		public string Import(string clipUrl, string thumbUrl, string title, string description, int categoryId = 713, int privacy = 0) {
			try {
				var postUrl = $"https://api-v2.medal.tv/users/{UserId.ToString ( )}/content";
				var contentType = "application/json";

				var http = WebRequest.CreateHttp ( postUrl );
				http.ContentType = contentType;
				http.Method = "POST";
				http.AllowAutoRedirect = true;
				http.CachePolicy = new RequestCachePolicy ( RequestCacheLevel.BypassCache );
				http.Referer = "no-referrer";
				http.UserAgent = "Medal Overlay for Streamlabs Chatbot";
				http.Headers.Add ( "X-Authentication", $"{UserId.ToString ( )},{AuthKey}" );

				var data = new ImportData {
					ContentUrl = clipUrl,
					CategoryId = categoryId,
					Privacy = privacy,
					ContentDescription = description,
					ContentTitle = title,
					ThumbnailUrl = thumbUrl
				};

				var body = Newtonsoft.Json.JsonConvert.SerializeObject ( data, Formatting.None );
				using ( var reqs = http.GetRequestStream ( ) ) {
					var unicodeEncoding = new UnicodeEncoding ( );
					var bytesData = unicodeEncoding.GetBytes ( body );
					reqs.Write ( bytesData, 0, bytesData.Length );
				}

				var resp = http.GetResponse ( );
				using ( var resps = resp.GetResponseStream ( ) ) {
					using ( var sr = new StreamReader ( resps ) ) {
						return sr.ReadToEnd ( );
					}
				}
			} catch ( Exception e ) {
				return $"{{ \"error\": \"{e.Message}\", \"stack\": \"{e.StackTrace}\" }}";
			}
		}

		public class ImportData {
			[JsonProperty("contentUrl")]
			public string ContentUrl { get; set; }
			[JsonProperty("categoryId")]
			public int CategoryId { get; set; } = 713;
			[JsonProperty("risk")]
			public int Risk { get; set; } = 0;
			[JsonProperty("privacy")]
			public int Privacy { get; set; } = 0;
			[JsonProperty("contentType")]
			public int ContentType { get; set; } = 15;
			[JsonProperty("contentDescription")]
			public string ContentDescription { get; set; }
			[JsonProperty("contentTitle")]
			public string ContentTitle { get; set; }
			[JsonProperty ( "thumbnailUrl" )]
			public string ThumbnailUrl { get; set; } = "empty";
		}
	}
}
