import os
import threading
import time

import av
import cv2
import mediapipe as mp
from streamlit_webrtc import VideoProcessorBase

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BASE_DIR, "gesture_recognizer.task")

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

GESTURE_LABELS = {
    "Thumb_Up": "👍 Yes",
    "Thumb_Down": "👎 No",
    "Victory": "✌️ Peace",
    "Pointing_Up": "☝️ Up",
    "Fist": "✊ Sorry",
    "Open_Palm": "👋 Hello",
    "ILoveYou": "🤟 I Love You",
}

# A single noisy frame shouldn't count as a real gesture, and one held gesture
# shouldn't re-trigger every frame while it's held. STABILITY_FRAMES requires
# several consecutive identical predictions before we call it a real
# detection; COOLDOWN_SECONDS blocks the same gesture from re-firing too soon.
STABILITY_FRAMES = 5
COOLDOWN_SECONDS = 1.5


class GestureVideoProcessor(VideoProcessorBase):
    """Runs MediaPipe's gesture recognizer on frames streamed from the
    browser's camera over WebRTC (instead of cv2.VideoCapture(0), which only
    ever opened the camera of the machine running the Streamlit server)."""

    def __init__(self) -> None:
        options = GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
        )
        self._recognizer = GestureRecognizer.create_from_options(options)
        self._start_time_ms = int(time.time() * 1000)
        self._recent_predictions: list = []
        self._last_triggered = {"gesture": None, "at": 0.0}
        self._lock = threading.Lock()
        # Read by the main script thread; written here from the WebRTC worker thread.
        self.last_stable_gesture = None
        self.last_stable_at = 0.0

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

        # Monotonically increasing ms since this stream started (the old code
        # added the full Unix epoch on every frame instead).
        timestamp_ms = int(time.time() * 1000) - self._start_time_ms
        results = self._recognizer.recognize_for_video(mp_image, timestamp_ms)

        raw_gesture = None
        if results.gestures:
            raw_gesture = results.gestures[0][0].category_name

        with self._lock:
            self._recent_predictions.append(raw_gesture)
            self._recent_predictions = self._recent_predictions[-STABILITY_FRAMES:]

            is_stable = (
                len(self._recent_predictions) == STABILITY_FRAMES
                and len(set(self._recent_predictions)) == 1
                and self._recent_predictions[0] is not None
            )

            now = time.time()
            if is_stable:
                stable_gesture = self._recent_predictions[0]
                already_shown_recently = (
                    stable_gesture == self._last_triggered["gesture"]
                    and now - self._last_triggered["at"] <= COOLDOWN_SECONDS
                )
                if not already_shown_recently:
                    self._last_triggered = {"gesture": stable_gesture, "at": now}
                    self.last_stable_gesture = stable_gesture
                    self.last_stable_at = now

        if raw_gesture:
            label = GESTURE_LABELS.get(raw_gesture, "Unknown gesture")
            cv2.putText(image, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

        return av.VideoFrame.from_ndarray(image, format="bgr24")
