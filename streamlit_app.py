"""
streamlit_app.py
----------------
Streamlit frontend untuk TextRank Summarizer.
Tampilan mengikuti desain index_contoh.html (light mode, indigo accent).
Jalankan lokal  : streamlit run streamlit_app.py
Deploy          : push ke GitHub → connect ke share.streamlit.io
"""

import streamlit as st
from textrank import textrank_summarize

# ──────────────────────────────────────────────────────────────────────────────
# Konfigurasi halaman
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Pemeringkas Teks TextRank",
    page_icon="✨",
    layout="centered",
)

MAX_WORDS = 3000

# ──────────────────────────────────────────────────────────────────────────────
# Custom CSS
# Strategi: style Streamlit's .block-container langsung menjadi "main-card"
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --primary:       #4f46e5;
        --primary-hover: #4338ca;
        --primary-light: #eef2ff;
        --bg-body:       #f8fafc;
        --card-bg:       #ffffff;
        --text-main:     #0f172a;
        --text-muted:    #64748b;
        --border-color:  #e2e8f0;
        --danger:        #ef4444;
        --success:       #10b981;
        --radius-lg:     16px;
        --radius-md:     10px;
        --radius-sm:     6px;
        --shadow: 0 10px 30px -5px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
    }

    html, body, [class*="css"], * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* ── Halaman background ── */
    .stApp {
        background-color: var(--bg-body) !important;
    }

    /* ── Ambient glow circles (fixed, di belakang segalanya) ── */
    .stApp::before {
        content: '';
        position: fixed;
        width: 350px; height: 350px;
        background: #c7d2fe;
        border-radius: 50%;
        filter: blur(90px);
        opacity: 0.4;
        top: -50px; left: -50px;
        pointer-events: none;
        z-index: 0;
    }
    .stApp::after {
        content: '';
        position: fixed;
        width: 400px; height: 400px;
        background: #fbcfe8;
        border-radius: 50%;
        filter: blur(90px);
        opacity: 0.4;
        bottom: -100px; right: -50px;
        pointer-events: none;
        z-index: 0;
    }

    /* ── Streamlit main block → jadikan main-card ── */
    .block-container {
        background: var(--card-bg) !important;
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow) !important;
        padding: 2rem 2rem 2.5rem 2rem !important;
        max-width: 680px !important;
        margin-top: 2rem !important;
        position: relative;
        z-index: 1;
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Header card ── */
    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding-bottom: 1.25rem;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 1.25rem;
    }
    .header-icon {
        width: 48px; height: 48px;
        background: var(--primary-light);
        color: var(--primary);
        border-radius: var(--radius-md);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }
    .header-title h1 {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: var(--text-main) !important;
        letter-spacing: -0.01em;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.3;
    }
    .header-title p {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin: 0.15rem 0 0 0;
    }

    /* ── Label rows ── */
    .label-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.4rem;
    }
    .section-label-text {
        display: flex; align-items: center; gap: 0.4rem;
        font-weight: 700; font-size: 0.9rem; color: #334155;
    }

    /* ── Badge word count ── */
    .badge {
        display: inline-flex; align-items: center; gap: 0.35rem;
        font-size: 0.8rem;
        background: #f1f5f9; color: #475569;
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    .badge.exceeded {
        background: #fef2f2; color: var(--danger); border-color: #fca5a5;
    }

    /* ── Slider group box ── */
    .slider-group {
        background: #f8fafc;
        border: 1px solid var(--border-color);
        padding: 1rem;
        border-radius: var(--radius-md);
        margin-bottom: 0.5rem;
    }
    .ratio-badge {
        background: var(--primary); color: #ffffff;
        font-size: 0.85rem; font-weight: 700;
        padding: 0.2rem 0.65rem; border-radius: 6px;
        box-shadow: 0 2px 6px rgba(79,70,229,0.25);
    }

    /* ── Textarea override ── */
    .stTextArea textarea {
        border: 1.5px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        font-size: 0.925rem !important;
        line-height: 1.6 !important;
        color: var(--text-main) !important;
        background: #ffffff !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3.5px rgba(79,70,229,0.12) !important;
    }
    .stTextArea label { display: none !important; }

    /* ── Slider override ── */
    .stSlider label { display: none !important; }
    .stSlider { margin-top: -0.5rem; }

    /* ── Primary button ── */
    .stButton > button {
        width: 100% !important;
        background: var(--primary) !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        padding: 0.85rem 1.25rem !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        box-shadow: 0 4px 12px rgba(79,70,229,0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: var(--primary-hover) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79,70,229,0.35) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Output divider ── */
    .output-divider {
        height: 1px;
        background: var(--border-color);
        margin: 1.25rem 0 1rem 0;
    }

    /* ── Stats bar ── */
    .stats-bar {
        display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;
        background: var(--primary-light);
        border: 1px solid #c7d2fe;
        border-radius: var(--radius-sm);
        padding: 0.5rem 0.85rem;
        font-size: 0.8rem; color: #3730a3; font-weight: 600;
        margin-bottom: 0.65rem;
    }
    .stat-item { display: flex; align-items: center; gap: 0.3rem; }
    .stat-item strong { color: var(--primary); }
    .stat-divider { color: #a5b4fc; font-size: 1rem; }

    /* ── Output placeholder ── */
    .output-placeholder {
        width: 100%;
        min-height: 130px;
        padding: 0.9rem;
        border: 1.5px solid var(--border-color);
        border-radius: var(--radius-md);
        background: #f8fafc;
        color: #94a3b8;
        font-size: 0.925rem;
        line-height: 1.6;
        font-style: italic;
    }

    /* output textarea background */
    div[data-testid="stTextArea"]:last-of-type textarea {
        background-color: #f8fafc !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Header  (HTML murni, aman karena tidak membungkus widget)
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="card-header">
        <div class="header-icon">✨</div>
        <div class="header-title">
            <h1>Pemeringkas Teks (TextRank)</h1>
            <p>Automatic extractive summarizer &middot; 10%&ndash;50% ratio &middot; 3000-word limit</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Input Text
# ──────────────────────────────────────────────────────────────────────────────

# Ambil nilai sebelumnya untuk hitung word count sebelum render ulang
prev_text = st.session_state.get("input_text", "")
word_count = len(prev_text.split()) if prev_text.strip() else 0
badge_cls  = "badge exceeded" if word_count > MAX_WORDS else "badge"

st.markdown(
    f"""
    <div class="label-row">
        <span class="section-label-text">📄&nbsp; Input Text</span>
        <span class="{badge_cls}">📝 {word_count} / {MAX_WORDS} words</span>
    </div>
    """,
    unsafe_allow_html=True,
)

input_text = st.text_area(
    label="input_hidden",
    placeholder="Type or paste your English text here (max 3000 words)...",
    height=190,
    key="input_text",
)

# Recompute setelah input
word_count = len(input_text.split()) if input_text.strip() else 0

# ──────────────────────────────────────────────────────────────────────────────
# Slider Ratio
# ──────────────────────────────────────────────────────────────────────────────

ratio_pct = st.session_state.get("ratio_slider", 30)

st.markdown(
    f"""
    <div class="slider-group">
        <div class="label-row">
            <span class="section-label-text">⚙️&nbsp; Summary Ratio:</span>
            <span class="ratio-badge">{ratio_pct}%</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

ratio_pct = st.slider(
    label="ratio_hidden",
    min_value=10,
    max_value=50,
    value=30,
    step=5,
    key="ratio_slider",
)
ratio = ratio_pct / 100

# ──────────────────────────────────────────────────────────────────────────────
# Tombol Summarize
# ──────────────────────────────────────────────────────────────────────────────

run = st.button("⚡  Summarize")

# ──────────────────────────────────────────────────────────────────────────────
# Output Section
# ──────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="output-divider"></div>', unsafe_allow_html=True)

if run:
    text = input_text.strip()

    if not text:
        st.warning("⚠️ Silakan masukkan teks terlebih dahulu.")
    elif word_count > MAX_WORDS:
        st.error(
            f"⚠️ Teks melebihi batas **{MAX_WORDS}** kata "
            f"(kamu memasukkan **{word_count}** kata)."
        )
    else:
        with st.spinner("Meringkas teks…"):
            result = textrank_summarize(text, ratio=ratio)

        if result.get("error"):
            st.error(f"⚠️ {result['error']}")
        else:
            orig         = result["original_sents"]
            kept         = result["summary_sents"]
            actual_ratio = round(kept / orig * 100) if orig else 0

            # Label output
            st.markdown(
                """
                <div class="label-row">
                    <span class="section-label-text">📋&nbsp; Summary Result</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Stats bar
            st.markdown(
                f"""
                <div class="stats-bar">
                    <span class="stat-item">📋 Original: <strong>{orig}</strong>&nbsp;sentences</span>
                    <span class="stat-divider">·</span>
                    <span class="stat-item">✅ Kept: <strong>{kept}</strong>&nbsp;sentences</span>
                    <span class="stat-divider">·</span>
                    <span class="stat-item">📊 Ratio: <strong>{actual_ratio}%</strong></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Textarea hasil (readonly via disabled)
            st.text_area(
                label="output_hidden",
                value=result["summary"],
                height=160,
                key="output_text",
            )

else:
    st.markdown(
        """
        <div class="label-row" style="margin-bottom:0.5rem;">
            <span class="section-label-text">📋&nbsp; Summary Result</span>
        </div>
        <div class="output-placeholder">
            The summarized text will appear here...
        </div>
        """,
        unsafe_allow_html=True,
    )
