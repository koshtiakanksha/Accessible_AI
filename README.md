# Accessible AI — Communication Modality Prototypes

A small collection of tools exploring different communication modalities for
accessibility — voice, captions, and gesture shortcuts, meeting in one conversation view.

## About the project

Accessible AI explores different communication modalities for accessibility — speech,
written captions, and gesture shortcuts — and merges them into one conversation view.
It started as four disconnected proof-of-concept demos and is being actively rebuilt
into a more cohesive, honestly-scoped project. This README describes what the app
**actually does today** — see [Roadmap](#roadmap) for where it's headed.

Each modality has a consistent accent color used everywhere it appears (cards, chat
bubbles, tags): **voice** (gold), **caption** (teal), **signal** (violet). Body text
uses Atkinson Hyperlegible, a typeface designed by the Braille Institute for maximum
legibility for low-vision readers.

## What's in here today

| Page | What it does | Known limitation |
|---|---|---|
| **Conversation** *(new)* | Merges the three interactive modalities below into one screen: speak → transcribed message, show a gesture → shortcut phrase (spoken aloud automatically), type a reply → spoken aloud. Includes quick-reply phrases and a downloadable transcript | Gesture detection here polls once per second rather than live video overlay, to keep the reply controls clickable at the same time |
| **Speech to Text** | Records your browser's microphone over WebRTC, then transcribes it on demand using `SpeechRecognition` | Requires an internet connection (Google's free Web Speech API); not real-time streaming — you record, then click Transcribe |
| **Text to Speech** | Converts typed text to audio with `gTTS` | Requires an internet connection (gTTS calls Google's TTS service) |
| **Sign Vocabulary Explorer** | Looks up a small, fixed set of stored sign images for known words/phrases | This is a vocabulary lookup, not sign-language translation — ASL has its own grammar that word-by-word image lookup doesn't capture |
| **Gesture Shortcuts** | Streams your browser's camera over WebRTC and recognizes 7 generic hand gestures (thumbs up, peace sign, etc.) via MediaPipe's built-in gesture recognizer, mapping each to a shortcut phrase | This is generic gesture recognition with manually assigned labels, not sign-language recognition |

## Why the naming changed

Earlier versions of this README described "Text-to-Sign Language" translation and
"Sign Language Recognition." Neither claim was accurate for what the code does — both
features work on a small fixed vocabulary/gesture set rather than actual sign-language
grammar. The pages and README now describe what's really happening.

## Tech stack

- **UI**: Streamlit (multipage app)
- **Browser mic/camera capture**: `streamlit-webrtc` (WebRTC), so both work on a hosted
  deployment, not just when running locally
- **Speech-to-text**: `SpeechRecognition` (Google Web Speech API)
- **Text-to-speech**: `gTTS`
- **Gesture recognition**: MediaPipe Gesture Recognizer, OpenCV

## Installation

### Prerequisites

Python 3.10+ is recommended.

### Steps

```bash
git clone https://github.com/koshtiakanksha/Accessible_AI.git
cd Accessible_AI
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

The speech and gesture pages capture your microphone/camera through your browser over
WebRTC, so they work the same way whether you're running locally or visiting a hosted
deployment (e.g. Streamlit Community Cloud) — you'll just need to grant the browser
mic/camera permission prompt.

## Evaluation

`scripts/evaluate_gestures.py` and `scripts/evaluate_speech.py` measure the two
ML-driven pieces of this app instead of just asserting they work.

```bash
pip install -r requirements-dev.txt
python scripts/evaluate_gestures.py test_data/gestures   # see test_data/gestures/README.md
python scripts/evaluate_speech.py
```

**Gesture recognizer** (`evaluate_gestures.py`): runs the exact model the app uses
against a labeled folder of your own gesture photos and reports per-class
precision/recall/F1, a confusion matrix, false-activation rate (how often a
no-hand/unsupported-gesture photo gets misread as a real gesture), and
inference latency. No photos are checked into this repo — add your own under
`test_data/gestures/<ClassName>/` (see the README there). A synthetic smoke
test (3 plain no-hand images) confirmed the pipeline runs end to end and
correctly measured **17.1ms average inference latency** and a **0%
false-activation rate on those 3 images** — real numbers, but from synthetic
smoke-test images, not a real accuracy evaluation. Populate the class folders
with real photos to get real per-class numbers.

**Speech-to-text** (`evaluate_speech.py`): synthesizes known sentences with
gTTS and round-trips them through the app's own transcription function,
reporting Word Error Rate. This is a synthetic-audio proxy, not a real-speech
benchmark — see the script's docstring for what it does and doesn't tell you.
The WER metric itself was unit-tested against hand-crafted reference/hypothesis
pairs to confirm it computes correctly.

## Known limitations (read before assuming a feature works)

- Speech-to-text is record-then-transcribe, not live streaming captions — you speak,
  stop, and click Transcribe.
- The sign vocabulary and gesture-shortcut sets are both small and fixed; neither is a
  general-purpose sign-language system.
- There is no automated test suite or accuracy evaluation yet (in progress — see
  Roadmap).
- gTTS and speech transcription both require an internet connection; there's no offline
  fallback for either.
- WebRTC connections can occasionally fail to establish behind restrictive
  firewalls/NATs without a TURN server configured — if the camera/mic preview never
  appears, that's the likely cause.

## Repo layout

```
Home.py                       Landing page
pages/1_Conversation.py       Merged voice + caption + gesture view
pages/2-5_*.py                Standalone single-modality pages
assets/theme.py               Shared design tokens + CSS + hero/card components
lib/speech_capture.py         WebRTC mic buffering + transcription
lib/gesture_capture.py        WebRTC camera + MediaPipe gesture recognition
lib/tts.py                    gTTS synthesis helper
scripts/evaluate_gestures.py  Gesture recognizer eval (precision/recall/F1/confusion matrix)
scripts/evaluate_speech.py    Speech pipeline round-trip WER check
test_data/gestures/           Your own labeled gesture photos go here (not checked in)
```

The standalone pages and Conversation mode both import from `lib/`, so there's one
implementation of each capability, not four copies drifting apart.

## Roadmap

This project is being rebuilt in phases toward a more complete, honestly-scoped
"one product" experience rather than four separate demos:

1. ✅ **Integrity pass** — fix known bugs, rename misleading features, document real
   limitations.
2. ✅ **Browser-based mic/camera capture** via `streamlit-webrtc` — the hosted demo now
   works for visitors, not just local runs.
3. ✅ **Conversation mode** — voice, captions, and gesture shortcuts merged into one
   screen.
4. 🔄 **In progress**: evaluation harnesses for the gesture recognizer and speech
   pipeline are built and working (see [Evaluation](#evaluation)) — actual accuracy
   numbers still need real gesture photos and a real-microphone environment to
   populate.
5. Basic automated tests + CI.

## Contributing

Contributions are welcome — fork, branch, commit, open a PR.

## License

MIT License.
