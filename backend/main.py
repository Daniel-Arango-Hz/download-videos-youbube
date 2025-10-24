from fastapi import FastAPI, UploadFile, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import traceback

app = FastAPI()
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/download")
async def download_video(url: str = Query(...), cookies: UploadFile = None):
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,  # 👈 fuerza que descargue solo una canción
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            # Opciones adicionales para evadir restricciones
            "nocheckcertificate": True,
            "geo_bypass": True,
            "extract_flat": False,
            "ignoreerrors": True,
            # Configuración del navegador
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
            }
        }

        if cookies:
            cookies_path = os.path.join(DOWNLOAD_DIR, "cookies.txt")
            with open(cookies_path, "wb") as f:
                f.write(await cookies.read())
            ydl_opts["cookiefile"] = cookies_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # Si yt-dlp devolvió None (por ejemplo cuando ignoreerrors=True y la descarga falló),
            # evitamos llamar a prepare_filename sobre None y devolvemos un error claro.
            if info is None:
                raise Exception("yt-dlp devolvió None: la descarga falló o fue ignorada. Comprueba la URL, cookies y opciones de yt-dlp.")

            filename = ydl.prepare_filename(info)
            file_mp3 = os.path.splitext(filename)[0] + ".mp3"

        return FileResponse(
            file_mp3,
            filename=os.path.basename(file_mp3),
            media_type="audio/mpeg"
        )

    except Exception as e:
        # Incluimos la traza para facilitar diagnóstico local. En un entorno de producción
        # conviene escribir en logs y no devolver trazas completas al cliente.
        tb = traceback.format_exc()
        return JSONResponse({"error": str(e), "traceback": tb}, status_code=500)
