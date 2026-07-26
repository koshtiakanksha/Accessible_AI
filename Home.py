import streamlit as st

from assets.theme import feature_card, inject_theme, render_hero

st.set_page_config(page_title="Accessible AI", page_icon="🗣️", layout="wide")
inject_theme()

render_hero(
    eyebrow="Accessible AI",
    headline="However you communicate, this app meets you there.",
    subhead=(
        "A voice becomes a caption. A caption becomes a reply. A raised hand becomes a "
        "shortcut. One conversation, several ways in."
    ),
)

st.write("")
st.markdown("### What's built today")
st.write(
    "Each piece below is real and working — not a mockup. Colors match how they show up "
    "together in **Conversation mode**, the merged view."
)

cols = st.columns(4)
with cols[0]:
    st.markdown(
        feature_card(
            "Voice", "tag-voice", "Speech to Text",
            "Record your browser mic, then transcribe it on demand.",
            "Record-then-transcribe, not live streaming captions.",
        ),
        unsafe_allow_html=True,
    )
with cols[1]:
    st.markdown(
        feature_card(
            "Caption", "tag-caption", "Text to Speech",
            "Type a reply and have it read aloud.",
            "Needs an internet connection (gTTS).",
        ),
        unsafe_allow_html=True,
    )
with cols[2]:
    st.markdown(
        feature_card(
            "Caption", "tag-caption", "Sign Vocabulary Explorer",
            "Look up a small set of stored signs for known words.",
            "A word lookup, not sign-language translation.",
        ),
        unsafe_allow_html=True,
    )
with cols[3]:
    st.markdown(
        feature_card(
            "Signal", "tag-signal", "Gesture Shortcuts",
            "Show a hand gesture to your camera to trigger a phrase.",
            "Generic gesture recognition, not sign-language recognition.",
        ),
        unsafe_allow_html=True,
    )

st.write("")
st.markdown("### Try it")
st.write("**Conversation mode**, in the sidebar, is where voice, captions, and gesture shortcuts come together in one screen.")

st.write("")
status_cols = st.columns(2)
with status_cols[0]:
    st.markdown(
        """
        <div class="status-col">
          <h4>Works today</h4>
          <ul>
            <li>Browser mic → transcription</li>
            <li>Type → spoken reply</li>
            <li>Gesture → shortcut phrase</li>
            <li>All three together in Conversation mode</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
with status_cols[1]:
    st.markdown(
        """
        <div class="status-col">
          <h4>Coming next</h4>
          <ul>
            <li>Measured gesture-recognition accuracy (precision/recall/F1)</li>
            <li>Transcription accuracy spot-check</li>
            <li>Automated tests + CI</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.caption("[View source on GitHub](https://github.com/koshtiakanksha/Accessible_AI) · MIT License")
