import cv2
import streamlit as st
import os
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time  # For handling timestamps

# Get the current directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Correct the model path (use "gesture_recognizer.task")
MODEL_PATH = os.path.join(BASE_DIR, "..", "gesture_recognizer.task")

# Ensure the model file exists before proceeding
if not os.path.exists(MODEL_PATH):
    st.error(f"Model file not found: {MODEL_PATH}")
    st.stop()

# Initialize MediaPipe Gesture Recognizer
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
mp_image = mp.Image  # Use MediaPipe's Image class

# Define correct gesture labels
GESTURE_LABELS = {
    "Thumb_Up": "👍 (Yes)",
    "Thumb_Down": "👎 (No)",
    "Victory": "✌️ (Peace)",
    "Pointing_Up": "☝️ (Up)",
    "Fist": "✊ (Sorry)",
    "Open_Palm": "👋 (Hello)",
    "ILoveYou": "🤟 (I Love You)"
}

# Create a gesture recognizer instance with the corrected model path in VIDEO mode
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO)  # Must be VIDEO mode for continuous recognition

# Streamlit UI
st.title("Gesture Shortcuts")
st.write("Show one of the supported hand gestures to the camera to trigger its shortcut phrase.")
st.caption(
    "This recognizes a fixed set of generic hand gestures (thumbs up, peace sign, etc.) using "
    "MediaPipe's built-in gesture recognizer — it is not sign-language recognition. Each gesture "
    "below is mapped to a shortcut phrase, not a linguistic sign."
)
st.write(", ".join(f"{k.replace('_', ' ')} → {v}" for k, v in GESTURE_LABELS.items()))

# Button to start/stop recognition
start_button = st.button("Start Recognition")
stop_button = st.button("Stop Recognition")

if start_button:
    stframe = st.empty()  # Create a placeholder for the camera feed

    cap = cv2.VideoCapture(0)
    with GestureRecognizer.create_from_options(options) as recognizer:
        start_time_ms = int(time.time() * 1000)  # Reference point for elapsed time

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert image to RGB
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert OpenCV image (NumPy array) to MediaPipe Image
            mp_image_obj = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

            # MediaPipe expects a monotonically increasing timestamp in ms since
            # the stream started, not the full Unix epoch added on every frame
            # (the old code did `timestamp += int(time.time() * 1000)`, which
            # grows by ~1.7 trillion ms per frame instead of the real elapsed time).
            timestamp = int(time.time() * 1000) - start_time_ms

            # Recognize gestures using `recognize_for_video()`
            gesture_results = recognizer.recognize_for_video(mp_image_obj, timestamp)

            # If a gesture is detected, display it
            if gesture_results.gestures:
                gesture_name = gesture_results.gestures[0][0].category_name  # Get first recognized gesture

                # Get the corresponding emoji label
                label = GESTURE_LABELS.get(gesture_name, "Unknown Gesture")

                cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

            # Show webcam feed in Streamlit
            stframe.image(frame, channels="BGR", use_container_width=True)

            # Stop Recognition
            if stop_button:
                break

    cap.release()
