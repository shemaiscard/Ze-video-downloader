import streamlit as st
import yt_dlp
import os
import re
from urllib.parse import urlparse

# Ensure the 'downloads' folder exists
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Configure Streamlit page settings
st.set_page_config(
    page_title="Ze Video Downloader",
    page_icon="📥",
    layout="centered"
)

# Modern UI Styling - Fixed missing parenthesis in gradient definition
st.markdown("""
    <style>
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

        .stTitle {
            color: var(--primary-color) !important;
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            text-align: center;
            margin-bottom: 2rem !important;
            background: linear-gradient(45deg, var(--primary-color), var(--accent-color)) !important;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stTextInput input {
            border: 2px solid var(--primary-color) !important;
            border-radius: 10px !important;
            padding: 0.75rem 1rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease;
        }

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

        .info-card {
            background: var(--bg-secondary);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

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
st.markdown("### Download any video from YouTube, TikTok, Instagram, and more")

# URL Input
url = st.text_input("🔗 Enter the video URL:", placeholder="Paste your video URL here...")

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def sanitize_filename(title):
    # Remove invalid characters and limit the length
    title = re.sub(r'[^\w\s-]', '', title)
    return title[:50].strip()

def get_ydl_opts(quality=None):
    base_opts = {
        'quiet': True,
        'outtmpl': 'downloads/%(title).50s.%(ext)s',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'cookies': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'tv_embedded', 'web_embedded', 'android_vr'],
                'formats': 'missing_pot',
                'skip': ['hls', 'dash']
            }
        },
        'format': '(bv*[ext=mp4][height<=1080]+ba[ext=m4a]/b[ext=mp4]/[protocol^=http])',
        'allow_unplayable_formats': True,
        'hls_use_mpegts': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }
    
    if quality == "720p MP4":
        base_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
    elif quality == "1080p MP4":
        base_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
    elif quality == "MP3":
        base_opts['format'] = 'bestaudio/best'
        base_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    elif quality == "M4A":
        base_opts['format'] = 'bestaudio/best'
        base_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192'
        }]
    
    return base_opts

def detect_service(url):
    domain = urlparse(url).netloc.lower()
    if 'tiktok' in domain:
        return "TikTok"
    elif 'youtube' in domain or 'youtu.be' in domain:
        return "YouTube"
    elif 'vimeo' in domain:
        return "Vimeo"
    elif 'instagram' in domain:
        return "Instagram"
    elif 'facebook' in domain:
        return "Facebook"
    return "Other"

# Main process button
process_button = st.button("Process")

if process_button or url:
    if not validate_url(url):
        st.error("❌ Invalid URL. Please enter a valid video URL.")
    else:
        service_type = detect_service(url)
        st.info(f"🔍 Detected Service: **{service_type}**")

        try:
            # First try with standard options
            ydl_opts = get_ydl_opts()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            # Extract video information
            title = sanitize_filename(info.get('title', 'Unknown Title'))
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown Uploader')
            upload_date = info.get('upload_date', 'Unknown Date')
            resolution = info.get('resolution', 'Unknown Resolution')
            video_url = info.get('url', None)
            file_size = info.get('filesize', 0)
            thumbnail_url = info.get('thumbnail', None)

            # Format duration and file size
            duration_str = f"{duration//3600:02}:{(duration%3600)//60:02}:{duration%60:02}"
            estimated_size = f"{file_size / (1024 * 1024):.2f} MB" if file_size else "Unknown"

            # Display video info
            col1, col2 = st.columns([1, 2])
            with col1:
                if thumbnail_url:
                    st.image(thumbnail_url, caption="Thumbnail", width=220)
            with col2:
                st.subheader("🎬 Video Information")
                st.write(f"**📌 Title:** {title}")
                st.write(f"**🕒 Duration:** {duration_str}")
                st.write(f"**📢 Uploader:** {uploader}")
                st.write(f"**📅 Upload Date:** {upload_date}")
                st.write(f"**🖥️ Resolution:** {resolution}")
                st.write(f"📂 **Estimated File Size:** {estimated_size}")

            # Video preview section
            if video_url:
                st.subheader("▶ Video Preview")
                st.video(video_url)
            elif thumbnail_url:
                st.subheader("🖼️ Image Preview")
                st.image(thumbnail_url, width=280)

            # Quality selection
            if service_type in ["TikTok", "Instagram", "Facebook"]:
                quality = st.radio("Select Quality:", options=["1080p MP4", "MP3", "M4A"])
            else:
                quality = st.radio("Select Quality:", options=["720p MP4", "1080p MP4", "MP3", "M4A"])

            # Download button
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
                        status_text.text("✅ Processing file...")

                # Set up the download options with the selected quality
                ydl_opts = get_ydl_opts(quality)
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Fix the filename path to ensure correct extension handling
                safe_title = sanitize_filename(title)
                ydl_opts['outtmpl'] = f'downloads/{safe_title}.%(ext)s'

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(url, download=True)
                        original_filename = ydl.prepare_filename(info_dict)
                        final_filename = original_filename
                        
                        # Adjust extension for audio formats
                        if quality == "MP3":
                            final_filename = os.path.splitext(original_filename)[0] + '.mp3'
                        elif quality == "M4A":
                            final_filename = os.path.splitext(original_filename)[0] + '.m4a'
                        
                        # Ensure we're getting the correct path
                        if not os.path.exists(final_filename) and os.path.exists(os.path.join('downloads', os.path.basename(final_filename))):
                            final_filename = os.path.join('downloads', os.path.basename(final_filename))

                    if os.path.exists(final_filename):
                        st.success("🎉 Download Complete!")
                        with open(final_filename, "rb") as file:
                            st.download_button(
                                label="⬇ Download File",
                                data=file.read(),
                                file_name=os.path.basename(final_filename),
                                mime="application/octet-stream",
                            )
                    else:
                        st.error(f"❌ File not found at {final_filename}! Try again.")

                except yt_dlp.utils.DownloadError as e:
                    if "PO token" in str(e):
                        # Fallback to HLS for YouTube
                        status_text.text("⚠️ Primary method failed, trying alternative...")
                        ydl_opts['extractor_args']['youtube']['player_client'] = ['ios', 'web_safari']
                        ydl_opts['format'] = 'bestvideo[protocol=m3u8]+bestaudio/best'
                        try:
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                info_dict = ydl.extract_info(url, download=True)
                                if os.path.exists(final_filename):
                                    st.success("🎉 Download Complete (HLS Fallback)!")
                                    with open(final_filename, "rb") as file:
                                        st.download_button(
                                            label="⬇ Download File",
                                            data=file.read(),
                                            file_name=os.path.basename(final_filename),
                                            mime="application/octet-stream",
                                        )
                                else:
                                    possible_files = [f for f in os.listdir("downloads") if safe_title in f]
                                    if possible_files:
                                        found_file = os.path.join("downloads", possible_files[0])
                                        st.success(f"🎉 Download Complete! Found file: {possible_files[0]}")
                                        with open(found_file, "rb") as file:
                                            st.download_button(
                                                label="⬇ Download File",
                                                data=file.read(),
                                                file_name=possible_files[0],
                                                mime="application/octet-stream",
                                            )
                                    else:
                                        st.error("❌ Could not find the downloaded file!")
                        except Exception as e:
                            st.error(f"❌ Fallback download failed: {e}")
                    else:
                        st.error(f"❌ Download error: {e}")
                except Exception as e:
                    st.error(f"❌ Error during download: {e}")

        except yt_dlp.utils.DownloadError as e:
            st.error(f"❌ Error fetching video info: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

# Footer
st.markdown("---")
st.markdown("ℹ️ For educational purposes only. Download only content you have rights to.")
