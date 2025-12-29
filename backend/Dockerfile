FROM python:3.10-slim

# Configura el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos a /app en el contenedor
COPY requirements.txt /app/

# Instala las dependencias del sistema necesarias para compilar psycopg2 y otras librerías
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && apt-get clean

# Instala las dependencias especificadas en el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación a /app en el contenedor
COPY . /app/

# Expone el puerto 8000 en el contenedor
EXPOSE 8000

# Define el comando por defecto para ejecutar la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]