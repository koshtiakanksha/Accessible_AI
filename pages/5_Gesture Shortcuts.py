import os
import time

import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from assets.theme import inject_theme
from lib.gesture_capture import GESTURE_LABELS, GestureVideoProcessor, MODEL_PATH

st.set_page_config(page_title="Gesture Shortcuts — Accessible AI", page_icon="👋", layout="wide")
inject_theme()

if not os.path.exists(MODEL_PATH):
    st.error(f"Model file not found: {MODEL_PATH}")
    st.stop()

st.title("Gesture Shortcuts")
st.write("Show one of the supported hand gestures to your camera to trigger its shortcut phrase.")
st.caption(
    "This recognizes a fixed set of generic hand gestures (thumbs up, peace sign, etc.) using "
    "MediaPipe's built-in gesture recognizer — it is not sign-language recognition. Video is "
    "streamed from your browser's camera over WebRTC, so this works on a hosted deployment too, "
    "not just when running locally."
)
st.write(", ".join(f"{k.replace('_', ' ')} → {v}" for k, v in GESTURE_LABELS.items()))

ctx = webrtc_streamer(
    key="gesture-shortcuts",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=GestureVideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
)

status_placeholder = st.empty()
if ctx.state.playing:
    while True:
        if ctx.video_processor:
            gesture = ctx.video_processor.last_stable_gesture
            if gesture:
                status_placeholder.success(
                    f"Last recognized: {GESTURE_LABELS.get(gesture, gesture)}"
                )
        else:
            break
        if not ctx.state.playing:
            break
        time.sleep(0.3)
else:
    status_placeholder.info("Click **Start** above and allow camera access to begin.")
