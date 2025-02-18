import streamlit as st
import yt_dlp
import os
import re

# --- Helper: Sanitize filename and limit title length (45 words) ---
def sanitize_filename(filename, max_words=45):
    """
    Remove characters not allowed in filenames and truncate the title to a specific number of words.
    """
    # Remove invalid characters: \ / * ? : " < > |
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    words = filename.split()
    return " ".join(words[:max_words])

# Ensure the 'downloads' folder exists
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Configure Streamlit page settings
st.set_page_config(
    page_title="Ze Video Downloader",
    page_icon="📥",
    layout="centered"
)

# Custom CSS with enhanced color schemes and responsive design
st.markdown("""
    <style>
        /* Modern CSS Reset and Base Styles */
        :root {
            --primary-color: #4F46E5;
            --secondary-color: #3B82F6;
            --accent-color: #06B6D4;
            --success-color: #10B981;
            --error-color: #EF4444;
            --warning-color: #F59E0B;
            --text-primary: #1F2937;
            --text-secondary: #4B5563;
            --bg-primary: #FFFFFF;
            --bg-secondary: #F3F4F6;
        }
        [data-theme="dark"] {
            --primary-color: #6366F1;
            --secondary-color: #60A5FA;
            --accent-color: #22D3EE;
            --success-color: #34D399;
            --error-color: #F87171;
            --warning-color: #FBBF24;
            --text-primary: #F9FAFB;
            --text-secondary: #E5E7EB;
            --bg-primary: #111827;
            --bg-secondary: #1F2937;
        }
        /* Main Container Styles */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(
                135deg,
                rgba(var(--bg-primary-rgb), 0.95),
                rgba(var(--bg-secondary-rgb), 0.95)
            );
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        /* Header Styles */
        .stTitle {
            color: var(--primary-color) !important;
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            text-align: center;
            margin-bottom: 2rem !important;
            background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        /* Input Field Styles */
        .stTextInput input {
            border: 2px solid var(--primary-color) !important;
            border-radius: 10px !important;
            padding: 0.75rem 1rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease;
        }
        .stTextInput input:focus {
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
        }
        /* Button Styles */
        .stButton > button {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
        }
        /* Card Styles */
        .info-card {
            background: var(--bg-secondary);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        /* Radio Button Styles */
        .stRadio > label {
            color: var(--text-primary) !important;
        }
        /* Alert and Message Styles */
        .stAlert {
            border-radius: 10px !important;
            padding: 1rem !important;
        }
        .success {
            background-color: var(--success-color) !important;
            color: white !important;
        }
        /* Progress Bar Styles */
        .stProgress > div > div {
            background: linear-gradient(
                45deg,
                green,
                blue
            ) !important;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .error {
            background-color: var(--error-color) !important;
            color: white !important;
        }
        .warning {
            background-color: var(--warning-color) !important;
            color: white !important;
        }
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-container {
                padding: 1rem;
            }
            .stTitle {
                font-size: 2rem !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("📥 Ze Video Downloader")
st.markdown("### Download videos (<1GB) from various platforms with ease! 🚀")

# URL Input
url = st.text_input("🔗 Enter the video URL:", placeholder="Paste your video URL here...")

def validate_url(url):
    return "http" in url and (".com" in url or ".be" in url)

if st.button("Process") or url:
    if not validate_url(url):
        st.error("❌ Invalid URL. Please enter a valid video URL.")
    else:
        # --- Detect Video Service ---
        def detect_service(url):
            url_lower = url.lower()
            if "tiktok" in url_lower:
                return "TikTok"
            elif "youtube" in url_lower or "youtu.be" in url_lower:
                return "YouTube"
            elif "vimeo" in url_lower:
                return "Vimeo"
            elif "instagram" in url_lower:
                return "Instagram"
            elif "facebook" in url_lower:
                return "Facebook"
            elif "snapchat" in url_lower or "snap" in url_lower:
                return "Snapchat"
            else:
                return "Other"

        service_type = detect_service(url)
        st.info(f"🔍 Detected Service: **{service_type}**")

        # --- Extract Video Info using yt_dlp ---
        ydl_opts = {
            'quiet': True,
            # For preview: select a format that has video & audio up to 720p.
            'format': 'best[height<=720]',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'nocheckcertificate': True,  # Avoid SSL errors
            'extract_flat': False,
            'postprocessors': [],
            'restrictfilenames': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            # Sanitize and truncate the title to 45 words (for display and filename)
            raw_title = info.get('title', 'Unknown Title')
            safe_title = sanitize_filename(raw_title, max_words=45)
            st.subheader(f"🎬 Video Title: {safe_title}")

            # Update the output template with the sanitized title
            ydl_opts['outtmpl'] = f"downloads/{safe_title}.%(ext)s"

            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown Uploader')
            upload_date = info.get('upload_date', 'Unknown Date')
            resolution = info.get('resolution', 'Unknown Resolution')
            file_size = info.get('filesize', 0)
            thumbnail_url = info.get('thumbnail', None)

            duration_str = f"{duration//3600:02}:{(duration%3600)//60:02}:{duration%60:02}"
            estimated_size = f"{file_size / (1024 * 1024):.2f} MB" if file_size else "Unknown"

            # --- Display Video Info & Preview ---
            col1, col2 = st.columns([1, 2])
            if service_type == "TikTok":
                # For TikTok, show thumbnail preview only
                with col1:
                    if thumbnail_url:
                        st.image(thumbnail_url, caption="Image Preview", width=220)
                    else:
                        st.warning("⚠ No thumbnail available.")
            else:
                # --- Determine Preview URL with sound ---
                preview_url = None
                if 'formats' in info and isinstance(info['formats'], list):
                    # Filter formats that have both video and audio, and height ≤720
                    valid_formats = [
                        fmt for fmt in info['formats']
                        if fmt.get('height') and fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt.get('height') <= 720
                    ]
                    if valid_formats:
                        # Choose the format with the highest resolution among those
                        preview_format = max(valid_formats, key=lambda x: x.get('height', 0))
                        preview_url = preview_format.get('url')
                if not preview_url:
                    preview_url = info.get('url', None)

                with col1:
                    if preview_url:
                        st.subheader("▶ Video Preview (With Sound)")
                        st.video(preview_url)
                    elif thumbnail_url:
                        st.subheader("🖼️ Image Preview")
                        st.image(thumbnail_url, width=280)
                    else:
                        st.warning("⚠ No preview available.")

            with col2:
                st.subheader("🎬 Video Information")
                st.write(f"**📌 Title:** {raw_title}")
                st.write(f"**🕒 Duration:** {duration_str}")
                st.write(f"**📢 Uploader:** {uploader}")
                st.write(f"**📅 Upload Date:** {upload_date}")
                st.write(f"**🖥️ Resolution:** {resolution}")
                st.write(f"📂 **Estimated File Size:** {estimated_size}")

            # --- Quality Selection ---
            quality = st.radio("Select Quality:", options=["720p MP4", "1080p MP4", "MP3", "M4A"])

            # --- Download Button ---
            if st.button("Download"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                def progress_hook(d):
                    if d['status'] == 'downloading':
                        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                        downloaded_bytes = d.get('downloaded_bytes', 0)
                        if total_bytes:
                            progress = downloaded_bytes / total_bytes
                            progress_bar.progress(min(progress, 1.0))
                            status_text.text(f"📥 Downloading: {int(progress * 100)}%")
                    elif d['status'] == 'finished':
                        progress_bar.progress(1.0)
                        status_text.text("✅ Download finished, processing file...")

                # Update yt_dlp options for downloading based on quality
                ydl_opts.update({
                    'progress_hooks': [progress_hook],
                    'noplaylist': True,
                })

                if quality == "720p MP4":
                    ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
                elif quality == "1080p MP4":
                    ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
                elif quality == "MP3":
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio', 
                        'preferredcodec': 'mp3', 
                        'preferredquality': '192'
                    }]
                elif quality == "M4A":
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio', 
                        'preferredcodec': 'm4a', 
                        'preferredquality': '192'
                    }]

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(url, download=True)
                        original_filename = ydl.prepare_filename(info_dict)
                        if quality == "M4A":
                            final_filename = os.path.splitext(original_filename)[0] + ".m4a"
                        else:
                            final_filename = original_filename

                    if os.path.exists(final_filename):
                        st.success("🎉 Download Complete!")
                        with open(final_filename, "rb") as file:
                            file_data = file.read()
                            st.download_button(
                                label="⬇ Download File",
                                data=file_data,
                                file_name=os.path.basename(final_filename),
                                mime="application/octet-stream",
                            )
                    else:
                        st.error("❌ File not found! Try again.")

                except Exception as e:
                    st.error(f"❌ Error during download: {e}")

        except yt_dlp.utils.DownloadError as e:
            st.error(f"❌ Error fetching video info: {e}")

st.markdown("</div>", unsafe_allow_html=True)