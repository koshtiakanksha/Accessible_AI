import os
import time

import speech_recognition as sr
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from assets.theme import inject_theme
from lib.gesture_capture import GESTURE_LABELS, GestureVideoProcessor, MODEL_PATH
from lib.speech_capture import SpeechAudioProcessor, transcribe_wav_bytes
from lib.tts import synthesize_to_file

st.set_page_config(page_title="Conversation — Accessible AI", page_icon="💬", layout="wide")
inject_theme()

QUICK_PHRASES = ["Hello", "Yes", "No", "Thank you", "One moment please", "Can you repeat that?"]

if "transcript" not in st.session_state:
    st.session_state.transcript = []  # list of {"kind": "voice"|"signal"|"reply", "text": str}
if "seen_gesture_at" not in st.session_state:
    st.session_state.seen_gesture_at = 0.0


def add_message(kind: str, text: str) -> None:
    st.session_state.transcript.append({"kind": kind, "text": text})


st.title("Conversation")
st.write(
    "Voice, captions, and gesture shortcuts in one place — this is what the four separate "
    "demo pages add up to."
)

left, center, right = st.columns([1.1, 1.4, 1])

# ---------------- Left: capture ----------------
with left:
    st.markdown('<span class="tag tag-voice">Voice</span>', unsafe_allow_html=True)
    st.markdown("**Speak**")
    audio_ctx = webrtc_streamer(
        key="conversation-audio",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=SpeechAudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )
    if st.button("Transcribe & add to conversation", disabled=not audio_ctx.state.playing):
        if audio_ctx.audio_processor:
            wav_bytes = audio_ctx.audio_processor.pop_wav_bytes()
            if wav_bytes is None:
                st.warning("No audio recorded yet — speak for a few seconds first.")
            else:
                try:
                    text = transcribe_wav_bytes(wav_bytes)
                    add_message("voice", text)
                    st.rerun()
                except sr.UnknownValueError:
                    st.warning("Couldn't understand that — try again.")
                except sr.RequestError as e:
                    st.error(f"Speech service unreachable: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="tag tag-signal">Signal</span>', unsafe_allow_html=True)
    st.markdown("**Show a gesture**")
    if not os.path.exists(MODEL_PATH):
        st.error("Gesture model file not found.")
        gesture_ctx = None
    else:
        gesture_ctx = webrtc_streamer(
            key="conversation-video",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=GestureVideoProcessor,
            media_stream_constraints={"video": True, "audio": False},
        )
        st.caption(", ".join(GESTURE_LABELS.values()))

# ---------------- Center: transcript ----------------
with center:
    top_cols = st.columns(2)
    if top_cols[0].button("Clear conversation"):
        st.session_state.transcript = []
        st.rerun()
    transcript_text = "\n".join(
        f"[{m['kind']}] {m['text']}" for m in st.session_state.transcript
    )
    top_cols[1].download_button(
        "Download transcript", transcript_text or "(empty)", file_name="conversation.txt",
        disabled=not st.session_state.transcript,
    )

    st.markdown("&nbsp;", unsafe_allow_html=True)
    if not st.session_state.transcript:
        st.info("Nothing yet — speak, show a gesture, or send a reply to start the conversation.")
    else:
        bubble_class = {"voice": "bubble-voice", "signal": "bubble-signal", "reply": "bubble-caption"}
        who_label = {"voice": "You (spoke)", "signal": "Gesture", "reply": "Reply"}
        for m in st.session_state.transcript:
            st.markdown(
                f"""<div class="bubble {bubble_class[m['kind']]}">
                        <span class="who">{who_label[m['kind']]}</span>{m['text']}
                    </div>""",
                unsafe_allow_html=True,
            )

# ---------------- Right: reply ----------------
with right:
    st.markdown('<span class="tag tag-caption">Caption</span>', unsafe_allow_html=True)
    st.markdown("**Reply**")
    reply_text = st.text_area("Type a reply", label_visibility="collapsed", key="reply_box")
    if st.button("Speak reply & add to conversation"):
        if not reply_text.strip():
            st.warning("Type something first.")
        else:
            try:
                path = synthesize_to_file(reply_text)
                add_message("reply", reply_text.strip())
                st.audio(path)
                st.rerun()
            except Exception as e:
                st.error(f"Couldn't generate speech: {e}")

    st.markdown("<br>**Quick phrases**", unsafe_allow_html=True)
    for phrase in QUICK_PHRASES:
        if st.button(phrase, key=f"quick_{phrase}"):
            try:
                path = synthesize_to_file(phrase)
                add_message("reply", phrase)
                st.audio(path)
                st.rerun()
            except Exception as e:
                st.error(f"Couldn't generate speech: {e}")

# ---------------- Gesture polling ----------------
# Full-script rerun once a second while the camera is on, rather than a
# blocking while-loop, so the reply controls on the right stay clickable
# in between. Not real-time, but keeps every widget interactive.
if gesture_ctx and gesture_ctx.state.playing and gesture_ctx.video_processor:
    gesture = gesture_ctx.video_processor.last_stable_gesture
    at = gesture_ctx.video_processor.last_stable_at
    if gesture and at > st.session_state.seen_gesture_at:
        st.session_state.seen_gesture_at = at
        phrase = GESTURE_LABELS.get(gesture, gesture)
        add_message("signal", phrase)
        try:
            path = synthesize_to_file(phrase.split(" ", 1)[-1])  # speak the phrase, skip the emoji
            st.audio(path, autoplay=True)
        except Exception:
            pass
        st.rerun()
    time.sleep(1)
    st.rerun()
