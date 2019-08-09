"use strict";

// Start ws connection after document is loaded
jQuery(document).ready(function() {

	// Connect if API_Key is inserted
	// Else show an error on the overlay
	if (typeof API_Key === "undefined") {
		$("body").html("No API Key found or load!<br>Rightclick on the script in ChatBot and select \"Insert API Key\"");
		$("body").css({"font-size": "20px", "color": "#ff8080", "text-align": "center"});
	} else {
		connectWebsocket();
	}

});

function videoLoaded() {
	console.log("video loaded");
	$('#video-container video').removeClass().addClass(settings.InTransition + ' animated');
}

function videoEnded() {
	console.log("video ended");
	$("#video-container video").removeClass().addClass(settings.OutTransition + ' animated')
		.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
			$(this).hide().removeClass();
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
	socket.onopen = function() {
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
				var eventData = JSON.parse(socketMessage.data || "{}");
				console.log(eventData);
				// <video autoplay src="videos/MuricaBear/orangejustice.webm"></video>
				$("#video-container video")
					.show()
					.prop("autoplay", true)
					.prop("muted", true)
					.attr("src", `${settings.VideoPath}/${eventData.video}`)
					.on("play", function() { return videoLoaded(); })
					.on("ended", function () { return videoEnded(); });
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
	socket.onerror = function(error) {
		console.log("Error: " + error);
	};

	//-------------------------------------------
	//  Websocket Event: OnClose
	//-------------------------------------------
	socket.onclose = function() {
		console.log("close");
		// Clear socket to avoid multiple ws objects and EventHandlings
		socket = null;
		// Try to reconnect every 5s
		setTimeout(function(){connectWebsocket()}, 5000);
	};

}
