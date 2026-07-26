"""
Round-trip transcription check: synthesizes a set of known test sentences
with gTTS, feeds that audio through the exact same transcription function the
app uses (lib.speech_capture.transcribe_wav_bytes), and reports Word Error
Rate (WER) per sentence and overall.

IMPORTANT — what this does and doesn't tell you:
This is a synthetic-audio proxy, not a human-speech benchmark. It tells you
whether the pipeline faithfully round-trips clean, clearly-enunciated
synthetic speech end to end — useful as a regression check (did a dependency
bump silently break transcription?) and as a latency measurement. It does
NOT tell you how the app performs on real accents, background noise, or
natural speaking pace — don't report this number as "real-world accuracy."

Requires internet access to gTTS and Google's Web Speech API (both are
reached by the app itself, so if this can't run, the app's Speech-to-Text
page can't either, which is itself useful to know).

Usage:
    python scripts/evaluate_speech.py
    python scripts/evaluate_speech.py --report my_speech_report.md
"""

import argparse
import os
import sys
import tempfile
import time

import av
from gtts import gTTS
import jiwer
import speech_recognition as sr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.speech_capture import RESAMPLE_RATE, transcribe_wav_bytes

TEST_SENTENCES = [
    "hello how are you today",
    "please can you help me find the exit",
    "thank you very much for your time",
    "i would like a glass of water",
    "can you repeat that one more time",
    "the weather is nice this afternoon",
]


def synthesize_wav_bytes(text: str) -> bytes:
    """Synthesizes `text` with gTTS (mp3) and decodes it to the same 16kHz
    mono PCM WAV format the live microphone path produces, using PyAV (which
    the project already depends on via streamlit-webrtc — no extra audio
    dependency needed just for this)."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        gTTS(text=text).save(tmp.name)
        mp3_path = tmp.name

    try:
        container = av.open(mp3_path)
        resampler = av.AudioResampler(format="s16", layout="mono", rate=RESAMPLE_RATE)
        pcm_chunks = []
        for frame in container.decode(audio=0):
            for resampled in resampler.resample(frame):
                pcm_chunks.append(bytes(resampled.planes[0]))
        container.close()
    finally:
        os.remove(mp3_path)

    import io
    import wave

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(RESAMPLE_RATE)
        wav_file.writeframes(b"".join(pcm_chunks))
    return wav_buffer.getvalue()


def evaluate(sentences):
    rows = []
    for sentence in sentences:
        try:
            wav_bytes = synthesize_wav_bytes(sentence)
        except Exception as e:
            rows.append({"reference": sentence, "hypothesis": None, "wer": None, "error": str(e)})
            continue

        start = time.time()
        try:
            hypothesis = transcribe_wav_bytes(wav_bytes)
            latency = time.time() - start
            wer = jiwer.wer(sentence, hypothesis)
            rows.append(
                {
                    "reference": sentence,
                    "hypothesis": hypothesis,
                    "wer": wer,
                    "latency_s": latency,
                    "error": None,
                }
            )
        except sr.UnknownValueError:
            rows.append({"reference": sentence, "hypothesis": "", "wer": 1.0, "error": None})
        except sr.RequestError as e:
            rows.append({"reference": sentence, "hypothesis": None, "wer": None, "error": str(e)})
    return rows


def render_report(rows) -> str:
    scored = [r for r in rows if r["wer"] is not None]
    corpus_wer = (
        jiwer.wer([r["reference"] for r in scored], [r["hypothesis"] for r in scored])
        if scored
        else None
    )
    avg_latency = (
        sum(r.get("latency_s", 0) for r in scored) / len(scored) if scored else None
    )

    lines = ["# Speech-to-Text Evaluation Report (synthetic round-trip)\n"]
    lines.append(
        "**This measures pipeline round-trip fidelity on clean synthetic speech, "
        "not real-world accuracy.** See the script docstring for why.\n"
    )
    if corpus_wer is not None:
        lines.append(f"**Corpus Word Error Rate: {corpus_wer:.1%}** ({len(scored)}/{len(rows)} sentences scored)\n")
    if avg_latency is not None:
        lines.append(f"**Average transcription latency: {avg_latency:.2f}s per sentence**\n")

    lines.append("## Per-sentence results\n")
    lines.append("| Reference | Hypothesis | WER | Notes |")
    lines.append("|---|---|---|---|")
    for r in rows:
        if r["error"]:
            lines.append(f"| {r['reference']} | — | — | Error: {r['error']} |")
        else:
            lines.append(
                f"| {r['reference']} | {r['hypothesis']} | {r['wer']:.1%} | |"
            )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--report", default="speech_eval_report.md")
    args = parser.parse_args()

    print(f"Running {len(TEST_SENTENCES)} synthetic round-trip test sentences...")
    rows = evaluate(TEST_SENTENCES)
    report = render_report(rows)
    with open(args.report, "w") as f:
        f.write(report)
    print(f"Report written to {args.report}")


if __name__ == "__main__":
    main()
