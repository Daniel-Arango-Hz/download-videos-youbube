import yt_dlp
import streamlit as st
import os

# Estilos personalizados para centrar el contenido
st.markdown(
    """
    <style>
        div[data-testid="stModal"] {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .block-container {
            max-width: 600px;
            margin: auto;
            text-align: center;
        }
        .stButton > button {
            width: 100%;
        }
        .stDownloadButton > button {
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

class VideoDownloader:
    def __init__(self, url, format_option, output_path):
        self.url = url
        self.format_option = format_option
        self.output_path = output_path

    def download(self, progress_callback):
        """Método para descargar el video/audio en el formato seleccionado."""
        ydl_opts = {
            "noplaylist": True,
            "progress_hooks": [progress_callback],
            "quiet": True,
            "outtmpl": os.path.join(self.output_path, "%(title)s.%(ext)s"),
            "nocheckcertificate": True,
            "geo_bypass": True,
            "geo_bypass_country": "US",
            "cookies_from_browser": ("chrome",),  # Usa cookies de Chrome automáticamente
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": "https://www.youtube.com/"
            }
        }

        if self.format_option == "MP4 (video)":
            ydl_opts["format"] = "bestvideo+bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"
        elif self.format_option == "MP3 (audio)":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
            ydl_opts["ext"] = "mp3"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                st.toast(f"Descargando desde: {self.url} en formato: {self.format_option}")
                info = ydl.extract_info(self.url, download=True)

                file_extension = "mp3" if self.format_option == "MP3 (audio)" else info.get("ext", "mp4")
                file_path = os.path.join(self.output_path, f"{info['title']}.{file_extension}")

                return file_path if os.path.exists(file_path) else None
        except Exception as e:
            st.toast(f"Error al descargar: {str(e)}", icon="❌")
            st.error(f"Error al descargar: {str(e)}")
            return None

def on_progress(d):
    """Función para mostrar el progreso de descarga."""
    if d.get("status") == "downloading":
        total_bytes = d.get("total_bytes", 0)
        downloaded_bytes = d.get("downloaded_bytes", 0)
        if total_bytes > 0:
            st.session_state.progress = downloaded_bytes / total_bytes

def reset_states():
    """Reinicia los estados de la aplicación."""
    for key in ["should_clear_url", "file_path", "file_name", "progress", "is_downloading", "show_success"]:
        st.session_state[key] = None
    st.rerun()

def main():
    st.title("📥 Descargador de Videos y Audios")

    # Inicializar estados en Streamlit si no existen
    for key in ["should_clear_url", "progress", "is_downloading", "file_path", "file_name", "show_success", "last_url"]:
        if key not in st.session_state:
            st.session_state[key] = None

    url = st.text_input("🔗 Ingrese la URL del video:", value=st.session_state.get("last_url", ""))
    if url:
        st.session_state.last_url = url

    format_options = ["MP4 (video)", "MP3 (audio)"]
    selected_format = st.selectbox("🎞️ Seleccione el formato de descarga:", format_options)

    output_path = "./downloads"
    os.makedirs(output_path, exist_ok=True)

    # Deshabilitar botón si no hay URL o si ya se está descargando un archivo
    is_button_disabled = not bool(url) or bool(st.session_state.is_downloading) or bool(st.session_state.file_path)

    st.divider()

    # Botón de descarga centrado
    if st.button("🚀 Obtener", disabled=is_button_disabled):
        if url:
            st.session_state.is_downloading = True
            st.session_state.progress = 0.0

            with st.spinner("⏳ Descargando archivo... Por favor, espera."):
                downloader = VideoDownloader(url, selected_format, output_path)
                file_path = downloader.download(on_progress)

                if file_path:
                    st.session_state.file_path = file_path
                    st.session_state.file_name = os.path.basename(file_path)
                    st.success("✅ ¡Tu archivo se ha descargado exitosamente!")
                    st.toast("¡Descarga completada con éxito!", icon="✅")
                    st.session_state.show_success = True
                else:
                    st.error("❌ Error: No se pudo completar la descarga")

            st.session_state.is_downloading = False
            st.rerun()

    if st.session_state.is_downloading:
        st.progress(st.session_state.progress)

    if st.session_state.show_success:
        st.success("✅ ¡Descarga completada!")

    # Mostrar botón de descarga si el archivo existe
    if st.session_state.file_path and os.path.exists(st.session_state.file_path):
        with open(st.session_state.file_path, "rb") as f:
            if st.download_button(
                label="📥 Descargar el archivo",
                data=f,
                file_name=st.session_state.file_name,
                mime="application/octet-stream"
            ):
                try:
                    f.close()
                    os.remove(st.session_state.file_path)
                    st.toast("🗑️ Archivo temporal eliminado exitosamente.")
                except Exception as e:
                    st.error(f"❌ No se pudo eliminar el archivo temporal: {e}")
                finally:
                    st.success("🎉 ¡Descarga completada! La página se recargará en unos segundos...")
                    st.balloons()
                    reset_states()

    # Botón de reinicio
    if st.session_state.file_path or st.session_state.is_downloading:
        if st.button("🔄 Reiniciar"):
            reset_states()

if __name__ == "__main__":
    main()
