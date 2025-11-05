FROM python:3.10-slim


WORKDIR /app


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

COPY ./backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt



COPY ./backend /app/backend
COPY ./backend/alembic.ini /app/alembic.ini




EXPOSE 8000


COPY entrypoint.sh .

# 2. Asegúrate de que sea ejecutable DENTRO del contenedor
# RUN chmod +x ./entrypoint.sh

# CMD ["sh", "-c", "alembic -c backend/alembic.ini upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile certs/localhost+4-key.pem --ssl-certfile certs/localhost+4.pem"]

CMD ["sh", "-c", "alembic -c backend/alembic.ini upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 80"]

# ENTRYPOINT ["/app/entrypoint.sh"]