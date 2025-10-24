# Imagen base
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Copiamos los archivos
COPY . /app

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
