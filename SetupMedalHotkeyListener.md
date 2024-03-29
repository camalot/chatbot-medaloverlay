# HOW TO SETUP FOR MULTI-PC

1. [DATA ACCESS](#data-access)
2. [TRIGGERING CLIP](#triggering-clip)

Follow these steps to set that up.

## TERMS

- `Game PC`: This is the PC that you game on. This is the PC that is running Medal.
- `Chatbot PC`: This is the PC that runs chatbot. If you run this on the same system as your games, you do not need this setup.

## DATA ACCESS

The medaloverlay chatbot script needs access to multiple files and folders that are used by Medal. We can gain access to them via network shares. The script only needs read access.

- `%APPDATA%\Medal\Store` - This path is used to get some settings information like your Medal UserName, UserId, and Path to where you store your clips.
  The easiest way to set this up is to install Medal on both your Game PC and your Stream PC. Alternatively, you can follow the SHARE method below to accomplish this as well.
- `CLIPS_FOLDER` - This one is even harder. Because the path that Medal uses, needs to be the SAME path on your Chatbot PC. So if the clips folder is `C:\users\my_user\Videos\Medal`, that EXACT folder needs to exist on the chatbot PC. 

Setting up Shares and Symbolic Links.

- Install [Link Shell Extension](https://schinagl.priv.at/nt/hardlinkshellext/linkshellextension.html) on the Chatbot PC
- On Game PC
  - Navigate to your Medal Clips folder Parent. In my case, the path is `C:\Users\darthminos\Videos\MedalClips`, so I am going to navigate to `C:\Users\darthminos\Videos`. We are actually going to go UP 1 folder from there. So we are at `C:\Users\darthminos\`.
  - Right Click the Parent folder and click *Properties* (ex: `C:\Users\darthminos\Videos`)  
  - Select the Sharing Tab  
  ![](https://i.imgur.com/Ob1v960.png)
  - Click on *Advanced Sharing* and check *Share this folder*  
  ![](https://i.imgur.com/3tTraBS.png)
  - Click *OK* and then *Close*
- Now on the **CHATBOT PC** 
  - Navigate to that share. It should look something like this (You will probably have other folders and files in your path)  
  ![](https://i.imgur.com/sjXecqG.png)
  - Right Click on the MedalClips folder (your folder name may be different) and choose *Pick Link Source*  
 ![](https://i.imgur.com/321Bbs7.png)
  - Navigate to `C:\Users\darthminos\Videos` on the Chatbot PC (using the same path you have on your Game PC).
  - Right click in that folder and choose `Drop As > Symbolic Link`  
  ![](https://i.imgur.com/Dwx0dZu.png)
  - Now you will see the `MedalClips` folder in your `Videos` folder on the Chatbot PC.


For the `%APPDATA%\Medal\Store` folder Do the exact same thing.

- Share `%APPDATA%\Medal on Game PC
- On Chatbot PC, create `%APPDATA%\Medal`
- *Pick Link Source* for `\\COMPUTER_NAME\Medal\Store`
- Navigate to `%APPDATA%\Medal` on Chatbot PC
- Right Click in that folder and `Drop As > Symbolic Link`

## TRIGGERING CLIP

To handle the trigging of the clip from the Chatbot PC to the Game PC we will use the MedalHotkeyListener.

This tool is a zip package that can be downloaded in the assets section of each release. It is meant to run on Game PC.

It will receive a command from the MedalOverlay Script telling that PC to trigger a Medal clip.

```
TODO: DOCUMENT THIS
```
