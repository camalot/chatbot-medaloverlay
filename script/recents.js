"use strict";

let clipQueue = [];
let isClipPlaying = false;
let refreshAfter = false;
let stopPlayback = false;
let page = 0;
let perPage = 25;
let IS_CEF = window.obsstudio !== undefined;

let getMedalApiKey = () => {
	if (settings.PrivateApiKey && settings.PrivateApiKey !== "") {
		return settings.PrivateApiKey;
	} else {
		return settings.PublicApiKey;
	}
};

let validateSettings = () => {
	let hasApiKey = typeof API_Key !== "undefined";
	let hasSettings = typeof settings !== "undefined";
	let hasUserId = hasSettings && settings.UserId !== "";
	return {
		isValid: hasApiKey && hasSettings && hasUserId,
		hasSettings: hasSettings,
		hasApiKey: hasApiKey,
		hasUserId: hasUserId
	};
};

let initializeUI = () => {
	$("#video-container .video-box video.replay")
		.on("error", function (e) { console.error(`Error: ${e}`); })
		.prop("volume", settings.RecentVolume / 100)
		.prop("muted", IS_CEF ? settings.RecentMuteAudio : true)
		.on("canplay", videoLoaded)
		.on("ended pause", videoEnded)
		.on("timeupdate", timelapse);

	if (settings.ProgressBarBackgroundColor != null && settings.ProgressBarBackgroundColor !== "") {
		$(":root")
			.css("--progress-bg", settings.ProgressBarBackgroundColor);
	}

	if (settings.ProgressBarFillColor != null && settings.ProgressBarFillColor !== "") {
		$(":root")
			.css("--progress-fill", settings.ProgressBarFillColor);
	}

	if (settings.RecentShowVideoProgress) {
		$("#video-container .video-box progress").removeClass("hidden");
	} else {
		$("#video-container .video-box progress").addClass("hidden");
	}
};


let timelapse = (e) => {

	let video = $("#video-container .video-box video.replay").get(0);
	let pbar = $("#video-container .video-box progress").get(0);
	if (video.duration && video.currentTime) {
		let percent = (100 / video.duration) * video.currentTime;
		pbar.value = percent;
	} else {
		pbar.value = 0;
	}
};

let videoLoaded = (e) => {
	isClipPlaying = true;
};

let videoEnded = (e) => {
	isClipPlaying = false;

	if (refreshAfter) {
		return location.reload();
	}

	if (stopPlayback) {
		console.log("stopped playback...");
		return;
	}

	if (clipQueue.length > 0) {
		return queueVideo(clipQueue.pop());
	} else {
		// set next page
		page += 1;
		return getVideoQueue(page, perPage, () => {
			return queueVideo(clipQueue.pop());
		});
	}
};

let queueVideo = (clipData) => {
	if (clipData) {
		$("#video-container .video-box video.replay")
			.prop("autoplay", true)
			.prop("preload", true)
			.prop("loop", false)
			.prop("volume", settings.RecentVolume / 100)
			.attr("src", clipData.url)
			.empty()
			.append(`<source src="${clipData.url}" type="video/mp4" />`);

		let title = $("#video-container .video-box .title");
		title.html(clipData.title);
		if (settings.RecentShowTitle) {
			title.removeClass("hidden");
		} else {
			title.addClass("hidden");
		}
		$("#video-container .video-box .views")
			.html(clipData.views);
	}
};

// Connect to ChatBot websocket
// Automatically tries to reconnect on
// disconnection by recalling this method
let connectWebsocket = () => {
	//-------------------------------------------
	//  Create WebSocket
	//-------------------------------------------
	let socket = new WebSocket("ws://127.0.0.1:3337/streamlabs");

	//-------------------------------------------
	//  Websocket Event: OnOpen
	//-------------------------------------------
	socket.onopen = () => {
		console.log("open");
		// AnkhBot Authentication Information
		let auth = {
			author: "DarthMinos",
			website: "darthminos.tv",
			api_key: API_Key,
			events: [
				"EVENT_MEDAL_RECENT_MUTE",
				"EVENT_MEDAL_RECENT_STOP",
				"EVENT_MEDAL_RECENT_PLAY",
				"EVENT_MEDAL_RECENT_SKIP",
				"EVENT_MEDAL_RELOAD"
			]
		};

		// Send authentication data to ChatBot ws server

		socket.send(JSON.stringify(auth));
	};

	//-------------------------------------------
	//  Websocket Event: OnMessage
	//-------------------------------------------
	socket.onmessage = (message) => {
		console.log(message);
		// Parse message
		let socketMessage = JSON.parse(message.data);
		let eventName = socketMessage.event;
		console.log(socketMessage);
		let videoPlayer = $("#video-container video.replay").get(0);
		switch (eventName) {
			case "EVENT_MEDAL_RECENT_MUTE":
				let $vp = $(videoPlayer);
				$vp.trigger("click");
				let muted = $vp.prop("muted");
				console.log(`Set Muted: ${!muted}`);
				$vp.prop("muted", !muted);
				break;
			case "EVENT_MEDAL_RECENT_PLAY":
				console.log("PLAY VIDEO");
				stopPlayback = false;
				videoPlayer.play();
				break;
			case "EVENT_MEDAL_RECENT_STOP":
				console.log("STOP VIDEO");
				stopPlayback = true;
				videoPlayer.pause();
				break;
			case "EVENT_MEDAL_RECENT_SKIP":
				console.log("SKIP VIDEO");
				stopPlayback = false;
				videoPlayer.pause();
				break;
			case "EVENT_MEDAL_RELOAD":
				if (isClipPlaying) {
					refreshAfter = true;
				} else {
					location.reload();
				}
				break;
			default:
				console.log(eventName);
				break;
		}
	};

	//-------------------------------------------
	//  Websocket Event: OnError
	//-------------------------------------------
	socket.onerror = (error) => {
		console.error(`Error: ${error}`);
	};

	//-------------------------------------------
	//  Websocket Event: OnClose
	//-------------------------------------------
	socket.onclose = () => {
		console.log("close");
		// Clear socket to avoid multiple ws objects and EventHandlings
		socket = null;
		// Try to reconnect every 5s
		setTimeout(() => { connectWebsocket(); }, 5000);
	};

};

let getVideoQueue = (p, pp, completeCB, errorCB) => {
	let medalApiKey = getMedalApiKey();

	if (settings.UserId == null || settings.UserId === "") {
		return errorCB("Settings UserId is unset");
	}

	$.ajax({
		url: `https://developers.medal.tv/v1/latest?userId=${settings.UserId}&limit=${pp}&offset=${p * pp}`,
		headers: {
			"Authorization": `Basic ${btoa(medalApiKey)}`
		},
		success: (data) => {
			for (let x = data.contentObjects.length - 1; x >= 0; --x) {
				let clip = null;
				let obj = data.contentObjects[x];
				if (obj.unbrandedFileUrl && obj.unbrandedFileUrl !== "" && obj.unbrandedFileUrl !== "not_authorized" && settings.UseNonWatermarkedVideo) {
					clip = {
						url: obj.unbrandedFileUrl,
						title: obj.contentTitle || "",
						views: obj.contentViews || 0
					};
				} else if (obj.rawFileUrl && obj.rawFileUrl !== "" && obj.rawFileUrl !== "not_authorized") {
					clip = {
						url: obj.rawFileUrl,
						title: obj.contentTitle || "",
						views: obj.contentViews || 0
					};
				}	else {
					if (obj.contentId) {
						let vid = obj.contentId.replace(/^cid/, "");
						clip = {
							url: `http://files.medal.tv/${settings.UserId}/share-${vid}.mp4`,
							title: obj.contentTitle || "",
							views: obj.contentViews || 0
						};
					}
				}

				if(clip !== null) {
					clipQueue.push(clip);
				}
			}

			// if we are at the end of the data, start at the begining
			if(clipQueue.length === 0 && p > 0) {
				page = 0;
				return getVideoQueue(page, pp, completeCB, errorCB);
			} else if (clipQueue.length === 0 && page === 0) {
				// there are no clips
				return errorCB("No clip data was present.");
			} else {
				return completeCB();
			}

		},
		complete: (xhr, status) => {
		},
		error: (xhr, status, errorThrown) => {
			if (errorCB) {
				return errorCB(errorThrown);
			}
		}
	});
	return;
};

$(() => {
	let validatedSettings = validateSettings();

	// Connect if API_Key is inserted
	// Else show an error on the overlay
	if (!validatedSettings.isValid) {
		$(".config-messages").removeClass("hidden");
		$(".config-messages .settings").removeClass(validatedSettings.hasSettings ? "valid" : "hidden");
		$(".config-messages .api-key").removeClass(validatedSettings.hasApiKey ? "valid" : "hidden");
		$(".config-messages .medal-userid").removeClass(validatedSettings.hasUserId ? "valid" : "hidden");
		return;
	}

	getVideoQueue(page, perPage, () => {
		initializeUI();
		$("video.replay").trigger("click");
		connectWebsocket();
		queueVideo(clipQueue.pop());
	}, (err) => {
		console.error(err);
	});
});
