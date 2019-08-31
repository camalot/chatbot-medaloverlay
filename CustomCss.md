## SELECTORS

```css
#video-container .video-box {
  /* This is the container that holds the video-border-box and the video elements */
}

#video-container .video-box .video-border-box {
	/* This container sits directly on top of the video and is sized the same as the video */
}

#video-container .video-box video {
	/* This is the video container */
}

progress[value] {
	/* change the height and position of the progress bar */
	/* height: 7px; */
	/* left: 113px; */
	/* padding: 0 113px 0 0 */
	/* margin: 0 0 3px 0 */
}

progress::-webkit-progress-value {
	/* set the bar color */
  /*background: #57d12a;*/
}
```