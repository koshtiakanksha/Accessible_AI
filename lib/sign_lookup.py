"""
Core logic for isolated sign lookup: "show a sign to the camera, get back the
most likely matching words" — the same task ASL Citizen's own paper frames as
"dictionary retrieval," deliberately distinct from continuous sign-language
translation (which needs grammar, co-articulation, and facial/non-manual
markers this does not attempt to handle).

Reuses the same gesture_recognizer.task model already in this repo — its
result includes raw hand landmarks alongside its 7-class gesture output, so
no separate hand-landmark model needs to be downloaded.

Method: each video becomes a fixed-length sequence of normalized hand
landmarks, and lookup is uniform-resampling + cosine-distance nearest
neighbor against a reference database built from labeled example videos.
This is a deliberately simple baseline, not the I3D video-CNN the ASL Citizen
paper trains — see README for why that's a reasonable tradeoff here (no GPU,
no multi-day training run) and what upgrading it later would involve.
"""

import os

import cv2
import mediapipe as mp
import numpy as np

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BASE_DIR, "gesture_recognizer.task")

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

SEQUENCE_LENGTH = 30  # frames every clip gets resampled to, regardless of original length
NUM_LANDMARKS = 21    # MediaPipe hand landmark count
FEATURE_DIM = NUM_LANDMARKS * 3  # x, y, z per landmark


def _make_recognizer(running_mode) -> "GestureRecognizer":
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=running_mode,
        num_hands=1,  # ASL Citizen's signs are predominantly single-hand;
                      # two-hand support is a documented possible upgrade.
    )
    return GestureRecognizer.create_from_options(options)


def _normalize_landmarks(landmarks) -> np.ndarray:
    """Centers on the wrist and scales by hand size, so the same sign looks
    the same regardless of where the hand is in frame or how close to the
    camera it is."""
    points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])  # (21, 3)
    wrist = points[0]
    centered = points - wrist
    scale = np.linalg.norm(centered[9])  # middle-finger MCP joint distance from wrist
    if scale < 1e-6:
        scale = 1.0
    return (centered / scale).flatten()  # (63,)


def _process_frames(frames_bgr, fps: float, recognizer) -> np.ndarray:
    """Shared core: runs the recognizer over a sequence of already-decoded
    BGR frames (from either a video file or a buffered live webcam feed) and
    returns the (T, 63) normalized landmark sequence, dropping frames with no
    detected hand."""
    frame_vectors = []
    for frame_idx, frame in enumerate(frames_bgr):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        timestamp_ms = int(frame_idx / fps * 1000)
        result = recognizer.recognize_for_video(mp_image, timestamp_ms)
        if result.hand_landmarks:
            frame_vectors.append(_normalize_landmarks(result.hand_landmarks[0]))
    return np.array(frame_vectors) if frame_vectors else np.zeros((0, FEATURE_DIM))


def extract_landmark_sequence_from_video(video_path: str) -> np.ndarray:
    """Runs every frame of a video file through the gesture recognizer's
    underlying hand-landmark detection. Frames with no detected hand are
    dropped, not zero-filled — this deliberately mirrors how ASL Citizen's
    own preprocessing removes video where nothing was detected."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    recognizer = _make_recognizer(VisionRunningMode.VIDEO)
    try:
        frames = []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(frame)
        return _process_frames(frames, fps, recognizer)
    finally:
        cap.release()


def extract_landmark_sequence_from_frames(frames_bgr, fps: float = 30.0) -> np.ndarray:
    """Same as extract_landmark_sequence_from_video, but for a list of BGR
    frames already buffered in memory — used by the live webcam page, which
    buffers frames from streamlit-webrtc rather than reading a video file."""
    recognizer = _make_recognizer(VisionRunningMode.VIDEO)
    return _process_frames(frames_bgr, fps, recognizer)


def resample_sequence(sequence: np.ndarray, length: int = SEQUENCE_LENGTH) -> np.ndarray:
    """Uniformly resamples a (T, 63) sequence to a fixed (length, 63) length
    by index interpolation, so clips of different durations/frame rates
    become directly comparable. Returns a zero array if the input is empty
    (no hand ever detected)."""
    if sequence.shape[0] == 0:
        return np.zeros((length, FEATURE_DIM))
    if sequence.shape[0] == 1:
        return np.repeat(sequence, length, axis=0)
    original_idx = np.linspace(0, sequence.shape[0] - 1, num=sequence.shape[0])
    target_idx = np.linspace(0, sequence.shape[0] - 1, num=length)
    resampled = np.empty((length, sequence.shape[1]))
    for dim in range(sequence.shape[1]):
        resampled[:, dim] = np.interp(target_idx, original_idx, sequence[:, dim])
    return resampled


def sequence_to_feature(sequence: np.ndarray) -> np.ndarray:
    """Full pipeline from a raw (T, 63) landmark sequence to one flat
    comparable feature vector."""
    return resample_sequence(sequence).flatten()


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom < 1e-9:
        return 1.0
    return 1.0 - float(np.dot(a, b) / denom)


def top_k_matches(query_feature: np.ndarray, reference: dict, k: int = 5):
    """reference: {label: [feature_vector, feature_vector, ...]} (a label can
    have multiple example clips). Returns a list of (label, distance) sorted
    ascending by distance, one best-match entry per label, truncated to k."""
    best_per_label = []
    for label, examples in reference.items():
        best = min(cosine_distance(query_feature, ex) for ex in examples)
        best_per_label.append((label, best))
    best_per_label.sort(key=lambda pair: pair[1])
    return best_per_label[:k]
