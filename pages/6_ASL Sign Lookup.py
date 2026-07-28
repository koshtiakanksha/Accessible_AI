import os
import threading

import numpy as np
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer

from assets.theme import inject_theme
from lib.sign_lookup import extract_landmark_sequence_from_frames, sequence_to_feature, top_k_matches

st.set_page_config(page_title="ASL Sign Lookup — Accessible AI", page_icon="🔎", layout="wide")
inject_theme()

REFERENCE_PATH = "sign_reference.npz"


class FrameBufferProcessor(VideoProcessorBase):
    """Just buffers raw frames from the browser's camera — the actual
    landmark extraction runs once, on demand, when you click Look Up, not
    live on every frame (unlike Gesture Shortcuts) since a real sign needs a
    few seconds of motion, not a single-frame classification."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._frames = []

    def recv(self, frame):
        with self._lock:
            self._frames.append(frame.to_ndarray(format="bgr24"))
        return frame  # unchanged passthrough; we just want a copy

    def pop_frames(self):
        with self._lock:
            frames, self._frames = self._frames, []
        return frames


@st.cache_data
def load_reference(path: str):
    if not os.path.exists(path):
        return None
    data = np.load(path)
    return {
        key[len("label::"):]: list(data[key])
        for key in data.files
        if key.startswith("label::")
    }


st.title("ASL Sign Lookup")
st.write(
    "Show a sign to your camera for a couple of seconds, then click **Look up this sign** "
    "to see the closest matching words."
)
st.caption(
    "This retrieves nearest matches from a small reference vocabulary — it does not "
    "translate continuous signing, and it will only recognize signs that are actually in "
    "the reference database (see README: Expanding the vocabulary and the gesture set)."
)

reference = load_reference(REFERENCE_PATH)

if reference is None:
    st.warning(
        f"No reference database found at `{REFERENCE_PATH}`. This page needs one built from "
        f"real labeled sign videos first — see `scripts/build_sign_reference.py` and the "
        f"README section on the ASL Citizen dataset. There's nothing to look up against yet."
    )
    st.stop()

st.caption(f"Reference vocabulary ({len(reference)} signs): " + ", ".join(sorted(reference.keys())))

ctx = webrtc_streamer(
    key="sign-lookup",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=FrameBufferProcessor,
    media_stream_constraints={"video": True, "audio": False},
)

if st.button("Look up this sign", disabled=not ctx.state.playing):
    if not ctx.video_processor:
        st.warning("Start the camera above first.")
    else:
        frames = ctx.video_processor.pop_frames()
        if len(frames) < 5:
            st.warning("Not enough video captured yet — show the sign for a couple of seconds first.")
        else:
            with st.spinner("Matching against the reference vocabulary..."):
                sequence = extract_landmark_sequence_from_frames(frames, fps=15)
                if sequence.shape[0] == 0:
                    st.warning("No hand detected in that clip — try again with your hand clearly in frame.")
                else:
                    feature = sequence_to_feature(sequence)
                    matches = top_k_matches(feature, reference, k=5)
                    st.subheader("Closest matches")
                    for label, distance in matches:
                        st.write(f"**{label}** — similarity {1 - distance:.0%}")
