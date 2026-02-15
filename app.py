import streamlit as st
import sqlite3
import uuid
import os
from datetime import datetime
from openai import OpenAI


st.set_page_config(
    page_title="💌 Digital Love Letter Generator",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="collapsed",
)


try:
    
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY") or st.session_state.get("openai_key", "")
    if api_key:
        return OpenAI(api_key=api_key)
    return None



DB_PATH = "love_letters.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS letters (
            id TEXT PRIMARY KEY,
            points TEXT,
            style TEXT,
            theme TEXT,
            intensity INTEGER,
            text TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_letter(points, style, theme, intensity, text):
    letter_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO letters VALUES (?,?,?,?,?,?,?)",
        (letter_id, points, style, theme, intensity, text, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    return letter_id


def load_letter(letter_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT * FROM letters WHERE id=?", (letter_id,)).fetchone()
    conn.close()
    if row:
        return {"id": row[0], "points": row[1], "style": row[2],
                "theme": row[3], "intensity": row[4], "text": row[5], "created_at": row[6]}
    return None



STYLE_DESCRIPTIONS = {
    "Romantic": "deeply romantic, heartfelt, with tender imagery and soft vulnerability",
    "Cute": "adorable, playful, warm and sweet like a morning hug",
    "Long-distance": "yearning, hopeful, bridging the ache of miles with love",
    "Anniversary": "celebratory, nostalgic, honoring the journey of togetherness",
    "Apology": "sincere, remorseful yet hopeful, earnest and healing",
    "Shakespearean": "elevated Elizabethan language, iambic-inflected prose, timeless and grand",
    "Bollywood poetic": "dramatic, passionate, lyrical with metaphors of stars, rain, and eternal longing",
}


def generate_letter(points: str, style: str, intensity: int, client) -> str:
    tone_desc = STYLE_DESCRIPTIONS.get(style, "romantic")
    intensity_desc = (
        "gentle and subtle" if intensity < 30
        else "warmly expressive" if intensity < 60
        else "deeply passionate and intense" if intensity < 85
        else "overwhelmingly ardent, pouring with emotion"
    )

    prompt = f"""Convert the following feelings into a heartfelt love letter.

Style: {style} — {tone_desc}
Emotional Intensity: {intensity}/100 — The tone should be {intensity_desc}
Desired Length: 140–170 words
Tone: sincere, poetic, natural — avoid clichés, use fresh imagery

Feelings (bullet points from the sender):
{points}

Rules:
- Preserve every feeling mentioned above — do not invent new ones
- Write as a first-person letter addressed to "you" (no placeholders like [Name])
- Begin with a tender opening line, not "Dear" alone
- End with a closing sentiment that feels earned, not generic
- Use sensory imagery: light, seasons, warmth, sound, texture
- The letter should feel like it was written by a real human in love
- Output ONLY the letter text, nothing else"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.88,
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()



THEMES = {
    "Vintage parchment": {
        "bg": "#f5e6c8",
        "card_bg": "#fdf3dc",
        "text": "#3d2b1f",
        "accent": "#8b4513",
        "border": "#c8a96e",
        "shadow": "rgba(139,69,19,0.25)",
        "font_body": "'Playfair Display', Georgia, serif",
        "font_display": "'Great Vibes', cursive",
        "gradient": "linear-gradient(135deg, #fdf3dc 0%, #f5e6c8 100%)",
        "texture": "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c8a96e' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        "envelope_color": "#d4a96a",
        "seal_color": "#8b4513",
    },
    "Floral wedding": {
        "bg": "#fdf0f5",
        "card_bg": "#ffffff",
        "text": "#4a2040",
        "accent": "#c0598a",
        "border": "#f0b8d4",
        "shadow": "rgba(192,89,138,0.2)",
        "font_body": "'Dancing Script', cursive",
        "font_display": "'Great Vibes', cursive",
        "gradient": "linear-gradient(135deg, #ffffff 0%, #fdf0f5 50%, #fff5f9 100%)",
        "texture": "",
        "envelope_color": "#f0b8d4",
        "seal_color": "#c0598a",
    },
    "Minimal dark": {
        "bg": "#0f0f0f",
        "card_bg": "#1a1a1a",
        "text": "#e8e0d8",
        "accent": "#c8a96e",
        "border": "#333333",
        "shadow": "rgba(200,169,110,0.15)",
        "font_body": "'Montserrat', sans-serif",
        "font_display": "'Cinzel', serif",
        "gradient": "linear-gradient(135deg, #1a1a1a 0%, #111111 100%)",
        "texture": "",
        "envelope_color": "#2a2a2a",
        "seal_color": "#c8a96e",
    },
    "Neon love": {
        "bg": "#0d001a",
        "card_bg": "#130028",
        "text": "#f0e0ff",
        "accent": "#ff2d9e",
        "border": "#9b00ff",
        "shadow": "rgba(255,45,158,0.35)",
        "font_body": "'Montserrat', sans-serif",
        "font_display": "'Cinzel', serif",
        "gradient": "linear-gradient(135deg, #130028 0%, #0d001a 100%)",
        "texture": "",
        "envelope_color": "#1e003d",
        "seal_color": "#ff2d9e",
    },
    "Handwritten diary": {
        "bg": "#f4f0e8",
        "card_bg": "#fafaf5",
        "text": "#2c2416",
        "accent": "#7a5c3a",
        "border": "#d4c8a8",
        "shadow": "rgba(122,92,58,0.2)",
        "font_body": "'Dancing Script', cursive",
        "font_display": "'Dancing Script', cursive",
        "gradient": "linear-gradient(135deg, #fafaf5 0%, #f4f0e8 100%)",
        "texture": "repeating-linear-gradient(transparent, transparent 27px, #d4c8a8 27px, #d4c8a8 28px)",
        "envelope_color": "#d4c8a8",
        "seal_color": "#7a5c3a",
    },
}



def inject_global_css():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Dancing+Script:wght@400;600&family=Great+Vibes&family=Cinzel:wght@400;600&family=Montserrat:wght@300;400;500&display=swap" rel="stylesheet">

    <style>
    /* Reset & base */
    html, body, [data-testid="stAppViewContainer"] {
        background: #0a0008 !important;
    }
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(ellipse at 20% 20%, #1a0010 0%, #0a0008 50%, #000510 100%) !important;
        min-height: 100vh;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="block-container"] { max-width: 760px; padding-top: 2rem; }

    /* Hide Streamlit chrome */
    #MainMenu, footer { display: none !important; }

    /* Main title */
    .love-title {
        font-family: 'Great Vibes', cursive;
        font-size: 3.8rem;
        color: #ff9ec4;
        text-align: center;
        text-shadow: 0 0 40px rgba(255,100,160,0.5), 0 0 80px rgba(255,100,160,0.2);
        margin-bottom: 0.2rem;
        line-height: 1.1;
    }
    .love-subtitle {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: rgba(255,200,220,0.5);
        text-align: center;
        margin-bottom: 2.5rem;
    }

    /* Step cards */
    .step-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(10px);
    }
    .step-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.65rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: rgba(255,160,200,0.6);
        margin-bottom: 0.6rem;
    }

    /* Inputs */
    [data-testid="stTextArea"] textarea,
    [data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: #ffe0ee !important;
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.05rem !important;
        padding: 0.8rem 1rem !important;
        transition: border-color 0.3s;
    }
    [data-testid="stTextArea"] textarea:focus,
    [data-testid="stTextInput"] input:focus {
        border-color: rgba(255,100,160,0.5) !important;
        box-shadow: 0 0 0 2px rgba(255,100,160,0.1) !important;
    }
    [data-testid="stTextArea"] textarea::placeholder,
    [data-testid="stTextInput"] input::placeholder { color: rgba(255,200,220,0.3) !important; }

    /* Labels */
    [data-testid="stTextArea"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.2em !important;
        text-transform: uppercase !important;
        color: rgba(255,180,210,0.7) !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: #ffe0ee !important;
    }

    /* Slider */
    [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background: #ff6aac !important;
        border: 2px solid #ff9ec4 !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] div[class*="Track"] {
        background: rgba(255,106,172,0.3) !important;
    }

    /* Buttons */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #ff2d9e 0%, #9b1de8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
        padding: 0.7rem 2.2rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 20px rgba(255,45,158,0.35) !important;
    }
    [data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(255,45,158,0.5) !important;
    }

    /* Info/success boxes */
    [data-testid="stInfo"], [data-testid="stSuccess"], [data-testid="stWarning"] {
        background: rgba(255,45,158,0.08) !important;
        border: 1px solid rgba(255,45,158,0.2) !important;
        border-radius: 10px !important;
        color: #ffb8d4 !important;
    }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,100,160,0.3); border-radius: 2px; }

    /* Radio / pill selectors */
    [data-testid="stRadio"] label {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.78rem !important;
        color: rgba(255,180,210,0.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)



def render_letter_card(letter_text: str, theme_name: str, auto_open: bool = False) -> str:
    t = THEMES[theme_name]
    escaped = letter_text.replace("`", "\\`").replace("$", "\\$").replace("\\", "\\\\").replace("\n", "\\n")

    neon_glow = ""
    if theme_name == "Neon love":
        neon_glow = f"""
            box-shadow: 0 0 0 1px {t['border']}, 0 0 20px {t['shadow']}, 0 0 60px rgba(155,0,255,0.15);
            text-shadow: 0 0 8px rgba(255,45,158,0.4);
        """

    floral_deco = ""
    if theme_name == "Floral wedding":
        floral_deco = """
        <div style="position:absolute;top:-10px;left:50%;transform:translateX(-50%);font-size:1.6rem;opacity:0.7;">
            🌸 🌺 🌸
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Dancing+Script:wght@400;600&family=Great+Vibes&family=Cinzel:wght@400;600&family=Montserrat:wght@300;400;500&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    background: {t['bg']};
    min-height: 100vh;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 20px;
    {'background-image:' + t['texture'] + ';' if t.get('texture') else ''}
}}

/* ── Envelope ── */
.scene {{
    width: 100%;
    max-width: 560px;
    position: relative;
}}

.envelope-wrap {{
    perspective: 1000px;
    width: 100%;
    cursor: pointer;
    user-select: none;
}}

.envelope {{
    width: 100%;
    position: relative;
    transition: transform 0.3s;
}}
.envelope:hover {{ transform: scale(1.01); }}

.env-body {{
    background: {t['envelope_color']};
    border-radius: 4px 4px 8px 8px;
    padding: 60px 30px 40px;
    position: relative;
    min-height: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 40px {t['shadow']};
    overflow: hidden;
}}
.env-body::before {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 50%;
    background: rgba(0,0,0,0.05);
    clip-path: polygon(0 100%, 50% 0%, 100% 100%);
}}
.env-body::after {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 50%;
    background: rgba(255,255,255,0.06);
    clip-path: polygon(0 0, 50% 100%, 100% 0);
}}

.env-flap {{
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 110px;
    background: {t['envelope_color']};
    filter: brightness(0.92);
    clip-path: polygon(0 0, 50% 100%, 100% 0);
    transform-origin: top center;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 10;
}}
.env-flap.open {{
    transform: rotateX(180deg);
}}

.env-seal {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 54px; height: 54px;
    background: {t['seal_color']};
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    z-index: 5;
    transition: opacity 0.3s, transform 0.3s;
}}
.env-seal.hidden {{ opacity:0; transform: translate(-50%,-50%) scale(0.5); }}

.env-cta {{
    position: absolute;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    font-family: {t['font_body']};
    font-size: 0.78rem;
    color: {t['text']};
    opacity: 0.55;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    white-space: nowrap;
    transition: opacity 0.3s;
    z-index: 5;
}}

/* ── Letter card ── */
.letter-wrap {{
    display: none;
    margin-top: -10px;
    position: relative;
    z-index: 1;
    transform: translateY(-20px);
    opacity: 0;
    transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.5s ease;
}}
.letter-wrap.visible {{
    display: block;
}}
.letter-wrap.animated {{
    transform: translateY(0);
    opacity: 1;
}}

.letter-card {{
    background: {t['gradient']};
    border: 1px solid {t['border']};
    border-radius: 4px 4px 12px 12px;
    padding: 42px 44px 48px;
    position: relative;
    {neon_glow if neon_glow else f"box-shadow: 0 12px 50px {t['shadow']};"}
    overflow: hidden;
}}
.letter-card::before {{
    content: '';
    position: absolute;
    inset: 0;
    {'background-image:' + t['texture'] + '; opacity: 0.6;' if t.get('texture') else ''}
    pointer-events: none;
}}

.letter-heading {{
    font-family: {t['font_display']};
    font-size: 2.2rem;
    color: {t['accent']};
    text-align: center;
    margin-bottom: 24px;
    line-height: 1.2;
    opacity: 0;
    transform: translateY(10px);
    transition: opacity 0.5s ease 0.2s, transform 0.5s ease 0.2s;
}}
.letter-heading.shown {{ opacity: 1; transform: translateY(0); }}

.letter-line {{
    font-family: {t['font_body']};
    font-size: 1.05rem;
    color: {t['text']};
    line-height: 1.85;
    opacity: 0;
    transform: translateY(6px);
    transition: opacity 0.4s ease, transform 0.4s ease;
    margin-bottom: 2px;
}}
.letter-line.shown {{ opacity: 1; transform: translateY(0); }}

.letter-footer {{
    text-align: right;
    margin-top: 24px;
    font-family: {t['font_display']};
    font-size: 1.4rem;
    color: {t['accent']};
    opacity: 0;
    transition: opacity 0.5s ease;
}}
.letter-footer.shown {{ opacity: 1; }}

/* ── Action bar ── */
.action-bar {{
    display: flex;
    gap: 10px;
    margin-top: 16px;
    flex-wrap: wrap;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.5s ease 0.5s;
}}
.action-bar.shown {{ opacity: 1; }}

.btn {{
    font-family: {t['font_body']};
    font-size: 0.78rem;
    padding: 8px 18px;
    border-radius: 50px;
    border: 1px solid {t['border']};
    background: transparent;
    color: {t['accent']};
    cursor: pointer;
    transition: all 0.25s;
    letter-spacing: 0.05em;
}}
.btn:hover {{
    background: {t['accent']};
    color: {t['card_bg']};
    transform: translateY(-1px);
}}
.btn-primary {{
    background: {t['accent']};
    color: {t['card_bg']};
}}
.btn-primary:hover {{ filter: brightness(1.1); }}

/* ── Canvas confetti ── */
#confetti-canvas {{
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 9999;
}}

{floral_deco}
</style>
</head>
<body>

<canvas id="confetti-canvas"></canvas>

<div class="scene">

  <!-- ENVELOPE -->
  <div class="envelope-wrap" id="envelopeWrap" onclick="openEnvelope()">
    <div class="envelope">
      <div class="env-body">
        <div class="env-flap" id="envFlap"></div>
        <div class="env-seal" id="envSeal">💌</div>
        <div class="env-cta" id="envCta">Click to open your letter</div>
      </div>
    </div>
  </div>

  <!-- LETTER -->
  <div class="letter-wrap" id="letterWrap">
    <div class="letter-card">
      {floral_deco}
      <div class="letter-heading" id="letterHeading">A Letter For You</div>
      <div id="letterLines"></div>
      <div class="letter-footer" id="letterFooter">With all my love ♥</div>
    </div>
    <div class="action-bar" id="actionBar">
      <button class="btn" onclick="readLetter()">🔊 Read Letter</button>
      <button class="btn" onclick="downloadCard()">⬇ Save as PNG</button>
      <button class="btn" onclick="toggleMusic()">🎵 Music</button>
    </div>
  </div>

</div>

<!-- Background music -->
<audio id="bgMusic" loop preload="none">
  <source src="https://www.soundjay.com/misc/sounds/bell-ringing-01.mp3" type="audio/mpeg">
</audio>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
const LETTER_TEXT = `{escaped}`;
let opened = false;
let musicOn = false;

function openEnvelope() {{
  if (opened) return;
  opened = true;

  // Flip flap
  document.getElementById('envFlap').classList.add('open');
  document.getElementById('envSeal').classList.add('hidden');
  document.getElementById('envCta').style.opacity = '0';

  // Show letter wrapper
  setTimeout(() => {{
    const lw = document.getElementById('letterWrap');
    lw.style.display = 'block';
    requestAnimationFrame(() => {{
      requestAnimationFrame(() => {{
        lw.classList.add('animated');
      }});
    }});
  }}, 550);

  // Heading
  setTimeout(() => {{
    document.getElementById('letterHeading').classList.add('shown');
  }}, 900);

  // Build lines
  const lines = LETTER_TEXT.split('\\n').filter(l => l.trim());
  const container = document.getElementById('letterLines');
  lines.forEach((line, i) => {{
    const div = document.createElement('div');
    div.className = 'letter-line';
    div.textContent = line;
    container.appendChild(div);
    setTimeout(() => {{ div.classList.add('shown'); }}, 1100 + i * 55);
  }});

  const totalDelay = 1100 + lines.length * 55 + 200;
  setTimeout(() => {{
    document.getElementById('letterFooter').classList.add('shown');
  }}, totalDelay);
  setTimeout(() => {{
    document.getElementById('actionBar').classList.add('shown');
    fireHearts();
  }}, totalDelay + 200);
}}

// ── Confetti hearts ──
function fireHearts() {{
  const canvas = document.getElementById('confetti-canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const hearts = [];
  const emojis = ['💕','💗','💖','💓','💝','❤️','🌹'];

  for (let i = 0; i < 55; i++) {{
    hearts.push({{
      x: Math.random() * canvas.width,
      y: canvas.height + 30,
      emoji: emojis[Math.floor(Math.random() * emojis.length)],
      vx: (Math.random() - 0.5) * 3.5,
      vy: -(Math.random() * 5 + 3),
      size: Math.random() * 18 + 14,
      alpha: 1,
      rot: Math.random() * Math.PI * 2,
      rotV: (Math.random() - 0.5) * 0.08,
    }});
  }}

  function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    hearts.forEach(h => {{
      ctx.save();
      ctx.globalAlpha = Math.max(0, h.alpha);
      ctx.font = h.size + 'px serif';
      ctx.translate(h.x, h.y);
      ctx.rotate(h.rot);
      ctx.fillText(h.emoji, -h.size/2, h.size/2);
      ctx.restore();
      h.x += h.vx;
      h.y += h.vy;
      h.vy += 0.06;
      h.alpha -= 0.008;
      h.rot += h.rotV;
    }});
    if (hearts.some(h => h.alpha > 0)) requestAnimationFrame(draw);
    else ctx.clearRect(0, 0, canvas.width, canvas.height);
  }}
  requestAnimationFrame(draw);
}}

// ── Voice reading ──
function readLetter() {{
  if ('speechSynthesis' in window) {{
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(LETTER_TEXT);
    utter.rate = 0.88;
    utter.pitch = 1.05;
    const voices = window.speechSynthesis.getVoices();
    const femaleVoice = voices.find(v =>
      v.lang.startsWith('en') && (v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('samantha') || v.name.toLowerCase().includes('karen') || v.name.toLowerCase().includes('victoria') || v.gender === 'female')
    );
    if (femaleVoice) utter.voice = femaleVoice;
    window.speechSynthesis.speak(utter);
  }}
}}

// ── Music ──
function toggleMusic() {{
  const audio = document.getElementById('bgMusic');
  if (!musicOn) {{
    audio.volume = 0.25;
    audio.play().catch(() => {{}});
    musicOn = true;
  }} else {{
    audio.pause();
    musicOn = false;
  }}
}}

// ── Download PNG ──
async function downloadCard() {{
  const card = document.querySelector('.letter-card');
  if (!card) return;
  try {{
    const canvas = await html2canvas(card, {{ scale: 2, useCORS: true, backgroundColor: '{t["card_bg"]}' }});
    const link = document.createElement('a');
    link.download = 'love-letter.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  }} catch(e) {{ alert('Download failed: ' + e.message); }}
}}

// Auto-open on shared view
{'openEnvelope();' if auto_open else ''}

// Load voices async
if ('speechSynthesis' in window) {{
  window.speechSynthesis.onvoiceschanged = function() {{ window.speechSynthesis.getVoices(); }};
  window.speechSynthesis.getVoices();
}}
</script>
</body>
</html>
"""
    return html



def main():
    init_db()
    inject_global_css()

    
    params = st.query_params
    letter_id = params.get("id", None)

    if letter_id:
        
        data = load_letter(letter_id)
        if data:
            st.markdown('<div class="love-title">💌 A Letter For You</div>', unsafe_allow_html=True)
            st.markdown('<div class="love-subtitle">Someone sent you a love letter</div>', unsafe_allow_html=True)
            theme = data["theme"] if data["theme"] in THEMES else "Vintage parchment"
            html = render_letter_card(data["text"], theme, auto_open=True)
            import streamlit.components.v1 as components
            components.html(html, height=750, scrolling=True)
        else:
            st.error("Letter not found. It may have been removed.")
        return

   
    import streamlit.components.v1 as components

    st.markdown('<div class="love-title">💌 Digital Love Letter Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="love-subtitle">Turn your feelings into poetry</div>', unsafe_allow_html=True)

    
    if not os.environ.get("OPENAI_API_KEY"):
        with st.expander("🔑 Set OpenAI API Key", expanded=not st.session_state.get("openai_key")):
            key_input = st.text_input("API Key", type="password", placeholder="sk-...", label_visibility="collapsed")
            if key_input:
                st.session_state["openai_key"] = key_input
                st.success("Key saved for this session ✓")

    
    st.markdown('<div class="step-card"><div class="step-label">Step 1 — Your Feelings</div>', unsafe_allow_html=True)
    points = st.text_area(
        "Feelings",
        placeholder="• I love how you laugh at my terrible jokes\n• I miss you every time a good song plays\n• You make ordinary days feel like magic\n• I'm scared of how much I need you",
        height=150,
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    
    st.markdown('<div class="step-card"><div class="step-label">Step 2 — Style & Emotion</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1.3, 1])
    with col1:
        style = st.selectbox(
            "Style",
            list(STYLE_DESCRIPTIONS.keys()),
            label_visibility="visible",
        )
    with col2:
        intensity = st.slider("Love Intensity", 0, 100, 75)
    st.markdown('</div>', unsafe_allow_html=True)

    
    st.markdown('<div class="step-card"><div class="step-label">Step 3 — Card Theme</div>', unsafe_allow_html=True)
    theme = st.selectbox(
        "Theme",
        list(THEMES.keys()),
        label_visibility="visible",
    )
    st.markdown('</div>', unsafe_allow_html=True)

   
    st.markdown("")
    col_gen, _ = st.columns([1, 2])
    with col_gen:
        generate_btn = st.button("✨ Generate Love Letter")

    if generate_btn:
        if not points.strip():
            st.warning("Please write at least one feeling above.")
        else:
            client = get_openai_client()
            if not client:
                st.error("Please set your OpenAI API key above.")
            else:
                with st.spinner("Composing your letter with love… 💫"):
                    try:
                        letter_text = generate_letter(points, style, intensity, client)
                        letter_id = save_letter(points, style, theme, intensity, letter_text)
                        st.session_state["letter_text"] = letter_text
                        st.session_state["letter_id"] = letter_id
                        st.session_state["letter_theme"] = theme
                        st.session_state["show_letter"] = True
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

    
    if st.session_state.get("show_letter") and st.session_state.get("letter_text"):
        st.markdown("---")
        st.markdown('<div class="step-label" style="font-family:Montserrat,sans-serif;font-size:0.65rem;letter-spacing:0.3em;text-transform:uppercase;color:rgba(255,160,200,0.6);margin-bottom:0.8rem;">Step 4 — Your Letter</div>', unsafe_allow_html=True)

        html = render_letter_card(
            st.session_state["letter_text"],
            st.session_state.get("letter_theme", theme),
        )
        components.html(html, height=700, scrolling=True)

       
        st.markdown('<div class="step-card" style="margin-top:1rem;"><div class="step-label">Step 5 — Share Your Letter</div>', unsafe_allow_html=True)
        lid = st.session_state.get("letter_id", "")
        share_url = f"?id={lid}"

        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            st.text_input("Share link", value=share_url, label_visibility="collapsed")
        with col_s2:
            st.info(f"ID: `{lid}`")

        st.markdown(
            f"📋 Share this link with your recipient: `{share_url}`  \n"
            "They'll see the animated envelope open and the letter reveal itself.",
            unsafe_allow_html=False,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    elif not st.session_state.get("show_letter"):
        
        st.markdown("---")
        demo_html = """
        <div style="display:flex;justify-content:center;align-items:center;height:160px;opacity:0.35;">
          <div style="text-align:center;font-family:'Great Vibes',cursive;font-size:3rem;color:#ff9ec4;">
            Your letter awaits…
          </div>
        </div>
        <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap" rel="stylesheet">
        """
        components.html(demo_html, height=160)



if "show_letter" not in st.session_state:
    st.session_state["show_letter"] = False

if __name__ == "__main__":
    main()#
