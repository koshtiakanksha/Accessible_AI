import streamlit as st
import cv2
import av
import numpy as np
import mediapipe as mp
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# Load MediaPipe Gesture Recognizer
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Load the model
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path="gesture_recognizer.task"),
    running_mode=VisionRunningMode.VIDEO
)

# Define VideoProcessor Class
class GestureRecognitionProcessor(VideoProcessorBase):
    def __init__(self):
        self.recognizer = GestureRecognizer.create_from_options(options)

    def recv(self, frame: av.VideoFrame):
        image = frame.to_ndarray(format="bgr24")

        # Convert image to MediaPipe format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        # Run gesture recognition
        gesture_results = self.recognizer.recognize(mp_image)

        # Draw recognized gesture text
        if gesture_results.gestures:
            detected_gesture = gesture_results.gestures[0][0].category_name
            cv2.putText(image, f"Gesture: {detected_gesture}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")


# Streamlit UI
st.title("Sign Language Recognition Using MediaPipe Gesture Recognizer")
st.write("Show your hand gestures in front of the camera.")

# Start video stream
webrtc_streamer(key="gesture", video_processor_factory=GestureRecognitionProcessor)
