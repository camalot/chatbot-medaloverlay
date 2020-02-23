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
Website = "http://darthminos.tv"
Description = "Triggers Medal.tv and plays the video back on stream"
Creator = "DarthMinos"
Version = "1.0.0-snapshot"
MedalInviteUrl = "https://medal.tv/invite/"
MedalPartnerUrl = "https://medal.tv/?ref="
DefaultMedalPartnerRef = "DarthMinos_partner"
MedalPublicApiKey = "pub_YiUDXfg4MRtOrIeeWOV4v26foDP6QTcY"
Repo = "camalot/chatbot-medaloverlay"
# ---------------------------------------
#	Set Variables
# ---------------------------------------


DonateLink = "https://paypal.me/camalotdesigns"
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
ReadMeFile = "https://github.com/camalot/chatbot-medaloverlay/blob/develop/ReadMe.md"

ScriptSettings = None
MedalUserSettings = None

CurrentClipId = None
LastClipTriggerUser = None
ClipWatcher = None
ProcessManager = None
Initialized = False

TriggerCooldownTime = None
TriggerCount = 0
TriggerList = []

PollCooldownTime = None
# ---------------------------------------
#	Script Classes
# ---------------------------------------

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
            Parent.Log(ScriptName, str(e))
    def Reload(self, jsonData):
        return
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
def SendOverlaySettingsUpdate():
    Parent.Log(ScriptName, "EVENT_MEDAL_SETTINGS: " + json.dumps(ScriptSettings.__dict__))
    Parent.BroadcastWsEvent("EVENT_MEDAL_SETTINGS", json.dumps(ScriptSettings.__dict__))
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
    MedalUserSettings = UserSettings()
    Parent.Log(ScriptName, json.dumps(MedalUserSettings.__dict__))

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
        if ScriptSettings.NotifyChatOfClips:
            Parent.SendTwitchMessage("Medal.tv clip generation did not get the required triggers of " + str(ScriptSettings.RequiredTriggerCount) + " to generate the clip.")

    if PollCooldownTime is None or datetime.datetime.now() >= PollCooldownTime:
        PollCooldownTime = datetime.datetime.now() + datetime.timedelta(minutes=ScriptSettings.TwitchClipPollRate)
        # PollTwitchClips()
    return


def ProcessTwitchClip(clip):
    privacyLevel = {
        "Public": 0,
        "Private": 1
    }

    created = datetime.datetime.strptime(clip['created_at'],  "%Y-%m-%dT%H:%M:%SZ")
    videoId = clip['slug']
    data = {
        "contentUrl": clip['url'],
        "categoryId": 713, # https://developers.medal.tv/v1/categories
        "risk": 0,
        "privacy": privacyLevel[ScriptSettings.TwitchClipMedalPrivacy],
        "contentType": 15,
        "contentDescription": "Clipped on " + clip["broadcaster"]["channel_url"] + " by " + clip["curator"]["name"] + ". Imported through Medal Overlay Script for Streamlabs Chatbot - https://github.com/" + Repo,
        "contentTitle": clip["title"] + " - " + clip["game"],
        "thumbnailUrl": clip["thumbnails"]["medium"]
    }

    Parent.Log(ScriptName, json.dumps(data))

    # Parent.PostRequest("https://api-v2.medal.tv/users/" + MedalUserSettings.userId + "/content", {
    #     "Content-Type": "application/json",
    #     "X-Authentication": MedalUserSettings.userId + "," + MedalUserSettings.key
    # }, data , True)
    return

def PollTwitchClips():
# {
#     "clips": [
#         {
#             "slug": "EnergeticSmoothLegGivePLZ",
#             "tracking_id": "624546459",
#             "url": "https://clips.twitch.tv/EnergeticSmoothLegGivePLZ?tt_medium=clips_api&tt_content=url",
#             "embed_url": "https://clips.twitch.tv/embed?clip=EnergeticSmoothLegGivePLZ&tt_medium=clips_api&tt_content=embed",
#             "embed_html": "<iframe src='https://clips.twitch.tv/embed?clip=EnergeticSmoothLegGivePLZ&tt_medium=clips_api&tt_content=embed' width='640' height='360' frameborder='0' scrolling='no' allowfullscreen='true'></iframe>",
#             "broadcaster": {
#                 "id": "58491861",
#                 "name": "darthminos",
#                 "display_name": "DarthMinos",
#                 "channel_url": "https://www.twitch.tv/darthminos",
#                 "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/7658bffb-94ae-4b01-acd1-b812630a7e07-profile_image-150x150.png"
#             },
#             "curator": {
#                 "id": "39040920",
#                 "name": "carrilla_saavaa",
#                 "display_name": "Carrilla_Saavaa",
#                 "channel_url": "https://www.twitch.tv/carrilla_saavaa",
#                 "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/d0b2bae5-dc6c-47d4-92ec-46d42cc691ce-profile_image-150x150.png"
#             },
#             "vod": {
#                 "id": "554165376",
#                 "url": "https://www.twitch.tv/videos/554165376?t=1h44m2s",
#                 "offset": 6242,
#                 "preview_image_url": "https://vod-secure.twitch.tv/_404/404_processing_320x240.png"
#             },
#             "broadcast_id": "36964459280",
#             "game": "Tom Clancy's Rainbow Six: Siege",
#             "language": "en",
#             "title": "really?",
#             "views": 5,
#             "duration": 26.28,
#             "created_at": "2020-02-19T00:15:20Z",
#             "thumbnails": {
#                 "medium": "https://clips-media-assets2.twitch.tv/AT-cm%7C624546459-preview-480x272.jpg",
#                 "small": "https://clips-media-assets2.twitch.tv/AT-cm%7C624546459-preview-260x147.jpg",
#                 "tiny": "https://clips-media-assets2.twitch.tv/AT-cm%7C624546459-preview-86x45.jpg"
#             }
#         }
#     ],
#     "_cursor": "MQ=="
# }
    # https://api.twitch.tv/kraken/clips/top?channel=darthminos&limit=1&trending=false&period=day
    resp = Parent.GetRequest("https://api.twitch.tv/kraken/clips/top?channel=" + Parent.GetChannelName().lower() + "&limit=1&trending=false&period=week", headers={
        "Accept": "application/vnd.twitchtv.v5+json",
        "Client-ID": "z70figj04uestgfncd83m6qww1zm0l"
    })
    clips = json.loads(json.loads(resp)['response'])['clips']
    if len(clips) > 0:
        for clip in clips:
            ProcessTwitchClip(clip)

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
    try:
        src_files = os.listdir(libsDir)
        tempdir = tempfile.mkdtemp()
        Parent.Log(ScriptName, tempdir)
        for file_name in src_files:
            full_file_name = os.path.join(libsDir, file_name)
            if os.path.isfile(full_file_name):
                Parent.Log(ScriptName, "Copy: " + full_file_name)
                shutil.copy(full_file_name, tempdir)
        updater = os.path.join(tempdir, "ChatbotScriptUpdater.exe")
        updaterConfigFile = os.path.join(tempdir, "update.manifest")
        repoVals = Repo.split('/')
        updaterConfig = {
            "path": os.path.realpath(os.path.join(currentDir,"../")),
            "version": Version,
            "requiresRestart": True,
            "name": ScriptName,
            "kill": ["mohttpd"],
            "execute": {
                "before": [],
                "after": []
            },
            "chatbot": os.path.join(chatbotRoot, "Streamlabs Chatbot.exe"),
            "script": os.path.basename(os.path.dirname(os.path.realpath(__file__))),
            "website": Website,
            "repository": {
                "owner": repoVals[0],
                "name": repoVals[1]
            }
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
def OpenDonateLink():
    os.startfile(DonateLink)
    return
def OpenEdgeFontsUrl():
    os.startfile("https://edgewebfonts.adobe.com/fonts")

def RecentPlayBackPlay():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_PLAY", None)
def RecentPlayBackStop():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_STOP", None)
def RecentPlayMute():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_MUTE", None)
def RecentPlayNext():
    Parent.BroadcastWsEvent("EVENT_MEDAL_RECENT_SKIP", None)
