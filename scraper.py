"""
scraper.py
----------
Modul scraping artikel khusus BBC News menggunakan trafilatura.

Fungsi utama:
    scrape_bbc(url) -> dict
        Mengembalikan dict dengan key:
            "text"    : str  -- teks artikel yang sudah bersih
            "title"   : str  -- judul artikel (jika ditemukan)
            "url"     : str  -- URL yang diproses
            "error"   : str | None

Batasan:
    - Hanya menerima domain bbc.com dan bbc.co.uk
    - Hanya URL yang mengandung path artikel (bukan homepage)
    - Menggunakan trafilatura untuk ekstraksi teks bersih
"""

from urllib.parse import urlparse
import requests
import trafilatura

# ──────────────────────────────────────────────────────────────────────────────
# Konfigurasi
# ──────────────────────────────────────────────────────────────────────────────

ALLOWED_DOMAINS = {"bbc.com", "bbc.co.uk"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 10  # detik


# ──────────────────────────────────────────────────────────────────────────────
# Helper: validasi URL
# ──────────────────────────────────────────────────────────────────────────────

def _validate_bbc_url(url: str) -> str | None:
    """
    Validasi URL BBC.
    Mengembalikan pesan error (str) jika tidak valid, atau None jika OK.
    """
    url = url.strip()

    if not url:
        return "URL tidak boleh kosong."

    if not url.startswith(("http://", "https://")):
        return "URL harus diawali dengan http:// atau https://"

    try:
        parsed = urlparse(url)
    except Exception:
        return "Format URL tidak valid."

    # Cek domain
    hostname = parsed.hostname or ""
    # Hapus prefix 'www.'
    clean_host = hostname.removeprefix("www.")
    if clean_host not in ALLOWED_DOMAINS:
        return (
            f"❌ Domain '{hostname}' tidak diizinkan. "
            f"Hanya URL dari bbc.com atau bbc.co.uk yang diterima."
        )

    # Pastikan ada path (bukan hanya homepage)
    path = parsed.path.rstrip("/")
    if not path or path in ("/news", "/sport", "/weather"):
        return (
            "URL yang dimasukkan bukan artikel spesifik. "
            "Gunakan URL langsung ke halaman artikel BBC."
        )

    return None  # valid


# ──────────────────────────────────────────────────────────────────────────────
# Fungsi utama
# ──────────────────────────────────────────────────────────────────────────────

def scrape_bbc(url: str) -> dict:
    """
    Scrape dan ekstrak teks dari artikel BBC News.

    Parameters
    ----------
    url : str -- URL artikel BBC

    Returns
    -------
    dict dengan key: text, title, url, error
    """
    url = url.strip()

    # ── Validasi URL ──────────────────────────────────────────────────────────
    err = _validate_bbc_url(url)
    if err:
        return {"text": "", "title": "", "url": url, "error": err}

    # ── Fetch HTML ────────────────────────────────────────────────────────────
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return {
            "text": "", "title": "", "url": url,
            "error": "Koneksi timeout. Coba lagi atau periksa URL."
        }
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else "?"
        return {
            "text": "", "title": "", "url": url,
            "error": f"Halaman tidak dapat diakses (HTTP {code})."
        }
    except requests.exceptions.RequestException as e:
        return {
            "text": "", "title": "", "url": url,
            "error": f"Gagal mengambil halaman: {str(e)}"
        }

    html = response.text

    # ── Ekstraksi teks dengan trafilatura ─────────────────────────────────────
    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_recall=True,      # prioritaskan tidak melewatkan konten
        url=url,
    )

    # Ekstrak metadata (judul)
    meta = trafilatura.extract_metadata(html, default_url=url)
    title = meta.title if (meta and meta.title) else ""

    if not extracted or len(extracted.strip()) < 100:
        return {
            "text": "", "title": title, "url": url,
            "error": (
                "Tidak dapat mengekstrak teks dari halaman ini. "
                "Pastikan URL mengarah ke halaman artikel BBC, bukan halaman indeks atau video."
            )
        }

    return {
        "text": extracted.strip(),
        "title": title,
        "url": url,
        "error": None,
    }
