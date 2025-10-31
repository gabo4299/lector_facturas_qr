import asyncio
import time
import os
import sys
from pathlib import Path
import re

from backend.db import models

# --- Configuración del Path ---
# Añadimos la raíz del proyecto al path para que el script
# pueda encontrar el paquete 'backend'.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# --- Importaciones de tu aplicación ---
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import NullPool, func, select, text

# --- Función principal de prueba ---
async def test_database_connection():
    """
    Intenta conectarse a la base de datos y ejecutar una consulta simple.
    """
    print("--- Iniciando prueba de conexión a la base de datos ---")
    
    # 1. Cargar las variables de entorno desde el archivo .env
    print("Cargando variables de entorno desde el archivo .env...")
    # load_dotenv(os.path.join(project_root, '.env'))
    load_dotenv()
    
    db_url = os.getenv("ASYNC_DATABASE")
    
    if not db_url:
        print("❌ ERROR: La variable de entorno 'DATABASE_URL' no está definida en tu archivo .env.")
        return

    # Ofuscar la contraseña para no mostrarla en la consola
    safe_url = re.sub(r":([^@]+)@", r":*****@", db_url)
    print(f"Intentando conectar a: {safe_url}")

    
        # 2. Crear el motor de SQLAlchemy
    try:
        engine = create_async_engine(db_url,
                                     pool_size=10,
                                     max_overflow=5,
    
                                    # Esta es tu red de seguridad:
                                    # Antes de usar una conexión del pool, SQLAlchemy hará un 'ping' (SELECT 1).
                                    # Si PgBouncer la cerró, la reemplazará automáticamente.
                                    pool_pre_ping=True,
                                    
                                    # Esta es tu optimización:
                                    # Cierra y reemplaza proactivamente cualquier conexión que tenga más de 5 minutos.
                                    pool_recycle=300)

        async with engine.connect() as connection:
            # --- PRUEBA 1: Latencia de Conexión (Round-trip) ---
            print("\n[Paso 1/2] Probando latencia de conexión básica...")
            
            start_latency = time.perf_counter()
            result_latency = await connection.execute(text("SELECT 1"))
            value = result_latency.scalar_one()
            end_latency = time.perf_counter()
            
            latency_ms = (end_latency - start_latency) * 1000

            if value != 1:
                print(f"⚠️ La conexión funcionó, pero la respuesta fue inesperada: {value}")
                return
            
            print(f"✅ Conexión básica exitosa. Latencia de red (ida y vuelta): {latency_ms:.2f} ms")

            # --- PRUEBA 2: Rendimiento de una Consulta Real ---
            print("\n[Paso 2/2] Ejecutando consulta simple (contando usuarios)...")
            
            start_query = time.perf_counter()
            # Creamos una consulta para contar todos los usuarios
            query = select(func.count()).select_from(models.User)
            result_query = await connection.execute(query)
            user_count = result_query.scalar_one()
            end_query = time.perf_counter()

            query_ms = (end_query - start_query) * 1000

            print(f"✅ Consulta ejecutada exitosamente. Se encontraron {user_count} usuarios.")
            print(f"   -> Tiempo de ejecución de la consulta: {query_ms:.2f} ms")
            
            print(f"\n--- Resumen ---")
            print(f"Latencia de Red: {latency_ms:.2f} ms")
            print(f"Tiempo de Consulta: {query_ms:.2f} ms")
            print(f"Tiempo Total (aprox.): {(latency_ms + query_ms):.2f} ms")
        
    except Exception as e:
        print("\n❌ ¡Falló la prueba!")
        print (e)
        # ... (tu manejo de errores existente) ...
    
    finally:
        if 'engine' in locals():
            await engine.dispose()
            print("\nRecursos del motor liberados.")


# --- Punto de entrada para ejecutar el script ---
if __name__ == "__main__":
    asyncio.run(test_database_connection())