"use strict";

let clipQueue = [];
let isClipPlaying = false;
let refreshAfter = false;
let stopPlayback = false;
let page = 0;
let perPage = 25;
let IS_CEF = window.obsstudio !== undefined;
let USER_PLAY = false;
if (!window.settings) {
	window.settings = {};
}
window.settings = { ...window.DEFAULT_SETTINGS, ...window.settings };
window.medal = { ...{}, ...window.MEDAL_USER_SETTINGS};

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
	let hasUserId = hasSettings && medal.userId !== "";
	return {
		isValid: hasApiKey && hasSettings && hasUserId,
		hasSettings: hasSettings,
		hasApiKey: hasApiKey,
		hasUserId: hasUserId
	};
};

let initializeUI = () => {
	$("#video-container .video-box video.replay")
		.on("error", function (e) {
			console.error(e);
			videoEnded(e);
		})
		.prop("volume", settings.HighlightVolume / 100)
		.prop("muted", IS_CEF ? settings.HighlightMuteAudio : true)
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

	if (settings.HighlightShowVideoProgress) {
		$("#video-container .video-box progress").removeClass("hidden");
	} else {
		$("#video-container .video-box progress").addClass("hidden");
	}


	var fontName = settings.FontName;
	var customFontName = settings.CustomFontName;
	if (fontName && fontName === "custom" && customFontName && customFontName !== "") {
		loadFontsScript(customFontName);
	} else {
		$(":root").css("--font-name", fontName);
	}

	$(":root")
		.css("--replay-font-color", `${settings.TitleFontColor || "rgba(255,255,255,1)"}`)
		.css("--replay-font-size", `${settings.TitleFontSize || 3.5}em`)
		.css("--replay-text-align", `${settings.TitleTextAlign || "center"}`)
		;

};

function loadFontsScript(font) {
	let fnt = font.toLowerCase().replace(" ", "-");
	var script = document.createElement('script');
	script.onload = function () {
		$(":root").css("--font-name", `${fnt}, Arial, sans-serif`);
	};
	script.src = `http://use.edgefonts.net/${fnt}.js`;

	document.head.appendChild(script);
}



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
		return queueVideo(null);
	}
};

let queueVideo = (clipData) => {
	if (clipData) {
		$("#video-container .video-box video.replay")
			.prop("autoplay", settings.HighlightAutoStartVideo || USER_PLAY)
			.prop("preload", true)
			.prop("loop", false)
			.prop("volume", settings.HighlightVolume / 100)
			.attr("src", clipData.url)
			.empty()
			.append(`<source src="${clipData.url}" type="video/mp4" />`);

		let videoPlayer = $("#video-container .video-box video.replay").get(0);
		videoPlayer.playbackRate = settings.HighlightPlaybackSpeed || 1.0;
		console.log(`playback speed: ${settings.HighlightPlaybackSpeed || 1.0}`);

		let title = $("#video-container .video-box .title");
		title.html(clipData.title);
		if (settings.HighlightShowTitle) {
			title.removeClass("hidden");
		} else {
			title.addClass("hidden");
		}
		$("#video-container .video-box .views")
			.html(clipData.views);
	} else {
		console.log("no more clips");
		$("#video-container .video-box video.replay")
			.attr("src", "")
			.empty();
		$("#video-container .video-box .title").empty().addClass("hidden");
		stopPlayback = true;
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
				"EVENT_MEDAL_HIGHLIGHT_STOP",
				"EVENT_MEDAL_HIGHLIGHT_PLAY",
				"EVENT_MEDAL_HIGHLIGHT_SKIP",
				"EVENT_MEDAL_RELOAD",
				"EVENT_MEDAL_SETTINGS"
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
		let eventData = typeof socketMessage.data === "string" ? JSON.parse(socketMessage.data || "{}") : socketMessage.data;
		let videoPlayer = $("#video-container video.replay").get(0);
		switch (eventName) {
			case "EVENT_MEDAL_HIGHLIGHT_PLAY":
				console.log("PLAY VIDEO");
				stopPlayback = false;
				USER_PLAY = true;
				let userName = eventData.user;
				startVideoQueue(userName, eventData.max || 5, () => {
					$(videoPlayer).prop("autoplay", settings.HighlightAutoStartVideo || USER_PLAY);
					queueVideo(clipQueue.pop());
					videoPlayer.play();
				}, (err) => {
					console.log("in error callback");
					console.error(err);
				});
				break;
			case "EVENT_MEDAL_HIGHLIGHT_STOP":
				console.log("STOP VIDEO");
				stopPlayback = true;
				USER_PLAY = false;
				$(videoPlayer).prop("autoplay", settings.HighlightAutoStartVideo || USER_PLAY)
				videoPlayer.pause();
				break;
			case "EVENT_MEDAL_HIGHLIGHT_SKIP":
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
			case "EVENT_MEDAL_SETTINGS":
				window.settings = eventData;
				if (validateSettings()) {
					initializeUI();
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

let startVideoQueue = (user, limit, completeCB, errorCB) => {
	let medalApiKey = getMedalApiKey();

	if (user == null || user === "") {
		return errorCB("Settings user is unset");
	}
	$.ajax({
		url: `http://perks.darthminos.tv/api/v1/medal/${user}`,
		// url: `http://localhost:3000/api/v1/medal/${user}`,
		error: function(err) {
			console.error(err);
		},
		success: function(data) {
			console.log(data);
			getVideoQueue(data.userId, limit || 5, completeCB, errorCB);
		},
		complete: function(jxhr, status) {
		}
	});
}

let getVideoQueue = (userId, limit, completeCB, errorCB) => {
	let medalApiKey = getMedalApiKey();

	if (userId == null || userId === "") {
		return errorCB("Settings UserId is unset");
	}

	$.ajax({
		url: `https://developers.medal.tv/v1/latest?userId=${userId}&limit=${limit || 5}`,
		headers: {
			"Authorization": `Basic ${btoa(medalApiKey)}`
		},
		success: (data) => {
			let clips = data.contentObjects;
			if (settings.HighlightRandom) {
				clips = shuffle(clips);
			}
			for (let x = clips.length - 1; x >= 0; --x) {
				let clip = null;
				let obj = clips[x];
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
							url: `http://files.medal.tv/${userId}/share-${vid}.mp4`,
							title: obj.contentTitle || "",
							views: obj.contentViews || 0
						};
					}
				}

				if(clip !== null) {
					clipQueue.push(clip);
				}
			}

			// // if we are at the end of the data, start at the begining
			// if(clipQueue.length === 0 && p > 0) {
			// 	page = 0;
			// 	return getVideoQueue(userId, page, pp, completeCB, errorCB);
			// } else if (clipQueue.length === 0 && page === 0) {
			// 	// there are no clips
			// 	return errorCB("No clip data was present.");
			// } else {
			// 	return completeCB();
			// }
			// return completeCB();
			return completeCB();
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

let shuffle = (array) => {
	var currentIndex = array.length, temporaryValue, randomIndex;
	// While there remain elements to shuffle...
	while (0 !== currentIndex) {
		// Pick a remaining element...
		randomIndex = Math.floor(Math.random() * currentIndex);
		currentIndex -= 1;
		// And swap it with the current element.
		temporaryValue = array[currentIndex];
		array[currentIndex] = array[randomIndex];
		array[randomIndex] = temporaryValue;
	}
	return array;
}


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

	// getVideoQueue(page, perPage, () => {
		initializeUI();
		$("video.replay").trigger("click");
		connectWebsocket();
		// queueVideo(clipQueue.pop());
	// }, (err) => {
	// 	console.error(err);
	// });
});
