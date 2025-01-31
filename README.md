# 🚀 YT Downloader Pro

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.22.0-FF4B4B)
![yt-dlp](https://img.shields.io/badge/yt--dlp-2023.7.6-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

**YT Downloader Pro** es una aplicación web moderna y fácil de usar para descargar videos y audio de YouTube en formatos MP4 y MP3. Desarrollada con Python y Streamlit, ofrece una interfaz intuitiva y un flujo de trabajo optimizado.

## ✨ Características principales

- **Previsualización de videos**: Muestra miniaturas, título, duración y estadísticas del video.
- **Descargas rápidas**: Soporte para MP4 (hasta 720p) y MP3 (calidad de 192kbps).
- **Interfaz moderna**: Diseño limpio y responsive.
- **Proceso en dos pasos**: Carga el video primero, luego descárgalo.
- **Manejo de errores**: Notificaciones claras para problemas comunes.
- **Descarga automática**: Los archivos se descargan directamente en tu dispositivo.

## 🛠️ Requisitos del sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- FFmpeg (para conversión de formatos)

## 🚀 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tuusuario/yt-downloader-pro.git
   cd yt-downloader-pro

2. Instala las dependencias:
pip install -r requirements.txt

3. Asegúrate de tener FFmpeg instalado:

Windows: Descarga desde ffmpeg.org y añádelo al PATH.

Linux: sudo apt install ffmpeg

macOS: brew install ffmpeg

4. Ejecuta la aplicación:
streamlit run app.py
Abre tu navegador en http://localhost:8501.

🖥️ Uso
1. Ingresa la URL del video de YouTube.

2. Haz clic en Cargar Video para previsualizar.

3. Selecciona el formato deseado (MP4 o MP3).

4. Haz clic en Descargar Ahora.

* ¡Listo! El archivo se descargará automáticamente.

🛠️ Tecnologías utilizadas
Python: Lenguaje principal del proyecto.

* Streamlit: Framework para la interfaz web.

* yt-dlp: Biblioteca para descargar contenido de YouTube.

* FFmpeg: Conversión y procesamiento de medios.

* Base64: Codificación de archivos para descarga.

📂 Estructura del proyecto
yt-downloader-pro/
├── app.py                # Código principal de la aplicación
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Este archivo
└── downloads/            # Carpeta temporal para archivos descargados

🤝 Contribución
¡Las contribuciones son bienvenidas! Sigue estos pasos:

1. Haz un fork del proyecto.

2. Crea una rama (git checkout -b feature/nueva-funcionalidad).

3. Haz commit de tus cambios (git commit -m 'Añade nueva funcionalidad').

4. Haz push a la rama (git push origin feature/nueva-funcionalidad).

5. Abre un Pull Request.


Nota: Este proyecto es solo para fines educativos. Asegúrate de cumplir con los términos de servicio de YouTube al utilizarlo.



