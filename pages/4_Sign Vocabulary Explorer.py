import json
import os

import streamlit as st

from assets.theme import inject_theme

st.set_page_config(page_title="Sign Vocabulary Explorer — Accessible AI", page_icon="🤟", layout="wide")
inject_theme()

st.title("Sign Vocabulary Explorer")
st.caption(
    "This looks up a small set of stored sign images for known words and phrases. "
    "It is a vocabulary lookup, not a sign-language translator — ASL has its own grammar "
    "that isn't captured by displaying English words one at a time."
)

SIGN_IMAGE_FOLDER = "sign_language_images"
MANIFEST_PATH = os.path.join(SIGN_IMAGE_FOLDER, "manifest.json")


@st.cache_data
def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH) as f:
        entries = json.load(f)
    return {e["phrase"].lower(): e for e in entries if e.get("phrase") and e.get("image")}


manifest = load_manifest()

if not manifest:
    st.error(
        f"No vocabulary found — check that {MANIFEST_PATH} exists and lists at least one entry."
    )
    st.stop()


def show_lookup(text: str) -> None:
    key = text.lower().strip()
    if key in manifest:
        entry = manifest[key]
        st.image(os.path.join(SIGN_IMAGE_FOLDER, entry["image"]), caption=entry["phrase"], width=320)
        return

    # No match for the whole phrase — fall back to whichever individual
    # words we do have signs for, and say plainly which ones we don't.
    words = key.split()
    found_any = False
    missing = []
    cols = st.columns(min(len(words), 4) or 1)
    col_i = 0
    for word in words:
        if word in manifest:
            entry = manifest[word]
            with cols[col_i % len(cols)]:
                st.image(os.path.join(SIGN_IMAGE_FOLDER, entry["image"]), caption=entry["phrase"], width=200)
            col_i += 1
            found_any = True
        else:
            missing.append(word)

    if missing:
        st.warning(
            f"No sign found for: {', '.join(missing)}. "
            f"See the list below for everything currently covered."
        )
    if not found_any and not missing:
        st.warning("Please enter some text.")


left, right = st.columns([2, 1])

with left:
    user_text = st.text_input("Enter a word or phrase to look up:")
    if st.button("Show Sign(s)"):
        if user_text.strip():
            show_lookup(user_text)
        else:
            st.warning("Please enter some text.")

with right:
    st.markdown("**Everything currently covered**")
    st.caption("Browse instead of guessing — this is the full vocabulary right now.")
    for phrase in sorted(e["phrase"] for e in manifest.values()):
        st.write(f"- {phrase}")
    st.caption(
        "Want to add more? See `sign_language_images/README.md` for how — and why sign "
        "accuracy matters more than vocabulary size."
    )
