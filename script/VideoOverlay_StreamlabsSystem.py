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

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------------------
#   [Required] Script Information
#---------------------------------------
ScriptName = "Video Overlay"
Website = "darthminos.tv"
Description = "Video overlay that plays a video from the command"
Creator = "DarthMinos"
Version = "1.0.0-snapshot"

# ---------------------------------------
#	Set Variables
# ---------------------------------------


SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
AliasesFile = os.path.join(os.path.dirname(__file__), "aliases.json")
ReadMeFile = os.path.join(os.path.dirname(__file__), "ReadMe.txt")
ScriptSettings = None
CommandList = None
Aliases = None


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
            self.Command = "!vo"
            self.APIKey = ""
            self.Permission = "Everyone"
            self.VideoPath = "videos/"
            self.Cooldown = 10

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

def RunVideo(group, action):
    # Broadcast WebSocket Event
    payload = {
        "group": group,
        "action": action
    }
    Parent.BroadcastWsEvent("EVENT_VIDEO", json.dumps(payload))
    return

def GetValidArguments(group):
    global FullVideosPath
    path = os.path.join(os.path.dirname(__file__),ScriptSettings.VideoPath + "/" + group)
    ValidCommands = [name.lower().replace(".webm", "") for name in os.listdir(path) if re.match(r'^.*\.webm$', name)]
    Parent.Log(ScriptName, ", ".join(ValidCommands))
    return ValidCommands

def ExistsInAliases(command):
    Parent.Log(ScriptName, ", ".join(Aliases.keys()))
    if command in Aliases.keys():
        Parent.Log(ScriptName, "YES")
        return True
    else:
        Parent.Log(ScriptName, "NO")
        return False
    return

#---------------------------------------
#   [Required] Initialize Data / Load Only
#---------------------------------------
def Init():
    """ Initialize script or startup or reload. """
    Parent.Log(ScriptName, "Initialize")
    # Globals
    global ScriptSettings
    global Aliases
    global CommandList

    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)
    Aliases = Aliases(AliasesFile).__dict__
    FullVideosPath = os.path.join(os.path.dirname(__file__),ScriptSettings.VideoPath)
    Parent.Log(ScriptName, FullVideosPath)
    CommandList = ['!' + name.lower() for name in os.listdir(FullVideosPath) ]
    # Parent.Log(ScriptName, "Commands:")
    # Parent.Log(ScriptName, ''.join([str(x) + ',' for x in CommandList]))
    return

def Execute(data):
    if data.IsChatMessage():
        commandTrigger = data.GetParam(0).lower()
        #   Check if the proper command is used, the command is not on cooldown and the user has permission to use the command
        if commandTrigger == ScriptSettings.Command and not Parent.IsOnCooldown(ScriptName, commandTrigger):
            Parent.SendTwitchMessage(data.User + " you can trigger alerts with the following commands. " + " ?, ".join(CommandList) + " ?")
        elif ExistsInAliases(commandTrigger):
            alias = random.choice(Aliases.get(commandTrigger))
            RunVideo(alias.get("group"), alias.get("action"))
        elif data.GetParam(0).lower() in CommandList:
            group = commandTrigger.strip("!")
            if not Parent.IsOnCooldown(ScriptName, commandTrigger):
                if Parent.HasPermission(data.User, ScriptSettings.Permission, ""):
                    Parent.Log(ScriptName, "Param Count: " + str(data.GetParamCount()))
                    validActions = GetValidArguments(group)
                    action = random.choice(validActions)
                    if data.GetParamCount() >= 2:
                        action = data.GetParam(1).lower()
                        if action in validActions:
                            RunVideo(group, action)
                        elif action == "?":
                            Parent.SendTwitchMessage(data.User + ", Usage for !" + group + " [" + ", ".join(validActions) + "]")
                        else:
                            Parent.Log(ScriptName, "Action `" + action + "` is not valid")
                    elif data.GetParamCount() <= 1:
                        # random
                        RunVideo(group, action)
                    else:
                        Parent.Log(ScriptName, "Sent " + data.GetParamCount() - 1 + " params, expected 0 or 1. Message: " + data.Message)
                else:
                    # no permission
                    Parent.Log(ScriptName, "Permission Denied for {data.User}".format())
                Parent.AddCooldown(ScriptName, "!" + group, ScriptSettings.Cooldown)
            else:
                Parent.Log(ScriptName, commandTrigger + " is currently on cooldown")
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
    """ Open the script readme file in users default .txt application. """
    os.startfile(ReadMeFile)
    return
