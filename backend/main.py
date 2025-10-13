# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 👈 1. Importa CORSMiddleware

from backend.api import facturas_manuales, facturas_electronicas,auth,proyectos,usuarios,categorias,empresas,batch
import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
app = FastAPI()


# 🚩🚩🚩🚩🚩 atencion al procesar en pdf la factura si tiene una como ej 4,390.00 se omite el 4 gran error 
origins = "*"
# 👇 3. Añade el middleware a tu aplicación.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite los orígenes especificados
    allow_credentials=True, # Permite cookies/credenciales
    allow_methods=["*"],    # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permite todas las cabeceras
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
    return {"message": "Bienvenido a la API de Facturas"}
