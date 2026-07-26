import streamlit as st
from gtts import gTTS
import os
import tempfile
import uuid

st.title("Text to Speech")
st.caption(
    "Enter text and it will be converted to speech using gTTS (Google Text-to-Speech). "
    "Requires an internet connection since gTTS calls Google's service."
)

text = st.text_area("Enter text:")

if st.button("Convert to Speech"):
    if not text.strip():
        st.warning("Please enter some text first.")
    else:
        try:
            tts = gTTS(text=text.strip())
            # Unique filename per request so concurrent users never overwrite
            # each other's audio (the old code always wrote to "output.mp3").
            output_path = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")
            tts.save(output_path)
            st.audio(output_path)
        except Exception as e:
            st.error(f"Couldn't generate speech: {e}")
