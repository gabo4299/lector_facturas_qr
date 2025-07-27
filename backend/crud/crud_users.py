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


async def get_user(db: AsyncSession, user_id: int):
    """Busca un usuario por su ID."""
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Obtiene una lista de todos los usuarios."""
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def update_user(db: AsyncSession, user_id: int, user_update_data: schemas.UserUpdate):
    """Actualiza los datos de un usuario."""
    db_user = await get_user(db, user_id=user_id)
    if not db_user:
        return None

    update_data = user_update_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    """Elimina un usuario."""
    db_user = await get_user(db, user_id=user_id)
    if not db_user:
        return None

    await db.delete(db_user)
    await db.commit()
    return db_user