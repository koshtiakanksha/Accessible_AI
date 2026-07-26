import os
import tempfile
import uuid

from gtts import gTTS


def synthesize_to_file(text: str) -> str:
    """Synthesizes speech for `text` and returns a path to a uniquely-named
    mp3 file (avoids concurrent users overwriting a shared "output.mp3")."""
    tts = gTTS(text=text.strip())
    output_path = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")
    tts.save(output_path)
    return output_path
