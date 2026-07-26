import io
import threading
import wave

import av
import speech_recognition as sr
from streamlit_webrtc import AudioProcessorBase

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
        return frames  # nothing needs to play back to the user

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


def transcribe_wav_bytes(wav_bytes: bytes) -> str:
    """Runs the buffered recording through Google's free Web Speech API.
    Raises sr.UnknownValueError or sr.RequestError on failure."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio)
