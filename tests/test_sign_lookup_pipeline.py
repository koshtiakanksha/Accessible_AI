import cv2
import numpy as np

from lib.sign_lookup import (
    FEATURE_DIM,
    extract_landmark_sequence_from_frames,
    extract_landmark_sequence_from_video,
    sequence_to_feature,
)


def _make_synthetic_no_hand_video(path: str, num_frames: int = 15) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (320, 240))
    for _ in range(num_frames):
        frame = np.full((240, 320, 3), (30, 40, 50), dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_extract_from_video_with_no_hand_returns_empty_but_does_not_crash(tmp_path):
    video_path = tmp_path / "no_hand.mp4"
    _make_synthetic_no_hand_video(str(video_path))

    sequence = extract_landmark_sequence_from_video(str(video_path))

    assert sequence.shape == (0, FEATURE_DIM)


def test_extract_from_video_and_from_frames_agree(tmp_path):
    """The live-webcam-buffer path and the video-file path share the same
    underlying frame processing — this pins that down so a future refactor
    can't silently make them diverge."""
    video_path = tmp_path / "no_hand.mp4"
    _make_synthetic_no_hand_video(str(video_path))

    from_video = extract_landmark_sequence_from_video(str(video_path))

    cap = cv2.VideoCapture(str(video_path))
    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    from_frames = extract_landmark_sequence_from_frames(frames, fps=10)

    assert from_video.shape == from_frames.shape


def test_empty_sequence_still_produces_full_length_feature_vector(tmp_path):
    video_path = tmp_path / "no_hand.mp4"
    _make_synthetic_no_hand_video(str(video_path))
    sequence = extract_landmark_sequence_from_video(str(video_path))

    feature = sequence_to_feature(sequence)

    assert feature.shape == (30 * FEATURE_DIM,)
    assert np.all(feature == 0)
