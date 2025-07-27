from backend.db import models
from backend.schemas import  schemas 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select



from backend.db import models
from backend.schemas import  schemas 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select



async def get_empresa(db: AsyncSession, empresa_id: int):
    result = await db.execute(select(models.Empresa).filter(models.Empresa.id == empresa_id))
    return result.scalar_one_or_none()

async def get_empresas(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Busca un todos los empresas"""
    result = await db.execute(select(models.Empresa).offset(skip).limit(limit))
    return result.scalars().all()


async def create_empresa(db: AsyncSession, empresa: schemas.EmpresaCreate):
    """Crea un nuevo empresa."""

    db_empresa = models.empresa(**empresa.model_dump())
    
    db.add(db_empresa)
    await db.commit()
    await db.refresh(db_empresa)
    return db_empresa

async def update_empresa(db: AsyncSession, empresa_id: int, empresa_update: schemas.EmpresaCreate):
    '''update empresa'''
    db_empresa = await get_empresa(db, empresa_id==empresa_id )
    if not db_empresa:
        return None 


    
    for key, value in empresa_update.model_dump(exclude_unset=True).items():
        setattr(db_empresa, key, value)

    db.add(db_empresa) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_empresa) # Refresca la instancia con los nuevos datos de la DB
    return db_empresa



async def delete_empresa(db: AsyncSession, empresa_id: int):
    """
    elimina empresa
    """
    # Busca la factura que se va a eliminar
    db_empresa = await get_empresa(db, factura_id=empresa_id)
    if not db_empresa:
        return None # Retorna None si no se encontró

    await db.delete(db_empresa) 
    await db.commit() 
    return db_empresa 