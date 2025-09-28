from backend.db import models
from backend.schemas import  schemas 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select



async def get_batch(db: AsyncSession, batch_id: int):
    result = await db.execute(select(models.Batch).filter(models.Batch.id == batch_id))
    return result.scalar_one_or_none()

async def get_batchs(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Busca un todos los batchs"""
    result = await db.execute(select(models.Batch).offset(skip).limit(limit))
    return result.scalars().all()


async def create_batch(db: AsyncSession, batch: schemas.BatchCreate):
    """Crea un nuevo batch."""

    db_batch = models.Batch(**batch.model_dump(exclude_unset=True))
    
    db.add(db_batch)
    await db.commit()
    await db.refresh(db_batch)
    return db_batch

async def update_batch(db: AsyncSession, batch_id: int, batch_update: schemas.BatchBase):
    '''update batch'''
    db_batch = await get_batch(db, batch_id=batch_id )
    if not db_batch:
        return None 


    
    for key, value in batch_update.model_dump(exclude_unset=True).items():
        setattr(db_batch, key, value)

    db.add(db_batch) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_batch) # Refresca la instancia con los nuevos datos de la DB
    return db_batch



async def delete_batch(db: AsyncSession, batch_id: int):
    """
    elimina batch
    """
    # Busca la factura que se va a eliminar
    db_batch = await get_batch(db, factura_id=batch_id)
    if not db_batch:
        return None # Retorna None si no se encontró

    await db.delete(db_batch) 
    await db.commit() 
    return db_batch 


async def get_batch_by_name_and_proyect(db:AsyncSession, name:str,proyect_id:int):
    result = await db.execute(select(models.Batch).filter(models.Batch.nombre == name,models.Batch.proyecto_id==proyect_id))
    return result.scalar_one_or_none()


async def get_or_create_batch(db: AsyncSession,proyect_id:int, name: str,description:str="") -> models.Batch:
    """
    Busca una empresa por su NIT. Si no existe, la crea.
    """
    db_batch = await get_batch_by_name_and_proyect(db, name=name,proyect_id=proyect_id)
    
    if db_batch:
        return db_batch

    # Si no existe, la creamos
   
    
    nueva_batch = models.Batch(
        descripcion=description,
        nombre=name,
        proyecto_id=proyect_id
    )
    db.add(nueva_batch)
    await db.commit()
    await db.refresh(nueva_batch)
    return nueva_batch