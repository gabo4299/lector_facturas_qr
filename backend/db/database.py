# database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
# Reemplaza con tus credenciales de PostgreSQL
from dotenv import load_dotenv 

load_dotenv()
import os

DATABASE_URL=os.getenv("ASYNC_DATABASE")



# Crea el motor asíncrono
engine = create_async_engine(DATABASE_URL,
                             connect_args={"statement_cache_size": 0,},
                            #  execution_options={"postgresql_prepare_threshold": 0,},
                            #  pool_pre_ping=True,
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
