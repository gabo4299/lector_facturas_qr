FROM python:3.10-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# --- PASO 1: INSTALAR TODAS LAS DEPENDENCIAS DEL SISTEMA EN UN SOLO PASO ---
# Esto incluye 'libzbar0' para los QR y la lista completa de librerías
# que Playwright/Chromium necesita para funcionar en un entorno Linux mínimo.

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    \
    # --- AÑADE ESTA LÍNEA ---
    libzbar0 \
    # -----------------------
    \
    # Dependencias de sistema para Playwright/Chromium
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libgbm1 libatspi2.0-0 libx11-6 libxcomposite1 libxdamage1 libxext6 \
    libxfixes3 libxrandr2 libxss1 libasound2 libxkbcommon0 \
    \
    # Limpiamos la caché de apt
    && rm -rf /var/lib/apt/lists/*
# --- PASO 2: INSTALAR LAS DEPENDENCIAS DE PYTHON ---
COPY ./backend/requirements.txt .
# Instalamos Playwright primero para poder usar su comando
RUN pip install --no-cache-dir -r requirements.txt



COPY ./backend /app/backend
COPY ./backend/alembic.ini /app/alembic.ini

# COPY ./alembic /app/alembic
# COPY alembic.ini /app/alembic.ini
# COPY client_secret.json /app/client_secret.json

# 6. Expone el puerto que tu aplicación usará
EXPOSE 8000

# 7. El comando que se ejecutará para iniciar tu app
#    Primero corre las migraciones de Alembic y luego inicia Uvicorn.
CMD ["sh", "-c", "alembic -c backend/alembic.ini upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile certs/localhost+4-key.pem --ssl-certfile certs/localhost+4.pem"]