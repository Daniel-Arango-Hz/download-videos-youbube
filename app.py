import yt_dlp
import streamlit as st
import os
import shutil

class VideoDownloader:
    def __init__(self, url, format_option, output_path):
        self.url = url
        self.format_option = format_option
        self.output_path = output_path

    def download(self, progress_callback):
        """Método para descargar el video/audio en el formato seleccionado."""
        ydl_opts = {
            'noplaylist': True,
            'progress_hooks': [progress_callback],
            'quiet': True,
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
        }

        if self.format_option == "MP4 (video)":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif self.format_option == "MP3 (audio)":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            # Ensure the extension is set to mp3 for audio downloads
            ydl_opts['ext'] = 'mp3'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                st.toast(f"Descargando desde: {self.url} en formato: {self.format_option}")
                info = ydl.extract_info(self.url, download=True)
                
                # Handle the file path differently for MP3 downloads
                if self.format_option == "MP3 (audio)":
                    # The file will be in MP3 format after conversion
                    file_path = os.path.join(self.output_path, f"{info['title']}.mp3")
                else:
                    file_path = os.path.join(self.output_path, f"{info['title']}.{info['ext']}")
                
                # Verify the file exists
                if os.path.exists(file_path):
                    return file_path
                else:
                    # Try to find the file with a different extension
                    possible_files = [f for f in os.listdir(self.output_path) if f.startswith(info['title'])]
                    if possible_files:
                        return os.path.join(self.output_path, possible_files[0])
                    
                return file_path
        except Exception as e:
            error_message = str(e)
            st.toast(f"Error al descargar: {error_message}", icon="❌")
            st.error(f"Error al descargar: {error_message}")
            return None

def on_progress(d):
    """Función para mostrar el progreso de descarga."""
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes > 0:
            progress = downloaded_bytes / total_bytes
            st.session_state.progress = progress

def reset_states():
    """Función para reiniciar todos los estados"""
    if 'should_clear_url' not in st.session_state:
        st.session_state.should_clear_url = False
    st.session_state.should_clear_url = True
    if 'file_path' in st.session_state:
        st.session_state.file_path = None
    if 'file_name' in st.session_state:
        st.session_state.file_name = None
    if 'progress' in st.session_state:
        st.session_state.progress = 0.0
    if 'is_downloading' in st.session_state:
        st.session_state.is_downloading = False
    if 'show_success' in st.session_state:
        st.session_state.show_success = False
    st.rerun()

def main():
    st.title("Descargador de Videos y Audios 📹🎵")
    
    # Inicializar estados de Streamlit
    if 'should_clear_url' not in st.session_state:
        st.session_state.should_clear_url = False
    if 'progress' not in st.session_state:
        st.session_state.progress = 0.0
    if 'is_downloading' not in st.session_state:
        st.session_state.is_downloading = False
    if 'file_path' not in st.session_state:
        st.session_state.file_path = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'show_success' not in st.session_state:
        st.session_state.show_success = False
    if 'last_url' not in st.session_state:
        st.session_state.last_url = ""

    # Manejar el valor inicial del input URL
    initial_url = "" if st.session_state.should_clear_url else st.session_state.get('last_url', "")
    if st.session_state.should_clear_url:
        st.session_state.should_clear_url = False

    # Input de URL con valor inicial controlado
    url = st.text_input("Ingrese la URL del video: ", value=initial_url)
    
    # Guardar la última URL usada
    if url:
        st.session_state.last_url = url

    # Opciones de formato de descarga
    format_options = ["MP4 (video)", "MP3 (audio)"]
    selected_format = st.selectbox("Seleccione el formato de descarga:", format_options)

    # Asegurar que el directorio de salida existe
    output_path = './downloads'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Calcular el estado de deshabilitado del botón
    is_button_disabled = bool(
        not url or 
        st.session_state.is_downloading or 
        (st.session_state.file_path is not None)
    )

    # Mostrar el botón "Obtener"
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("Obtener", 
                    disabled=is_button_disabled,
                    use_container_width=True):
            if url:
                st.session_state.is_downloading = True
                st.session_state.progress = 0.0

                with st.spinner("Descargando archivo... Por favor, espera."):
                    downloader = VideoDownloader(url, selected_format, output_path)
                    file_path = downloader.download(on_progress)

                    if file_path and os.path.exists(file_path):
                        st.session_state.file_path = file_path
                        st.session_state.file_name = os.path.basename(file_path)
                        st.success("¡Tu archivo se ha descargado exitosamente!")
                        st.toast("¡Descarga completada con éxito!", icon="✅")
                        st.session_state.show_success = True
                    else:
                        st.error("Error: No se pudo completar la descarga")
                
                st.session_state.is_downloading = False
                st.rerun()

    # Mostrar el progreso mientras se descarga
    if st.session_state.is_downloading:
        st.progress(st.session_state.progress)

    # Mostrar mensaje de éxito si corresponde
    if st.session_state.show_success:
        st.success("¡Descarga completada!")

    # Manejo de la descarga del archivo
    if st.session_state.file_path and os.path.exists(st.session_state.file_path):
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            with open(st.session_state.file_path, "rb") as f:
                if st.download_button(
                    label="Descargar el archivo",
                    data=f,
                    file_name=st.session_state.file_name,
                    mime="application/octet-stream",
                    use_container_width=True
                ):
                    try:
                        # Cerrar el archivo antes de intentar eliminarlo
                        f.close()
                        os.remove(st.session_state.file_path)
                        st.toast("Archivo temporal eliminado exitosamente.", icon="🗑️")
                    except Exception as e:
                        st.error(f"No se pudo eliminar el archivo temporal: {e}")
                    finally:
                        st.success("¡Descarga completada! La página se recargará en unos segundos...")
                        st.balloons()
                        reset_states()

    # Botón para reiniciar
    if st.session_state.file_path or st.session_state.is_downloading:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button("Reiniciar", use_container_width=True):
                reset_states()

if __name__ == "__main__":
    main()