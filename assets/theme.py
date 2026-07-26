"""
Shared visual identity for Accessible AI.

Design concept: three real communication modalities — voice, written
captions, and gesture shortcuts — meeting in one conversation. Each modality
gets its own accent color, used consistently everywhere it appears (cards,
chat bubbles, tags), so the color itself carries information rather than
just decorating the page.

Body/UI text uses Atkinson Hyperlegible — a typeface designed by the Braille
Institute specifically for maximum legibility for low-vision readers. That's
not a random choice: it's the one piece of this design that's directly
grounded in what the app is actually for.
"""

import streamlit as st

INK = "#16222B"        # primary text, hero background
INK_SOFT = "#55636B"   # secondary/muted text
MIST = "#EDF1F0"       # page background (cool, not the default warm cream)
PAPER = "#FFFFFF"      # card background
VOICE = "#D9992E"      # accent: speech / voice input
CAPTION = "#1D6C74"    # accent: written text / captions
SIGNAL = "#5B4B8A"     # accent: gesture shortcuts

_FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?"
    "family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&"
    "family=Atkinson+Hyperlegible:wght@400;700&display=swap"
)


def inject_theme() -> None:
    """Injects global fonts, colors, and component CSS. Call once near the
    top of every page so the whole app reads as one product, not four
    separate demos."""
    st.markdown(
        f"""
        <style>
        @import url('{_FONT_IMPORT}');

        html, body, [class*="css"] {{
            font-family: 'Atkinson Hyperlegible', sans-serif;
        }}

        .stApp {{
            background: {MIST};
        }}

        h1, h2, h3, .display-font {{
            font-family: 'Fraunces', serif;
            color: {INK};
            font-weight: 600;
        }}

        p, li, label, .stMarkdown {{
            color: {INK};
        }}

        .stButton > button {{
            font-family: 'Atkinson Hyperlegible', sans-serif;
            border-radius: 8px;
            border: 1.5px solid {INK};
            color: {INK};
            font-weight: 700;
        }}
        .stButton > button:hover {{
            border-color: {CAPTION};
            color: {CAPTION};
        }}

        /* ---- Hero ---- */
        .hero {{
            background: {INK};
            margin: -5rem -4rem 2.5rem -4rem;
            padding: 3rem 4rem 2.5rem 4rem;
            border-radius: 0 0 20px 20px;
        }}
        .hero .eyebrow {{
            font-family: 'Atkinson Hyperlegible', sans-serif;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            font-size: 0.75rem;
            font-weight: 700;
            color: {VOICE};
            margin-bottom: 0.5rem;
        }}
        .hero h1 {{
            color: {PAPER};
            font-size: 2.6rem;
            line-height: 1.15;
            margin: 0 0 0.75rem 0;
        }}
        .hero p {{
            color: #C9D2D6;
            font-size: 1.05rem;
            max-width: 46ch;
            margin: 0 0 1.5rem 0;
        }}

        /* ---- Modality tags ---- */
        .tag {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            margin-bottom: 0.6rem;
        }}
        .tag-voice {{ background: {VOICE}22; color: {VOICE}; }}
        .tag-caption {{ background: {CAPTION}22; color: {CAPTION}; }}
        .tag-signal {{ background: {SIGNAL}22; color: {SIGNAL}; }}

        /* ---- Feature cards ---- */
        .feature-card {{
            background: {PAPER};
            border-radius: 14px;
            padding: 1.25rem 1.4rem;
            height: 100%;
            border: 1px solid #DDE3E1;
        }}
        .feature-card h3 {{
            font-size: 1.15rem;
            margin: 0 0 0.4rem 0;
        }}
        .feature-card p {{
            font-size: 0.92rem;
            color: {INK_SOFT};
            margin: 0;
        }}
        .feature-card .caveat {{
            font-size: 0.8rem;
            color: {INK_SOFT};
            font-style: italic;
            margin-top: 0.5rem;
        }}

        /* ---- Chat bubbles (conversation view) ---- */
        .bubble {{
            border-radius: 12px;
            padding: 0.6rem 0.9rem;
            margin-bottom: 0.6rem;
            max-width: 90%;
            font-size: 0.95rem;
        }}
        .bubble .who {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            display: block;
            margin-bottom: 0.15rem;
        }}
        .bubble-voice {{ background: {VOICE}18; border-left: 3px solid {VOICE}; }}
        .bubble-voice .who {{ color: {VOICE}; }}
        .bubble-signal {{ background: {SIGNAL}18; border-left: 3px solid {SIGNAL}; margin-left: auto; }}
        .bubble-signal .who {{ color: {SIGNAL}; }}
        .bubble-caption {{ background: {CAPTION}18; border-left: 3px solid {CAPTION}; margin-left: auto; }}
        .bubble-caption .who {{ color: {CAPTION}; }}

        /* ---- Today / next panel ---- */
        .status-col {{
            background: {PAPER};
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            border: 1px solid #DDE3E1;
        }}
        .status-col h4 {{
            font-family: 'Fraunces', serif;
            margin: 0 0 0.6rem 0;
            color: {INK};
        }}
        .status-col ul {{
            margin: 0;
            padding-left: 1.1rem;
            color: {INK_SOFT};
            font-size: 0.92rem;
        }}

        @media (prefers-reduced-motion: reduce) {{
            .bar, .pulse-dot, .wave-hand {{ animation: none !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(eyebrow: str, headline: str, subhead: str) -> None:
    """Renders the dark hero band with the animated voice → caption →
    gesture signature graphic."""
    st.markdown(
        f"""
        <div class="hero">
          <div class="eyebrow">{eyebrow}</div>
          <h1>{headline}</h1>
          <p>{subhead}</p>
          {_signature_svg()}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _signature_svg() -> str:
    """A voice waveform flows into a caption bubble, which flows into a
    raised-hand shortcut — the three modalities this app actually bridges,
    in the order a conversation moves through them."""
    bars = "".join(
        f'<rect class="bar" x="{60 + i * 16}" y="70" width="8" height="40" rx="4" '
        f'fill="{VOICE}" style="animation:bar-bounce 1.1s ease-in-out {i * 0.13}s infinite alternate;"/>'
        for i in range(6)
    )
    return f"""
    <svg viewBox="0 0 880 170" width="100%" height="150" xmlns="http://www.w3.org/2000/svg"
         role="img" aria-label="A voice waveform flows into a caption bubble, then into a raised hand shortcut icon">
      <style>
        @keyframes bar-bounce {{
          from {{ transform: scaleY(0.5); }}
          to   {{ transform: scaleY(1.15); }}
        }}
        .bar {{ transform-box: fill-box; transform-origin: bottom; }}
        @keyframes fade-pulse {{
          0%, 100% {{ opacity: 0.55; }}
          50% {{ opacity: 1; }}
        }}
        .caption-bubble {{ animation: fade-pulse 2.4s ease-in-out infinite; }}
        @keyframes wave {{
          0%, 100% {{ transform: rotate(-6deg); }}
          50% {{ transform: rotate(6deg); }}
        }}
        .wave-hand {{ transform-box: fill-box; transform-origin: bottom center; animation: wave 1.8s ease-in-out infinite; }}
      </style>

      <!-- station 1: voice waveform -->
      {bars}

      <!-- connector 1 -->
      <path id="p1" d="M 190 90 C 280 40, 320 40, 400 85" fill="none" stroke="{VOICE}"
            stroke-width="2" stroke-dasharray="4 7" opacity="0.6"/>
      <circle r="5" fill="{CAPTION}">
        <animateMotion dur="2.6s" repeatCount="indefinite" path="M 190 90 C 280 40, 320 40, 400 85"/>
      </circle>

      <!-- station 2: caption bubble -->
      <g class="caption-bubble">
        <rect x="410" y="55" width="150" height="70" rx="16" fill="{CAPTION}" opacity="0.18"/>
        <path d="M 430 125 L 430 140 L 448 125 Z" fill="{CAPTION}" opacity="0.18"/>
        <rect x="428" y="75" width="110" height="8" rx="4" fill="{CAPTION}"/>
        <rect x="428" y="92" width="80" height="8" rx="4" fill="{CAPTION}"/>
      </g>

      <!-- connector 2 -->
      <path d="M 570 90 C 630 45, 660 45, 710 85" fill="none" stroke="{CAPTION}"
            stroke-width="2" stroke-dasharray="4 7" opacity="0.6"/>
      <circle r="5" fill="{SIGNAL}">
        <animateMotion dur="2.6s" repeatCount="indefinite" path="M 570 90 C 630 45, 660 45, 710 85"/>
      </circle>

      <!-- station 3: raised hand (gesture shortcut) -->
      <g class="wave-hand">
        <rect x="735" y="95" width="50" height="45" rx="14" fill="{SIGNAL}"/>
        <rect x="740" y="55" width="10" height="45" rx="5" fill="{SIGNAL}"/>
        <rect x="754" y="45" width="10" height="55" rx="5" fill="{SIGNAL}"/>
        <rect x="768" y="48" width="10" height="52" rx="5" fill="{SIGNAL}"/>
        <rect x="782" y="58" width="10" height="42" rx="5" fill="{SIGNAL}"/>
      </g>
    </svg>
    """


def feature_card(tag: str, tag_class: str, title: str, description: str, caveat: str = "") -> str:
    caveat_html = f'<p class="caveat">{caveat}</p>' if caveat else ""
    return f"""
    <div class="feature-card">
      <span class="tag {tag_class}">{tag}</span>
      <h3>{title}</h3>
      <p>{description}</p>
      {caveat_html}
    </div>
    """
