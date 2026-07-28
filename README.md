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

## Expanding the vocabulary and the gesture set

These are two different problems with very different costs.

**Adding sign vocabulary** (the words/phrases Sign Vocabulary Explorer knows) is a
data change, not a code change: add an image to `sign_language_images/` and a line
to `sign_language_images/manifest.json`, then run
`python scripts/validate_sign_vocabulary.py` to check nothing's missing or orphaned.
**Read `sign_language_images/README.md` before adding any image** — an incorrect
handshape can genuinely mislead someone trying to communicate, so sign images need
to come from a verified source (a fluent signer, a recognized ASL reference), not
be improvised.

**Adding a new gesture shortcut** (beyond the 7 MediaPipe ships built in — Thumb_Up,
Thumb_Down, Victory, Pointing_Up, Fist, Open_Palm, ILoveYou) is a real machine-learning
project, not a config change: those 7 are the fixed output classes of Google's
pretrained model, and there's no flag to add an 8th. Doing this for real means
collecting ~100+ of your own labeled example photos per new gesture and fine-tuning
a new classification head with MediaPipe Model Maker. `scripts/train_custom_gesture.py`
is a template for that workflow (based on Google's documented API) — it needs its own
heavier dependency (`mediapipe-model-maker`, TensorFlow-based) and a real photo dataset
to actually run, neither of which are included here.

**Recognizing real ASL words from video** (not just 7 static hand poses) is a
different, bigger capability — the **ASL Sign Lookup** page and the tools behind it.

## ASL Sign Lookup — real-word sign recognition

Gesture Shortcuts recognizes 7 fixed static hand poses. ASL Sign Lookup is a separate
module aimed at actual ASL vocabulary: show a sign to your webcam, get back the closest
matching words from a reference dictionary. This mirrors how
[ASL Citizen](https://www.microsoft.com/en-us/research/project/asl-citizen/) — the
dataset this is built around — frames its own task: **dictionary retrieval**, not
continuous translation. Signs involve motion over time, so this needed a genuinely
different approach than the single-frame Model Maker classifier above.

**Why ASL Citizen over other options** (MS-ASL, WLASL): those distribute only
metadata pointing to external videos (mostly YouTube), most of which have died since
2019 — and none of them were collected with signer consent. ASL Citizen is 83k+ videos
across 2,731 signs from 52 consenting signers, downloadable directly from Microsoft
(non-commercial research license, citation required — see the project page).

**How it works**: `lib/sign_lookup.py` extracts a hand-landmark sequence per video/clip
using the same `gesture_recognizer.task` model already in this repo (its result includes
raw landmarks alongside the 7-class classification, so no extra model download was
needed), normalizes it for position/scale, resamples every clip to a fixed length, and
matches new clips against a reference database by nearest-neighbor cosine distance. This
is a deliberately simple baseline — not the I3D video-CNN ASL Citizen's own paper trains
— chosen because it needs no GPU and no multi-day training run. All the resampling/
distance-metric logic is unit-tested against synthetic sequences; the video-decode
pipeline was smoke-tested end to end with a synthetic no-hand clip.

**Setting it up requires the real dataset**, which isn't included here:

```bash
wget https://download.microsoft.com/download/b/8/8/b88c0bae-e6c1-43e1-8726-98cf5af36ca4/ASL_Citizen.zip
unzip ASL_Citizen.zip

python scripts/build_sign_reference.py \
    --videos-dir ASL_Citizen/videos --labels-csv ASL_Citizen/splits/train.csv \
    --classes hello thank-you please yes no help water bathroom \
    --out sign_reference.npz

python scripts/evaluate_sign_lookup.py \
    --reference sign_reference.npz \
    --videos-dir ASL_Citizen/videos --labels-csv ASL_Citizen/splits/test.csv
```

Start with a small, deliberately chosen vocabulary (10-30 everyday signs) rather than
all 2,731 classes — `build_sign_reference.py` processes every matching video through the
gesture recognizer, and a small working vocabulary beats a huge unfinished one.
`evaluate_sign_lookup.py` reports recall@1/@5/@10 on a held-out split, the same metric
the ASL Citizen paper itself uses — no numbers are claimed here until that's actually
been run against real data.

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

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/
```

28 tests, all currently passing, covering what's actually testable without a
camera, microphone, or real network access to Google's services:

- Sign lookup retrieval math (resampling, cosine distance, top-k ranking) —
  `tests/test_sign_lookup.py`
- The full video → landmark → feature pipeline, run end to end against a
  synthetic no-hand video — `tests/test_sign_lookup_pipeline.py`
- Gesture evaluation's precision/recall/F1/confusion-matrix computation —
  `tests/test_evaluate_gestures.py`
- The sign vocabulary manifest validator (missing files, orphaned images,
  duplicate phrases) — `tests/test_validate_sign_vocabulary.py`
- WAV encoding correctness in the live audio buffer —
  `tests/test_speech_capture.py`
- TTS filename uniqueness (a regression test for the original shared
  `output.mp3` bug), with `gTTS` mocked since real synthesis needs network
  access — `tests/test_tts.py`

`.github/workflows/ci.yml` runs a full compile check, this test suite, and the
vocabulary validator on every push and pull request.

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
scripts/validate_sign_vocabulary.py  Checks manifest.json against the image files on disk
scripts/train_custom_gesture.py      Template for training new gesture classes (needs your own data)
scripts/build_sign_reference.py      Builds an ASL sign reference database from ASL Citizen (needs the dataset)
scripts/evaluate_sign_lookup.py      Recall@k evaluation for ASL Sign Lookup (needs the dataset)
lib/sign_lookup.py                   Landmark extraction + nearest-neighbor retrieval for ASL Sign Lookup
pages/6_ASL Sign Lookup.py           Real-word sign recognition (needs a built reference database)
sign_language_images/manifest.json   Phrase → image mapping for Sign Vocabulary Explorer
tests/                        Unit tests (pytest) — see Testing section below
.github/workflows/ci.yml      Runs compile check + tests + manifest validation on push/PR
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
5. ✅ **Automated tests + CI** — 28 unit tests covering the retrieval math, the
   evaluation harnesses' metric computation, the vocabulary validator, WAV encoding,
   and TTS filename uniqueness (mocked where real network calls would be needed);
   `.github/workflows/ci.yml` runs them plus a full compile check and the manifest
   validator on every push/PR.

Beyond the original 5 phases: **ASL Sign Lookup** (see above) — real-word sign
recognition via ASL Citizen, not on the original roadmap but a bigger capability
upgrade than any single phase here. Populating its reference database with real
data is its own next step, independent of phases 1-5.

## Contributing

Contributions are welcome — fork, branch, commit, open a PR.

## License

MIT License.
