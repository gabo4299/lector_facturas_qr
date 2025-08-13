# main.py
from fastapi import FastAPI
from backend.api import facturas_manuales, facturas_electronicas
app = FastAPI()

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
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Facturas"}
