# ... (importaciones existentes)
from backend.db import models
from backend.schemas import  schemas # Importa el nuevo módulo
from backend.services import  security # Importa el nuevo módulo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# --- CRUD para Usuarios ---

async def get_user_by_email(db: AsyncSession, email: str):
    """Busca un usuario por su email."""
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    """Crea un nuevo usuario y hashea su contraseña."""
    # Hasheamos la contraseña antes de guardarla
    hashed_password = security.get_password_hash(user.password)
    
    # Creamos el objeto del modelo de la DB, usando la contraseña hasheada
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


