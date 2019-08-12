namespace Test {
	partial class Form1 {
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.IContainer components = null;

		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		/// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
		protected override void Dispose ( bool disposing ) {
			if ( disposing && ( components != null ) ) {
				components.Dispose ( );
			}
			base.Dispose ( disposing );
		}

		#region Windows Form Designer generated code

		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent ( ) {
			this.trigger = new System.Windows.Forms.Button();
			this.start = new System.Windows.Forms.Button();
			this.pause = new System.Windows.Forms.Button();
			this.stop = new System.Windows.Forms.Button();
			this.SuspendLayout();
			// 
			// trigger
			// 
			this.trigger.Location = new System.Drawing.Point(12, 12);
			this.trigger.Name = "trigger";
			this.trigger.Size = new System.Drawing.Size(96, 23);
			this.trigger.TabIndex = 1;
			this.trigger.Text = "Trigger Test";
			this.trigger.UseVisualStyleBackColor = true;
			this.trigger.Click += new System.EventHandler(this.trigger_Click);
			// 
			// start
			// 
			this.start.Location = new System.Drawing.Point(12, 56);
			this.start.Name = "start";
			this.start.Size = new System.Drawing.Size(96, 23);
			this.start.TabIndex = 2;
			this.start.Text = "Start";
			this.start.UseVisualStyleBackColor = true;
			this.start.Click += new System.EventHandler(this.start_Click);
			// 
			// pause
			// 
			this.pause.Location = new System.Drawing.Point(12, 94);
			this.pause.Name = "pause";
			this.pause.Size = new System.Drawing.Size(96, 23);
			this.pause.TabIndex = 3;
			this.pause.Text = "Pause";
			this.pause.UseVisualStyleBackColor = true;
			this.pause.Click += new System.EventHandler(this.pause_Click);
			// 
			// stop
			// 
			this.stop.Location = new System.Drawing.Point(12, 134);
			this.stop.Name = "stop";
			this.stop.Size = new System.Drawing.Size(96, 23);
			this.stop.TabIndex = 4;
			this.stop.Text = "Stop";
			this.stop.UseVisualStyleBackColor = true;
			this.stop.Click += new System.EventHandler(this.stop_Click);
			// 
			// Form1
			// 
			this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.ClientSize = new System.Drawing.Size(120, 179);
			this.Controls.Add(this.stop);
			this.Controls.Add(this.pause);
			this.Controls.Add(this.start);
			this.Controls.Add(this.trigger);
			this.MaximizeBox = false;
			this.MaximumSize = new System.Drawing.Size(136, 218);
			this.MinimizeBox = false;
			this.MinimumSize = new System.Drawing.Size(136, 218);
			this.Name = "Form1";
			this.Text = "Form1";
			this.ResumeLayout(false);

		}

		#endregion
		private System.Windows.Forms.Button trigger;
		private System.Windows.Forms.Button start;
		private System.Windows.Forms.Button pause;
		private System.Windows.Forms.Button stop;
	}
}

