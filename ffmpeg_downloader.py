import os
import platform
import shutil
import stat
import tarfile
import zipfile
import urllib.request

FFMPEG_DIR = os.path.join(os.path.dirname(__file__), "ffmpeg")
os.makedirs(FFMPEG_DIR, exist_ok=True)

def download_ffmpeg():
    system = platform.system()
    if system == "Linux":
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        archive_name = "ffmpeg-linux.tar.xz"
        bin_name = "ffmpeg"
    elif system == "Darwin":
        url = "https://evermeet.cx/ffmpeg/getrelease/zip"
        archive_name = "ffmpeg-mac.zip"
        bin_name = "ffmpeg"
    elif system == "Windows":
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        archive_name = "ffmpeg-win.zip"
        bin_name = "ffmpeg.exe"
    else:
        raise Exception(f"Unsupported OS: {system}")

    archive_path = os.path.join(FFMPEG_DIR, archive_name)
    ffmpeg_bin_path = os.path.join(FFMPEG_DIR, bin_name)

    if os.path.isfile(ffmpeg_bin_path):
        print("ffmpeg ya está descargado.")
        return

    print(f"Descargando ffmpeg desde {url} ...")
    urllib.request.urlretrieve(url, archive_path)

    print("Extrayendo ffmpeg...")
    if system == "Linux":
        with tarfile.open(archive_path, "r:xz") as tar:
            for member in tar.getmembers():
                if member.name.endswith("/ffmpeg"):
                    member.name = os.path.basename(member.name)
                    tar.extract(member, FFMPEG_DIR)
                    shutil.move(os.path.join(FFMPEG_DIR, "ffmpeg"), ffmpeg_bin_path)
                    break
    elif system == "Darwin":
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            for name in zip_ref.namelist():
                if name == "ffmpeg":
                    zip_ref.extract(name, FFMPEG_DIR)
                    shutil.move(os.path.join(FFMPEG_DIR, "ffmpeg"), ffmpeg_bin_path)
                    break
    elif system == "Windows":
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            for name in zip_ref.namelist():
                if name.endswith("bin/ffmpeg.exe"):
                    zip_ref.extract(name, FFMPEG_DIR)
                    src = os.path.join(FFMPEG_DIR, name)
                    shutil.move(src, ffmpeg_bin_path)
                    break

    # Haz ejecutable el binario (Linux/Mac)
    if system in ("Linux", "Darwin"):
        st = os.stat(ffmpeg_bin_path)
        os.chmod(ffmpeg_bin_path, st.st_mode | stat.S_IEXEC)

    os.remove(archive_path)
    print("ffmpeg descargado y listo en:", ffmpeg_bin_path)

if __name__ == "__main__":
    download_ffmpeg()
