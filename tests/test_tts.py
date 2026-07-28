from unittest.mock import patch

from lib.tts import synthesize_to_file


def test_synthesize_to_file_generates_unique_paths_per_call():
    """Regression test for the original bug: the app used to always write to
    a single shared "output.mp3", so concurrent users would overwrite each
    other's audio. This confirms two calls never collide."""
    with patch("lib.tts.gTTS") as mock_gtts:
        mock_gtts.return_value.save = lambda path: open(path, "w").close()

        path1 = synthesize_to_file("hello")
        path2 = synthesize_to_file("hello")

        assert path1 != path2


def test_synthesize_to_file_passes_stripped_text_to_gtts():
    with patch("lib.tts.gTTS") as mock_gtts:
        mock_gtts.return_value.save = lambda path: open(path, "w").close()

        synthesize_to_file("  hello world  ")

        mock_gtts.assert_called_once_with(text="hello world")
