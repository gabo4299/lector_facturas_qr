
from pathlib import Path


p = Path(__file__).resolve()

while p.name != 'backend' and p.parent != p:
    p = p.parent


if p.name == 'backend':
    backend_dir = p
    print(f"Directorio 'backend' encontrado en: {backend_dir}")
else:
    
    raise FileNotFoundError("No se pudo encontrar el directorio 'backend' subiendo desde la ubicación del script.")

app_state={}
BACKEND_DIR = backend_dir

# 3. Construimos la ruta a la carpeta de destino a partir de la ruta de 'backend'
FACTURAS_DIR = BACKEND_DIR / "data" / "facturas"

# 4. Nos aseguramos de que el directorio exista al iniciar la aplicación
print(f"Asegurando que el directorio de facturas exista en: {FACTURAS_DIR}")
FACTURAS_DIR.mkdir(parents=True, exist_ok=True) 

