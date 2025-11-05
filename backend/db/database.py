# database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
# Reemplaza con tus credenciales de PostgreSQL
from dotenv import load_dotenv 
from backend.config import settings
load_dotenv()
import os

DATABASE_URL=os.getenv("ASYNC_DATABASE")

connect_args = {}

if settings.is_production:
    print("Modo Producción: Activando SSL y statement_cache_size=0")
    connect_args["ssl"] = True
    # Esto también es para PgBouncer (Neon/Supabase) en producción
    connect_args["statement_cache_size"] = 0 
    # otras opcines 
    #  execution_options={"postgresql_prepare_threshold": 0,},
    #  pool_pre_ping=True,
    # --- AJUSTES PARA SUPABASE (PgBouncer) ---
    # poolclass=NullPool  # Opción 1: La más simple y segura.
    
    # Opción 2: Un pool pequeño y bien configurado (Recomendado)
    # pool_size=10,             # Mantén un número bajo de conexiones "favoritas".
    # max_overflow=5,          # No permitas crear más conexiones que las del pool.
    # pool_recycle=300,        # Recicla/reemplaza conexiones cada 5 minutos (300s).
    # pool_pre_ping=True,       # Antes de usar una conexión, haz un "ping" para ver si sigue viva.
else:
    print("Modo Desarrollo: Sin SSL")
    connect_args["statement_cache_size"] = 0 
    # No añades nada, o pones configs específicas de desarrollo si las tuvieras

# Crea el motor asíncrono
engine = create_async_engine(DATABASE_URL,
                             connect_args=connect_args,
                             echo=False,)

# Crea una fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# AsyncSessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
#     class_=AsyncSession,
# )

# Base para los modelos declarativos de SQLAlchemy
Base = declarative_base()
