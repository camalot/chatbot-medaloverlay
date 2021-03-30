using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace MedalHotkeyListener {

	public class Payload {
		[JsonProperty ( "hotkey" )]
		public string Hotkey { get; set; }
		[JsonProperty ( "user" )]
		public string User { get; set; }
	}
}
