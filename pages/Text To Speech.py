import streamlit as st
import requests

st.title("Text to Speech")

text = st.text_area("Enter text:")
if st.button("Convert to Speech"):
    response = requests.post("http://127.0.0.1:8000/text-to-speech/", json={"text": text})
    st.audio("output.mp3")
