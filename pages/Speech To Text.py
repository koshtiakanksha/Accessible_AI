import io
import threading
import wave

import av
import speech_recognition as sr
import streamlit as st
from streamlit_webrtc import AudioProcessorBase, WebRtcMode, webrtc_streamer

RESAMPLE_RATE = 16000  # Hz, mono, 16-bit — matches what SpeechRecognition expects


class SpeechAudioProcessor(AudioProcessorBase):
    """Buffers audio streamed from the browser's microphone over WebRTC
    (instead of sr.Microphone(), which only ever opened the microphone of the
    machine running the Streamlit server — never the visitor's browser)."""

    def __init__(self) -> None:
        self._resampler = av.AudioResampler(format="s16", layout="mono", rate=RESAMPLE_RATE)
        self._lock = threading.Lock()
        self._buffer: list[bytes] = []

    def recv_queued(self, frames: list) -> list:
        with self._lock:
            for frame in frames:
                for resampled in self._resampler.resample(frame):
                    self._buffer.append(bytes(resampled.planes[0]))
        # Nothing needs to play back to the user, so just pass frames through.
        return frames

    def pop_wav_bytes(self) -> bytes | None:
        """Returns the buffered audio as WAV bytes and clears the buffer."""
        with self._lock:
            if not self._buffer:
                return None
            pcm_data = b"".join(self._buffer)
            self._buffer = []

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(RESAMPLE_RATE)
            wav_file.writeframes(pcm_data)
        return wav_buffer.getvalue()


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
            recognizer = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
                audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio)
                st.subheader("Transcribed Text:")
                st.write(text)
            except sr.UnknownValueError:
                st.warning("Sorry, I couldn't understand that — try recording again.")
            except sr.RequestError as e:
                st.error(f"Could not reach the speech recognition service: {e}")
