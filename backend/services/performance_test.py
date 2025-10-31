import asyncio
import sys
import os
import time
from pathlib import Path

from backend.schemas import schemas

# --- Configuración del Path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from sqlalchemy.ext.asyncio import AsyncSession
# --- Importaciones de tu aplicación ---
from backend.db.database import AsyncSessionLocal
from backend.crud import (
    crud_proyecto
)
from sqlalchemy import text

# --- FUNCIÓN DE PRUEBA: LA "ANTIGUA FORMA" ---
async def get_full_resume_old_way(db: AsyncSession, proyecto_id: int):
    """Simula la forma ineficiente, con múltiples llamadas secuenciales."""
    proyecto_obj = await crud_proyecto.get_proyecto(db, proyecto_id=proyecto_id)
    if not proyecto_obj: return None

    # Múltiples viajes de ida y vuelta a la base de datos
    suma_total = await crud_proyecto.get_suma_total_proyecto(db, proyecto_id=proyecto_obj.id)
    suma_facturas_manuales = await crud_proyecto.get_suma_manuales_proyecto(db, proyecto_id=proyecto_obj.id)
    suma_facturas_electronicas = await crud_proyecto.get_suma_electronicas_proyecto(db, proyecto_id=proyecto_obj.id)
    count_manuales=await crud_proyecto.get_count_facturas_manuales(db, proyecto_id=proyecto_obj.id)
    count_electronicas=await crud_proyecto.get_count_facturas_electronicas(db, proyecto_id=proyecto_obj.id)
    resumen_batches = await crud_proyecto.get_resumen_batches_por_proyecto(db, proyecto_id=proyecto_obj.id)
    resumen_categorias = await crud_proyecto.get_resumen_categoria_por_proyecto(db, proyecto_id=proyecto_obj.id)
    resumen_empresas= await crud_proyecto.get_resumen_empresa_por_proyecto(db, proyecto_id=proyecto_obj.id)
    proyecto_data = schemas.Proyecto.model_validate(proyecto_obj).model_dump()

    
    return {"proyecto_nombre": proyecto_obj.nombre, "suma_total": suma_total}


# --- FUNCIÓN DE PRUEBA: LA "NUEVA FORMA" ---
async def get_full_resume_new_way(db: AsyncSession, proyecto_id: int):
    """Llama a la nueva función optimizada."""
    return await crud_proyecto.get_proyecto_full_resume(db, proyecto_id=proyecto_id)


# --- SCRIPT PRINCIPAL ---
async def main():
    """
    Ejecuta ambas funciones y compara sus tiempos de ejecución.
    """
    # --- CONFIGURACIÓN ---
    # Pon aquí el ID de un proyecto que tenga bastantes facturas para ver la diferencia
    PROYECTO_ID_DE_PRUEBA = 14 
    
    print("--- Iniciando prueba de rendimiento ---")
    async with AsyncSessionLocal() as db:
        try:
            # "Calentamiento": Hacemos una consulta simple para establecer la conexión
            # y que no afecte a la primera medición.
            await db.execute(text("SELECT 1"))
            print(f"Probando con Proyecto ID: {PROYECTO_ID_DE_PRUEBA}\n")

            # --- Medir la FORMA ANTIGUA ---
            print("Midiendo la forma antigua (múltiples consultas)...")
            start_old = time.perf_counter()
            resultado_old = await get_full_resume_old_way(db, proyecto_id=PROYECTO_ID_DE_PRUEBA)
            end_old = time.perf_counter()
            duration_old = (end_old - start_old) * 1000
            if not resultado_old:
                print("El proyecto no fue encontrado. Abortando.")
                return
            print(f"  -> Tiempo de ejecución: {duration_old:.2f} ms\n")

            # --- Medir la FORMA NUEVA ---
            print("Midiendo la forma nueva (consulta optimizada)...")
            start_new = time.perf_counter()
            resultado_new = await get_full_resume_new_way(db, proyecto_id=PROYECTO_ID_DE_PRUEBA)
            end_new = time.perf_counter()
            duration_new = (end_new - start_new) * 1000
            print(f"  -> Tiempo de ejecución: {duration_new:.2f} ms\n")

            # --- Conclusión ---
            print("--- Resultados de la Comparación ---")
            print(f"Forma Antigua: {duration_old:.2f} ms")
            print(f"Forma Nueva:   {duration_new:.2f} ms")
            if duration_new > 0:
                mejora = duration_old / duration_new
                print(f"\n✅ La nueva forma es ~{mejora:.1f} veces más rápida.")

        except Exception as e:
            print(f"\n❌ Ocurrió un error durante la prueba: {e}")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(main())