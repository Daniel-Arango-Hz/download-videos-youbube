# Usamos una imagen base de Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos los archivos del proyecto al contenedor
COPY . /app

# Instalamos las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto donde Streamlit se ejecutará
EXPOSE 8501

# Comando para iniciar la aplicación
CMD ["streamlit", "run", "app.py"]
