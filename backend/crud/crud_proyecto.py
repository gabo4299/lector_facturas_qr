from backend.db import models
from backend.schemas import  schemas 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_proyecto(db: AsyncSession, proyecto_id: int):
    result = await db.execute(select(models.Proyecto).filter(models.Proyecto.id == proyecto_id))
    return result.scalar_one_or_none()

async def get_proyectos(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Busca un todos los proyectos"""
    result = await db.execute(select(models.Proyecto).offset(skip).limit(limit))
    return result.scalars().all()


async def create_proyecto(db: AsyncSession, proyecto: schemas.ProyectoCreate):
    """Crea un nuevo proyecto."""

    db_user = models.Proyecto(**proyecto.model_dump())
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
async def update_proyecto(db: AsyncSession, proyecto_id: int, proyecto_update: schemas.ProyectoCreate):
    '''update proyecto'''
    db_proyecto = await get_proyecto(db, proyecto_id==proyecto_id )
    if not db_proyecto:
        return None 


    
    for key, value in proyecto_update.model_dump(exclude_unset=True).items():
        setattr(db_proyecto, key, value)

    db.add(db_proyecto) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_proyecto) # Refresca la instancia con los nuevos datos de la DB
    return db_proyecto



async def delete_proyecto(db: AsyncSession, proyecto_id: int):
    """
    elimina proyecto
    """
    # Busca la factura que se va a eliminar
    db_proyecto = await get_proyecto(db, factura_id=proyecto_id)
    if not db_proyecto:
        return None # Retorna None si no se encontró

    await db.delete(db_proyecto) 
    await db.commit() 
    return db_proyecto 
