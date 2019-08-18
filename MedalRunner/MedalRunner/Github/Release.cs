using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Semver;

namespace MedalRunner.Github {
	public class Release {

		[JsonProperty ( "node_id" )]
		public string NodeId { get; set; }
		[JsonProperty ( "id" )]
		public int Id { get; set; }
		[JsonProperty ( "name" )]
		public string Name { get; set; }
		[JsonProperty ( "tag_name" )]
		public string TagName { get; set; }
		[JsonProperty ( "body" )]
		public string Body { get; set; }
		[JsonProperty ( "created_at" )]
		public DateTime CreatedAt { get; set; }
		[JsonProperty ( "published_ad" )]
		public DateTime PublishedAt { get; set; }
		[JsonProperty ( "assets" )]
		public List<ReleaseAsset> Assets { get; set; }
	}

	public class ReleaseAsset {
		[JsonProperty ( "node_id" )]
		public string NodeId { get; set; }
		[JsonProperty ( "id" )]
		public int Id { get; set; }
		[JsonProperty( "browser_download_url" )]
		public string DownloadUrl { get; set; }
		[JsonProperty ( "size" )]
		public int Size { get; set; }
		[JsonProperty ( "content_type" )]
		public string ContentType { get; set; }
		[JsonProperty ( "name" )]
		public string Name { get; set; }
		[JsonProperty ( "label" )]
		public string Label { get; set; }
	}

	public class UpdateCheck {
		public bool HasUpdate { get; set; }
		public SemVersion LatestVersion { get; set; }
		public SemVersion UserVersion { get; set; }
		public ReleaseAsset Asset { get; set; }

	}
}
