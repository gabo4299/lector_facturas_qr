#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# Imprime la variable de entorno para depurar
echo "ENTRYPOINT: El entorno (APP_ENV) es: '$APP_ENV'"

# Ejecuta las migraciones de Alembic en CUALQUIER entorno
# Asegúrate que la ruta a tu .ini sea correcta desde la raíz del proyecto
echo "ENTRYPOINT: Ejecutando migraciones de Alembic..."
alembic -c backend/alembic.ini upgrade head
echo "ENTRYPOINT: Migraciones completadas."

# Decide qué servidor iniciar basado en la variable APP_ENV
if [ "$APP_ENV" = "production" ]; then
    # --- MODO PRODUCCIÓN ---
    echo "ENTRYPOINT: Iniciando Gunicorn para Producción..."
    # Render te da la variable $PORT. Usamos 8000 como default si no existe.
    exec gunicorn backend.main:app \
        -w 1 \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:${PORT:-80}
else
    # --- MODO DESARROLLO (o cualquier otro) ---
    echo "ENTRYPOINT: Iniciando Uvicorn para Desarrollo (con SSL local)..."
    # Este es el comando que tenías
    exec uvicorn backend.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --ssl-keyfile certs/localhost+4-key.pem \
        --ssl-certfile certs/localhost+4.pem
fi