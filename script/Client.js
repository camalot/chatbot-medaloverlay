"use strict";
let isClipPlaying = false;
let refreshAfter = false;

if (!window.settings) {
	window.settings = {};
}

window.settings = { ...DEFAULT_SETTINGS, ...window.settings };

// Start ws connection after document is loaded
jQuery(document).ready(function () {
	// verify settings...
	let validatedSettings = validateSettings();

	// Connect if API_Key is inserted
	// Else show an error on the overlay
	if (!validatedSettings.isValid) {
		$(".config-messages").removeClass("hidden");
		$(".config-messages .settings").removeClass(validatedSettings.hasSettings ? "valid" : "hidden");
		$(".config-messages .api-key").removeClass(validatedSettings.hasApiKey ? "valid" : "hidden");
		$(".config-messages .medal-username").removeClass(validatedSettings.hasUsername ? "valid" : "hidden");
		$(".config-messages .medal-video-path").removeClass(validatedSettings.hasVideoPath ? "valid" : "hidden");
		$(".config-messages .medal-hotkey").removeClass(validatedSettings.hasHotkey ? "valid" : "hidden");

		return;
	}

	initializeUI();
	connectWebsocket();
});

function initializeUI() {
	let positionHorizontalClass = (settings.PositionHorizontal.toLowerCase() || "right");
	let positionVerticalClass = (settings.PositionVertical.toLowerCase() || "middle");

	let usePositionHorizontal = settings.UsePositionHorizontal;
	let usePositionVertical = settings.UsePositionVertical;

	$("#video-container")
		.addClass(positionHorizontalClass)
		.addClass(positionVerticalClass);
	$(".progress-container")
		.addClass(positionHorizontalClass)
		.addClass(positionVerticalClass);

	if (!usePositionHorizontal) {
		$("#video-container")
			.removeClass(positionHorizontalClass);
		$("#video-container .video-box")
			.css("left", settings.AbsolutePositionLeft !== 0 ? `${settings.AbsolutePositionLeft}px` : 'initial')
			.css("right", settings.AbsolutePositionRight !== 0 ? `${settings.AbsolutePositionRight}px` : 'initial');

		$(".progress-container")
			.removeClass(positionHorizontalClass);
		$(".progress-container")
			.css("left", settings.AbsolutePositionLeft !== 0 ? `${settings.AbsolutePositionLeft}px` : 'initial')
			.css("right", settings.AbsolutePositionRight !== 0 ? `${settings.AbsolutePositionRight}px` : 'initial');
	}

	if (!usePositionVertical) {
		$("#video-container")
			.removeClass(positionVerticalClass);
		$("#video-container .video-box")
			.css("top", settings.AbsolutePositionTop !== 0 ? `${settings.AbsolutePositionTop}px` : 'initial')
			.css("bottom", settings.AbsolutePositionBottom !== 0 ? `${settings.AbsolutePositionBottom}px` : 'initial');
		$(".progress-container")
			.removeClass(positionVerticalClass);
		$(".progress-container")
			.css("top", settings.AbsolutePositionTop !== 0 ? `${settings.AbsolutePositionTop}px` : 'initial')
			.css("bottom", settings.AbsolutePositionBottom !== 0 ? `${settings.AbsolutePositionBottom}px` : 'initial');

	}

	let vwidth = settings.VideoWidth || 320;
	if (vwidth <= 0) {
		vwidth = 320;
	}
	let vheight = Math.round((vwidth / 16) * 9);


	var fontName = settings.FontName;
	var customFontName = settings.CustomFontName;
	if (fontName && fontName === "custom" && customFontName && customFontName !== "") {
		loadFontsScript(customFontName);
	} else {
		$(":root").css("--font-name", fontName);
	}


	$(":root")
		.css("--video-width", `${vwidth}px`)
		.css("--video-height", `${vheight}px`)
		.css("--replay-font-color", `${settings.TitleFontColor || "rgba(255,255,255,1)"}`)
		.css("--replay-font-size", `${settings.TitleFontSize || 3.5}em`)
		.css("--replay-text-align", `${settings.TitleTextAlign || "center"}`)
		;


	$("#video-container video.replay")
		.on("error", function (e) { console.error(`Error: ${e}`); })
		.on("canplay", videoLoaded)
		.on("ended pause", videoEnded)
		.on("timeupdate", timelapse);

	$("#video-container .video-box .video-border-box")
		.addClass(settings.VideoFrameBackground)
		/*.css("background-size", `${vwidth}px ${vheight}px`)*/;

	if (settings.VideoFrameCustomBackground != null && settings.VideoFrameCustomBackground !== "") {
		$("#video-container .video-box .video-border-box.custom")
			.css("background-image", `url('${settings.VideoFrameCustomBackground}')`);
	}

	if (settings.ProgressBarBackgroundColor != null && settings.ProgressBarBackgroundColor !== "") {
		$(":root")
			.css("--progress-bg", settings.ProgressBarBackgroundColor);
	}

	if (settings.ProgressBarFillColor != null && settings.ProgressBarFillColor !== "") {
		$(":root")
			.css("--progress-fill", settings.ProgressBarFillColor);
	}
}

function validateSettings() {
	let hasApiKey = typeof API_Key !== "undefined";
	let hasSettings = typeof settings !== "undefined";
	let hasVideoPath = hasSettings && settings.VideoPath !== "";
	let hasUsername = hasSettings && settings.userName !== "";
	let hasHotkey = hasSettings && settings.HotKey !== "";

	return {
		isValid: hasApiKey && hasHotkey && hasUsername && hasVideoPath && hasSettings,
		hasSettings: hasSettings,
		hasApiKey: hasApiKey,
		hasHotkey: hasHotkey,
		hasUsername: hasUsername,
		hasVideoPath: hasVideoPath
	};
}

function loadFontsScript(font) {
	let fnt = font.toLowerCase().replace(" ", "-");
	var script = document.createElement('script');
	script.onload = function () {
		$(":root").css("--font-name", `${fnt}, Arial, sans-serif`);
	};
	script.src = `http://use.edgefonts.net/${fnt}.js`;

	document.head.appendChild(script);
}

function timelapse(e) {
	let video = $("#video-container .video-box video.replay").get(0);
	let pbar = $("#video-container .video-box progress").get(0);
	if (video.duration && video.currentTime) {
		let percent = (100 / video.duration) * video.currentTime;
		pbar.value = percent;
	} else {
		pbar.value = 0;
	}
}

function videoLoaded(e) {
	console.log("video loaded");
	isClipPlaying = true;
	//	$("#video-container .video-box progress").attr("max", this.duration);
	$('#video-container .video-box')
		.addClass(settings.InTransition + ' animated')
		.removeClass("hidden")
		.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
			$(this).removeClass().addClass("video-box");
		});
	$("#video-container").removeClass("hidden");
}

function videoEnded(e) {
	console.log("video ended");
	isClipPlaying = false;

	$("#video-container .video-box")
		.removeClass().addClass("video-box")
		.addClass(settings.OutTransition + ' animated')
		.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
			$(this).removeClass().addClass("video-box");

			$("#video-container").addClass("hidden");

			if (refreshAfter) {
				location.reload();
			}
		});
}

// Connect to ChatBot websocket
// Automatically tries to reconnect on
// disconnection by recalling this method
function connectWebsocket() {

	//-------------------------------------------
	//  Create WebSocket
	//-------------------------------------------
	let socket = new WebSocket("ws://127.0.0.1:3337/streamlabs");

	//-------------------------------------------
	//  Websocket Event: OnOpen
	//-------------------------------------------
	socket.onopen = function () {
		console.log("open");
		// AnkhBot Authentication Information
		let auth = {
			author: "DarthMinos",
			website: "darthminos.tv",
			api_key: API_Key,
			events: [
				"EVENT_MEDAL_PLAY",
				"EVENT_MEDAL_STOP",
				"EVENT_MEDAL_START",
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
	socket.onmessage = function (message) {
		console.log(message);
		// Parse message
		let socketMessage = JSON.parse(message.data);
		let eventName = socketMessage.event;
		console.log(socketMessage);
		let eventData = typeof socketMessage.data === "string" ? JSON.parse(socketMessage.data || "{}") : socketMessage.data;

		switch (eventName) {
			case "EVENT_MEDAL_PLAY":
				if (isClipPlaying) {
					console.log("Received event to play, but video already playing.");
					return;
				}
				console.log(eventData);
				let webfile = `http://localhost:${eventData.port}/${eventData.video}`;

				$("#video-container video.replay")
					.show()
					.prop("autoplay", true)
					.prop("muted", true)
					.attr("src", webfile)
					.empty()
					.append(`<source src="${webfile}" type="video/mp4" />`);
				let videoPlayer = $("#video-container video.replay").get(0);
				videoPlayer.playbackRate = settings.PlaybackSpeed || 1.0;
				console.log(`playback speed: ${settings.PlaybackSpeed || 1.0}`);

				break;
			case "EVENT_MEDAL_STOP":
				console.log("STOP VIDEO");
				$("#video-container video.replay")
					.get(0)
					.pause();
				break;
			case "EVENT_MEDAL_RELOAD":
				if(isClipPlaying) {
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
	socket.onerror = function (error) {
		console.error(`Error: ${error}`);
	};

	//-------------------------------------------
	//  Websocket Event: OnClose
	//-------------------------------------------
	socket.onclose = function () {
		console.log("close");
		// Clear socket to avoid multiple ws objects and EventHandlings
		socket = null;
		// Try to reconnect every 5s
		setTimeout(function () { connectWebsocket() }, 5000);
	};

}
