import streamlit as st
from PIL import Image

# Page configuration
st.set_page_config(page_title="Accessible AI", layout="wide")

# Load the uploaded image
image_path = "dev/Home.png"
image = Image.open(image_path)

# Display layout
st.image(image, use_container_width=True)