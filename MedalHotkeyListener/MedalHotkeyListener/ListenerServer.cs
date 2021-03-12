using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using Newtonsoft.Json;

namespace MedalHotkeyListener {
	public class ListenerServer {

		public ListenerServer ( ) {
			Server = new HttpListener ( );
			var host = Dns.GetHostEntry ( Dns.GetHostName ( ) );
			Server.Prefixes.Add ( $"http://+:{Port}/" );
		}

		private HttpListener Server { get; set; }
		private int Port { get; set; } = 19191;
		private IPAddress Address { get; set; } = IPAddress.Any;

		public void Start ( ) {
			try {
				Server.Start ( );
				Console.WriteLine ( $"Listening on {Address}:{Port}" );
				var listenThread = new Thread ( new ThreadStart ( StartListen ) );
				listenThread.Start ( );
			} catch ( Exception ex ) {
				Console.WriteLine ( ex.ToString ( ) );
			}
		}

		public void Stop ( ) {
			try {
				Server.Stop ( );
			} catch ( Exception ex ) {
				Console.WriteLine ( ex.ToString ( ) );
			}
		}
		private void StartListen ( ) {
			while ( Server.IsListening ) {
				if ( Server.IsListening ) {
					try {
						var context = Server.GetContext ( );
						string payloadData;
						using ( var strm = context.Request.InputStream ) {
							byte[] data = new byte[1024];
							using ( var ms = new MemoryStream ( ) ) {

								int numBytesRead;
								while ( ( numBytesRead = strm.Read ( data, 0, data.Length ) ) > 0 ) {
									ms.Write ( data, 0, numBytesRead );
								}
								payloadData = Encoding.UTF8.GetString ( ms.ToArray ( ) );

							}
						}
						using ( var tr = new StringReader ( payloadData ) ) {
							using ( var jr = new JsonTextReader ( tr ) ) {
								Console.WriteLine ( payloadData );
								var payload = JsonSerializer.CreateDefault ( ).Deserialize<Payload> ( jr );
								ProcessPayload ( payload );
								context.Response.StatusCode = 200;
								context.Response.Close ( );
							}
						}
					} catch( System.Net.HttpListenerException hle ) {
						Console.WriteLine ( "Exiting..." );
					}catch ( Exception ex ) {
						Console.WriteLine ( ex );
					}
				}
			}
		}
		private void ProcessPayload ( Payload payload ) {
			SendKeys.SendWait ( payload.Hotkey );
		}
	}
}

