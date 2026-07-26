import speech_recognition as sr
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from assets.theme import inject_theme
from lib.speech_capture import SpeechAudioProcessor, transcribe_wav_bytes

st.set_page_config(page_title="Speech to Text — Accessible AI", page_icon="🎙️", layout="wide")
inject_theme()

st.title("Speech-to-Text Converter")
st.write("Record yourself speaking, then click **Transcribe** to convert it to text.")
st.caption(
    "Audio is streamed from your browser's microphone over WebRTC, so this works on a hosted "
    "deployment too, not just when running locally. Transcription uses Google's free Web Speech "
    "API via the `SpeechRecognition` library and requires an internet connection."
)

ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=SpeechAudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

col1, col2 = st.columns(2)
transcribe_clicked = col1.button("Transcribe recorded audio", disabled=not ctx.state.playing)
clear_clicked = col2.button("Clear buffered audio", disabled=not ctx.state.playing)

if clear_clicked and ctx.audio_processor:
    ctx.audio_processor.pop_wav_bytes()  # discard whatever's buffered
    st.info("Cleared.")

if transcribe_clicked:
    if not ctx.audio_processor:
        st.warning("Start the recorder above first.")
    else:
        wav_bytes = ctx.audio_processor.pop_wav_bytes()
        if wav_bytes is None:
            st.warning("No audio recorded yet — speak for a few seconds, then try again.")
        else:
            try:
                text = transcribe_wav_bytes(wav_bytes)
                st.subheader("Transcribed Text:")
                st.write(text)
            except sr.UnknownValueError:
                st.warning("Sorry, I couldn't understand that — try recording again.")
            except sr.RequestError as e:
                st.error(f"Could not reach the speech recognition service: {e}")
