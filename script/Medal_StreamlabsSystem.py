# -*- coding: utf-8 -*-
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
import time
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


ScriptName = "Medal Overlay"
Website = "http://darthminos.tv"
Description = "Triggers Medal.tv and plays the video back on stream"
Creator = "DarthMinos"
Version = "1.0.0-snapshot"
MedalInviteUrl = "https://medal.tv/invite/"
MedalPartnerUrl = "https://medal.tv/?ref="
DefaultMedalPartnerRef = "DarthMinos_partner"
MedalPublicApiKey = "pub_YiUDXfg4MRtOrIeeWOV4v26foDP6QTcY"
Repo = "camalot/chatbot-medaloverlay"
DonateLink = "https://paypal.me/camalotdesigns"
ReadMeFile = "https://github.com/camalot/chatbot-medaloverlay/blob/develop/ReadMe.md"


SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
CachedClipsFile = os.path.join(os.path.dirname(__file__), "clips.json")

ScriptSettings = None
MedalUserSettings = None
ClipsCacheData = None
MedalCategories = None

CurrentClipId = None
LastClipTriggerUser = None
ClipWatcher = None
ProcessManager = None
Initialized = False

TriggerCooldownTime = None
TriggerCount = 0
TriggerList = []

PollCooldownTime = None

timestr = time.strftime("%Y%m%d")
logDir = os.path.join(os.path.dirname(__file__), "logs/")
if not os.path.exists(logDir):
    os.makedirs(logDir)
LogFile = os.path.join(os.path.dirname(__file__), "logs/" + ScriptName + "-" + timestr + ".log")
Logger = MedalRunner.Logger(LogFile)
# ---------------------------------------
#	Script Classes
# ---------------------------------------

class MedalCategoriesCache(object):
    def __init__(self):
        try:
            self.categories = []
            resp = Parent.GetRequest("https://developers.medal.tv/v1/categories", {
                "Content-Type": "application/json",
                "Authorization": MedalPublicApiKey
            })
            responseText = json.loads(resp, encoding="utf-8")['response']
            self.categories = json.loads(responseText, encoding="utf-8")
        except Exception as e:
            Logger.Error(ScriptName, str(e))
            Parent.Log(ScriptName, str(e))

    def Find(self, game):
        result = next((x for x in self.categories if x['categoryName'].lower().strip() == game.lower().strip()), None)
        if result is None:
            result = next((x for x in self.categories if x['alternativeName'].lower().strip() == game.lower().strip()), None)
        if result is None:
            result = next((x for x in self.categories if x['categoryName'].lower().strip().replace(":", "") == game.lower().strip().replace(":", "")), None)
        if result is None:
            result = next((x for x in self.categories if x['alternativeName'].lower().strip().replace(":", "") == game.lower().strip().replace(":", "")), None)
        return result

class ClipsCache(object):
    def __init__(self):
        try:
            self.clips = []
            with codecs.open(CachedClipsFile, encoding="utf-8-sig", mode="r") as f:
                data = json.load(f, encoding="utf-8")
                self.__dict__.update(self.cleanup(data))
        except Exception as e:
            Logger.Error(ScriptName, str(e))
            Parent.Log(ScriptName, str(e))

    def Save(self):
        try:
            with codecs.open(CachedClipsFile, encoding="utf-8-sig", mode="w") as outfile:
                json.dump(self.__dict__, outfile)
        except Exception as e:
            Logger.Error(ScriptName, str(e))
            Parent.Log(ScriptName, str(e))

    def Add(self, clip):
        if self.Find(clip['slug']) is None:
            self.clips.append(clip)
        return

    def Find(self, clipId):
        result = next((x for x in self.clips if x['slug'] == clipId), None)
        return result

    def cleanup(self, ldata):
        # timeWindow = datetime.datetime.now() - datetime.timedelta(days=7)
        # for x in ldata:
        #     created = datetime.datetime.strptime(x['created_at'],  "%Y-%m-%dT%H:%M:%SZ")
        #     if created < timeWindow:
        #         Parent.Log(ScriptName, "Remove Clip: " + x['slug'])
        #         Logger.Debug(ScriptName, "Remove Clip: " + x['slug'])
        #         ldata.remove(x)
        return ldata
class UserSettings(object):
    """ Holds the values from the medal/user.json """
    def __init__(self):
        """ Load the user.json file if available """
        try:
            settingsfile = os.path.realpath(os.path.join(os.getenv('APPDATA'), "Medal/store/user.json"))
            self.key = None
            self.userId = None
            self.userName = None

            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                fileSettings = json.load(f, encoding="utf-8")
                self.__dict__.update(fileSettings)
        except Exception as e:
            Logger.Error(ScriptName, str(e))
            Parent.Log(ScriptName, str(e))
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
            self.MedalPartnerRef = DefaultMedalPartnerRef
            self.FontColor = "rgba(255,255,255,1)"
            self.FontName = "days-one"
            self.CustomFontName = ""
            self.TitleFontSize = 3.5
            self.TitleTextAlign = "center"
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
            self.RecentAutoStartVideo = True
            self.RecentMuteAudio = False
            self.RecentRandom = False
            self.RecentVolume = 100
            self.RecentShowVideoProgress = True
            self.UseNonWatermarkedVideo = False
            self.RecentShowTitle = True

            self.EnableTwitchClipAutoImport = False
            self.TwitchClipMedalPrivacy = "Public"
            self.TwitchClipPollRate = 1
            self.TwitchClientId = ""

            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                fileSettings = json.load(f, encoding="utf-8")
                self.__dict__.update(fileSettings)

        except Exception as e:
            Logger.Error(ScriptName, str(e))
            Parent.Log(ScriptName, str(e))

    def Reload(self, jsonData):
        """ Reload settings from the user interface by given json data. """
        Parent.Log(ScriptName, "Reload Settings")
        Logger.Debug(ScriptName, str(e))
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
    Logger.Debug(ScriptName, tool + " \"" + webdir + "\" " + str(port) + " 127.0.0.1")
    os.spawnl(os.P_NOWAITO, tool, tool, webdir, str(port), "127.0.0.1")
    return
def SendOverlaySettingsUpdate():
    Parent.Log(ScriptName, "EVENT_MEDAL_SETTINGS: " + json.dumps(ScriptSettings.__dict__))
    Logger.Debug(ScriptName, "EVENT_MEDAL_SETTINGS: " + json.dumps(ScriptSettings.__dict__))
    Parent.BroadcastWsEvent("EVENT_MEDAL_SETTINGS", json.dumps(ScriptSettings.__dict__))
def ReloadOverlay():
    Parent.Log(ScriptName, "EVENT_MEDAL_RELOAD: " + json.dumps(None))
    Logger.Debug(ScriptName, "EVENT_MEDAL_RELOAD: " + json.dumps(None))
    Parent.BroadcastWsEvent("EVENT_MEDAL_RELOAD", json.dumps(None))
    return
def PlayVideoById(videoId):
    # Broadcast WebSocket Event
    payload = {
        "port": ScriptSettings.WebPort,
        "video": str(videoId) + ".mp4"
    }
    Parent.Log(ScriptName, "EVENT_MEDAL_PLAY: " + json.dumps(payload))
    Logger.Debug(ScriptName, "EVENT_MEDAL_PLAY: " + json.dumps(payload))
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
        Logger.Debug(ScriptName, "Event: ClipReady: " + eventArgs.ClipId)

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
    Logger.Debug(ScriptName, "Event: ClipStarted: " + eventArgs.ClipId)
    return

#---------------------------------------
# Event Handler for ClipWatcher.MonitorStart
#---------------------------------------
def OnMonitorStart(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorStart")
    Logger.Debug(ScriptName, "Event: MonitorStart")
    return
#---------------------------------------
# Event Handler for ClipWatcher.MonitorStop
#---------------------------------------
def OnMonitorStop(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorStop")
    Logger.Debug(ScriptName, "Event: MonitorStop")
    return
#---------------------------------------
# Event Handler for ClipWatcher.MonitorPause
#---------------------------------------
def OnMonitorPause(sender, eventArgs):
    Parent.Log(ScriptName, "Event: MonitorPause")
    Logger.Debug(ScriptName, "Event: MonitorPause")
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
    global ClipsCacheData
    global MedalUserSettings
    global MedalCategories

    MedalUserSettings = UserSettings()
    ClipsCacheData = ClipsCache()
    MedalCategories = MedalCategoriesCache()

    if Initialized:
        Parent.Log(ScriptName, "Skip Initialization. Already Initialized.")
        Logger.Debug(ScriptName, "Skip Initialization. Already Initialized.")
        return

    Parent.Log(ScriptName, "Initialize")
    Logger.Debug(ScriptName, "Initialize")
    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)
    if ScriptSettings.VideoPath == "":
        Parent.Log(ScriptName, "Video Path Not Currently Set.")
        Logger.Debug(ScriptName, "Video Path Not Currently Set.")
        return

    webDirectory = os.path.join(os.path.dirname(__file__), ScriptSettings.VideoPath)


    customcss = os.path.join(os.path.dirname(__file__), "./custom.css")
    csstemplate = os.path.join(os.path.dirname(__file__), "./custom-sample.css")
    if not os.path.exists(customcss):
        shutil.copyfile(csstemplate, customcss)

    if not os.path.exists(webDirectory):
        Parent.Log(ScriptName, "Video Path Does Not Exist: " + webDirectory)
        Logger.Debug(ScriptName, "Video Path Does Not Exist: " + webDirectory)
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
    # Register()
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
                message = Parse("$MedalDescription\n👀 Get Medal: $MedalPartnerLink 👀 Follow " + Parent.GetChannelName() +
                 ": $MedalFollowLink 👀 Create a clip with the $MedalClipCommand command.", data.User, data.UserName, None, None, data.Message)
                Parent.SendTwitchMessage(message)
            elif commandTrigger == "!medaloverlay":
                Parent.AddCooldown(ScriptName, commandTrigger, ScriptSettings.Cooldown)
                message = Parse("$MedalOverlayDescription", data.User, data.UserName, None, None, data.Message)
                Parent.SendTwitchMessage(message)
            elif commandTrigger == ScriptSettings.Command:
                if Parent.HasPermission(data.User, ScriptSettings.Permission, ""):
                    if data.User in TriggerList:
                        Parent.Log(ScriptName, "User already triggered the command. Skipping.")
                        Logger.Debug(ScriptName, "User already triggered the command. Skipping.")
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
                        Logger.Debug(ScriptName, "Sending HotKey: " + ScriptSettings.HotKey)
                        MedalRunner.Keys.SendKeys(ScriptSettings.HotKey)
                        TriggerCount = 0
                        TriggerCooldownTime = None
                        TriggerList = []
                    else:
                        triggerDiff = ScriptSettings.RequiredTriggerCount - TriggerCount
                        if TriggerCount == 1:
                            Parent.Log(ScriptName, "init clip trigger.")
                            Logger.Debug(ScriptName, "init clip trigger.")
                            TriggerCooldownTime = datetime.datetime.now() + datetime.timedelta(seconds=ScriptSettings.TriggerCooldown)
                            if ScriptSettings.NotifyChatOfClips:
                                Parent.SendTwitchMessage(data.User + " has initialized a medal.tv clip. Need " + str(triggerDiff) + " more to generate the clip.")
                        else:
                            Parent.Log(ScriptName, "Additional trigger of clip generation.")
                            Logger.Debug(ScriptName, "Additional trigger of clip generation.")
                            if ScriptSettings.NotifyChatOfClips:
                                Parent.SendTwitchMessage(data.User + " triggered a medal.tv clip. Need " + str(triggerDiff) + " more to generate the clip.")
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters)
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    result = parseString
    if result:
        if "$MedalFollowLink" in result:
            result = result.replace("$MedalFollowLink", MedalInviteUrl + ScriptSettings.Username)
        if "$MedalPartnerLink" in result:
            result = result.replace("$MedalPartnerLink", MedalPartnerUrl + (ScriptSettings.MedalPartnerRef or DefaultMedalPartnerRef))
        if "$MedalClipCommand" in result:
            result = result.replace("$MedalClipCommand", ScriptSettings.Command)
        if "$MedalUserName" in result:
            result = result.replace("$MedalUserName", ScriptSettings.Username)
        if "$MedalUserId" in result:
            # result = result.replace("$MedalUserId", ScriptSettings.UserId)
            result = result.replace("$MedalUserId", MedalUserSettings.userId)
        if "$MedalDescription" in result:
            result = result.replace("$MedalDescription", "The Medal desktop client records clips with one button press, posts them on medal.tv, and gives you a shareable link. No lag, no fuss.")
        if "$MedalOverlayDescription" in result:
            result = result.replace("$MedalOverlayDescription", "Medal Overlay is a StreamLabs Chatbot Script developed by DarthMinos: https://twitch.tv/darthminos To Download or find out more visit https://github.com/camalot/chatbot-medaloverlay")
        return result.replace('\\n', '\n').strip()
    return result
#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    global Initialized
    global ClipWatcher
    Parent.Log(ScriptName, "Unload")
    Logger.Debug(ScriptName, "Unload")
    Parent.Log(ScriptName, "Kill mohttpd Process")
    Logger.Debug(ScriptName, "Kill mohttpd Process")
    stop = ProcessManager.Stop("mohttpd")
    Parent.Log(ScriptName, stop)
    Logger.Debug(ScriptName, stop)
    Parent.Log(ScriptName, "Killed mohttpd Process")
    Logger.Debug(ScriptName, "Killed mohttpd Process")

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
    Logger.Debug(ScriptName, "State Changed: " + str(state))
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
    SendOverlaySettingsUpdate()
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    global TriggerCooldownTime
    global TriggerCount
    global TriggerList

    global PollCooldownTime

    if TriggerCooldownTime is not None and datetime.datetime.now() >= TriggerCooldownTime:
        TriggerCooldownTime = None
        TriggerCount = 0
        TriggerList = []
        Parent.Log(ScriptName, "Reset clip trigger due to cooldown exceeded")
        Logger.Debug(ScriptName, "Reset clip trigger due to cooldown exceeded")
        if ScriptSettings.NotifyChatOfClips:
            Parent.SendTwitchMessage("Medal.tv clip generation did not get the required triggers of " + str(ScriptSettings.RequiredTriggerCount) + " to generate the clip.")


    if ScriptSettings.EnableTwitchClipAutoImport:
        if Parent.GetStreamingService().lower() == "twitch" :
            if PollCooldownTime is None or datetime.datetime.now() >= PollCooldownTime:
                PollCooldownTime = datetime.datetime.now() + datetime.timedelta(minutes=ScriptSettings.TwitchClipPollRate)
                PollTwitchClips()
    return


def ProcessTwitchClip(clip):
    try:
        privacyLevel = {
            "Public": 0,
            "Private": 1
        }

        timeWindow = datetime.datetime.now() - datetime.timedelta(minutes=30)
        created = datetime.datetime.strptime(clip['created_at'],  "%Y-%m-%dT%H:%M:%SZ")
        videoId = clip['slug']

        if created >= timeWindow:
            if ClipsCacheData.Find(videoId) is None:
                Parent.Log(ScriptName, "Process Twitch Clip: " + videoId)
                Logger.Debug(ScriptName, "Process Twitch Clip: " + videoId)
                categoryId = 713
                # category = MedalCategories.Find(clip['game'])
                # if category is not None:
                #     categoryId = category['categoryId']
                # If the clip was not cached, add it
                # description = "Clipped on " + clip["broadcaster"]["channel_url"] + " by " + clip["curator"]["name"] + ". Imported through Medal Overlay Script for Streamlabs Chatbot - https://github.com/" + Repo
                description = "Clipped by " + clip["curator"]["name"]
                clipImporter = MedalRunner.Importer(MedalUserSettings.userId, MedalUserSettings.key)
                result = clipImporter.Import(clip['url'], clip["thumbnails"]["medium"], clip["title"] + " - " + clip["game"], description, categoryId, privacyLevel[ScriptSettings.TwitchClipMedalPrivacy])
                Parent.Log(ScriptName, result)
                Logger.Debug(ScriptName, result)
                resultData = json.loads(result, encoding="utf-8")
                if 'contentId' in resultData:
                    clip["medalContentId"] = resultData['contentId']
                    Parent.Log(ScriptName, json.dumps(clip))
                    Logger.Debug(ScriptName, json.dumps(clip))
                    Parent.Log(ScriptName, "Clip has been imported: https://medal.tv/clips/" + str(resultData['contentId']))
                    Logger.Debug(ScriptName, "Clip has been imported: https://medal.tv/clips/" + str(resultData['contentId']))
                else:
                    Parent.Log(ScriptName, json.dumps(resultData))
                    Logger.Debug(ScriptName, json.dumps(resultData))
                Parent.Log(ScriptName, "BEFORE CLIP CACHE")
                Logger.Debug(ScriptName, "BEFORE CLIP CACHE")
                ClipsCacheData.Add(clip)
                Parent.Log(ScriptName, "AFTER CLIP CACHE")
                Logger.Debug(ScriptName, "AFTER CLIP CACHE")
        else:
            Parent.Log(ScriptName, "Clip created outside of the allotted time window")
            Logger.Debug(ScriptName, "Clip created outside of the allotted time window")
    except Exception as e:
        Parent.Log(ScriptName, str(e))
        Logger.Error(ScriptName, str(e))

def PollTwitchClips():

    testJSON = """{
    "clips": [
        {
            "slug": "EnergeticSmoothLegGivePLZ",
            "tracking_id": "624546459",
            "url": "https://clips.twitch.tv/EnergeticSmoothLegGivePLZ?tt_medium=clips_api&tt_content=url",
            "embed_url": "https://clips.twitch.tv/embed?clip=EnergeticSmoothLegGivePLZ&tt_medium=clips_api&tt_content=embed",
            "embed_html": "<iframe src='https://clips.twitch.tv/embed?clip=EnergeticSmoothLegGivePLZ&tt_medium=clips_api&tt_content=embed' width='640' height='360' frameborder='0' scrolling='no' allowfullscreen='true'></iframe>",
            "broadcaster": {
                "id": "58491861",
                "name": "darthminos",
                "display_name": "DarthMinos",
                "channel_url": "https://www.twitch.tv/darthminos",
                "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/7658bffb-94ae-4b01-acd1-b812630a7e07-profile_image-150x150.png"
            },
            "curator": {
                "id": "39040920",
                "name": "carrilla_saavaa",
                "display_name": "Carrilla_Saavaa",
                "channel_url": "https://www.twitch.tv/carrilla_saavaa",
                "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/d0b2bae5-dc6c-47d4-92ec-46d42cc691ce-profile_image-150x150.png"
            },
            "vod": {
                "id": "554165376",
                "url": "https://www.twitch.tv/videos/554165376?t=1h44m2s",
                "offset": 6242,
                "preview_image_url": "https://vod-secure.twitch.tv/_404/404_processing_320x240.png"
            },
            "broadcast_id": "36964459280",
            "game": "Tom Clancy's Rainbow Six: Siege",
            "language": "en",
            "title": "really?",
            "views": 5,
            "duration": 26.28,
            "created_at": "2020-02-19T00:15:20Z",
            "thumbnails": {
                "medium": "https://clips-media-assets2.twitch.tv/AT-cm%7C624546459-preview-480x272.jpg",
                "small": "https://clips-media-assets2.twitch.tv/AT-cm%7C624546459-preview-260x147.jpg",
                "tiny": "https://clips-media-assets2.twitch.tv/AT-cm%7C624546459-preview-86x45.jpg"
            }
        }
    ],
    "_cursor": "MQ=="
}
"""
    # clips = json.loads(testJSON)['clips']
    # https://api.twitch.tv/kraken/clips/top?channel=darthminos&limit=1&trending=false&period=day

    resp = Parent.GetRequest("https://api.twitch.tv/kraken/clips/top?channel=" + Parent.GetChannelName().lower() + "&limit=5&trending=false&period=day", headers={
        "Accept": "application/vnd.twitchtv.v5+json",
        "Client-ID": ScriptSettings.TwitchClientId
    })
    clips = json.loads(json.loads(resp)['response'])['clips']
    if len(clips) > 0:
        for clip in clips:
            ProcessTwitchClip(clip)
    ClipsCacheData.Save()
    return


# def Register():
#     payload = {
#         "channel": Parent.GetChannelName(),
#         "user": ScriptSettings.Username,
#         "userId": ScriptSettings.UserId,
#         "command": ScriptSettings.Command,
#         "platform": Parent.GetStreamingService()
#     }
#     Parent.Log(ScriptName, json.dumps(payload))
#     Parent.PostRequest("http://files.bit13.local:1880/medaloverlay/users", {"Content-Type": "application/json"}, payload, True)

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
def OpenScriptUpdater():
    currentDir = os.path.realpath(os.path.dirname(__file__))
    chatbotRoot = os.path.realpath(os.path.join(currentDir, "../../../"))
    libsDir = os.path.join(currentDir, "libs/updater")
    Parent.Log(ScriptName, libsDir)
    Logger.Error(ScriptName, libsDir)
    try:
        src_files = os.listdir(libsDir)
        tempdir = tempfile.mkdtemp()
        Parent.Log(ScriptName, tempdir)
        for file_name in src_files:
            full_file_name = os.path.join(libsDir, file_name)
            if os.path.isfile(full_file_name):
                Parent.Log(ScriptName, "Copy: " + full_file_name)
                shutil.copy(full_file_name, tempdir)
        updater = os.path.join(tempdir, "ApplicationUpdater.exe")
        updaterConfigFile = os.path.join(tempdir, "update.manifest")
        repoVals = Repo.split('/')
        updaterConfig = {
            "path": os.path.realpath(os.path.join(currentDir,"../")),
            "version": Version,
            "requiresRestart": True,
            "name": ScriptName,
            "kill": ["mohttpd"],
            "execute": {
                "before": [{
                    "command": "cmd",
                    "arguments": [ "/c", "del /q /f /s ChatbostScriptUpdater.exe" ],
                    "workingDirectory": "${PATH}\\${FOLDERNAME}\\Libs\\updater\\",
                    "ignoreExitCode": true,
                    "validExitCodes": [ 0 ]
                }],
                "after": []
            },
            "application": os.path.join(chatbotRoot, "Streamlabs Chatbot.exe"),
            "folderName": os.path.basename(os.path.dirname(os.path.realpath(__file__))),
            "processName": "Streamlabs Chatbot",
            "website": Website,
            "repository": {
                "owner": repoVals[0],
                "name": repoVals[1]
            }
        }
        Parent.Log(ScriptName, updater)
        configJson = json.dumps(updaterConfig)
        Parent.Log(ScriptName, configJson)
        Logger.Error(ScriptName, configJson)
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
def OpenDonateLink():
    os.startfile(DonateLink)
    return
def OpenEdgeFontsUrl():
    os.startfile("https://edgewebfonts.adobe.com/fonts")

def OpenTwitchRegisterApplication():
    os.startfile("https://dev.twitch.tv/console/apps/create")
    return

def RecentPlayBackPlay():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_PLAY", None)
def RecentPlayBackStop():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_STOP", None)
def RecentPlayMute():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_MUTE", None)
def RecentPlayNext():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_SKIP", None)
