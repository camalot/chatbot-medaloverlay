## MEDAL OVERLAY

[![](https://i.imgur.com/bby6d49.png)](https://medal.tv/invite/DarthMinos)

This is a StreamLabs Chatbot Script that allows chat to trigger a [Medal](https://medal.tv/) clip creation, and then play the clip back on stream.


[![](https://i.imgur.com/btO3tM8m.gif)](https://i.imgur.com/btO3tM8.mp4)

## INSTALL

- Download the latest zip file from [Releases](https://github.com/camalot/chatbot-medaloverlay/releases)
- Extract to `[Chatbot Install Directory]/Services/Scripts/`
- Reload Scripts in StreamLabs Chatbot
- Right click on `Medal Overlay` and select `Insert API Key`. Click yes on the dialog.  
[![](https://i.imgur.com/Lk13yXml.png)](https://i.imgur.com/Lk13yXm.png)  

## CONFIGURATION

Make sure the script is enabled  
[![](https://i.imgur.com/JQcHol4l.png)](https://i.imgur.com/JQcHol4.png)  

Click on the script in the list to bring up the configuration.

### GENERAL SETTINGS  

[![](https://i.imgur.com/YSfPNiWl.png)](https://i.imgur.com/YSfPNiW.png)  

| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Clip Command` | The command to trigger the clip creation | `!clip` |
| `Permission Level` | The permission level required to trigger the command | `Everyone` |
| `Cooldown` | The amount of seconds between each allowed clip creation | `60` |
| `Clip Start Wait` | The amount of time (in seconds) that the bot will wait for Medal to start creating the clip | `2` |
| `Clip Complete Wait` | The amount of time (in seconds) that the bot will wait for Medal to complete the creation of the clip | `120` |

### MEDAL SETTINGS  

[![](https://i.imgur.com/dGo9JEAl.png)](https://i.imgur.com/dGo9JEA.png)  


| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Username` | Your Medal Username | `""` | 
| `HotKey` | Your Medal HotKey in [SendKeys Format](SendKeys.md) | `{F8}` | 
| `Videos Path` | The path to your Medal Videos | `videos/` | 

> **NOTE:** Changes this will require you to refresh the cache of the browser source in your broadcast software

### POSITION SETTINGS  

[![](https://i.imgur.com/MiVeB2Sl.png)](https://i.imgur.com/MiVeB2S.png)  


| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `Vertical` | Vertical position of the video | `Middle` | 
| `Horizontal` | Horizontal position of the video | `Right` | 

> **NOTE:** Changes this will require you to refresh the cache of the browser source in your broadcast software

### TRAMSITION SETTINGS  

[![](https://i.imgur.com/0Kzcmmvl.png)](https://i.imgur.com/0Kzcmmv.png)  


| ITEM | DESCRIPTION | DEFAULT | 
| ---- | ----------- | ------- | 
| `IN` | The video entrance transition when the video initially loads | `slideInDown` | 
| `OUT` | The video exit transition when the video ends | `slideOutDown` | 

> **NOTE:** Changes this will require you to refresh the cache of the browser source in your broadcast software

### INFORMATION  

[![](https://i.imgur.com/UYRuqdbl.png)](https://i.imgur.com/UYRuqdb.png)  

| ITEM | DESCRIPTION | 
| ---- | ----------- | 
| `GET MEDAL` | Opens a link to get Medal | 
| `OPEN README` | Opens the link to this document | 
| `OPEN SENDKEYS DOCS` | Opens the link to the [SendKeys](SendKeys.md) documentation | 
| `SAVE SETTINGS` | Save any changes to the Medal Overlay settings | 

## OBS / SLOBS  

- Add a new `Browser Source` in OBS / SLOBS  
[![](https://i.imgur.com/TAMQkeql.png)](https://i.imgur.com/TAMQkeq.png)
- Set as a `Local File` and choose the `Overlay.html` in the `Medal Overlay` script directory. You can easily get to the script directory location from right clicking on `Medal Overlay` and choose `Open Script Folder`.
- Set the `width` and `height` to the resolution of your `Base (Canvas) Resolution`. 
- Add any additional custom CSS that you would like to add.
- Check both `Shutdown source when not visible` and `Refresh browser when scene becomes active`.  
[![](https://i.imgur.com/nouqPh0l.png)](https://i.imgur.com/nouqPh0.png)