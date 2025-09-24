# main.py
from fastapi import FastAPI
from backend.api import facturas_manuales, facturas_electronicas,auth,proyectos,usuarios,categorias,empresas
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

app.include_router(
    facturas_electronicas.router,
    prefix="/facturas", # Añade un prefijo a todas las rutas del router
    tags=["Facturas Electronicas"]      # Agrupa estos endpoints en la documentación
)
app.include_router(
    auth.router,
    prefix="/auth", # Añade un prefijo a todas las rutas del router
    tags=["autentificacion"]      # Agrupa estos endpoints en la documentación
)

app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(proyectos.router, prefix="/proyectos", tags=["Proyectos"])
app.include_router(categorias.router, prefix="/categorias", tags=["Categorias"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Facturas"}
