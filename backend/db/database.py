# database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Reemplaza con tus credenciales de PostgreSQL
from dotenv import load_dotenv 

load_dotenv()
import os

DATABASE_URL=os.getenv("ASYNC_DATABASE")



# Crea el motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=False)

# Crea una fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Base para los modelos declarativos de SQLAlchemy
Base = declarative_base()
