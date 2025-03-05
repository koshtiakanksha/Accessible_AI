import streamlit as st
import os

st.title("Text-to-Sign Language Converter")

# Folder containing sign language images
SIGN_IMAGE_FOLDER = "sign_language_images"

# Function to display sign images
def display_sign_images(text):
    available_images = {img.lower(): img for img in os.listdir(SIGN_IMAGE_FOLDER)}  # Normalize filenames

    # Try to find an exact match for a full phrase
    if f"{text.lower()}.png" in available_images:
        phrase_image_path = os.path.join(SIGN_IMAGE_FOLDER, available_images[f"{text.lower()}.png"])
        st.image(phrase_image_path, caption=text, use_container_width=False)
    else:
        # If the phrase is not found, check word-by-word
        words = text.lower().split()
        for word in words:
            word_image_path = os.path.join(SIGN_IMAGE_FOLDER, available_images.get(f"{word}.png", ""))
            if os.path.exists(word_image_path):
                st.image(word_image_path, caption=word.capitalize(), use_container_width=False)
            else:
                st.warning(f"No sign found for '{word}'.")

# User Input
user_text = st.text_input("Enter a phrase to convert into Sign Language:")

if st.button("Convert to Sign Language"):
    if user_text:
        display_sign_images(user_text.strip())  # Trim any extra spaces
    else:
        st.warning("Please enter some text.")
