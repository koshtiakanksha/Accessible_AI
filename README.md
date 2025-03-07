# Accessible AI: Bridging Communication Gaps

![Accessible AI](dev/Home.png)  


## 📌 About the Project

**Accessible AI** is an inclusive communication tool that helps bridge gaps between speech, text, and sign language. It is designed for individuals with disabilities, enabling seamless interaction using AI-powered solutions.

## ✨ Features

- **Speech-to-Text**: Converts spoken language into text using AI-powered transcription.
- **Text-to-Speech**: Converts written text into speech for accessibility.
- **Text-to-Sign Language**: Displays sign language representations for given text.
- **Sign Language Recognition**: Uses a webcam to recognize and interpret hand gestures into text.

## 🚀 Live Demo

You can access the app here: [Accessible AI on Streamlit](https://accessibleai-rsmecrot2tjcargzxvf2td.streamlit.app/)
The features may not work due to the constraints of hosting it on Streamlit, but you can clone the repository to use all the features.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI (Replaced with direct API calls for Hugging Face compatibility)
- **AI Models**:
  - Speech-to-Text: `SpeechRecognition`, `Whisper ASR`
  - Text-to-Speech: `gTTS`
  - Sign Language Recognition: `MediaPipe`, `OpenCV`
- **Deployment**: Streamlit

## 📥 Installation

### Prerequisites
Ensure you have **Python 3.8+** installed.

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/koshtiakanksha/Accessible_AI.git
   cd Accessible_AI
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Streamlit app:**
   ```bash
   streamlit run Home.py
   ```

## 📌 Usage

1. **Speech-to-Text**
   - Click **Start Recording** and speak.
   - The app will transcribe your speech into text.

2. **Text-to-Speech**
   - Enter text and click **Convert to Speech**.
   - The app will generate and play the speech.

3. **Text-to-Sign Language**
   - Type text and the corresponding sign language images will be displayed.

4. **Sign Language Recognition**
   - Click **Start Recognition** and show a hand gesture.
   - The app will identify and display the recognized gesture.

## 🚀 Deployment

### Hugging Face Spaces

To deploy on Hugging Face:

1. Create a **Hugging Face Space** (use Streamlit template).
2. Push your files to the repository:
   ```bash
   git add .
   git commit -m "Deploy Accessible AI"
   git push
   ```
3. Your app will be deployed automatically.

## 🐛 Troubleshooting

- **Camera not opening?** Use `streamlit-webrtc` instead of OpenCV.
- **PyAudio error?** Replace with `speech_recognition` or `whisper ASR`.
- **Connection refused for text-to-speech?** Remove FastAPI calls and use `gTTS`.

## 🤝 Contributing

Contributions are welcome! Follow these steps:
1. Fork the repository.
2. Create a new branch.
3. Commit changes and push to GitHub.
4. Open a Pull Request.

## 📜 License

This project is licensed under the **MIT License**.

---

🌟 **Let's make AI more accessible for everyone!** 🌟

