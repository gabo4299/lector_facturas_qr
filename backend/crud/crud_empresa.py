import math
from sqlalchemy import asc, desc, func, or_
from backend.db import models
from backend.schemas import  schemas 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select



from backend.db import models
from backend.schemas import  schemas 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_empresa_by_nit(db: AsyncSession, nit: str):
    """Busca una empresa por su NIT."""
    result = await db.execute(select(models.Empresa).filter(models.Empresa.nit == nit))
    return result.scalar_one_or_none()

async def get_or_create_empresa(db: AsyncSession, nit: str, nombre: str = None,rubro:str=None) -> models.Empresa:
    """
    Busca una empresa por su NIT. Si no existe, la crea.
    """
    db_empresa = await get_empresa_by_nit(db, nit=nit)
    
    if db_empresa:
        return db_empresa

    # Si no existe, la creamos
    nombre_empresa = nombre or f"Empresa con NIT {nit}"
    
    nueva_empresa = models.Empresa(
        nit=nit,
        nombre=nombre_empresa,
        rubro=rubro
    )
    db.add(nueva_empresa)
    await db.commit()
    await db.refresh(nueva_empresa)
    return nueva_empresa

async def get_empresa(db: AsyncSession, empresa_id: int):
    result = await db.execute(select(models.Empresa).filter(models.Empresa.id == empresa_id))
    return result.scalar_one_or_none()

async def get_empresas(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Busca un todos los empresas"""
    result = await db.execute(select(models.Empresa).offset(skip).limit(limit))
    return result.scalars().all()

async def get_empresas_paginacion(db: AsyncSession,
                                   search:str=None,page:int=1,size:int=10,
                                   sort_by: str = "id", # Por defecto ordena por id
                                    sort_order: str = "asc"):
    """Busca un todos los empresas"""
    sortable_columns = {
        "id": models.Empresa.id,
        "nombre": models.Empresa.nombre,
        "nit": models.Empresa.nit,
        "rubro": models.Empresa.rubro,
    }
    
    # Si el sort_by no es válido, usa 'id' por defecto
    sort_column = sortable_columns.get(sort_by, models.Empresa.id)

    # 2. Determina la dirección del ordenamiento
    order_function = desc if sort_order == "desc" else asc
    query = select(models.Empresa).order_by(order_function(sort_column))
    if search:
        query = query.where(
            or_(
                models.Empresa.nombre.ilike(f"%{search}%"), # ilike es case-insensitive
                models.Empresa.nit.ilike(f"%{search}%"),
                models.Empresa.rubro.ilike(f"%{search}%")
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

async def create_empresa(db: AsyncSession, empresa: schemas.EmpresaCreate):
    """Crea un nuevo empresa."""

    db_empresa = models.Empresa(**empresa.model_dump())
    
    db.add(db_empresa)
    await db.commit()
    await db.refresh(db_empresa)
    return db_empresa

async def update_empresa(db: AsyncSession, empresa_id: int, empresa_update: schemas.EmpresaUpdate):
    '''update empresa'''
    db_empresa = await get_empresa(db, empresa_id=empresa_id )
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
    db_empresa = await get_empresa(db, empresa_id=empresa_id)
    if not db_empresa:
        return None # Retorna None si no se encontró

    await db.delete(db_empresa) 
    await db.commit() 
    return db_empresa 