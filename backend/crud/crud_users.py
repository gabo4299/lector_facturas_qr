# ... (importaciones existentes)
import math
import os
from sqlalchemy import asc, desc, func, or_
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
    db_user = models.User(email=user.email, password=hashed_password,name=user.name)
    
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


async def get_users_paginacion(db: AsyncSession,
                                   search:str=None,page:int=1,size:int=10,
                                   sort_by: str = "id", # Por defecto ordena por id
                                    sort_order: str = "asc"):
    """Busca un todos los categorias"""
    sortable_columns = {
        "id": models.User.id,
        "name": models.User.name,
        "email": models.User.email,
        
    }
    
    # Si el sort_by no es válido, usa 'id' por defecto
    sort_column = sortable_columns.get(sort_by, models.User.id)

    # 2. Determina la dirección del ordenamiento
    order_function = desc if sort_order == "desc" else asc
    query = select(models.User).order_by(order_function(sort_column))
    if search:
        query = query.where(
            or_(
                models.User.name.ilike(f"%{search}%"), # ilike es case-insensitive
                models.User.email.ilike(f"%{search}%")
            )
        )
    count_statement = select(func.count()).select_from(query.subquery())
    total_items_result = await db.execute(count_statement)
    total_items = total_items_result.scalar_one()
    if total_items == 0:
        return { "items": [], "total": 0, "page": page, "size": size, "pages": 0 }
    total_pages = math.ceil(total_items / size)

    # 5. Aplica la paginación (offset y limit)
    offset = (page - 1) * size
    paginated_statement = query.offset(offset).limit(size)

    # 6. Ejecuta la consulta principal y obtén los resultados
    result = await db.execute(paginated_statement)
    items = result.scalars().all() # 👈 .scalars().all() para obtener la lista de objetos

    # 7. Devuelve la respuesta estructurada
    return {
        "items": items,
        "total": total_items,
        "page": page,
        "size": size,
        "pages": total_pages,
    }

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

async def get_or_create_user_by_google(db: AsyncSession, google_user_info: dict) -> models.User:
    """
    Busca un usuario por su email. Si no existe, lo crea a partir de la info de Google.
    """
    user = await get_user_by_email(db, email=google_user_info['email'])
    
    if user:
        # Si el usuario ya existe, simplemente lo devolvemos.
        # Aquí podrías añadir lógica para actualizar su nombre o foto si ha cambiado en Google.
        return user

    # Si el usuario no existe, lo creamos.
    print(f"INFO: Creando nuevo usuario para {google_user_info['email']} desde Google.")
    
    # Creamos una contraseña aleatoria y segura, ya que este usuario no la usará.
    # El inicio de sesión siempre será a través de Google.
    random_password = security.get_password_hash(os.urandom(16).hex())

    new_user_data = schemas.UserCreate(
        email=google_user_info['email'],
        password=random_password, # ¡Importante! No se usa, pero el modelo lo requiere.
        name=google_user_info.get('name', 'Usuario de Google')
    )
    
    # Reutilizamos la función de creación de usuario que ya hashea la contraseña
    # (aunque en este caso ya está hasheada, la función es la correcta).
    db_user = models.User(
        email=new_user_data.email, 
        password=new_user_data.password, 
        name=new_user_data.name
    )
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