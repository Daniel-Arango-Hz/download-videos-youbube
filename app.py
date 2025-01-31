import yt_dlp
import streamlit as st
import os
import base64
import time
from datetime import datetime

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
        'format': 'bestaudio/best' if format_type == "MP3" else 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }] if format_type == "MP3" else [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        ext = 'mp3' if format_type == "MP3" else 'mp4'
        return os.path.join('downloads', f"{info['title']}.{ext}")

def main():
    st.set_page_config(page_title="YT Downloader", page_icon="🎬", layout="centered")
    
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
    
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 YT Downloader Pro</h1>", unsafe_allow_html=True)

    # Primer paso: Cargar video
    with st.form(key='cargar_form'):
        url = st.text_input("**URL de YouTube**", placeholder="Pega el enlace aquí...")
        if st.form_submit_button("🎥 Cargar Video"):
            if not url:
                st.warning("⚠️ Por favor ingresa una URL válida de YouTube")
            else:
                try:
                    with st.spinner('Buscando video...'):
                        st.session_state.video_info = get_video_info(url)
                    st.success("¡Video cargado correctamente!")
                except Exception as e:
                    st.error(f"❌ Error al encontrar el video: {str(e)}")
                    if 'video_info' in st.session_state:
                        del st.session_state.video_info

    # Segundo paso: Mostrar previsualización y descarga
    if 'video_info' in st.session_state:
        info = st.session_state.video_info
        with st.container():
            st.markdown("<div class='preview-card'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(info.get('thumbnail', ''),
                       use_container_width=True,
                       caption="Vista previa")
            
            with col2:
                st.subheader(info.get('title', 'Sin título'))
                
                duration = info.get('duration', 0)
                minutes, seconds = divmod(duration, 60)
                hours, minutes = divmod(minutes, 60)
                duration_str = f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"
                
                st.markdown(f"""
                <div class="info-text">
                📺 Canal: **{info.get('uploader', 'Desconocido')}**  
                🕒 Duración: **{duration_str}**  
                📅 Fecha de subida: **{datetime.strptime(info['upload_date'], '%Y%m%d').strftime('%d/%m/%Y')}**  
                👁️ Vistas: **{info.get('view_count', 'N/A'):,}**  
                👍 Likes: **{info.get('like_count', 'N/A'):,}**
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Tercer paso: Selección de formato y descarga
        format_type = st.selectbox("**Seleccionar Formato**", ["MP4", "MP3"], key='format_select')
        if st.button("⬇️ Descargar Ahora", type="primary", key='descargar_boton'):
            try:
                os.makedirs("downloads", exist_ok=True)
                with st.spinner('Procesando descarga...'):
                    file_path = download_media(url, format_type)
                    
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
                    st.success("✅ Descarga completada con éxito!")
                    time.sleep(1)
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error en la descarga: {str(e)}")
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)

if __name__ == "__main__":
    main()