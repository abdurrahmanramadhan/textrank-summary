"""
streamlit_app.py
----------------
Streamlit frontend untuk TextRank Summarizer.
Tampilan mengikuti desain index_contoh.html (light mode, indigo accent).
Mendukung input teks langsung dan web scraping khusus BBC News.
Jalankan lokal  : streamlit run streamlit_app.py
Deploy          : push ke GitHub → connect ke share.streamlit.io
"""

import html
import streamlit as st
from textrank import textrank_summarize
from scraper import scrape_bbc

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

    /* ── Streamlit top header / toolbar ── */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ── Sembunyikan footer streamlit default ── */
    footer { display: none !important; }

    /* ── Container utama sebagai kartu putih di tengah ── */
    .block-container {
        max-width: 680px !important;
        margin: 2.5rem auto 3rem auto !important;
        padding: 2.25rem 2.25rem 2rem 2.25rem !important;
        background: var(--card-bg) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow) !important;
        border: 1px solid var(--border-color) !important;
    }

    @media (max-width: 640px) {
        .block-container {
            margin: 1rem !important;
            padding: 1.5rem 1.25rem !important;
        }
    }

    /* ── Header kartu ── */
    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.75rem;
    }
    .header-icon {
        width: 48px;
        height: 48px;
        background: var(--primary-light);
        color: var(--primary);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .header-title h1 {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: var(--text-main) !important;
        letter-spacing: -0.02em;
        margin: 0 !important;
        line-height: 1.3 !important;
    }
    .header-title p {
        font-size: 0.825rem !important;
        color: var(--text-muted) !important;
        margin: 0.2rem 0 0 0 !important;
    }

    /* ── Segmented Mode Selector (Radio) ── */
    div[data-testid="stRadio"] {
        margin-bottom: 1rem;
    }
    div[data-testid="stRadio"] > div {
        display: flex;
        gap: 0.5rem;
        background: #f1f5f9;
        padding: 0.35rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    div[data-testid="stRadio"] label {
        flex: 1;
        text-align: center;
        background: transparent;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] label:hover {
        color: var(--primary) !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: #ffffff !important;
        color: var(--primary) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    div[data-testid="stRadio"] input[type="radio"] {
        display: none;
    }

    /* ── Baris label (label + badge) ── */
    .label-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .section-label-text {
        font-weight: 700;
        font-size: 0.9rem;
        color: var(--text-main);
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* ── Badges ── */
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
    .badge.bbc {
        background: #fef2f2; color: #b91c1c; border-color: #fecaca;
    }

    /* ── BBC Article Box ── */
    .bbc-article-box {
        background: #f8fafc;
        border: 1.5px solid #e2e8f0;
        border-left: 4px solid #bb1919;
        border-radius: var(--radius-md);
        padding: 0.85rem 1rem;
        margin: 0.6rem 0 0.85rem 0;
    }
    .bbc-tag {
        display: inline-block;
        background: #bb1919;
        color: white;
        font-weight: 800;
        font-size: 0.7rem;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        letter-spacing: 0.5px;
        margin-bottom: 0.35rem;
    }
    .bbc-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.4;
        margin-bottom: 0.25rem;
    }
    .bbc-meta {
        font-size: 0.78rem;
        color: #64748b;
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
    }

    /* ── Slider group box ── */
    .slider-group {
        background: #f8fafc;
        border: 1px solid var(--border-color);
        padding: 1rem;
        border-radius: var(--radius-md);
        margin-top: 1rem;
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

    /* ── TextInput override ── */
    .stTextInput input {
        border: 1.5px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        font-size: 0.925rem !important;
        color: var(--text-main) !important;
        background: #ffffff !important;
        padding: 0.65rem 0.85rem !important;
    }
    .stTextInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3.5px rgba(79,70,229,0.12) !important;
    }
    .stTextInput label { display: none !important; }

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

    /* Secondary button styling (Fetch button) */
    .secondary-btn > button {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1.5px solid var(--border-color) !important;
        box-shadow: none !important;
        font-weight: 600 !important;
        padding: 0.65rem 1rem !important;
        margin-top: 0.25rem !important;
    }
    .secondary-btn > button:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: var(--text-main) !important;
        transform: translateY(0) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

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
# Header
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="card-header">
        <div class="header-icon">✨</div>
        <div class="header-title">
            <h1>Pemeringkas Teks (TextRank)</h1>
            <p>Automatic extractive summarizer &middot; 10%&ndash;50% ratio &middot; BBC Scraping &amp; Text</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# Mode Selector: Input Teks Langsung vs BBC News URL
# ──────────────────────────────────────────────────────────────────────────────

input_mode = st.radio(
    "Metode Input",
    options=["📝 Input Teks Langsung", "🌐 Scrape Berita BBC"],
    horizontal=True,
    label_visibility="collapsed",
    key="input_mode_radio",
)

active_text = ""
article_title = ""

# ──────────────────────────────────────────────────────────────────────────────
# Tab 1: Input Teks Langsung
# ──────────────────────────────────────────────────────────────────────────────
if input_mode == "📝 Input Teks Langsung":
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
    active_text = input_text.strip()

# ──────────────────────────────────────────────────────────────────────────────
# Tab 2: Scrape Berita BBC
# ──────────────────────────────────────────────────────────────────────────────
else:
    st.markdown(
        """
        <div class="label-row">
            <span class="section-label-text">🌐&nbsp; BBC Article URL</span>
            <span class="badge bbc">🔴 BBC Whitelist: bbc.com</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    url_val = st.text_input(
        label="url_hidden",
        placeholder="https://www.bbc.com/news/articles/...",
        key="bbc_url_input",
    )

    if "bbc_cache" not in st.session_state:
        st.session_state["bbc_cache"] = None

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        fetch_clicked = st.button("📥 Ambil Teks Artikel", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        sample_clicked = st.button("📌 Pakai Contoh Link BBC", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if sample_clicked:
        sample_url = "https://www.bbc.com/news/articles/c04j3q0w5y4o"
        st.session_state["bbc_url_input"] = sample_url
        st.rerun()

    if fetch_clicked:
        target_url = url_val.strip()
        if not target_url:
            st.warning("⚠️ Masukkan URL artikel BBC terlebih dahulu.")
        else:
            with st.spinner("Mengambil artikel dari BBC News..."):
                res = scrape_bbc(target_url)
            if res.get("error"):
                st.error(res["error"])
                st.session_state["bbc_cache"] = None
            else:
                st.session_state["bbc_cache"] = res
                st.toast("✅ Artikel berhasil diambil dari BBC!")

    # Jika sudah ada artikel yang di-cache
    cached = st.session_state.get("bbc_cache")
    if cached and cached.get("text"):
        words_num = len(cached["text"].split())
        safe_title = html.escape(cached.get("title") or "Artikel BBC News")
        safe_url = html.escape(cached.get("url") or "")
        display_url = safe_url if len(safe_url) < 60 else safe_url[:57] + "..."

        st.markdown(
            f"""
            <div class="bbc-article-box">
                <span class="bbc-tag">BBC NEWS</span>
                <div class="bbc-title">{safe_title}</div>
                <div class="bbc-meta">
                    <span>📊 <strong>{words_num}</strong> kata</span>
                    <span>🔗 <a href="{safe_url}" target="_blank" style="color: inherit; text-decoration: underline;">{display_url}</a></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("📖 Lihat Teks Lengkap Artikel BBC"):
            st.write(cached["text"])

        active_text = cached["text"]
        article_title = cached.get("title") or ""

# ──────────────────────────────────────────────────────────────────────────────
# Slider Ratio (Bersama)
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
    # Jika mode BBC tapi belum di-fetch dan user sudah mengisi URL
    if input_mode != "📝 Input Teks Langsung" and not active_text:
        target_url = st.session_state.get("bbc_url_input", "").strip()
        if not target_url:
            st.warning("⚠️ Silakan masukkan URL artikel BBC terlebih dahulu.")
        else:
            with st.spinner("Mengambil artikel dari BBC News..."):
                res = scrape_bbc(target_url)
            if res.get("error"):
                st.error(res["error"])
            else:
                st.session_state["bbc_cache"] = res
                active_text = res["text"]
                article_title = res.get("title") or ""

    word_count = len(active_text.split()) if active_text else 0

    if not active_text:
        if input_mode == "📝 Input Teks Langsung":
            st.warning("⚠️ Silakan masukkan teks terlebih dahulu.")
    elif word_count > MAX_WORDS:
        st.error(
            f"⚠️ Teks melebihi batas **{MAX_WORDS}** kata "
            f"(saat ini **{word_count}** kata)."
        )
    else:
        with st.spinner("Meringkas teks dengan TextRank…"):
            result = textrank_summarize(active_text, ratio=ratio)

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

            # Jika ada judul artikel BBC, tampilkan di atas stats
            if article_title:
                safe_t = html.escape(article_title)
                st.markdown(
                    f"""
                    <div style="font-size:0.85rem; font-weight:700; color:#0f172a; margin-bottom:0.4rem;">
                        📰 BBC Article: <span style="color:#4f46e5;">{safe_t}</span>
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

            # Textarea hasil
            st.text_area(
                label="output_hidden",
                value=result["summary"],
                height=170,
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
