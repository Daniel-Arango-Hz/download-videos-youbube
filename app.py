import yt_dlp
import streamlit as st
import os
import base64
import time
import re
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the 'downloads' directory if it doesn't exist
os.makedirs("downloads", exist_ok=True)

def sanitize_filename(filename):
    """Remove invalid characters from filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def download_media(url, format_type):
    ydl_opts = {
        'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'format': 'bestvideo[ext=mp4]+bestaudio/best' if format_type == "MP4" else 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }] if format_type == "MP4" else [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'progress_hooks': [progress_hook],
    }

    # Specific configuration for TikTok
    if "tiktok.com" in url:
        ydl_opts['extractor_args'] = {
            'TikTok': {
                'download_without_watermark': True,
            }
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = 'mp4' if format_type == "MP4" else 'mp3'
            safe_title = sanitize_filename(info['title'])
            file_path = os.path.join('downloads', f"{safe_title}.{ext}")

            # Ensure the file is completely downloaded
            while not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                time.sleep(1)

            # Check if the file size is reasonable (more than 1KB)
            if os.path.getsize(file_path) < 1024:
                raise Exception("Downloaded file is too small, possibly corrupted.")

            return file_path
    except Exception as e:
        logger.error(f"Error downloading media: {str(e)}")
        raise

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            progress = d.get('_percent_str', '0%')
            # Remove ANSI color codes and convert to float
            progress_clean = re.sub(r'\x1b\[[0-9;]*m', '', progress)
            progress_float = float(progress_clean.strip('%')) / 100
            st.session_state.progress_bar.progress(progress_float)
        except ValueError:
            # If conversion fails, don't update the progress bar
            pass
    elif d['status'] == 'finished':
        st.session_state.progress_bar.progress(1.0)

def main():
    st.set_page_config(page_title="YT/TikTok Downloader", page_icon="🎬", layout="centered")
    
    st.markdown("""
    <style>
        .preview-card {
            border: 1px solid #FF4B4B;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .preview-thumbnail {
            border-radius: 8px;
        }
        .info-text {
            color: #666;
            font-size: 0.9em;
        }
        .stButton>button {
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 YT/TikTok Downloader</h1>", unsafe_allow_html=True)

    # Step 1: Load video
    with st.form(key='load_form'):
        url = st.text_input("**YouTube or TikTok URL**", placeholder="Paste the link here...")
        if st.form_submit_button("🎥 Load Video"):
            if not url:
                st.warning("⚠️ Please enter a valid URL")
            else:
                try:
                    with st.spinner('Searching for video...'):
                        st.session_state.video_info = get_video_info(url)
                    st.success("Video loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error finding the video: {str(e)}")
                    if 'video_info' in st.session_state:
                        del st.session_state.video_info

    # Step 2: Show preview and download
    if 'video_info' in st.session_state:
        info = st.session_state.video_info
        with st.container():
            st.markdown("<div class='preview-card'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                thumbnail = info.get('thumbnail', '')
                if thumbnail:
                    st.image(thumbnail, use_container_width=True, caption="Preview")
                else:
                    st.warning("No preview found")
            
            with col2:
                st.subheader(info.get('title', 'No title'))
                
                duration = info.get('duration', 0)
                minutes, seconds = divmod(duration, 60)
                hours, minutes = divmod(minutes, 60)
                duration_str = f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"
                
                st.markdown(f"""
                <div class="info-text">
                📺 Channel: **{info.get('uploader', 'Unknown')}**  
                🕒 Duration: **{duration_str}**  
                📅 Upload date: **{datetime.strptime(info.get('upload_date', '19700101'), '%Y%m%d').strftime('%d/%m/%Y') if 'upload_date' in info else 'Unknown'}**  
                👁️ Views: **{info.get('view_count', 'N/A'):,}**  
                👍 Likes: **{info.get('like_count', 'N/A'):,}**
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Step 3: Format selection and download
        format_type = st.selectbox("**Select Format**", ["MP4", "MP3"], key='format_select')
        if st.button("⬇️ Download Now", type="primary", key='download_button'):
            try:
                st.session_state.progress_bar = st.progress(0)
                with st.spinner('Processing download...'):
                    file_path = download_media(url, format_type)
                    
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"Could not find the file: {file_path}")
                    
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    
                    b64 = base64.b64encode(file_bytes).decode()
                    mime_type = "audio/mp3" if format_type == "MP3" else "video/mp4"
                    file_name = os.path.basename(file_path)
                    
                    js = f"""
                    <script>
                        function downloadFile() {{
                            var link = document.createElement('a');
                            link.href = 'data:{mime_type};base64,{b64}';
                            link.download = '{file_name}';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }}
                        window.onload = downloadFile;
                    </script>
                    """
                    st.components.v1.html(js, height=0)
                    os.remove(file_path)
                    del st.session_state.video_info
                    st.success("✅ Download completed successfully!")
                    time.sleep(1)
                    st.rerun()
            
            except Exception as e:
                logger.error(f"Error during download: {str(e)}")
                st.error(f"❌ Download error: {str(e)}")
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)

if __name__ == "__main__":
    main()

