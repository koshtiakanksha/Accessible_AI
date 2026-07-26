import streamlit as st

from assets.theme import inject_theme
from lib.tts import synthesize_to_file

st.set_page_config(page_title="Text to Speech — Accessible AI", page_icon="🔊", layout="wide")
inject_theme()

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
            output_path = synthesize_to_file(text)
            st.audio(output_path)
        except Exception as e:
            st.error(f"Couldn't generate speech: {e}")
