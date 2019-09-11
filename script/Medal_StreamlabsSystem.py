#---------------------------------------
#   Import Libraries
#---------------------------------------
import sys
import clr
import json
import codecs
import os
import re
import random
import datetime
import glob
import time
import threading
import shutil
import tempfile

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

sys.path.append(os.path.join(os.path.dirname(__file__), "Libs"))
clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "./Libs/MedalRunner.dll"))
import MedalRunner

#---------------------------------------
#   [Required] Script Information
#---------------------------------------
ScriptName = "Medal Overlay"
Website = "darthminos.tv"
Description = "Triggers Medal.tv and plays the video back on stream"
Creator = "DarthMinos"
Version = "1.0.0-snapshot"
MedalInviteUrl = "https://medal.tv/invite/"
MedalPublicApiKey = "pub_YiUDXfg4MRtOrIeeWOV4v26foDP6QTcY"
# ---------------------------------------
#	Set Variables
# ---------------------------------------


SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
ReadMeFile = "https://github.com/camalot/chatbot-medaloverlay/blob/develop/ReadMe.md"
ScriptSettings = None

CurrentClipId = None
LastClipTriggerUser = None
ClipWatcher = None
ProcessManager = None
Initialized = False

TriggerCooldownTime = None
TriggerCount = 0
TriggerList = []
# ---------------------------------------
#	Script Classes
# ---------------------------------------

class Settings(object):
    """ Class to hold the script settings, matching UI_Config.json. """

    def __init__(self, settingsfile=None):
        """ Load in saved settings file if available else set default values. """
        try:
            self.Command = "!clip"
            self.Permission = "Everyone"
            self.VideoPath = ""
            self.Cooldown = 60
            self.HotKey = "{F8}"
            self.Username = ""
            self.UserId = ""
            self.PositionVertical = "Middle"
            self.PositionHorizontal = "Right"
            self.InTransition = "slideInLeft"
            self.OutTransition = "slideOutRight"
            self.AbsolutePositionTop = 0
            self.AbsolutePositionLeft = 0
            self.AbsolutePositionBottom = 0
            self.AbsolutePositionRight = 0
            self.VideoWidth = 320
            self.UsePositionVertical = True
            self.UsePositionHorizontal = True
            self.WebPort = 9191
            # self.OverlayWebPort = 9292
            self.OnlyTriggerOffCommand = False
            self.TriggerCooldown = 60
            self.RequiredTriggerCount = 1
            self.NotifyChatOfClips = True
            self.VideoFrameCustomBackground = None
            self.VideoFrameBackground = "default"
            self.ProgressBarFillColor = "#ffb53b"
            self.ProgressBarBackgroundColor = "transparent"
            self.PublicApiKey = MedalPublicApiKey
            self.PrivateApiKey = ""
            self.RecentMuteAudio = False
            self.RecentVolume = 100
            self.RecentShowVideoProgress = True
            self.UseNonWatermarkedVideo = False
            self.RecentShowTitle = True
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                fileSettings = json.load(f, encoding="utf-8")
                self.__dict__.update(fileSettings)

        except Exception as e:
            Parent.Log(ScriptName, str(e))

    def Reload(self, jsonData):
        """ Reload settings from the user interface by given json data. """
        Parent.Log(ScriptName, "Reload Settings")
        fileLoadedSettings = json.loads(jsonData, encoding="utf-8")
        self.__dict__.update(fileLoadedSettings)

#---------------------------------------
#   Functions
#---------------------------------------


#---------------------------------------
# Starts the mohttpd executable to serve the media files
#---------------------------------------
def StartHttpd(app, webdir, port):
    tool = os.path.join(os.path.dirname(__file__), "./Libs/mohttpd.exe")
    # copytool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./Libs/" + app + "/mohttpd.exe")
    # if not os.path.exists(copytool):
    #     shutil.copyfile(tool, copytool)
    index = os.path.join(webdir, "./index.html")
    if not os.path.exists(index):
        with open(index, 'w'): pass
    Parent.Log(ScriptName, tool + " \"" + webdir + "\" " + str(port) + " 127.0.0.1")
    os.spawnl(os.P_NOWAITO, tool, tool, webdir, str(port), "127.0.0.1")
    return

def ReloadOverlay():
    Parent.Log(ScriptName, "EVENT_MEDAL_RELOAD: " + json.dumps(None))
    Parent.BroadcastWsEvent("EVENT_MEDAL_RELOAD", json.dumps(None))
    return
def PlayVideoById(videoId):
    # Broadcast WebSocket Event
    payload = {
        "port": ScriptSettings.WebPort,
        "video": str(videoId) + ".mp4"
    }
    Parent.Log(ScriptName, "EVENT_MEDAL_PLAY: " + json.dumps(payload))
    Parent.BroadcastWsEvent("EVENT_MEDAL_PLAY", json.dumps(payload))

#---------------------------------------
# Event Handler for ClipWatcher.ClipReady
#---------------------------------------
def OnClipReady(sender, eventArgs):
    try:
        global CurrentClipId
        global LastClipTriggerUser

        if ScriptSettings.OnlyTriggerOffCommand and CurrentClipId is None:
            return

        if CurrentClipId != eventArgs.ClipId:
            # This clip is not one we expected.
            return

        triggerUser = Parent.GetChannelName()
        if LastClipTriggerUser is not None:
            triggerUser = LastClipTriggerUser
        if ScriptSettings.NotifyChatOfClips:
            Parent.SendTwitchMessage(triggerUser + ", clip processing completed. Video will play shortly.")
        Parent.Log(ScriptName, "Event: ClipReady: " + eventArgs.ClipId)

        PlayVideoById(eventArgs.ClipId)

        CurrentClipId = None
        LastClipTriggerUser = None
    except Exception as e:
        Parent.Log(ScriptName, str(e))
    return

#---------------------------------------
# Event Handler for ClipWatcher.ClipStarted
#---------------------------------------
def OnClipStarted(sender, eventArgs):
    global CurrentClipId
    global TriggerCooldownTime
    global TriggerCount

    if(ScriptSettings.OnlyTriggerOffCommand and CurrentClipId is None):
        return

    if CurrentClipId == eventArgs.ClipId:
        # This clip already triggered.
        return

    TriggerCooldownTime = None
    TriggerCount = 0
    CurrentClipId = eventArgs.ClipId
    triggerUser = Parent.GetChannelName()
    if LastClipTriggerUser is not None:
        triggerUser = LastClipTriggerUser
    # Add a cooldown on the command since a clip is currently processing.
    Parent.AddCooldown(ScriptName, ScriptSettings.Command, ScriptSettings.Cooldown)
    if ScriptSettings.NotifyChatOfClips:
        Parent.SendTwitchMessage(triggerUser + " has triggered a medal.tv clip. Clip is processing...")
    Parent.Log(ScriptName, "Event: ClipStarted: " + eventArgs.ClipId)
    return

#---------------------------------------
# Event Handler for ClipWatcher.MonitorStart
#---------------------------------------
def OnMonitorStart(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorStart")
    return
#---------------------------------------
# Event Handler for ClipWatcher.MonitorStop
#---------------------------------------
def OnMonitorStop(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorStop")
    return
#---------------------------------------
# Event Handler for ClipWatcher.MonitorPause
#---------------------------------------
def OnMonitorPause(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorPause")
    return


#---------------------------
#   Chatbot Functions
#---------------------------

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    """ Initialize script or startup or reload. """
    # Globals
    global ScriptSettings
    global ClipWatcher
    global ProcessManager
    global Initialized

    if Initialized:
        Parent.Log(ScriptName, "Skip Initialization. Already Initialized.")
        return

    Parent.Log(ScriptName, "Initialize")
    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)
    if ScriptSettings.VideoPath == "":
        Parent.Log(ScriptName, "Video Path Not Currently Set.")
        return

    webDirectory = os.path.join(os.path.dirname(__file__), ScriptSettings.VideoPath)


    customcss = os.path.join(os.path.dirname(__file__), "./custom.css")
    csstemplate = os.path.join(os.path.dirname(__file__), "./custom-sample.css")
    if not os.path.exists(customcss):
        shutil.copyfile(csstemplate, customcss)

    if not os.path.exists(webDirectory):
        Parent.Log(ScriptName, "Video Path Does Not Exist: " + webDirectory)
        return

    ProcessManager = MedalRunner.Process()
    ClipWatcher = MedalRunner.Watcher(webDirectory)
    ClipWatcher.ClipReady += OnClipReady
    ClipWatcher.ClipStarted += OnClipStarted
    ClipWatcher.MonitorStart += OnMonitorStart
    ClipWatcher.MonitorStop += OnMonitorStop
    ClipWatcher.MonitorPause += OnMonitorPause
    ClipWatcher.Start()
    StartHttpd("mohttpd", webDirectory, ScriptSettings.WebPort)
    # StartHttpd("overlayhttpd", os.path.dirname(os.path.abspath(__file__)), ScriptSettings.OverlayWebPort)
    Initialized = True
    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    global CurrentClipId
    global LastClipTriggerUser
    global TriggerCooldownTime
    global TriggerCount
    global TriggerList

    if data.IsChatMessage():
        commandTrigger = data.GetParam(0).lower()
        if not Parent.IsOnCooldown(ScriptName, commandTrigger):
            if commandTrigger == "!medal":
                Parent.AddCooldown(ScriptName, commandTrigger, ScriptSettings.Cooldown)
                Parent.SendTwitchMessage("The Medal desktop client records clips with one button press, posts them on medal.tv, and gives you a shareable link. No lag, no fuss. " +
                "Get Medal and follow " + Parent.GetChannelName() + ". " + MedalInviteUrl + ScriptSettings.Username + " - Use command " + ScriptSettings.Command +
                " in the chat to trigger a clip.")
            elif commandTrigger == "!medaloverlay":
                Parent.AddCooldown(ScriptName, commandTrigger, ScriptSettings.Cooldown)
                Parent.SendTwitchMessage("Medal Overlay is a StreamLabs Chatbot Script developed by DarthMinos: https://twitch.tv/darthminos To Download or find out more visit https://github.com/camalot/chatbot-medaloverlay")
            elif commandTrigger == ScriptSettings.Command:
                if Parent.HasPermission(data.User, ScriptSettings.Permission, ""):
                    if data.User in TriggerList:
                        Parent.Log(ScriptName, "User already triggered the command. Skipping.")
                        return
                    TriggerList.append(data.User)
                    TriggerCount += 1
                    # only add normal cooldown if TriggerCount >= RequiredTriggerCount
                    if TriggerCount >= ScriptSettings.RequiredTriggerCount:
                        Parent.AddCooldown(ScriptName, commandTrigger, ScriptSettings.Cooldown)
                        # Get the time stamp format that is used of the file name.
                        LastClipTriggerUser = data.User
                        CurrentClipId = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        Parent.Log(ScriptName, "Sending HotKey: " + ScriptSettings.HotKey)
                        MedalRunner.Keys.SendKeys(ScriptSettings.HotKey)
                        TriggerCount = 0
                        TriggerCooldownTime = None
                        TriggerList = []
                    else:
                        triggerDiff = ScriptSettings.RequiredTriggerCount - TriggerCount
                        if TriggerCount == 1:
                            Parent.Log(ScriptName, "init clip trigger.")
                            TriggerCooldownTime = datetime.datetime.now() + datetime.timedelta(seconds=ScriptSettings.TriggerCooldown)
                            if ScriptSettings.NotifyChatOfClips:
                                Parent.SendTwitchMessage(data.User + " has initialized a medal.tv clip. Need " + str(triggerDiff) + " more to generate the clip.")
                        else:
                            Parent.Log(ScriptName, "Additional trigger of clip generation.")
                            if ScriptSettings.NotifyChatOfClips:
                                Parent.SendTwitchMessage(data.User + " triggered a medal.tv clip. Need " + str(triggerDiff) + " more to generate the clip.")
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters)
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    # if "$myparameter" in parseString:
    #     return parseString.replace("$myparameter","I am a cat!")

    return parseString

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    global Initialized
    global ClipWatcher
    Parent.Log(ScriptName, "Unload")
    Parent.Log(ScriptName, "Kill mohttpd Process")
    stop = ProcessManager.Stop("mohttpd")
    Parent.Log(ScriptName, stop)
    Parent.Log(ScriptName, "Killed mohttpd Process")

    if ClipWatcher is not None:
        Parent.Log(ScriptName, "Clear ClipWatcher Events")
        ClipWatcher.ClipReady -= OnClipReady
        ClipWatcher.ClipStarted -= OnClipStarted
        ClipWatcher.MonitorStart -= OnMonitorStart
        ClipWatcher.MonitorStop -= OnMonitorStop
        ClipWatcher.MonitorPause -= OnMonitorPause
        ClipWatcher.Stop()
        ClipWatcher = None

    Initialized = False
    # End of Unload
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    Parent.Log(ScriptName, "State Changed: " + str(state))
    if state:
        Init()
    else:
        Unload()
    return

# ---------------------------------------
# [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
# ---------------------------------------
def ReloadSettings(jsondata):
    Parent.Log(ScriptName, "Reload Settings")
    # Reload saved settings and validate values
    Unload()
    Init()
    ReloadOverlay()
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    global TriggerCooldownTime
    global TriggerCount
    global TriggerList
    if TriggerCooldownTime is not None and datetime.datetime.now() >= TriggerCooldownTime:
        TriggerCooldownTime = None
        TriggerCount = 0
        TriggerList = []
        Parent.Log(ScriptName, "Reset clip trigger due to cooldown exceeded")
        if ScriptSettings.NotifyChatOfClips:
            Parent.SendTwitchMessage("Medal.tv clip generation did not get the required triggers of " + str(ScriptSettings.RequiredTriggerCount) + " to generate the clip.")
    return

# ---------------------------------------
# Script UI Button Functions
# ---------------------------------------
def OpenReadMeLink():
    os.startfile(ReadMeFile)
    return
def OpenSendKeysLink():
    os.startfile("https://github.com/camalot/chatbot-medaloverlay/blob/develop/SendKeys.md")
    return
def OpenMedalInviteLink():
    os.startfile("https://medal.tv/invite/DarthMinos")
    return
def OpenDownloadMedalLink():
    os.startfile("https://medal.tv/?ref=DarthMinos_partner")
    return
def OpenFollowOnTwitchLink():
    os.startfile("https://twitch.tv/DarthMinos")
    return
def OpenDonateLink():
    os.startfile("https://twitch.tv/DarthMinos")
    return
def OpenScriptUpdater():
    currentDir = os.path.realpath(os.path.dirname(__file__))
    chatbotRoot = os.path.realpath(os.path.join(currentDir, "../../../"))
    libsDir = os.path.join(currentDir, "Libs/")
    Parent.Log(ScriptName, libsDir)
    try:
        src_files = os.listdir(libsDir)

        tempdir = tempfile.mkdtemp()
        Parent.Log(ScriptName, tempdir)
        for file_name in src_files:
            full_file_name = os.path.join(libsDir, file_name)
            if os.path.isfile(full_file_name) and file_name != "mohttpd.exe" and "_log" not in file_name:
                Parent.Log(ScriptName, "Copy: " + full_file_name)
                shutil.copy(full_file_name, tempdir)
        updater = os.path.join(tempdir, "MedalOverlayUpdater.exe")
        updaterConfigFile = os.path.join(tempdir, "chatbot.json")
        updaterConfig = {
            "path": os.path.realpath(os.path.join(currentDir,"../")),
            "version": Version,
            "chatbot": os.path.join(chatbotRoot, "Streamlabs Chatbot.exe")
        }
        Parent.Log(ScriptName, updater)
        configJson = json.dumps(updaterConfig)
        Parent.Log(ScriptName, configJson)
        with open(updaterConfigFile, "w+") as f:
            f.write(configJson)
        os.startfile(updater)
    except OSError as exc: # python >2.5
        raise

def OpenOverlayPreview():
    os.startfile(os.path.realpath(os.path.join(os.path.dirname(__file__), "overlay.html")))
def StopCurrentVideo():
    Parent.BroadcastWsEvent("EVENT_MEDAL_STOP", None)
def PlayRandomVideo():
    randomVideo = random.choice(glob.glob(ScriptSettings.VideoPath + "/*.mp4"))
    if randomVideo is not None:
        videoId = os.path.splitext(os.path.basename(randomVideo))[0]
        PlayVideoById(videoId)
def PlayMostRecent():
    fileList = glob.glob(ScriptSettings.VideoPath + "/*.mp4")
    if fileList is not None and fileList is not []:
        mostRecent = max(fileList, key=os.path.getctime)
        videoId = os.path.splitext(os.path.basename(mostRecent))[0]
        PlayVideoById(videoId)

def OpenCustomCSSFile():
    customcss = os.path.join(os.path.dirname(__file__), "./custom.css")
    os.startfile(customcss, "edit")

def OpenSpecialPrivileges():
    os.startfile("https://docs.google.com/forms/d/e/1FAIpQLSeLxbs1UchRGT6Nb6WYD_0gO7821SbRrAnDYjqVOXNrPBrJ4g/viewform")

def GeneratePrivateKey():
    os.startfile("https://developers.medal.tv/v1/generate_private_key")

def OpenOverlayRecents():
    os.startfile(os.path.realpath(os.path.join(os.path.dirname(__file__), "recents.html")))


def RecentPlayBackPlay():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_PLAY", None)
def RecentPlayBackStop():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_STOP", None)
def RecentPlayMute():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_MUTE", None)
def RecentPlayNext():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_SKIP", None)
