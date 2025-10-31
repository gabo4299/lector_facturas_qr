import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
# --- Configuración del Path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# --- Importaciones de tu aplicación ---
from backend.db.database import AsyncSessionLocal
from backend.db import models
from sqlalchemy.future import select

# --- CONFIGURACIÓN DE LA FECHA ---
# Define una fecha de inicio base para tus facturas más antiguas.
# ¡Puedes cambiar esta fecha por la que tú quieras!
BASE_START_DATE = datetime(2025, 9, 1, tzinfo=timezone.utc)

# Minutos a añadir por cada ID. Si tienes muchas facturas, puedes usar segundos.
MINUTES_PER_ID = 5 

async def backfill_table(model):
    """
    Rellena la 'fecha_creacion' para todas las filas de un modelo
    que la tengan en NULL, procesando en lotes.
    """
    print(f"\n--- Iniciando backfill para la tabla: {model.__tablename__} ---")
    BATCH_SIZE = 100
    offset = 0
    total_actualizadas = 0

    while True:
        # 1. Creamos una sesión NUEVA y FRESCA para cada lote.
        async with AsyncSessionLocal() as batch_db:
            try:
                # 2. Buscamos un lote de facturas que AÚN NO TENGAN fecha_creacion
                query = select(model).order_by(model.id).offset(offset).limit(BATCH_SIZE)
                
                result = await batch_db.execute(query)
                facturas_lote = result.scalars().all()
                
                # 3. Si el lote está vacío, hemos terminado con esta tabla
                if not facturas_lote:
                    print(f"No hay más facturas que actualizar en {model.__tablename__}.")
                    break

                print(f"Procesando lote de {len(facturas_lote)} facturas...")

                # 4. Iteramos y asignamos la nueva fecha
                for factura in facturas_lote:
                    # Lógica de fecha: Base + (ID * N minutos)
                    # Esto asegura que un ID más bajo tenga una fecha más antigua.
                    offset_minutos = factura.id * MINUTES_PER_ID
                    nueva_fecha = BASE_START_DATE + timedelta(minutes=offset_minutos)
                    factura.fecha_creacion = nueva_fecha
                
                # 5. Guardamos los cambios de ESTE LOTE
                await batch_db.commit()
                total_actualizadas += len(facturas_lote)
                print(f"Lote guardado exitosamente.")
                
                offset += BATCH_SIZE

            except Exception as e:
                print(f"\n❌ Ocurrió un error en el lote: {e}")
                print("Haciendo rollback de este lote y deteniendo el script.")
                await batch_db.rollback()
                break # Detiene el script si un lote falla

    return total_actualizadas

async def main():
    print("Iniciando script de backfill de fechas...")
    try:
        total_m = await backfill_table( models.FacturaManual)
        total_e = await backfill_table( models.FacturaElectronica)
        print("\n✅ ¡Backfill de fechas completado!")
        print(f"Facturas Manuales actualizadas: {total_m}")
        print(f"Facturas Electrónicas actualizadas: {total_e}")
    except Exception as e:
        print(f"\n❌ Ocurrió un error general: {e}")

if __name__ == "__main__":
    asyncio.run(main())