using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace MedalHotkeyListener {
	public sealed class Arguments {

		/// <summary>
		/// Initializes a new instance of the <see cref="Arguments"/> class.
		/// </summary>
		/// <param name="args">The args.</param>
		public Arguments ( params string[] args )
			: this ( ) {
			Parse ( args );
		}

		public Arguments ( ICollection<string> args ) {
			Parse ( args );
		}


		/// <summary>
		/// Initializes a new instance of the <see cref="Arguments"/> class.
		/// </summary>
		public Arguments ( ) {
			Parameters = new Dictionary<string, string> ( );
		}

		private Dictionary<string, string> Parameters { get; set; }

		/// <summary>
		/// Parses the specified args.
		/// </summary>
		/// <param name="args">The args.</param>
		private void Parse ( IEnumerable<string> args ) {
			Parameters.Clear ( );
			var spliter = new Regex ( @"^-{1,2}|^/|=|:", RegexOptions.IgnoreCase | RegexOptions.Compiled | RegexOptions.IgnorePatternWhitespace );
			var remover = new Regex ( @"^['""]?(.*?)['""]?$", RegexOptions.IgnoreCase | RegexOptions.Compiled | RegexOptions.IgnorePatternWhitespace );

			string parameter = null;
			string[] parts;

			// Valid parameters forms:
			// {-,/,--}param{ ,=,:}((",')value(",'))
			// Examples: 
			// -param1 value1 --param2 /param3:"Test-:-work" 
			//   /param4=happy -param5 '--=nice=--'
			foreach ( string txt in args ) {
				// Look for new parameters (-,/ or --) and a
				// possible enclosed value (=,:)
				parts = spliter.Split ( txt, 3 );

				switch ( parts.Length ) {
					// Found a value (for the last parameter 
					// found (space separator))
					case 1:
						if ( parameter != null ) {
							if ( !Parameters.ContainsKey ( parameter ) ) {
								parts[0] = remover.Replace ( parts[0], "$1" );
								Parameters.Add ( parameter, parts[0] );
							}
							parameter = null;
						}
						// else Error: no parameter waiting for a value (skipped)
						break;
					// Found just a parameter
					case 2:
						// The last parameter is still waiting. 
						// With no value, set it to true.
						if ( parameter != null ) {
							if ( !Parameters.ContainsKey ( parameter ) ) {
								Parameters.Add ( parameter, "true" );
							}
						}
						parameter = parts[1];
						break;

					// Parameter with enclosed value
					case 3:
						// The last parameter is still waiting. 
						// With no value, set it to true.
						if ( parameter != null ) {
							if ( !Parameters.ContainsKey ( parameter ) ) {
								Parameters.Add ( parameter, "true" );
							}
						}

						parameter = parts[1];

						// Remove possible enclosing characters (",')
						if ( !Parameters.ContainsKey ( parameter ) ) {
							parts[2] = remover.Replace ( parts[2], "$1" );
							Parameters.Add ( parameter, parts[2] );
						}

						parameter = null;
						break;
				}
			}
			// In case a parameter is still waiting
			if ( parameter != null ) {
				if ( !Parameters.ContainsKey ( parameter ) )
					Parameters.Add ( parameter, "true" );
			}
		}

		// Retrieve a parameter value if it exists 
		// (overriding C# indexer property)
		/// <summary>
		/// Gets the <see cref="System.String"/> with the specified param.
		/// </summary>
		/// <value></value>
		/// <exception cref="IndexOutOfRangeException">If it does not contain the specified param.</exception>
		public string this[String param] {
			get {
				return Get ( param );
			}
		}

		/// <summary>
		/// Gets the <see cref="System.String"/> with the specified paramlist.
		/// </summary>
		/// <value></value>
		/// <exception cref="IndexOutOfRangeException">If it does not contain the specified param.</exception>
		public string this[params String[] paramlist] {
			get {
				return Get ( paramlist );
			}
		}


		/// <summary>
		/// Gets the specified param value.
		/// </summary>
		/// <param name="param">The param.</param>
		/// <returns>The value of the param.</returns>
		/// <exception cref="IndexOutOfRangeException">If it does not contain the specified param.</exception>
		public String Get ( String param ) {
			if ( ContainsKey ( param ) ) {
				return Parameters[param];
			}

			throw new IndexOutOfRangeException ( );
		}

		/// <summary>
		/// Gets the value of a param from the specified paramlist.
		/// </summary>
		/// <param name="paramlist">The paramlist.</param>
		/// <returns>The value of the param.</returns>
		/// <exception cref="IndexOutOfRangeException">If it does not contain the specified param.</exception>
		public String Get ( params String[] paramlist ) {
			foreach ( var param in paramlist ) {
				if ( Parameters.ContainsKey ( param ) ) {
					return Parameters[param];
				}
			}

			throw new IndexOutOfRangeException ( );
		}

		/// <summary>
		/// Determines whether this instance contains the specified key.
		/// </summary>
		/// <param name="param">The param.</param>
		/// <returns>
		/// 	<c>true</c> if this instance contains the specified key; otherwise, <c>false</c>.
		/// </returns>
		public bool ContainsKey ( String param ) {
			return Parameters.ContainsKey ( param );
		}

		/// <summary>
		/// Determines whether this instance contains any of the params in the specified param list.
		/// </summary>
		/// <param name="paramlist">The paramlist.</param>
		/// <returns>
		/// 	<c>true</c> if this instance contains any of the params in the specified param list; otherwise, <c>false</c>.
		/// </returns>
		public bool ContainsKey ( params String[] paramlist ) {
			foreach ( var item in paramlist ) {
				if ( Parameters.ContainsKey ( item ) ) {
					return true;
				}
			}
			return false;
		}

		/// <summary>
		/// Determines whether the specified value contains value.
		/// </summary>
		/// <param name="value">The value.</param>
		/// <returns>
		/// 	<c>true</c> if the specified value contains value; otherwise, <c>false</c>.
		/// </returns>
		public bool ContainsValue ( string value ) {
			return Parameters.ContainsValue ( value );
		}

		/// <summary>
		/// Gets the keys.
		/// </summary>
		/// <value>The keys.</value>
		public Dictionary<string, string>.KeyCollection Keys {
			get { return Parameters.Keys; }
		}

		/// <summary>
		/// Gets the values.
		/// </summary>
		/// <value>The values.</value>
		public Dictionary<string, string>.ValueCollection Values {
			get { return this.Parameters.Values; }
		}

		/// <summary>
		/// Gets the count.
		/// </summary>
		/// <value>The count.</value>
		public int Count { get { return this.Parameters.Count; } }



		/// <summary>
		/// Returns a <see cref="T:System.String"></see> that represents the current <see cref="T:System.Object"></see>.
		/// </summary>
		/// <returns>
		/// A <see cref="T:System.String"></see> that represents the current <see cref="T:System.Object"></see>.
		/// </returns>
		public override string ToString ( ) {
			var sb = new StringBuilder ( );
			foreach ( string key in Parameters.Keys ) {
				sb.AppendFormat ( "/{0}={1} ", key, Parameters[key] );
			}
			return sb.ToString ( ).Trim ( );
		}
	}
}
