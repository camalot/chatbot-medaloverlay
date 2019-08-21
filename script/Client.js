"use strict";
let isClipPlaying = false;

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
		$("#video-container video")
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
		$("#video-container video")
			.css("top", settings.AbsolutePositionTop !== 0 ? `${settings.AbsolutePositionTop}px` : 'initial')
			.css("bottom", settings.AbsolutePositionBottom !== 0 ? `${settings.AbsolutePositionBottom}px` : 'initial');
		$(".progress-container")
			.removeClass(positionVerticalClass);
		$(".progress-container")
			.css("top", settings.AbsolutePositionTop !== 0 ? `${settings.AbsolutePositionTop}px` : 'initial')
			.css("bottom", settings.AbsolutePositionBottom !== 0 ? `${settings.AbsolutePositionBottom}px` : 'initial');

	}

	// max-width
	// min-width
	let vwidth = settings.VideoWidth || 320;
	if(vwidth <= 0) {
		vwidth = 320;
	}

	$("#video-container video")
		.on("error", function (e) { console.error(`Error: ${e}`); })
		.on("canplay", function () { return videoLoaded(); })
		.on("ended", function () { return videoEnded(); })
		.css("max-width", `${vwidth}px`)
		.css("min-width", `${vwidth}px`);


	connectWebsocket();


});

function validateSettings() {
	let hasApiKey = typeof API_Key !== "undefined";
	let hasSettings = typeof settings !== "undefined";
	let hasVideoPath = hasSettings && settings.VideoPath !== "";
	let hasUsername = hasSettings && settings.Username !== "";
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

function videoLoaded() {
	console.log("video loaded");
	isClipPlaying = true;
	$('#video-container video')
		.addClass(settings.InTransition + ' animated')
		.removeClass("hidden")
		.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
			console.log("after entrance animation");
			$(this).removeClass();
		});
	$("#video-container").removeClass("hidden");
}

function videoEnded() {
	console.log("video ended");
	isClipPlaying = false;
	$("#video-container video")
		.removeClass()
		.addClass(settings.OutTransition + ' animated')
		.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
			console.log("after exit animation");
			$(this).removeClass().addClass("hidden");

			$("#video-container").addClass("hidden");
		});
}

// Connect to ChatBot websocket
// Automatically tries to reconnect on
// disconnection by recalling this method
function connectWebsocket() {

	//-------------------------------------------
	//  Create WebSocket
	//-------------------------------------------
	var socket = new WebSocket("ws://127.0.0.1:3337/streamlabs");

	//-------------------------------------------
	//  Websocket Event: OnOpen
	//-------------------------------------------
	socket.onopen = function () {
		console.log("open");
		// AnkhBot Authentication Information
		var auth = {
			author: "DarthMinos",
			website: "darthminos.tv",
			api_key: API_Key,
			events: [
				"EVENT_MEDAL_PLAY",
				"EVENT_MEDAL_VIDEO_WAIT",
				"EVENT_MEDAL_VIDEO_TIMEOUT",
				"EVENT_MEDAL_START"
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
		var socketMessage = JSON.parse(message.data);
		var eventName = socketMessage.event;
		console.log(socketMessage);

		switch (eventName) {
			case "EVENT_MEDAL_PLAY":
				if (isClipPlaying) {
					console.log("Received event to play, but video already playing.");
					return;
				}
				let eventData = JSON.parse(socketMessage.data || "{}");
				console.log(eventData);
				let webfile = `http://localhost:${eventData.port}/${eventData.video}`;

				$("#video-container video")
					.show()
					.prop("autoplay", true)
					.prop("muted", true)
					.attr("src", webfile)
					.empty()
					.append(`<source src="${webfile}" type="video/mp4" />`);
				break;
			case "EVENT_MEDAL_VIDEO_WAIT":
				console.log(eventName);
				break;
			case "EVENT_MEDAL_VIDEO_TIMEOUT":
				console.log(eventName);
				break;
			case "EVENT_MEDAL_START":
				console.log(eventName);
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
