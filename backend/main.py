# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 👈 1. Importa CORSMiddleware

from backend.api import facturas_manuales, facturas_electronicas,auth,proyectos,usuarios,categorias,empresas,batch
import sys
import asyncio
import datetime
from backend.crud import crud_categoria
from backend.db.database import AsyncSessionLocal
from backend.config  import app_state
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())



@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- CÓDIGO QUE SE EJECUTA AL INICIAR EL SERVIDOR ---
    print("INFO: Iniciando servidor, cargando configuración inicial...")
    db = AsyncSessionLocal()
    try:
        # Buscamos la categoría 'Invalidas' y guardamos su ID en nuestro estado
        categoria_invalidas = await crud_categoria.get_categoria_by_name(db, "Invalidas")
        if categoria_invalidas:
            app_state["invalidas_cat_id"] = categoria_invalidas.id
            print(f"INFO: ID de categoría 'Invalidas' cargado en caché: {app_state['invalidas_cat_id']}")
        else:
            app_state["invalidas_cat_id"] = -1 # Un valor que nunca coincidirá
            print("WARN: No se encontró la categoría 'Invalidas' en la base de datos.")
    finally:
        await db.close()
    
    yield # La aplicación se ejecuta aquí

    # --- CÓDIGO QUE SE EJECUTA AL APAGAR EL SERVIDOR ---
    print("INFO: Apagando servidor.")
    app_state.clear()

app = FastAPI(lifespan=lifespan)



# 🚩🚩🚩🚩🚩 atencion al procesar en pdf la factura si tiene una como ej 4,390.00 se omite el 4 gran error 
origins = "*"
# 👇 3. Añade el middleware a tu aplicación.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite los orígenes especificados
    allow_credentials=True, # Permite cookies/credenciales
    allow_methods=["*"],    # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permite todas las cabeceras
    expose_headers=["Content-Disposition"]
)
# Incluye el router de facturas en la aplicación principal
app.include_router(
    facturas_manuales.router,
    prefix="/facturas", # Añade un prefijo a todas las rutas del router
    tags=["Facturas"]      # Agrupa estos endpoints en la documentación
)

app.include_router(
    facturas_electronicas.router,
    prefix="/facturas", # Añade un prefijo a todas las rutas del router
    tags=["Facturas Electronicas"]      # Agrupa estos endpoints en la documentación
)

# app.include_router(
#     facturas_electronicas.router,
#     prefix="/facturas", # Añade un prefijo a todas las rutas del router
#     tags=["Facturas Electronicas"]      # Agrupa estos endpoints en la documentación
# )
app.include_router(
    auth.router,
    prefix="/auth", # Añade un prefijo a todas las rutas del router
    tags=["autentificacion"]      # Agrupa estos endpoints en la documentación
)

app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(proyectos.router, prefix="/proyectos", tags=["Proyectos"])
app.include_router(categorias.router, prefix="/categorias", tags=["Categorias"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
app.include_router(batch.router, prefix="/batch", tags=["Batches"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Facturas" ,"time":datetime.datetime.now()}
