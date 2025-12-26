# Ze Video Downloader

Ze Video Downloader is a full-stack media extraction tool built with Python. It leverages the power of Streamlit for the frontend and yt-dlp for the backend to provide a seamless interface for downloading high-quality video and audio from major social platforms (YouTube, TikTok, Instagram, etc.).

---

## Technical Architecture & Construction

This project was engineered to solve the complexity of handling diverse media streams and dynamic content delivery.

### 1. Frontend Engineering (Streamlit + CSS3)
* **Custom UI Engine**: While built on Streamlit, the standard UI was overridden using injected CSS (via `st.markdown`). This implements a custom design system with CSS variables (`--primary-color`, `--bg-secondary`) that adapt to light and dark modes.
* **Responsive Design**: The CSS uses media queries and flexbox layouts to ensure the "glassmorphism" card effects and input fields scale correctly on mobile devices.
* **State Management**: Utilizes Streamlit's rerun execution model to handle the linear flow: Input -> Validation -> Metadata Preview -> Format Selection -> Download.

### 2. Backend Logic (Python & yt-dlp)
* **Anti-Bot Evasion**: The core downloader is configured with custom HTTP headers (`User-Agent`, `Referer`) to mimic a legitimate browser session. This prevents 403 Forbidden errors often encountered with standard scraping requests.
* **Service Detection**: Implements a heuristic `detect_service()` function that analyzes URL patterns to identify the source platform (e.g., distinguishing `youtu.be` from `tiktok.com`) to adjust UI feedback.
* **Data Sanitization**: A custom `sanitize_filename()` function uses Regex (`re.sub`) to strip illegal characters from video titles, preventing filesystem errors during the save process.

### 3. Media Processing Pipeline
* **Format Control**: The app dynamically modifies the `yt-dlp` configuration dictionary based on user selection:
    * *Video*: Uses syntax like `bestvideo[height<=1080]+bestaudio` to merge separate video/audio streams.
    * *Audio*: Triggers FFmpeg post-processors to convert raw streams into standardized MP3/M4A formats at 192kbps.
* **Progress Tracking**: A custom hook (`progress_hook`) intercepts the download stream to calculate real-time percentage, feeding data back to the Streamlit progress bar for immediate user feedback.

---

##  Key Features

* **Universal Compatibility**: Supports YouTube, TikTok, Vimeo, Instagram, Facebook, and Snapchat.
* **Smart Previews**: Fetches and displays thumbnails, video duration, and resolution before downloading.
* **Quality Options**: Offers specific resolutions (720p, 1080p) and audio-only extraction.
* **Secure File Handling**: Downloads are processed server-side in a temporary directory and streamed to the client, ensuring no persistent storage clutter.

---

##  Technology Stack

* **Language**: Python 3.x
* **Web Framework**: Streamlit
* **Core Engine**: yt-dlp (fork of youtube-dl)
* **Media Processing**: FFmpeg
* **Styling**: HTML5 / CSS3

---

##  Installation & Setup

1.  **Prerequisites**:
    Ensure Python and FFmpeg are installed and added to your system PATH.

2.  **Install Dependencies**:
    pip install streamlit yt-dlp requests

3.  **Run the Application**:
    streamlit run downloader.py

---

## Project Structure

├── downloader.py    # Main application logic and UI rendering

├── downloads/       # Temporary storage for processing files

└── README.txt       # Project documentation

---

##  Usage

1.  Paste a valid video URL into the input field.
2.  Review the file metadata (Title, Size, Duration).
3.  Select your desired format (Video or Audio).
4.  Click "Download" to process the file on the server.
5.  Click "Download File" to save the final artifact to your device.
