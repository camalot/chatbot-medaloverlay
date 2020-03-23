## MEDAL OVERLAY

[![](https://i.imgur.com/bby6d49.png)](https://medal.tv/invite/DarthMinos)

This is a [StreamLabs Chatbot](https://streamlabs.com/chatbot) Script that allows chat to trigger a [Medal](https://medal.tv/) clip creation, and then play the clip back on stream.  

This will trigger playback on stream if your community triggers the clip creation, or if you press the hotkey to trigger a clip.

[![See Medal Overlay In Action](https://img.youtube.com/vi/q2mIDQ8BcW4/0.jpg)](https://www.youtube.com/watch?v=q2mIDQ8BcW4)

There is a second overlay that is available with this script that allows continuous playback of your uploaded Medal clips.

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

### COMMAND SETTINGS  

[![](https://i.imgur.com/zIEYb0jl.png)](https://i.imgur.com/zIEYb0j.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Clip Command` | The command to trigger the clip creation | `!clip` |
| `Permission Level` | The permission level required to trigger the command | `Everyone` |
| `Only Trigger off the Command` | If checked, only clips triggered by chat will show up in the overlay. | `False` |  
| `Notify Chat About Clip Status` | If checked, will send message to chat about the status of the clip. | `True` |  
| `Required Commands to Trigger` | The number of people required to say the command in chat to trigger the clip. | `1` |
| `Trigger Cooldown` | The amount of time, in seconds, that chat has to reach the required trigger count. | `60` |
| `Cooldown` | The amount of seconds between each allowed clip creation | `60` |

### STYLE SETTINGS


[![](https://i.imgur.com/llP13eNl.png)](https://i.imgur.com/llP13eN.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Video Width` | The width of the video. Height will scale automatically | `320` | 
| `Clip Frame Border` | The frame border to use. Select `custom` to use your own iamge | `default` | 
| `Clip Frame Border Custom Url` | The url to the custom image. | `''` | 
| `Progress Bar Fill Color` | The color of the progress bar fill color | `#ffb53b` |  
| `Progress Bar Background Color` | The color of the progress bar background | `transparent` |  
| `In Transition` | The video entrance transition when the video initially loads | `slideInDown` | 
| `Out Transition` | The video exit transition when the video ends | `slideOutDown` | 
| `EDIT ADVANCED CSS` | Opens the `custom.css` file for editing. | |



### MEDAL SETTINGS  

[![](https://i.imgur.com/z6p6eDx.png)](https://i.imgur.com/z6p6eDx.png)  


| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Username` | Your Medal Username | `""` | 
| `User ID` | Your Medal User ID. This is the end of the url after you go to `https://medal.tv/YOUR_USERNAME`. This is used for the `RECENT CLIPS` overlay.  | `""` | 
| `HotKey` | Your Medal HotKey in [SendKeys Format](SendKeys.md) | `{F8}` | 
| `Videos Path` | The path to your Medal Videos | `` | 


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

### PLAYBACK
[![](https://i.imgur.com/lH7kBw5l.png)](https://i.imgur.com/lH7kBw5.png)  

| ITEM | DESCRIPTION | 
| ---- | ----------- | 
| `OPEN OVERLAY IN BROWSER` | Opens the Overlay page in browser for testing | 
| `PLAY MOST RECENT VIDEO` | Plays the most recent video | 
| `PLAY RANDOM VIDEO` | Plays a random video | 
| `STOP CURRENT VIDEO` | Stops the current video | 


### RECENT CLIPS
> Settings and controls for the `Recent Clips` Overlay.

[![](https://i.imgur.com/fS1cbG9l.png)](https://i.imgur.com/fS1cbG9.png)

| ITEM | DESCRIPTION | DEFAULT |
| ---- | ----------- | -------- |
| `Use Non-Watermarked Videos` | This will enable non-watermarked videos if checked, a private key is supplied, and that private key has been granted `Special Privileges`. | `false` | 
| `Private API Key` | This key is your personal private key to access the medal api. It allows you to use non-watermarked playback of clips | `""` | 
| `Generate Private API Key` | Generate a private api key for access to medal api |  | 
| `Special Privileges Form` | Complete the form to get `Special Privileges` to use non-watermarked videos. |  | 
| `Shuffle Videos` | Shuffle the videos on playback | `false` | 
| `Video Volume` | The playback volume of the video | `100` | 
| `Mute Playback Audio` | Mute the playback audio of the video | `false` | 
| `Show Playback Progress Bar` | Show a playback progress bar at on the video. | `true` | 
| `Open Recent Clips Overlay In Browser` | Opens the `Recent Clips` overlay file in your browser, to get the path for OBS, or to test out the playback. |  | 
| `Play` | Start playback, if stopped |  | 
| `Stop` | Stop playback, if playing |  | 
| `Mute/Unmute` | Toggle mute state of the video. |  | 


### TWITCH CLIP IMPORT (BETA)

Automatically import twitch clips to your Medal account. At most, it will find the 5 most recent clips, and import those. 

[![](https://i.imgur.com/3mOYNfKl.png)](https://i.imgur.com/3mOYNfK.png)

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Enable Twitch Clip Auto Import` | Should the auto import of twitch clips to medal be enabled | `false` | 
| `Twitch App Client ID` | The Twitch Client ID. Click the button `Get Your Twitch Client Id Here` and complete the form to retrieve the client id | `""` |
| `Poll Rate (minutes)` | The number of minutes between polling for new created clips | `1` | 
| `Video Privacy` | The privacy level of the video. | `Public` |

### ADVANCED SETTINGS

[![](https://i.imgur.com/r2xsWgKl.png)](https://i.imgur.com/r2xsWgK.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Web Port` | The mort used for the http server for the media files | `9191` | 



### INFORMATION  

[![](https://i.imgur.com/R6rH8XLl.png)](https://i.imgur.com/R6rH8XL.png)  

| ITEM | DESCRIPTION | 
| ---- | ----------- | 
| `GET MEDAL` | Opens a link to get Medal | 
| `FOLLOW ME ON MEDAL` | Opens a link to follow me on Medal | 
| `FOLLOW ME ON TWITCH` | Opens a link to follow me on Twitch | 
| `OPEN README` | Opens the link to this document | 
| `OPEN SENDKEYS DOCS` | Opens the link to the [SendKeys](SendKeys.md) documentation | 
| `CHECK FOR UPDATES` | Will Check if there are updates to the Medal Overlay Script. See below for more info. | 
| `SAVE SETTINGS` | Save any changes to the Medal Overlay settings | 


## MEDAL OVERLAY UPDATER

> **NOTE:** You must launch from within Streamlabs Chatbot. 

The application will open, and if there is an update it will tell you. You click on the `Download & Update` button. 

> **NOTE:** Applying the update will close down Streamlabs Chatbot. It will reopen after the update is complete.

[![](https://i.imgur.com/YKIGYDul.png)](https://i.imgur.com/YKIGYDu.png)

## OVERLAY SETUP IN OBS / SLOBS 

- Add a new `Browser Source` in OBS / SLOBS  
[![](https://i.imgur.com/TAMQkeql.png)](https://i.imgur.com/TAMQkeq.png)
- Set as a `Local File` and choose the `overlay.html` in the `Medal Overlay` script directory. You can easily get to the script directory location from right clicking on `Medal Overlay` and choose `Open Script Folder`.
- Set the `width` and `height` to the resolution of your `Base (Canvas) Resolution`. 
- Add any additional custom CSS that you would like to add.
- Check both `Shutdown source when not visible` and `Refresh browser when scene becomes active`.  
[![](https://i.imgur.com/nouqPh0l.png)](https://i.imgur.com/nouqPh0.png)


## RECENT CLIPS SETUP IN OBS / SLOBS 
See Above for sample images on these steps.

- Add a new `Browser Source` in OBS / SLOBS  
- Set as a `Local File` and choose the `recents.html` in the `Medal Overlay` script directory. You can easily get to the script directory location from right clicking on `Medal Overlay` and choose `Open Script Folder`.
- Set the `height` and `width` to the size you would like the video to be on your scene. 
- Add any additional custom CSS that you would like to add.
- Check both `Shutdown source when not visible` and `Refresh browser when scene becomes active`.  


## CUSTOM CSS

You can customize the look with custom css to add a border, or other styles to the video. Just edit the `custom.css` file, or you can use the `custom css` in SLOBS/OBS. 

Here is an example that uses a background uploaded to imgur.
```css
#video-container .video-box {
  /* This is the container that holds the video-border-box and the video elements */
}

#video-container .video-box .video-border-box {
	/* This container sits directly on top of the video and is sized the same as the video */
}

#video-container .video-box video {
	/* This is the video container */
}

progress[value] {
	/* change the height and position of the progress bar */
	/* height: 7px; */
	/* left: 113px; */
	/* padding: 0 113px 0 0 */
	/* margin: 0 0 3px 0 */
}

progress::-webkit-progress-value {
	/* set the bar color */
  /*background: #57d12a;*/
}

```

[Pre-made borders](https://imgur.com/a/5PTkzhR)  
[![](https://i.imgur.com/qxxcsWgl.png)](https://i.imgur.com/qxxcsWg.png)

Here is a sample
![](https://i.imgur.com/OMF0MKf.png)


## TECHNICAL INFORMATION

Files are served to the overlay via a lightweight http server called [tinyweb](https://www.ritlabs.com/en/products/tinyweb/install.php). It binds to port `9191` by default, and can be configured in the options. It also binds to the local internal address so the files are only accessible to the overlay. If you run chatbot on a different machine than you run OBS/SLOBS there will be an issue and it will not function correctly.