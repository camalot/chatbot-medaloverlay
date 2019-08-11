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

def RunVideo(video):
    # Broadcast WebSocket Event
    payload = {
        "video": video
    }
    Parent.Log(ScriptName, "EVENT_MEDAL_PLAY: " + json.dumps(payload))
    Parent.BroadcastWsEvent("EVENT_MEDAL_PLAY", json.dumps(payload))
    return

#---------------------------------------
#   [Required] Initialize Data / Load Only
#---------------------------------------
def Init():
    """ Initialize script or startup or reload. """
    Parent.Log(ScriptName, "Initialize")
    # Globals
    global ScriptSettings

    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)
    Parent.Log(ScriptName, ScriptSettings.Command)

    return

def WaitForFile(data, timestamp):
    path = os.path.join(os.path.dirname(__file__),ScriptSettings.VideoPath)
    waiting = True
    counter = 0
    max_file_wait = ScriptSettings.MaxInitWait * 10
    max_finish_wait = ScriptSettings.MaxFinishWait * 10

    Parent.Log(ScriptName, path + "/*" + timestamp + ".mp4")
    Parent.BroadcastWsEvent("EVENT_MEDAL_START", json.dumps({}))
    while(waiting):
        files = glob.glob(path + "/*" + timestamp + ".mp4")
        # if we found the video
        if(len(files) >= 1 or counter >= max_file_wait ):
            if(counter >= max_file_wait):
                Parent.BroadcastWsEvent("EVENT_MEDAL_VIDEO_TIMEOUT", json.dumps({
                    "counter": counter
                }))
                Parent.SendTwitchMessage(data.User + ", Processing took too long. The clip will still be created, just not shown.")
                return

            waiting = False
        else:
            counter += 1
            time.sleep(.1)
    waiting = True
    counter = 0
    while(waiting):
        thumbfiles = glob.glob(path + "/*" + timestamp + "-thumbnail.jpg")
        # if we found the thumb
        if(len(thumbfiles) >= 1 or counter >= max_finish_wait ):
            if(counter >= max_finish_wait):
                Parent.SendTwitchMessage(data.User + ", Processing took too long. The clip will still be created, just not shown.")
                return
            waiting = False
        else:
            counter += 1
            time.sleep(.1)

    if(len(files) >= 1 and len(thumbfiles) >= 1):
        Parent.SendTwitchMessage(data.User + ", clip processing completed. Video will play shortly.")
        filename = os.path.basename(files[0])
        Parent.Log(ScriptName, "Clip Processing Completed: " + filename)
        RunVideo(filename)
    else:
        Parent.Log(ScriptName, path + "/*" + timestamp + ".mp4")
def Execute(data):
    if data.IsChatMessage():
        commandTrigger = data.GetParam(0).lower()
        if commandTrigger == "!medal"and not Parent.IsOnCooldown(ScriptName, commandTrigger):
            Parent.AddCooldown(ScriptName, commandTrigger, ScriptSettings.Cooldown)
            Parent.SendTwitchMessage("The Medal desktop client records clips with one button press, posts them on medal.tv, and gives you a shareable link. No lag, no fuss. " +
            "Get Medal and follow me " + MedalInviteUrl + ScriptSettings.Username)
        elif commandTrigger == ScriptSettings.Command and not Parent.IsOnCooldown(ScriptName, commandTrigger):
            if not Parent.IsOnCooldown(ScriptName, commandTrigger):
                if Parent.HasPermission(data.User, ScriptSettings.Permission, ""):
                    Parent.AddCooldown(ScriptName, commandTrigger, ScriptSettings.Cooldown)

                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    Parent.Log(ScriptName, "Timestamp: " + timestamp)
                    Parent.SendTwitchMessage(data.User + " has triggered a medal.tv clip. Clip is processing...")
                    MedalRunner.Keys.SendKeys(ScriptSettings.HotKey)
                    thr = threading.Thread(target=WaitForFile, args=(data, timestamp), kwargs={})
                    thr.start()
            else:
                Parent.SendTwitchMessage(data.User + ", There is already an active clip being processed.")
                Parent.Log(ScriptName, "On Cooldown")
        else:
            Parent.Log(ScriptName, "Not my problem")
    return

def Unload():
    Parent.Log(ScriptName, "Unload")
    # End of Unload
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
