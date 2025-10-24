# Imagen base oficial de Python
FROM python:3.10-slim

# Instala dependencias del sistema necesarias para yt-dlp y ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Define el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos del backend al contenedor
COPY . /app

# Actualizamos pip e instalamos dependencias de Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Actualizamos yt-dlp a la última versión (evita errores con YouTube)
RUN yt-dlp -U || true

# Exponemos el puerto donde correrá FastAPI
EXPOSE 8000

# Comando de inicio del servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
