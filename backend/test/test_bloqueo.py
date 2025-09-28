 
import asyncio
import sys
import os
from pathlib import Path

# --- Configuración del Path ---
# Añadimos la raíz del proyecto al path para que el script
# pueda encontrar el paquete 'backend'.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# --- Importaciones de tu aplicación ---
from backend.db.database import engine 
from sqlalchemy.ext.asyncio import AsyncSession
from backend.crud import crud_facturas_electronicas

# --- Función principal de prueba ---
async def main():
    """
    Orquesta la prueba: crea una sesión de DB, llama a la función CRUD y muestra el resultado.
    """
    print("--- Iniciando script de prueba ---")
    
    # ID del proyecto que quieres probar
    PROYECTO_ID_DE_PRUEBA = 12
    
    # 1. Crea una sesión de base de datos manualmente.
    #    'async with' asegura que la sesión se cierre correctamente.
    print("Creando sesión de base de datos...")
    # 1. Conéctate directamente al motor de la base de datos
    async with engine.connect() as connection:
        # 2. Inicia una transacción principal que NUNCA se guardará
        await connection.begin()
        
        # 3. Crea una sesión de DB que está vinculada a esta transacción específica
        async with AsyncSession(bind=connection) as db:
            print("Sesión de prueba iniciada dentro de una transacción...")
            try:
                # 4. Ejecuta tu lógica de prueba aquí.
                #    Cualquier 'db.commit()' dentro de tus funciones CRUD
                #    solo guardará en un "savepoint" de esta transacción principal.
                facturas_bloqueadas = await crud_facturas_electronicas.obtener_y_bloquear_facturas_para_procesar(
                    db=db, proyecto_id=PROYECTO_ID_DE_PRUEBA
                )

                if not facturas_bloqueadas:
                    print("\nResultado: No se encontraron facturas para procesar.")
                else:
                    print(f"\nResultado: Se han 'bloqueado' temporalmente {len(facturas_bloqueadas)} facturas.")
                    for f in facturas_bloqueadas:
                        print(f"  - ID: {f.id}, Estado ahora: '{f.status}'")

            finally:
                # 5. ¡Paso clave! Deshacer la transacción principal.
                #    Esto revierte TODOS los cambios, incluyendo cualquier 'commit' interno.
                print("\nRealizando ROLLBACK de la transacción principal...")
                await connection.rollback()
    print("--- Script de prueba finalizado ---")


# --- Punto de entrada para ejecutar el script ---
if __name__ == "__main__":
    # asyncio.run() ejecuta la función asíncrona 'main'.
    asyncio.run(main())
