from backend.db import models
from backend.schemas import  schemas 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select



async def get_categoria(db: AsyncSession, categoria_id: int):
    result = await db.execute(select(models.Categoria).filter(models.Categoria.id == categoria_id))
    return result.scalar_one_or_none()

async def get_categorias(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Busca un todos los categorias"""
    result = await db.execute(select(models.Categoria).offset(skip).limit(limit))
    return result.scalars().all()


async def create_categoria(db: AsyncSession, categoria: schemas.CategoriaCreate):
    """Crea un nuevo categoria."""

    db_categoria = models.categoria(**categoria.model_dump())
    
    db.add(db_categoria)
    await db.commit()
    await db.refresh(db_categoria)
    return db_categoria

async def update_categoria(db: AsyncSession, categoria_id: int, categoria_update: schemas.CategoriaCreate):
    '''update categoria'''
    db_categoria = await get_categoria(db, categoria_id==categoria_id )
    if not db_categoria:
        return None 


    
    for key, value in categoria_update.model_dump(exclude_unset=True).items():
        setattr(db_categoria, key, value)

    db.add(db_categoria) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_categoria) # Refresca la instancia con los nuevos datos de la DB
    return db_categoria



async def delete_categoria(db: AsyncSession, categoria_id: int):
    """
    elimina categoria
    """
    # Busca la factura que se va a eliminar
    db_categoria = await get_categoria(db, factura_id=categoria_id)
    if not db_categoria:
        return None # Retorna None si no se encontró

    await db.delete(db_categoria) 
    await db.commit() 
    return db_categoria 
