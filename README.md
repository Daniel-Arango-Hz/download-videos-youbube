# Descargador de Videos y Audios 📹🎵

Esta es una aplicación basada en **Streamlit** que permite descargar videos o audios desde URLs compatibles (como YouTube) utilizando la biblioteca **yt-dlp**.

## Características

- Descarga de videos en formato MP4.
- Descarga de audios en formato MP3.
- Interfaz de usuario simple y amigable.
- Progreso de descarga en tiempo real.
- Eliminación automática de archivos temporales después de la descarga.
- Función de reinicio para limpiar el estado de la aplicación.

## Requisitos

Antes de ejecutar la aplicación, asegúrate de tener instalado lo siguiente:

- Python 3.8 o superior
- Las bibliotecas necesarias indicadas en el archivo `requirements.txt`

## Instalación

1. Clona este repositorio o descarga los archivos directamente.
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_PROYECTO>
   ```

2. Crea un entorno virtual (opcional, pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Asegúrate de que FFmpeg esté instalado en tu sistema (necesario para la conversión a MP3). Puedes instalarlo desde:
   - [Sitio oficial de FFmpeg](https://ffmpeg.org/)

## Ejecución

Para iniciar la aplicación, ejecuta el siguiente comando:

```bash
streamlit run app.py
```

Esto abrirá la aplicación en tu navegador predeterminado en la URL: `http://localhost:8501`

## Uso

1. Ingresa la URL del video que deseas descargar.
2. Selecciona el formato de descarga: `MP4 (video)` o `MP3 (audio)`.
3. Haz clic en el botón **Obtener** para iniciar la descarga.
4. Una vez descargado, podrás descargar el archivo a tu dispositivo.
5. Usa el botón **Reiniciar** para limpiar el estado de la aplicación y realizar otra descarga.

## Estructura del Proyecto

```
.
├── app.py                # Código principal de la aplicación
├── requirements.txt      # Dependencias del proyecto
├── downloads/            # Carpeta donde se guardan los archivos descargados
└── README.md             # Este archivo
```

## Dependencias

El archivo `requirements.txt` incluye las siguientes bibliotecas:

- `yt-dlp`: Manejo de descargas desde múltiples plataformas.
- `streamlit`: Creación de la interfaz de usuario.

Instala las dependencias usando:
```bash
pip install -r requirements.txt
```

## Notas

- La aplicación utiliza **yt-dlp**, que es una bifurcación de youtube-dl, para realizar las descargas. Esto asegura compatibilidad con múltiples plataformas de video.
- FFmpeg es necesario para convertir archivos de audio a MP3.

## Licencia

Este proyecto está bajo la licencia MIT. Siéntete libre de usarlo, modificarlo y distribuirlo.

---

¡Disfruta descargando videos y audios con facilidad! 😊

