## MEDAL OVERLAY

[![](https://i.imgur.com/bby6d49.png)](https://medal.tv/invite/DarthMinos)

This is a [StreamLabs Chatbot](https://streamlabs.com/chatbot) Script that allows chat to trigger a [Medal](https://medal.tv/) clip creation, and then play the clip back on stream.  

This will trigger playback on stream if your community triggers the clip creation, or if you press the hotkey to trigger a clip.

[![See Medal Overlay In Action](https://img.youtube.com/vi/q2mIDQ8BcW4/0.jpg)](https://www.youtube.com/watch?v=q2mIDQ8BcW4)

## REQUIREMENTS

- Install [StreamLabs Chatbot](https://streamlabs.com/chatbot)
- [Enable Scripts in StreamLabs Chatbot](https://github.com/StreamlabsSupport/Streamlabs-Chatbot/wiki/Prepare-&-Import-Scripts)
- [Microsoft .NET Framework 4.7.2 Runtime](https://dotnet.microsoft.com/download/dotnet-framework/net472)



## INSTALL

- Download the latest zip file from [Releases](https://github.com/camalot/chatbot-medaloverlay/releases/latest)
- Right-click on the downloaded zip file and choose `Properties`
- Click on `Unblock`  
[![](https://i.imgur.com/vehSSn7l.png)](https://i.imgur.com/vehSSn7.png)  
  > **NOTE:** If you do not see `Unblock`, the file is already unblocked.
- In Chatbot, Click on the import icon on the scripts tab.  
  ![](https://i.imgur.com/16JjCvR.png)
- Select the downloaded zip file
- Right click on `Medal Overlay` and select `Insert API Key`. Click yes on the dialog.  
[![](https://i.imgur.com/AWmtHKFl.png)](https://i.imgur.com/AWmtHKF.png)  

## CONFIGURATION

Make sure the script is enabled  
[![](https://i.imgur.com/JQcHol4l.png)](https://i.imgur.com/JQcHol4.png)  

Click on the script in the list to bring up the configuration.

### GENERAL SETTINGS  

[![](https://i.imgur.com/cR7ZnKjl.png)](https://i.imgur.com/cR7ZnKj.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Clip Command` | The command to trigger the clip creation | `!clip` |
| `Only Trigger off the Command` | If checked, only clips triggered by chat will show up in the overlay. | `False` |  
| `Required Commands to Trigger` | The number of people required to say the command in chat to trigger the clip. | `1` |
| `Trigger Cooldown` | The amount of time, in seconds, that chat has to reach the required trigger count. | `60` |
| `Cooldown` | The amount of seconds between each allowed clip creation | `60` |
| `Permission Level` | The permission level required to trigger the command | `Everyone` |
| `Video Width` | The width of the video. Height will scale automatically | `320` | 

### MEDAL SETTINGS  

[![](https://i.imgur.com/N1MVzWel.png)](https://i.imgur.com/N1MVzWe.png)  


| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Username` | Your Medal Username | `""` | 
| `HotKey` | Your Medal HotKey in [SendKeys Format](SendKeys.md) | `{F8}` | 
| `Videos Path` | The path to your Medal Videos | `` | 

> **NOTE:** Changes this will require you to refresh the cache of the browser source in your broadcast software

### ADVANCED SETTINGS

[![](https://i.imgur.com/r2xsWgKl.png)](https://i.imgur.com/r2xsWgK.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Web Port` | The mort used for the http server for the media files | `9191` | 


### POSITION SETTINGS  

[![](https://i.imgur.com/BjsAqpjl.png)](https://i.imgur.com/BjsAqpj.png)  


| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Use Preset Vertical` | If unchecked, absolute positions will be used | `true` |
| `Vertical` | Vertical position of the video | `Middle` | 
| `Use Preset Horizontal` | If unchecked, absolute positions will be used | `true` |
| `Horizontal` | Horizontal position of the video | `Right` | 
| `Absolute Top` | Absolute Top position of the video | `0` | 
| `Absolute Left` | Absolute Left position of the video | `0` | 
| `Absolute Bottom` | Absolute Bottom position of the video | `0` | 
| `Absolute Right` | Absolute Right position of the video | `0` | 

> **NOTE:** Changes this will require you to refresh the cache of the browser source in your broadcast software

### TRANSITION SETTINGS  

[![](https://i.imgur.com/0Kzcmmvl.png)](https://i.imgur.com/0Kzcmmv.png)  


| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `IN` | The video entrance transition when the video initially loads | `slideInDown` | 
| `OUT` | The video exit transition when the video ends | `slideOutDown` | 

> **NOTE:** Changes this will require you to refresh the cache of the browser source in your broadcast software

### PlayBack
[![](https://i.imgur.com/VcsPgRhl.png)](https://i.imgur.com/VcsPgRh.png)  

| ITEM | DESCRIPTION | 
| ---- | ----------- | 
| `OPEN OVERLAY IN BROWSER` | Opens the Overlay page in browser for testing | 
| `PLAY MOST RECENT VIDEO` | Plays the most recent video | 
| `PLAY RANDOM VIDEO` | Plays a random video | 



### INFORMATION  

[![](https://i.imgur.com/ZLO8YDdl.png)](https://i.imgur.com/ZLO8YDd.png)  

| ITEM | DESCRIPTION | 
| ---- | ----------- | 
| `GET MEDAL` | Opens a link to get Medal | 
| `OPEN README` | Opens the link to this document | 
| `OPEN SENDKEYS DOCS` | Opens the link to the [SendKeys](SendKeys.md) documentation | 
| `CHECK FOR UPDATES` | Will Check if there are updates to the Medal Overlay Script. See below for more info. | 
| `SAVE SETTINGS` | Save any changes to the Medal Overlay settings | 


## MEDAL OVERLAY UPDATER

> **NOTE:** You must launch from within Streamlabs Chatbot. 

The application will open, and if there is an update it will tell you. You click on the `Download & Update` button. 

> **NOTE:** Applying the update will close down Streamlabs Chatbot. It will reopen after the update is complete.

[![](https://i.imgur.com/YKIGYDul.png)](https://i.imgur.com/YKIGYDu.png)

## OBS / SLOBS  

- Add a new `Browser Source` in OBS / SLOBS  
[![](https://i.imgur.com/TAMQkeql.png)](https://i.imgur.com/TAMQkeq.png)
- Set as a `Local File` and choose the `Overlay.html` in the `Medal Overlay` script directory. You can easily get to the script directory location from right clicking on `Medal Overlay` and choose `Open Script Folder`.
- Set the `width` and `height` to the resolution of your `Base (Canvas) Resolution`. 
- Add any additional custom CSS that you would like to add.
- Check both `Shutdown source when not visible` and `Refresh browser when scene becomes active`.  
[![](https://i.imgur.com/nouqPh0l.png)](https://i.imgur.com/nouqPh0.png)


## CUSTOM CSS

You can customize the look with custom css to add a border, or other styles to the video. Just edit the `custom.css` file, or you can use the `custom css` in SLOBS/OBS. 

Here is an example that uses a background uploaded to imgur.
```css
#video-container .video-box {
  /* This is the container that holds the video-border-box and the video elements */
}

#video-container .video-box .video-border-box {
	/* This container sits directly on top of the video and is sized the same as the video */

	/* set the background image url */

	/* Default */
	/*background-image: url('https://i.imgur.com/Y4MefHd.png');*/

	/* Black */
	/*background-image: url('https://i.imgur.com/4HoOsZG.png');*/
	/* Blue */
	/*background-image: url('https://i.imgur.com/muOdiHv.png');*/
	/* Cyan */
	/*background-image: url('https://i.imgur.com/4c7aaLK.png');*/
	/* Gold */
	/*background-image: url('https://i.imgur.com/Y4MefHd.png');*/
	/* Green */
	/*background-image: url('https://i.imgur.com/PiwlVjd.png');*/
	/* Green2 */
	/*background-image: url('https://i.imgur.com/P9ZtCAn.png');*/
	/* Jade */
	/*background-image: url('https://i.imgur.com/2i82REJ.png');*/
	/* LightBlue */
	/*background-image: url('https://i.imgur.com/9M1EMbk.png');*/
	/* LightPink */
	/*background-image: url('https://i.imgur.com/O6bCgau.png');*/
	/* LightPurple */
	/*background-image: url('https://i.imgur.com/YuOjaYd.png');*/
	/* LightRed */
	/*background-image: url('https://i.imgur.com/PzSm5ja.png');*/
	/* Lime */
	/*background-image: url('https://i.imgur.com/xZqA9ve.png');*/
	/* Orange */
	/*background-image: url('https://i.imgur.com/ILkW15e.png');*/
	/* Pink */
	/*background-image: url('https://i.imgur.com/hcSEair.png');*/
	/* Purple */
	/*background-image: url('https://i.imgur.com/YQcy0RK.png');*/
	/* Red */
	/*background-image: url('https://i.imgur.com/NCoGlt4.png');*/
	/* RedPink */
	/*background-image: url('https://i.imgur.com/NVHo4ch.png');*/
	/* White */
	/*background-image: url('https://i.imgur.com/ejtPCBm.png');*/


	/* CUSTOM IMAGE (make sure it is 16:9 aspect ratio) */
	/*background-image: url('http://some-cool-domain/path-to-image.png');*/

}

#video-container .video-box video {
	/* This is the video container */
}
```

[Pre-made borders](https://imgur.com/a/5PTkzhR)  
[![](https://i.imgur.com/qxxcsWgl.png)](https://i.imgur.com/qxxcsWg.png)

Here is a sample
![](https://i.imgur.com/OMF0MKf.png)


## TECHNICAL INFORMATION

Files are served to the overlay via a lightweight http server called [tinyweb](https://www.ritlabs.com/en/products/tinyweb/install.php). It binds to port `9191` by default, and can be configured in the options. It also binds to the local internal address so the files are only accessible to the overlay.