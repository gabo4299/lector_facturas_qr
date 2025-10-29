import math
from sqlalchemy import asc, desc, func, or_
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

    db_categoria = models.Categoria(**categoria.model_dump())
    
    db.add(db_categoria)
    await db.commit()
    await db.refresh(db_categoria)
    return db_categoria

async def update_categoria(db: AsyncSession, categoria_id: int, categoria_update: schemas.CategoriaCreate):
    '''update categoria'''
    db_categoria = await get_categoria(db, categoria_id=categoria_id )
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
    db_categoria = await get_categoria(db, categoria_id=categoria_id)
    if not db_categoria:
        return None # Retorna None si no se encontró

    await db.delete(db_categoria) 
    await db.commit() 
    return db_categoria 


async def get_categoria_by_name(db:AsyncSession, name:str):
    result = await db.execute(select(models.Categoria).filter(models.Categoria.nombre == name))
    return result.scalar_one_or_none()


async def get_or_create_categoria(db: AsyncSession, name: str,description:str="") -> models.Categoria:
    """
    Busca una categoria por su NIT. Si no existe, la crea.
    """
    db_categoria = await get_categoria_by_name(db, name=name)
    
    if db_categoria:
        return db_categoria

    # Si no existe, la creamos
   
    
    nueva_categoria = models.Categoria(
        descripcion=description,
        nombre=name
    )
    db.add(nueva_categoria)
    await db.commit()
    await db.refresh(nueva_categoria)
    return nueva_categoria


async def get_categorias_paginacion(db: AsyncSession,
                                   search:str=None,page:int=1,size:int=10,
                                   sort_by: str = "id", # Por defecto ordena por id
                                    sort_order: str = "asc"):
    """Busca un todos los categorias"""
    sortable_columns = {
        "id": models.Categoria.id,
        "nombre": models.Categoria.nombre,
        "descripcion": models.Categoria.descripcion,
    }
    
    # Si el sort_by no es válido, usa 'id' por defecto
    sort_column = sortable_columns.get(sort_by, models.Categoria.id)

    # 2. Determina la dirección del ordenamiento
    order_function = desc if sort_order == "desc" else asc
    query = select(models.Categoria).order_by(order_function(sort_column))
    if search:
        query = query.where(
            or_(
                models.Categoria.nombre.ilike(f"%{search}%"), # ilike es case-insensitive
                models.Categoria.descripcion.ilike(f"%{search}%")
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
