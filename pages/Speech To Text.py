import streamlit as st
import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Streamlit UI
st.title("Speech-to-Text Converter")
st.write("Click the button below and start speaking. The app will convert your speech into text.")

# Function to recognize speech from microphone
def recognize_speech():
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
        try:
            audio = recognizer.listen(source, timeout=30)  # Listen for 5 seconds
            text = recognizer.recognize_google(audio)  # Convert speech to text
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError:
            return "Error: Could not request results from speech recognition service."

# Button to start speech recognition
if st.button("Start Recording"):
    result = recognize_speech()
    st.subheader("Transcribed Text:")
    st.write(result)
