import streamlit as st
import yt_dlp
import os
import requests
import re

# Load custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Ensure the 'downloads' folder exists
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Configure Streamlit page settings
st.set_page_config(
    page_title="Ze Video Downloader",
    page_icon="📥",
    layout="centered"
)

# App Header
st.title("📥 Ze Video Downloader")
st.markdown("### Download videos from various platforms with ease! 🚀")

# URL Input
url = st.text_input("🔗 Enter the video URL:", placeholder="Paste your video URL here...")

def validate_url(url):
    return "http" in url and (".com" in url or ".be" in url)

def sanitize_filename(title):
    # Remove or replace problematic characters
    title = re.sub(r'[^\w\s-]', '', title)
    # Limit to 50 characters and strip whitespace
    return title[:50].strip()

if st.button("process") or url:
    if not validate_url(url):
        st.error("❌ Invalid URL. Please enter a valid video URL.")
    else:
        # --- Detect Video Service ---
        def detect_service(url):
            url = url.lower()
            if "tiktok" in url:
                return "TikTok"
            elif "youtube" in url or "youtu.be" in url:
                return "YouTube"
            elif "vimeo" in url:
                return "Vimeo"
            elif "instagram" in url:
                return "Instagram"
            elif "facebook" in url:
                return "Facebook"
            elif "snapchat" in url or "snap" in url:
                return "Snapchat"
            return "Other"

        service_type = detect_service(url)
        st.info(f"🔍 Detected Service: **{service_type}**")

        # --- Extract Video Info using yt_dlp ---
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'outtmpl': 'downloads/%(title).50s.%(ext)s',  # Limit filename to 50 chars
            'noplaylist': True,
            'nocheckcertificate': True,
            'extract_flat': False,
        }

        # Removed YouTube-specific preview handling to use a normal video preview for all services

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            # Sanitize and limit title length
            original_title = info.get('title', 'Unknown Title')
            title = sanitize_filename(original_title)
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown Uploader')
            upload_date = info.get('upload_date', 'Unknown Date')
            resolution = info.get('resolution', 'Unknown Resolution')
            video_url = info.get('url', None)
            file_size = info.get('filesize', 0)
            thumbnail_url = info.get('thumbnail', None)

            duration_str = f"{duration//3600:02}:{(duration%3600)//60:02}:{duration%60:02}"
            estimated_size = f"{file_size / (1024 * 1024):.2f} MB" if file_size else "Unknown"

            # --- Display Video Info ---
            col1, col2 = st.columns([1, 2])
            image_col = col2 if "tiktok" in url else col1
            info_col = col1 if "tiktok" in url else col2

            # Display the image preview
            if thumbnail_url and not "tiktok" in url:
                with image_col:
                    st.image(thumbnail_url, caption="Image Preview", width=220)

            # Display video information
            with info_col:
                st.subheader("🎬 Video Information")
                st.write(f"**📌 Title:** {title}")
                st.write(f"**🕒 Duration:** {duration_str}")
                st.write(f"**📢 Uploader:** {uploader}")
                st.write(f"**📅 Upload Date:** {upload_date}")
                st.write(f"**🖥️ Resolution:** {resolution}")
                st.write(f"📂 **Estimated File Size:** {estimated_size}")
                
            if video_url and not "tiktok" in url:
                st.subheader("▶ Video Preview")
                st.video(video_url)
            elif thumbnail_url:
                st.subheader("🖼️ Image Preview")
                st.image(thumbnail_url, width=280)
            else:
                st.warning("⚠ No preview available.")

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

                # Update download options with sanitized filename
                ydl_opts.update({
                    'outtmpl': f'downloads/{sanitize_filename(title)}.%(ext)s',
                    'progress_hooks': [progress_hook],
                    'noplaylist': True,
                })

                # Format selection handling
                if quality == "720p MP4":
                    ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
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
                        final_filename = os.path.splitext(original_filename)[0] + ".m4a" if quality == "M4A" else original_filename

                    if os.path.exists(final_filename):
                        st.success("🎉 Download Complete!")
                        
                        # Stream the file to user
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
