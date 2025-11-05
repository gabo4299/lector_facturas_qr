
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
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


class Settings(BaseSettings):
    # Carga el archivo .env por defecto (para desarrollo)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # La variable "switch" que controla todo
    APP_ENV: str = "development" 
    
    # Configuraciones
    ALGORITHM:str
    GOOGLE_CLIENT_ID:str
    GOOGLE_CLIENT_SECRET:str
    GOOGLE_REDIRECT_URI:str
    ASYNC_DATABASE: str
    SYNC_DATABASE: str
    SECRET_KEY: str  # Importante para JWT, etc.
    GOOGLE_CLIENT_SECRET_PATH: str="client_secret.json"

    # Propiedades útiles
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

# Instancia única que se importará en toda tu app
settings = Settings()
