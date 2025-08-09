import yt_dlp
import streamlit as st
import os
import base64
import time
import re
from datetime import datetime
import logging
import shutil

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

def get_ffmpeg_location():
    # Busca ffmpeg en variable de entorno, en el PATH, o en la carpeta local del proyecto
    ffmpeg_path = os.environ.get("FFMPEG_PATH")
    if ffmpeg_path and os.path.isfile(ffmpeg_path):
        return ffmpeg_path
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        return ffmpeg_in_path
    # Busca en la carpeta local del proyecto
    local_ffmpeg = os.path.join(os.path.dirname(__file__), "ffmpeg", "ffmpeg")
    if os.path.isfile(local_ffmpeg):
        return local_ffmpeg
    # Para Windows
    local_ffmpeg_win = os.path.join(os.path.dirname(__file__), "ffmpeg", "ffmpeg.exe")
    if os.path.isfile(local_ffmpeg_win):
        return local_ffmpeg_win
    return None

def download_media(url, format_type, cookies_path=None):
    ydl_opts = {
        'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'format': 'bestvideo[ext=mp4]+bestaudio/best' if format_type == "MP4" else 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'progress_hooks': [progress_hook],
    }
    if cookies_path:
        ydl_opts['cookiefile'] = cookies_path

    # Specific configuration for TikTok
    if "tiktok.com" in url:
        ydl_opts['extractor_args'] = {
            'TikTok': {
                'download_without_watermark': True,
            }
        }

    ffmpeg_location = get_ffmpeg_location()
    if ffmpeg_location:
        ydl_opts['ffmpeg_location'] = ffmpeg_location

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

    st.markdown("**Opcional:** Sube tu archivo de cookies exportado del navegador para evitar bloqueos de YouTube.")
    cookies_file = st.file_uploader("Archivo de cookies (Netscape .txt)", type=["txt"])

    url = st.text_input("Pega el enlace de YouTube o TikTok para descargar el MP3 automáticamente", placeholder="Pega el enlace aquí...")
    if url:
        cookies_path = None
        if cookies_file is not None:
            cookies_path = os.path.join("downloads", f"cookies_{int(time.time())}.txt")
            with open(cookies_path, "wb") as f:
                f.write(cookies_file.read())
        try:
            st.session_state.progress_bar = st.progress(0)
            with st.spinner('Procesando descarga de MP3...'):
                file_path = download_media(url, "MP3", cookies_path)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                b64 = base64.b64encode(file_bytes).decode()
                mime_type = "audio/mp3"
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
                st.success("✅ ¡Descarga completada!")
        except Exception as e:
            logger.error(f"Error durante la descarga: {str(e)}")
            st.error(f"❌ Error en la descarga: {str(e)}")
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        finally:
            if cookies_path and os.path.exists(cookies_path):
                os.remove(cookies_path)

    if not get_ffmpeg_location():
        st.warning(
            "⚠️ ffmpeg no está instalado ni descargado. "
            "Haz clic en el botón para descargarlo automáticamente o ejecuta `python ffmpeg_downloader.py`."
        )
        if st.button("Descargar ffmpeg automáticamente"):
            import subprocess
            subprocess.run(["python", "ffmpeg_downloader.py"])
            st.experimental_rerun()

if __name__ == "__main__":
    main()

