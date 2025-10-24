from fastapi import FastAPI, UploadFile, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import traceback
from urllib.parse import quote
import re

app = FastAPI()
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize_for_filename(s: str, max_len: int = 120) -> str:
    # Reemplaza caracteres no permitidos en nombres de archivo y limita longitud
    s = re.sub(r'[\\/:*?"<>|]', '_', s)
    s = s.strip()
    if len(s) > max_len:
        s = s[:max_len].rstrip()
    # Asegura ASCII para la parte filename (fallback)
    ascii_safe = ''.join(ch if 32 <= ord(ch) <= 126 else '_' for ch in s)
    return ascii_safe or "audio"

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

        cookies_path = None
        if cookies:
            cookies_path = os.path.join(DOWNLOAD_DIR, "cookies.txt")
            with open(cookies_path, "wb") as f:
                f.write(await cookies.read())
            ydl_opts["cookiefile"] = cookies_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise Exception("yt-dlp devolvió None: la descarga falló o fue ignorada. Comprueba la URL, cookies y opciones de yt-dlp.")

            filename = ydl.prepare_filename(info)
            file_mp3 = os.path.splitext(filename)[0] + ".mp3"

        # Limpia el archivo de cookies si fue usado
        if cookies_path and os.path.exists(cookies_path):
            os.remove(cookies_path)

        # Construye nombres seguros y header Content-Disposition
        title = info.get("title") if isinstance(info, dict) else None
        if not title:
            title = os.path.splitext(os.path.basename(file_mp3))[0]
        download_name = f"{title}.mp3"
        ascii_name = sanitize_for_filename(download_name)
        # filename* debe ir percent-encoded (UTF-8)
        quoted_name = quote(download_name, safe='')
        content_disposition = f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{quoted_name}'

        return FileResponse(
            file_mp3,
            media_type="audio/mpeg",
            headers={"Content-Disposition": content_disposition}
        )

    except Exception as e:
        # Incluimos la traza para facilitar diagnóstico local. En un entorno de producción
        # conviene escribir en logs y no devolver trazas completas al cliente.
        tb = traceback.format_exc()
        return JSONResponse({"error": str(e), "traceback": tb}, status_code=500)
