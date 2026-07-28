import wave
import io

from lib.speech_capture import RESAMPLE_RATE, SpeechAudioProcessor


def test_pop_wav_bytes_returns_none_when_buffer_empty():
    processor = SpeechAudioProcessor()
    assert processor.pop_wav_bytes() is None


def test_pop_wav_bytes_clears_buffer_after_popping():
    processor = SpeechAudioProcessor()
    processor._buffer = [b"\x00\x00" * 100]  # fake PCM data, bypassing recv_queued

    first = processor.pop_wav_bytes()
    second = processor.pop_wav_bytes()

    assert first is not None
    assert second is None  # buffer was cleared, not left with stale audio


def test_pop_wav_bytes_produces_valid_wav_with_correct_format():
    processor = SpeechAudioProcessor()
    processor._buffer = [b"\x00\x00" * 1000]

    wav_bytes = processor.pop_wav_bytes()

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() == RESAMPLE_RATE
