import streamlit as st
import yt_dlp
import os
import re
import glob

# ── Folder setup ──────────────────────────────────────────────────────────────
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ze Video Downloader",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Dark glassmorphism background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Hero banner */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(6,182,212,0.10));
    border-radius: 24px;
    border: 1px solid rgba(99,102,241,0.25);
    margin-bottom: 1.8rem;
    backdrop-filter: blur(12px);
}
.hero h1 {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #818cf8, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero p {
    color: #94a3b8;
    font-size: 1.05rem;
    margin-top: 0.5rem;
}

/* Platform pills */
.platform-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin: 1rem 0 1.5rem;
}
.platform-pill {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    color: #cbd5e1;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.4px;
}

/* Cards */
.info-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
}
.info-card h4 { color: #c7d2fe; margin-bottom: 0.6rem; font-weight: 700; }
.info-card p  { color: #94a3b8; margin: 0.25rem 0; font-size: 0.93rem; }
.info-card span.val { color: #e2e8f0; font-weight: 600; }

/* Detected badge */
.badge {
    display: inline-block;
    background: linear-gradient(90deg, #6366f1, #0ea5e9);
    color: white;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 0.5rem;
    letter-spacing: 0.5px;
}

/* Streamlit overrides */
div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(99,102,241,0.5) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
}
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #0ea5e9) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.65rem 2.2rem !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
}
.stProgress > div > div {
    background: linear-gradient(90deg, #6366f1, #38bdf8) !important;
    border-radius: 8px !important;
}
.stSelectbox div[data-baseweb="select"] {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    border: 1.5px solid rgba(99,102,241,0.4) !important;
}
.stRadio > div { gap: 10px !important; }
label[data-testid="stWidgetLabel"] { color: #94a3b8 !important; }
.stAlert { border-radius: 12px !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.85) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Platform detection ─────────────────────────────────────────────────────────
PLATFORM_MAP = {
    "youtube.com": ("YouTube", ""),
    "youtu.be":    ("YouTube", ""),
    "tiktok.com":  ("TikTok", ""),
    "instagram.com":("Instagram",""),
    "facebook.com":("Facebook",""),
    "fb.watch":    ("Facebook",""),
    "twitter.com": ("Twitter/X",""),
    "x.com":       ("Twitter/X",""),
    "vimeo.com":   ("Vimeo",""),
    "dailymotion.com":("Dailymotion",""),
    "twitch.tv":   ("Twitch",""),
    "reddit.com":  ("Reddit",""),
    "bilibili.com":("Bilibili",""),
    "nicovideo.jp":("NicoVideo",""),
    "soundcloud.com":("SoundCloud",""),
    "mixcloud.com":("Mixcloud",""),
    "rumble.com":  ("Rumble",""),
    "odysee.com":  ("Odysee",""),
    "pinterest.com":("Pinterest",""),
    "linkedin.com":("LinkedIn",""),
    "snapchat.com":("Snapchat",""),
}

def detect_platform(url: str):
    url_lower = url.lower()
    for domain, (name, icon) in PLATFORM_MAP.items():
        if domain in url_lower:
            return name, icon
    return "Universal", ""

def validate_url(url: str) -> bool:
    return bool(re.match(r'https?://.+\..+', url.strip()))

def sanitize_filename(title: str) -> str:
    title = re.sub(r'[^\w\s\-]', '', title)
    return title[:60].strip()

def format_duration(seconds: int) -> str:
    if not seconds:
        return "Unknown"
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    return f"{h:02}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"

def format_size(b) -> str:
    if not b:
        return "Unknown"
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"

def get_ydl_base_opts(cookies_txt: str | None = None) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "geo_bypass_country": "US",
        # ── YouTube 403 fix: force mobile-web player client ──────────────────
        # Cloud server IPs (AWS/GCP/Streamlit) are blocked by YouTube's default
        # web player. The mobile web client ("mweb") has lighter restrictions.
        "extractor_args": {
            "youtube": {
                "player_client": ["mweb", "web_creator", "ios"],
                "player_skip": [],
            }
        },
        "http_headers": {
            # Mobile Chrome UA matches the mweb player client
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.6367.82 Mobile Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
        },
        # Retry on transient network errors
        "retries": 5,
        "fragment_retries": 5,
        "file_access_retries": 3,
    }
    if cookies_txt:
        opts["cookiefile"] = cookies_txt
    return opts

def build_format_string(quality: str) -> tuple[str, list | None]:
    """Return (format_string, postprocessors_or_None)."""
    pp = None
    if quality == "Best (auto)":
        fmt = "bestvideo+bestaudio/best"
    elif quality == "4K (2160p)":
        fmt = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
    elif quality == "1080p":
        fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    elif quality == "720p":
        fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
    elif quality == "480p":
        fmt = "bestvideo[height<=480]+bestaudio/best[height<=480]"
    elif quality == "360p":
        fmt = "bestvideo[height<=360]+bestaudio/best[height<=360]"
    elif quality == "MP3 (audio only)":
        fmt = "bestaudio/best"
        pp = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}]
    elif quality == "M4A (audio only)":
        fmt = "bestaudio/best"
        pp = [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a", "preferredquality": "256"}]
    elif quality == "FLAC (lossless)":
        fmt = "bestaudio/best"
        pp = [{"key": "FFmpegExtractAudio", "preferredcodec": "flac"}]
    else:
        fmt = "best"
    return fmt, pp

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    cookies_file = st.file_uploader(
        " Cookies file (optional)",
        type=["txt"],
        help="Upload a Netscape cookies.txt to bypass age-restrictions or login-walls.",
    )
    cookies_path = None
    if cookies_file:
        cookies_path = os.path.join(DOWNLOAD_DIR, "cookies.txt")
        with open(cookies_path, "wb") as f:
            f.write(cookies_file.read())
        st.success("Cookies loaded ✔")

    allow_playlist = st.toggle(" Allow playlist download", value=False)
    embed_subs = st.toggle(" Embed subtitles (if available)", value=False)
    embed_thumbnail = st.toggle(" Embed thumbnail in audio", value=True)
    write_info = st.toggle(" Save metadata JSON", value=False)

    st.markdown("---")
    st.markdown("###  Supported Platforms")
    all_platforms = "\n".join([f"• {n} {i}" for (n, i) in PLATFORM_MAP.values()])
    st.markdown(f"""
<div style='color:#94a3b8;font-size:0.82rem;line-height:1.7'>
YouTube  · TikTok  · Instagram  · Facebook <br>
Twitter/X  · Vimeo  · Dailymotion  · Twitch <br>
Reddit  · Bilibili  · NicoVideo  · SoundCloud <br>
Mixcloud  · Rumble  · Odysee  · Pinterest <br>
LinkedIn · Snapchat  · <b style='color:#818cf8'>+1000 more via yt-dlp</b>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button(" Clear downloads folder"):
        for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
            if not f.endswith("cookies.txt"):
                os.remove(f)
        st.success("Downloads cleared!")

# ── Hero header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <h1>📥 Ze Video Downloader</h1>
    <p>Download videos & audio from <b>1000+ platforms</b> — YouTube, TikTok, Instagram, Twitter/X, Twitch & more</p>
</div>
""", unsafe_allow_html=True)

# ── URL input ──────────────────────────────────────────────────────────────────
url = st.text_input(
    " Paste your video URL:",
    placeholder="https://www.youtube.com/watch?v=... or any supported URL",
    label_visibility="collapsed",
)

col_btn, col_info = st.columns([1, 4])
with col_btn:
    fetch_clicked = st.button(" Get Info", use_container_width=True)

# ── Main logic ─────────────────────────────────────────────────────────────────
if fetch_clicked or (url and "video_info" not in st.session_state):
    st.session_state.pop("video_info", None)

if fetch_clicked and url:
    if not validate_url(url):
        st.error(" Invalid URL. Please enter a valid http/https URL.")
    else:
        platform_name, platform_icon = detect_platform(url)
        st.markdown(f"<div class='badge'>{platform_icon} {platform_name}</div>", unsafe_allow_html=True)

        opts = get_ydl_base_opts(cookies_path)
        opts["noplaylist"] = not allow_playlist
        opts["extract_flat"] = False

        with st.spinner(" Fetching video information..."):
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                st.session_state["video_info"] = info
                st.session_state["platform"]   = (platform_name, platform_icon)
                st.session_state["url"]        = url
            except yt_dlp.utils.DownloadError as e:
                st.error(f" Could not fetch info: {e}")
            except Exception as e:
                st.error(f" Unexpected error: {e}")

# ── Show info if we have it ────────────────────────────────────────────────────
if "video_info" in st.session_state:
    info            = st.session_state["video_info"]
    platform_name, platform_icon = st.session_state["platform"]
    url             = st.session_state["url"]

    title       = sanitize_filename(info.get("title", "Unknown Title"))
    duration    = format_duration(info.get("duration", 0))
    uploader    = info.get("uploader") or info.get("channel") or "Unknown"
    upload_date = info.get("upload_date", "")
    if upload_date and len(upload_date) == 8:
        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    resolution  = info.get("resolution") or "Unknown"
    view_count  = info.get("view_count")
    like_count  = info.get("like_count")
    description = (info.get("description") or "")[:300]
    thumbnail   = info.get("thumbnail")
    direct_url  = info.get("url")
    is_live     = info.get("is_live", False)
    filesize    = format_size(info.get("filesize") or info.get("filesize_approx"))

    st.markdown("---")
    # ── Layout ─────────────────────────────────────────────────────────────────
    left, right = st.columns([1, 1.8])

    with left:
        if thumbnail:
            st.image(thumbnail, use_container_width=True)
        if is_live:
            st.warning(" This is a **LIVE stream** — only stream download is possible.")

    with right:
        st.markdown(f"""
<div class='info-card'>
    <h4> Video Information</h4>
    <p> Title: <span class='val'>{title}</span></p>
    <p> Platform: <span class='val'>{platform_icon} {platform_name}</span></p>
    <p> Duration: <span class='val'>{duration}</span></p>
    <p> Uploader: <span class='val'>{uploader}</span></p>
    <p> Upload Date: <span class='val'>{upload_date or "Unknown"}</span></p>
    <p> Resolution: <span class='val'>{resolution}</span></p>
    <p> File Size: <span class='val'>{filesize}</span></p>
    {"<p> Views: <span class='val'>" + f"{view_count:,}" + "</span></p>" if view_count else ""}
    {"<p> Likes: <span class='val'>" + f"{like_count:,}" + "</span></p>" if like_count else ""}
</div>
""", unsafe_allow_html=True)

        if description:
            with st.expander(" Description"):
                st.caption(description)

    # Video preview
    if direct_url and not is_live:
        with st.expander(" Preview video"):
            try:
                st.video(direct_url)
            except Exception:
                st.caption("Preview not available for this source.")

    st.markdown("---")

    # ── Quality selection ───────────────────────────────────────────────────────
    VIDEO_QUALITIES = ["Best (auto)", "4K (2160p)", "1080p", "720p", "480p", "360p"]
    AUDIO_QUALITIES = ["MP3 (audio only)", "M4A (audio only)", "FLAC (lossless)"]

    qcol1, qcol2 = st.columns([1, 2])
    with qcol1:
        dl_type = st.radio(" Download type:", ["Video", "Audio only"], horizontal=True)
    with qcol2:
        if dl_type == "Video":
            quality = st.selectbox("Quality:", VIDEO_QUALITIES)
        else:
            quality = st.selectbox("Format:", AUDIO_QUALITIES)

    # ── Download button ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬇️  Download Now", use_container_width=True):
        progress_bar = st.progress(0)
        status_text  = st.empty()

        def progress_hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done  = d.get("downloaded_bytes", 0)
                if total:
                    pct = min(done / total, 1.0)
                    progress_bar.progress(pct)
                    speed = d.get("speed") or 0
                    eta   = d.get("eta") or 0
                    status_text.markdown(
                        f"⬇️ **{int(pct*100)}%** — "
                        f"Speed: `{format_size(speed)}/s` — "
                        f"ETA: `{eta}s`"
                    )
            elif d["status"] == "finished":
                progress_bar.progress(1.0)
                status_text.markdown(" **Processing file…**")

        fmt, pp = build_format_string(quality)
        dl_opts = get_ydl_base_opts(cookies_path)
        dl_opts.update({
            "format":         fmt,
            "outtmpl":        f"{DOWNLOAD_DIR}/{sanitize_filename(title)}.%(ext)s",
            "progress_hooks": [progress_hook],
            "noplaylist":     not allow_playlist,
            "writeinfojson":  write_info,
        })
        if embed_subs:
            dl_opts["writesubtitles"] = True
            dl_opts["embedsubtitles"] = True
            dl_opts["subtitleslangs"] = ["en", "auto"]
        if embed_thumbnail and dl_type == "Audio only":
            dl_opts["embedthumbnail"] = True
        if pp:
            dl_opts["postprocessors"] = pp

        try:
            with yt_dlp.YoutubeDL(dl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                raw_name  = ydl.prepare_filename(info_dict)

            # Extension may change after post-processing
            base_noext = os.path.splitext(raw_name)[0]
            candidates = glob.glob(base_noext + ".*")
            final_file = candidates[0] if candidates else raw_name

            if os.path.exists(final_file):
                st.success(" Download Complete!")
                with open(final_file, "rb") as fh:
                    st.download_button(
                        label     = f" Save  {os.path.basename(final_file)}",
                        data      = fh.read(),
                        file_name = os.path.basename(final_file),
                        mime      = "application/octet-stream",
                        use_container_width=True,
                    )
            else:
                st.error(" File not found after download. Try a different quality.")

        except yt_dlp.utils.DownloadError as e:
            st.error(f" Download failed: {e}")
        except Exception as e:
            st.error(f" Unexpected error: {e}")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;color:#475569;font-size:0.8rem;'>
    Powered by <b>yt-dlp</b> · 1000+ platforms supported · For personal use only
</div>
""", unsafe_allow_html=True)
