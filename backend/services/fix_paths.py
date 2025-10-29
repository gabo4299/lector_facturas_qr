import asyncio
import sys
import os
from pathlib import Path

# Añadimos la raíz del proyecto al path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Importamos lo que necesitamos de nuestra app
from backend.db.database import AsyncSessionLocal
from backend.db import models
from sqlalchemy.future import select

async def main():
    print("--- Iniciando normalización de rutas de PDF (versión universal) ---")
    
    BATCH_SIZE = 50
    offset = 0
    total_corregidas = 0

    while True:
        async with AsyncSessionLocal() as db:
            try:
                query = select(models.FacturaElectronica).where(
                    models.FacturaElectronica.pdfIO.is_not(None)
                ).order_by(models.FacturaElectronica.id).offset(offset).limit(BATCH_SIZE)
                
                result = await db.execute(query)
                facturas_lote = result.scalars().all()
                
                if not facturas_lote:
                    print("No hay más facturas para procesar. Finalizando.")
                    break

                print(f"\nProcesando lote de {len(facturas_lote)} facturas...")
                
                for factura in facturas_lote:
                    path_antiguo = factura.pdfIO
                    path_nuevo = path_antiguo
                    
                    # --- LÓGICA DE NORMALIZACIÓN MEJORADA ---
                    # Buscamos la palabra 'backend' en cualquier parte de la ruta
                    if 'backend' in path_antiguo:
                        # 1. Divide la ruta en la primera aparición de 'backend'
                        #    y quédate con la parte de la derecha.
                        parte_relevante = path_antiguo.split('backend', 1)[1]
                        
                        # 2. Limpia cualquier separador ('\' o '/') que haya quedado al principio.
                        #    Ej: si teníamos '\data\...' ahora será 'data\...'.
                        parte_limpia = parte_relevante.lstrip('\\/')
                        
                        # 3. Reemplaza TODOS los separadores de Windows ('\') por separadores web ('/').
                        #    Ahora el resultado será 'data/facturas/...'
                        path_nuevo = parte_limpia.replace('\\', '/')
                    
                    # Comparamos si hubo un cambio para solo imprimir y modificar lo necesario
                    if path_nuevo != path_antiguo:
                        factura.pdfIO = path_nuevo
                        print(f"  - ID {factura.id}: '{path_antiguo}' -> '{path_nuevo}'")
                        total_corregidas += 1
                
                await db.commit()
                print(f"Lote guardado.")
                
                offset += len(facturas_lote)

            except Exception as e:
                print(f"\n❌ Ocurrió un error en el lote: {e}")
                await db.rollback()
                break

    print(f"\n✅ Normalización completada. Se han corregido un total de {total_corregidas} rutas.")


if __name__ == "__main__":
    asyncio.run(main())