import streamlit as st
import requests

st.title("🎵 YouTube Downloader")

url = st.text_input("Ingrese el enlace de YouTube:")
cookie_file = st.file_uploader("Suba su archivo de cookies (opcional)", type=["txt"])

if st.button("Descargar"):
    if not url:
        st.warning("Por favor ingrese un enlace válido.")
    else:
        with st.spinner("Descargando..."):
            try:
                backend_url = "https://back-music-v1.onrender.com/download"
                files = {"cookies": cookie_file} if cookie_file else None
                params = {"url": url}
                response = requests.get(backend_url, params=params, files=files, stream=True)

                # ✅ Verificamos si el backend devolvió un archivo
                content_type = response.headers.get("content-type", "")
                if "audio" in content_type:
                    content_disposition = response.headers.get("content-disposition", "")
                    filename = "audio.mp3"
                    if "filename=" in content_disposition:
                        filename = content_disposition.split("filename=")[1].strip('"')

                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    st.success(f"✅ Descarga completada: {filename}")
                    with open(filename, "rb") as f:
                        st.download_button(
                            label="Descargar archivo",
                            data=f,
                            file_name=filename,
                            mime="audio/mpeg"
                        )
                else:
                    # ⚠️ Si el backend devolvió JSON o error
                    error_msg = response.text
                    st.error(f"Error desde el backend:\n{error_msg}")

            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
