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
import signal

import SimpleHTTPServer
import SocketServer

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
# ---------------------------------------
#	Set Variables
# ---------------------------------------


SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
ReadMeFile = "https://github.com/camalot/chatbot-medaloverlay/blob/develop/ReadMe.md"
ScriptSettings = None

CurrentClipId = None
LastClipTriggerUser = None
ClipWatcher = None

# ---------------------------------------
#	Script Classes
# ---------------------------------------

class Settings(object):
    """ Class to hold the script settings, matching UI_Config.json. """

    def __init__(self, settingsfile=None):
        """ Load in saved settings file if available else set default values. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            self.Command = "!clip"
            self.Permission = "Everyone"
            self.VideoPath = "videos/"
            self.Cooldown = 60
            self.HotKey = "{F8}"
            self.Username = ""
            self.PositionVertical = "Middle"
            self.PositionHorizontal = "Right"
            self.InTransition = "SlideRight"
            self.OutTransition = "SlideRight"
            self.MaxInitWait = 2
            self.MaxFinishWait = 120
            self.AbsolutePositionTop = 0
            self.AbsolutePositionLeft = 0
            self.AbsolutePositionBottom = 0
            self.AbsolutePositionRight = 0
            self.VideoWidth = 320
            self.UsePositionVertical = True
            self.UsePositionHorizontal = True
            self.WebPort = 9191
            self.OnlyTriggerOffCommand = False

    def Reload(self, jsonData):
        """ Reload settings from the user interface by given json data. """
        self.__dict__ = json.loads(jsonData, encoding="utf-8")

class Aliases(object):
    def __init__(self, source=None):
        try:
            with codecs.open(source, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            Parent.Log(ScriptName, "Error loading `" + source + "` file")

    def Reload(self, jsonData):
        """ Reload settings from the user interface by given json data. """
        self.__dict__ = json.loads(jsonData, encoding="utf-8")
# ---------------------------------------
#	Functions
# ---------------------------------------

def StartHttpd(webdir, port):
    tool = os.path.join(os.path.dirname(__file__), "./Libs/mohttpd.exe")
    index = os.path.join(webdir, "./index.html")
    if not os.path.exists(index):
        with open(index, 'w'): pass
    Parent.Log(ScriptName, "ROOT DIRECTORY: " + webdir)
    Parent.Log(ScriptName, tool + " \"" + webdir + "\" " + str(port) + " 127.0.0.1")
    os.spawnl(os.P_NOWAITO, tool,tool, webdir, str(port), "127.0.0.1")
    return

def OnClipReady(sender, eventArgs):
    try:
        global CurrentClipId
        global LastClipTriggerUser

        if(ScriptSettings.OnlyTriggerOffCommand and CurrentClipId is None):
            return

        triggerUser = Parent.GetChannelName()
        if(LastClipTriggerUser is not None):
            triggerUser = LastClipTriggerUser

        Parent.SendTwitchMessage(triggerUser + ", clip processing completed. Video will play shortly.")
        Parent.Log(ScriptName, "Event: ClipReady: " + eventArgs.ClipId)

        # Broadcast WebSocket Event
        payload = {
            "port": ScriptSettings.WebPort,
            "video": str(eventArgs.ClipId) + ".mp4"
        }
        Parent.Log(ScriptName, "EVENT_MEDAL_PLAY: " + json.dumps(payload))
        Parent.BroadcastWsEvent("EVENT_MEDAL_PLAY", json.dumps(payload))

        CurrentClipId = None
        LastClipTriggerUser = None
    except Exception as e:
        Parent.Log(ScriptName, str(e.message))
    return

def OnClipStarted(sender, eventArgs):
    if(ScriptSettings.OnlyTriggerOffCommand and CurrentClipId is None):
        return

    triggerUser = Parent.GetChannelName()
    if(LastClipTriggerUser is not None):
        triggerUser = LastClipTriggerUser

    Parent.SendTwitchMessage(triggerUser + " has triggered a medal.tv clip. Clip is processing...")
    Parent.Log(ScriptName, "Event: ClipStarted: " + eventArgs.ClipId)
    return

def OnMonitorStart(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorStart")
    return

def OnMonitorStop(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorStop")
    return
def OnMonitorPause(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorPause")
    return
#---------------------------------------
#   [Required] Initialize Data / Load Only
#---------------------------------------
def Init():
    """ Initialize script or startup or reload. """
    Parent.Log(ScriptName, "Initialize")
    # Globals
    global ScriptSettings
    global ClipWatcher

    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)
    Parent.Log(ScriptName, ScriptSettings.Command)

    webDirectory = os.path.join(os.path.dirname(__file__), ScriptSettings.VideoPath)
    ClipWatcher = MedalRunner.Watcher(webDirectory)
    ClipWatcher.ClipReady += OnClipReady
    ClipWatcher.ClipStarted += OnClipStarted
    ClipWatcher.MonitorStart += OnMonitorStart
    ClipWatcher.MonitorStop += OnMonitorStop
    ClipWatcher.MonitorPause += OnMonitorPause
    ClipWatcher.Start()
    StartHttpd(webDirectory, ScriptSettings.WebPort)
    return

def Execute(data):
    global CurrentClipId
    if data.IsChatMessage():
        commandTrigger = data.GetParam(0).lower()
        if commandTrigger == "!medal" and not Parent.IsOnCooldown(ScriptName, commandTrigger):
            Parent.AddCooldown(ScriptName, commandTrigger, ScriptSettings.Cooldown)
            Parent.SendTwitchMessage("The Medal desktop client records clips with one button press, posts them on medal.tv, and gives you a shareable link. No lag, no fuss. " +
            "Get Medal and follow " + ScriptSettings.Username + ". " + MedalInviteUrl + ScriptSettings.Username + " - Use command " + ScriptSettings.Command +
            " in the chat to trigger a clip.")
        elif commandTrigger == ScriptSettings.Command and not Parent.IsOnCooldown(ScriptName, commandTrigger):
            if not Parent.IsOnCooldown(ScriptName, commandTrigger):
                if Parent.HasPermission(data.User, ScriptSettings.Permission, ""):
                    Parent.AddCooldown(ScriptName, commandTrigger, ScriptSettings.Cooldown)
                    # Get the time stamp format that is used of the file name.
                    LastClipTriggerUser = data.User
                    CurrentClipId = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    Parent.Log(ScriptName, "Timestamp: " + CurrentClipId)
                    Parent.Log(ScriptName, "Sending HotKey: " + ScriptSettings.HotKey)
                    MedalRunner.Keys.SendKeys(ScriptSettings.HotKey)
            else:
                Parent.SendTwitchMessage(data.User + ", There is already an active clip being processed.")
                Parent.Log(ScriptName, "On Cooldown")
    return

def Parse(parseString, userid, username, targetid, targetname, message):
    # if "$myparameter" in parseString:
    #     return parseString.replace("$myparameter","I am a cat!")

    return parseString

def Unload():
    Parent.Log(ScriptName, "Unload")
    try:
        Parent.Log(ScriptName, "Kill mohttpd Process")
        os.spawnl(os.P_WAIT, "taskkill", "/IM", "mohttpd.exe", "/F")
        Parent.Log(ScriptName, "Killed mohttpd Process")
    except Exception as e:
        Parent.Log(ScriptName, e.message)

    if(ClipWatcher is not None):
        ClipWatcher.ClipReady -= OnClipReady
        ClipWatcher.ClipStarted -= OnClipStarted
        ClipWatcher.MonitorStart -= OnMonitorStart
        ClipWatcher.MonitorStop -= OnMonitorStop
        ClipWatcher.MonitorPause -= OnMonitorPause
        ClipWatcher.Stop()

    # End of Unload
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

# ---------------------------------------
# Chatbot Save Settings Function
# ---------------------------------------
def ReloadSettings(jsondata):
    """ Set newly saved data from UI after user saved settings. """
    Parent.Log(ScriptName, "Reload Settings")
    # Reload saved settings and validate values
    ScriptSettings.Reload(jsondata)
    return


def Tick():
    return

# ---------------------------------------
# Script UI Button Functions
# ---------------------------------------
def OpenReadMe():
    os.startfile(ReadMeFile)
    return
def OpenSendKeys():
    os.startfile("https://github.com/camalot/chatbot-medaloverlay/blob/develop/SendKeys.md")
    return
def OpenMedalInvite():
    os.startfile("https://medal.tv/invite/DarthMinos")
    return
