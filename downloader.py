import streamlit as st
import yt_dlp
import os
import requests

# Ensure the 'downloads' folder exists
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Inject Tailwind CSS and custom styles for a dark, bluish glass morphism look
st.markdown(
    """
    <!-- Tailwind CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
      /* Global Body Styles */
      body {
          background: #0f172a; /* Dark bluish background */
          color: #e2e8f0;     /* Light text color */
          font-family: 'Inter', sans-serif;
      }
      /* Override Streamlit container background */
      .stApp {
          background: transparent;
      }
      /* Glass morphism container */
      .glass {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 15px;
          padding: 2rem;
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
          border: 1px solid rgba(255, 255, 255, 0.1);
          margin: 2rem auto;
          max-width: 800px;
      }
      /* Custom button override (if needed) */
      .btn-custom {
          @apply bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded;
      }
    </style>
    """, unsafe_allow_html=True
)

# Wrap main app content in a glass morphism container
#st.markdown('<div class="glass">', unsafe_allow_html=True)

st.title("📥 Ze Video Downloader")

# --- User Input ---
url = st.text_input("Enter the video URL:")

def validate_url(url):
    return "http" in url and (".com" in url or ".be" in url)

if url:
    if not validate_url(url):
        st.error("❌ Invalid URL. Please enter a valid video URL.")
    else:
        # --- Detect Video Service ---
        def detect_service(url):
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

        # --- Extract Video Info using yt_dlp (for all services including TikTok) ---
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'nocheckcertificate': True,  # Avoid SSL errors
            'extract_flat': False,
            'postprocessors': [],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get('title', 'Unknown Title')[:50]  # Limit title to 50 characters
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown Uploader')
            upload_date = info.get('upload_date', 'Unknown Date')
            resolution = info.get('resolution', 'Unknown Resolution')
            video_url = info.get('url', None)
            file_size = info.get('filesize', 0)  # Estimate file size
            thumbnail_url = info.get('thumbnail', None)  # Get thumbnail for preview

            duration_str = f"{duration//3600:02}:{(duration%3600)//60:02}:{duration%60:02}"
            estimated_size = f"{file_size / (1024 * 1024):.2f} MB" if file_size else "Unknown"

            # --- Display Video Info ---
            st.subheader("🎬 Video Information")
            st.write(f"**📌 Title:** {title}")
            st.write(f"**🕒 Duration:** {duration_str}")
            st.write(f"**📢 Uploader:** {uploader}")
            st.write(f"**📅 Upload Date:** {upload_date}")
            st.write(f"**🖥️ Resolution:** {resolution}")
            st.write(f"📂 **Estimated File Size:** {estimated_size}")

            # --- Video Preview ---
            if video_url and not "tiktok" in url:
                st.subheader("▶ Video Preview")
                st.video(video_url)
            elif thumbnail_url:
                st.subheader("🖼️ Image Preview")
                st.image(thumbnail_url)
            else:
                st.warning("⚠ No preview available.")

            # --- Quality Selection ---
            quality = st.radio("Select Quality:", options=["720p MP4", "1080p MP4", "MP3", "M4A", "Image (Social Media)"])

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

                # Update yt_dlp options for downloading
                ydl_opts.update({
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'progress_hooks': [progress_hook],
                    'noplaylist': True,
                })

                # Format selection handling
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
                elif quality == "Image (Social Media)":
                    ydl_opts['format'] = 'best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegVideoRemuxer', 
                        'preferedformat': 'jpg'
                    }]

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(url, download=True)
                        original_filename = ydl.prepare_filename(info_dict)
                        final_filename = os.path.splitext(original_filename)[0] + ".m4a" if quality == "M4A" else original_filename

                    if os.path.exists(final_filename):
                        st.success("🎉 Download Complete!")
                        with open(final_filename, "rb") as file:
                            st.download_button("⬇ Download File", file, os.path.basename(final_filename))
                    else:
                        st.error("❌ File not found! Try again.")

                except Exception as e:
                    st.error(f"❌ Error during download: {e}")

        except yt_dlp.utils.DownloadError as e:
            st.error(f"❌ Error fetching video info: {e}")

st.markdown("</div>", unsafe_allow_html=True)
