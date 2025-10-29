from collections import defaultdict
from datetime import datetime, time
import math
from sqlalchemy import and_, asc, desc, func, literal, or_, text, union_all
from sqlalchemy.orm import aliased
from backend.crud import crud_categoria,crud_batch
from backend.db import models
from backend.schemas import  schemas 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from sqlalchemy.orm import selectinload ,joinedload 



async def create_proyecto(db: AsyncSession,
                        proyecto: schemas.ProyectoCreate,
                        propietario_id: int):
    """Crea un nuevo proyecto."""

    db_proyecto = models.Proyecto(**proyecto.model_dump(), propietario_id=propietario_id)
    db.add(db_proyecto)
    
    # db.add(db_proyecto)
    await db.commit()
    await db.refresh(db_proyecto)
    asociacion_dueño = models.ProyectoUsuario(
        proyecto_id=db_proyecto.id,
        usuario_id=propietario_id,
        rol='dueño'
    )
    db.add(asociacion_dueño)
    await db.commit()
    await db.refresh(db_proyecto) # Refresca de nuevo para cargar la nueva asociación
    return await get_proyecto(db, proyecto_id=db_proyecto.id)



async def get_proyecto(db: AsyncSession, proyecto_id: int):
    query = select(models.Proyecto).options(
        # Usa joinedload para relaciones de uno (como el propietario)
        joinedload(models.Proyecto.propietario), 
        # Usa selectinload para relaciones de listas (de muchos)
        selectinload(models.Proyecto.asociaciones_usuario).joinedload(models.ProyectoUsuario.usuario),
        selectinload(models.Proyecto.batches)
    ).filter(models.Proyecto.id == proyecto_id)
    
    result = await db.execute(query)
    # unique() es importante cuando se usa joinedload para evitar filas duplicadas
    return result.unique().scalar_one_or_none()

async def get_asociacion_usuario_proyecto(db: AsyncSession, user_id: int, proyecto_id: int):
    query = select(models.ProyectoUsuario).options(
        joinedload(models.ProyectoUsuario.proyecto) # Carga el proyecto a la vez
    ).filter_by(usuario_id=user_id, proyecto_id=proyecto_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_proyecto_by_name(db: AsyncSession, proyecto_name: str):
    query = select(models.Proyecto).options(
        # Usa joinedload para relaciones de uno (como el propietario)
        joinedload(models.Proyecto.propietario), 
        # Usa selectinload para relaciones de listas (de muchos)
        selectinload(models.Proyecto.asociaciones_usuario).joinedload(models.ProyectoUsuario.usuario),
        selectinload(models.Proyecto.batches)
    ).filter(models.Proyecto.nombre == proyecto_name)
    
    result = await db.execute(query)
    # unique() es importante cuando se usa joinedload para evitar filas duplicadas
    return result.unique().scalar_one_or_none()

async def get_proyectos_by_user(db: AsyncSession, propietario_id: int, skip: int = 0, limit: int = 100):
    """Obtiene solo los proyectos que pertenecen a un usuario."""
    query = (
        select(models.Proyecto)
        .join(models.ProyectoUsuario, models.Proyecto.id == models.ProyectoUsuario.proyecto_id, isouter=True)
        .filter(
            # --- LA LÓGICA CLAVE ---
            or_(
                models.Proyecto.propietario_id == propietario_id,
                models.ProyectoUsuario.usuario_id == propietario_id
            )
        )
        # Las opciones de carga son cruciales para evitar errores de lazy loading
        .options(
            joinedload(models.Proyecto.propietario),
            selectinload(models.Proyecto.asociaciones_usuario).joinedload(models.ProyectoUsuario.usuario),
            selectinload(models.Proyecto.batches)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.unique().scalars().all()


async def get_proyectos_all(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Obtiene solo los proyectos que pertenecen a un usuario."""
    query = (
        select(models.Proyecto)
        .join(models.ProyectoUsuario, models.Proyecto.id == models.ProyectoUsuario.proyecto_id, isouter=True)
        
        # Las opciones de carga son cruciales para evitar errores de lazy loading
        .options(
            joinedload(models.Proyecto.propietario),
            selectinload(models.Proyecto.asociaciones_usuario).joinedload(models.ProyectoUsuario.usuario),
            selectinload(models.Proyecto.batches)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.unique().scalars().all()



async def get_proyectos_paginated_admin(db: AsyncSession,
                                   search:str=None,
                                   page:int=1,
                                   size:int=10,
                                   sort_by: str = "id", # Por defecto ordena por id
                                   sort_order: str = "asc"):
    """Busca un todos los proyectos"""
    manual_agg = (
        select(
            models.FacturaManual.proyecto_id,
            func.count(models.FacturaManual.id).label("count_manual"),
            func.sum(models.FacturaManual.monto_total).label("sum_manual")
        )
        .group_by(models.FacturaManual.proyecto_id)
        .subquery()
    )

    # Subconsulta para sumar y contar facturas electrónicas por proyecto
    electronica_agg = (
        select(
            models.FacturaElectronica.proyecto_id,
            func.count(models.FacturaElectronica.id).label("count_electronica"),
            func.sum(models.FacturaElectronica.monto_total).label("sum_electronica")
        )
        .group_by(models.FacturaElectronica.proyecto_id)
        .subquery()
    )

    # --- 2. Construcción de la consulta principal ---
    # Seleccionamos el modelo Proyecto y las columnas calculadas
    query = select(
        models.Proyecto,
        (
            func.coalesce(manual_agg.c.count_manual, 0) + 
            func.coalesce(electronica_agg.c.count_electronica, 0)
        ).label("total_facturas"),
        (
            func.coalesce(manual_agg.c.sum_manual, 0) + 
            func.coalesce(electronica_agg.c.sum_electronica, 0)
        ).label("suma_total_facturas")
    )

    # Unimos (LEFT JOIN) el proyecto con las subconsultas de agregación
    query = query.join_from(models.Proyecto, manual_agg, models.Proyecto.id == manual_agg.c.proyecto_id, isouter=True)
    query = query.join_from(models.Proyecto, electronica_agg, models.Proyecto.id == electronica_agg.c.proyecto_id, isouter=True)

    # --- 3. Aplicar filtros de búsqueda ---
    if search:
        query = query.where(
            or_(
                models.Proyecto.nombre.ilike(f"%{search}%"),
                models.Proyecto.nit_beneficiario.ilike(f"%{search}%")
            )
        )
    
    # --- 4. Contar el total de ítems para la paginación ---
    count_query = select(func.count()).select_from(query.subquery())
    total_items = (await db.execute(count_query)).scalar_one()
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0

    # --- 5. Aplicar ordenamiento dinámico ---
    sortable_columns = {
        "id": models.Proyecto.id,
        "nombre": models.Proyecto.nombre,
        "fecha_inicio": models.Proyecto.fecha_inicio,
        "total_facturas": "total_facturas", # Usamos el string del label
        "suma_total_facturas": "suma_total_facturas",
    }
    sort_column = sortable_columns.get(sort_by, models.Proyecto.id)
    
    # Si la columna es un string (una columna calculada), usamos text()
    order_expression = text(sort_column) if isinstance(sort_column, str) else sort_column
    order_function = desc if sort_order == "desc" else asc
    
    query = query.order_by(order_function(order_expression))

    # --- 6. Aplicar paginación ---
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # --- 7. Aplicar Eager Loading para las relaciones del Proyecto ---
    query = query.options(
        selectinload(models.Proyecto.asociaciones_usuario).joinedload(models.ProyectoUsuario.usuario),
        selectinload(models.Proyecto.batches)
    )

    # --- 8. Ejecutar y formatear la respuesta ---
    result = await db.execute(query)
    
    # El resultado ahora es una tupla: (Proyecto, total_facturas, suma_total_facturas)
    items = []
    for proyecto_obj, total_fact, suma_total in result.unique().all():
        proyecto_dict = schemas.Proyecto.model_validate(proyecto_obj).model_dump()
        proyecto_dict.update({
            "total_facturas": total_fact, 
            "suma_total_facturas": suma_total
        })
        proyecto_info_schema = schemas.ProyectoAdminInfo(**proyecto_dict)
        
        items.append(proyecto_info_schema)

    return {
        "items": items,
        "total": total_items,
        "page": page,
        "size": size,
        "pages": total_pages,
    }


async def update_proyecto(
    db: AsyncSession, 
    db_proyecto: models.Proyecto, # Recibe el objeto existente de la DB
    proyecto_update: schemas.ProyectoUpdate
) -> models.Proyecto:
    """
    Actualiza un proyecto en la base de datos con datos de un schema ProyectoUpdate.
    """
    # model_dump(exclude_unset=True) crea un diccionario solo con los campos
    # que el cliente realmente envió en la petición.
    update_data = proyecto_update.model_dump(exclude_unset=True)
    
    # Itera sobre los datos enviados y actualiza los atributos del objeto SQLAlchemy.
    for key, value in update_data.items():
        setattr(db_proyecto, key, value)

    db.add(db_proyecto) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_proyecto) # Refresca la instancia con los nuevos datos de la DB
    
    return await get_proyecto(db, proyecto_id=db_proyecto.id)



async def get_suma_total_proyecto(db: AsyncSession, proyecto_id: int,filtro_categoria:str="Invalidas"):
    """
    Calcula la suma de los montos de todas las facturas (manuales y electrónicas)
    de un proyecto específico directamente en la base de datos.
    """
    # Suma para facturas manuales
    cat=await crud_categoria.get_or_create_categoria(db,filtro_categoria)
    
    query_manual = select(func.sum(models.FacturaManual.monto_total)).filter(
        models.FacturaManual.proyecto_id == proyecto_id
        
    )
    result_manual = await db.execute(query_manual)
    total_manual = result_manual.scalar_one_or_none() or 0.0

    # Suma para facturas electrónicas
    # print("\n\n\n\n el cat de factura es ")
    # 🚩
    query_electronica = select(func.sum(models.FacturaElectronica.monto_total)).filter(
        models.FacturaElectronica.proyecto_id == proyecto_id
        , or_(
        models.FacturaElectronica.categoria_id != cat.id,
        models.FacturaElectronica.categoria_id == None)
    )
    result_electronica = await db.execute(query_electronica)
    total_electronica = result_electronica.scalar_one_or_none() or 0.0

    return total_manual + total_electronica




async def get_suma_manuales_proyecto(db: AsyncSession, proyecto_id: int,filtro_categoria:str="Invalidas"):
    """
    Calcula la suma de los montos de las  manual
    de un proyecto específico directamente en la base de datos.
    """
    # Suma para facturas manuales
    # cat=await crud_categoria.get_or_create_categoria(db,filtro_categoria)
    
    query_manual = select(func.sum(models.FacturaManual.monto_total)).filter(
        models.FacturaManual.proyecto_id == proyecto_id
        
    )
    result_manual = await db.execute(query_manual)
    total_manual = result_manual.scalar_one_or_none() or 0.0
    return total_manual

async def get_count_facturas_manuales(db: AsyncSession, proyecto_id: int) -> int:
    """Cuenta el número de facturas manuales en un proyecto."""
    query = select(func.count(models.FacturaManual.id)).filter(models.FacturaManual.proyecto_id == proyecto_id)
    result = await db.execute(query)
    return result.scalar_one()

async def get_count_facturas_electronicas(db: AsyncSession, proyecto_id: int) -> int:
    """Cuenta el número de facturas electrónicas en un proyecto."""
    query = select(func.count(models.FacturaElectronica.id)).filter(models.FacturaElectronica.proyecto_id == proyecto_id)
    result = await db.execute(query)
    return result.scalar_one()
async def get_suma_electronicas_proyecto(db: AsyncSession, proyecto_id: int,filtro_categoria:str="Invalidas"):
    """
    Calcula la suma de los montos de las  electrónicas
    de un proyecto específico directamente en la base de datos.
    """
    # Suma para facturas manuales
    cat=await crud_categoria.get_or_create_categoria(db,filtro_categoria)
    # Suma para facturas electrónicas
    # print("\n\n\n\n el cat de factura es ")
    # 🚩
    query_electronica = select(func.sum(models.FacturaElectronica.monto_total)).filter(
        models.FacturaElectronica.proyecto_id == proyecto_id
        , or_(
        models.FacturaElectronica.categoria_id != cat.id,
        models.FacturaElectronica.categoria_id == None)
    )
    result_electronica = await db.execute(query_electronica)
    total_electronica = result_electronica.scalar_one_or_none() or 0.0

    return  total_electronica

async def get_resumen_batches_por_proyecto(db: AsyncSession, proyecto_id: int,filtro_categoria="Invalidas") -> list:
    """
    Calcula la suma de los montos de las facturas para cada batch
    dentro de un proyecto específico.
    """
    # Usaremos un diccionario para sumar los totales de ambas tablas de facturas
    # defaultdict es útil porque crea una entrada con 0.0 si la clave no existe
    sumas_por_batch = defaultdict(float)
    cantidad_electronicas_por_batch = defaultdict(int)
    cantidad_manuales_por_batch = defaultdict(int)

    query_manual = (
        select(models.FacturaManual.batch_id, func.count(models.FacturaManual.id))
        .filter(models.FacturaManual.proyecto_id == proyecto_id)
        .filter(models.FacturaManual.batch_id.is_not(None)) # Ignoramos las que no tienen batch
        .group_by(models.FacturaManual.batch_id)
    )
    result_manual = await db.execute(query_manual)
    for batch_id, cantidad in result_manual.all():
        cantidad_manuales_por_batch[batch_id] += cantidad

    # Consulta para sumar facturas manuales por batch
    query_manual = (
        select(models.FacturaManual.batch_id, func.sum(models.FacturaManual.monto_total))
        .filter(models.FacturaManual.proyecto_id == proyecto_id)
        .filter(models.FacturaManual.batch_id.is_not(None)) # Ignoramos las que no tienen batch
        .group_by(models.FacturaManual.batch_id)
    )
    result_manual = await db.execute(query_manual)
    for batch_id, suma in result_manual.all():
        sumas_por_batch[batch_id] += suma
    cat=await crud_categoria.get_or_create_categoria(db,filtro_categoria)
    query_electronica = (
        select(models.FacturaElectronica.batch_id, func.count(models.FacturaElectronica.id))
        .filter(models.FacturaElectronica.proyecto_id == proyecto_id)
        .filter(models.FacturaElectronica.batch_id.is_not(None))
        .filter(or_(
            models.FacturaElectronica.categoria_id != cat.id,
            models.FacturaElectronica.categoria_id == None
        ))
        .group_by(models.FacturaElectronica.batch_id)
    )
    result_electronica = await db.execute(query_electronica)
    for batch_id, cantidad in result_electronica.all():
        cantidad_electronicas_por_batch[batch_id] += cantidad
    
    # Consulta para sumar facturas electrónicas por batch
    
    
    query_electronica = (
        select(models.FacturaElectronica.batch_id, func.sum(models.FacturaElectronica.monto_total))
        .filter(models.FacturaElectronica.proyecto_id == proyecto_id)
        .filter(models.FacturaElectronica.batch_id.is_not(None))
        .filter(or_(
                models.FacturaElectronica.categoria_id != cat.id,
                models.FacturaElectronica.categoria_id == None
            ))
        .group_by(models.FacturaElectronica.batch_id)
    )
    result_electronica = await db.execute(query_electronica)
    for batch_id, suma in result_electronica.all():
        sumas_por_batch[batch_id] += suma
    
    # Ahora, obtenemos los objetos completos de los batches para la respuesta
    if not sumas_por_batch:
        return []

    query_batches = select(models.Batch).filter(models.Batch.id.in_(sumas_por_batch.keys()))
    result_batches = await db.execute(query_batches)
    batches_obj = result_batches.scalars().all()

    # Combinamos los objetos Batch con sus sumas calculadas
    resumen_final = []
    for batch in batches_obj:
        resumen_final.append({
            "batch_info": batch,
            "monto_total_batch": sumas_por_batch.get(batch.id, 0.0),
            "cantidad_electronicas": cantidad_electronicas_por_batch.get(batch.id, 0),
            "cantidad_manuales": cantidad_manuales_por_batch.get(batch.id, 0)
        })

    return resumen_final

async def get_resumen_categoria_por_proyecto(db: AsyncSession, proyecto_id: int,filtro_categoria="Invalidas") -> list:
    """
    Calcula la suma de los montos de las facturas para cada categoria
    dentro de un proyecto específico.
    """
    # Usaremos un diccionario para sumar los totales de ambas tablas de facturas
    # defaultdict es útil porque crea una entrada con 0.0 si la clave no existe
    sumas_por_batch = defaultdict(float)
    cantidad_electronicas_por_batch = defaultdict(int)
    cantidad_manuales_por_batch = defaultdict(int)

    query_manual = (
        select(models.FacturaManual.categoria_id, func.count(models.FacturaManual.id))
        .filter(models.FacturaManual.proyecto_id == proyecto_id)
        .filter(models.FacturaManual.categoria_id.is_not(None)) # Ignoramos las que no tienen batch
        .group_by(models.FacturaManual.categoria_id)
    )
    result_manual = await db.execute(query_manual)
    for categoria_id, cantidad in result_manual.all():
        cantidad_manuales_por_batch[categoria_id] += cantidad

    # Consulta para sumar facturas manuales por batch
    query_manual = (
        select(models.FacturaManual.categoria_id, func.sum(models.FacturaManual.monto_total))
        .filter(models.FacturaManual.proyecto_id == proyecto_id)
        .filter(models.FacturaManual.categoria_id.is_not(None)) # Ignoramos las que no tienen batch
        .group_by(models.FacturaManual.categoria_id)
    )
    result_manual = await db.execute(query_manual)
    for categoria_id, suma in result_manual.all():
        sumas_por_batch[categoria_id] += suma
    cat=await crud_categoria.get_or_create_categoria(db,filtro_categoria)
    query_electronica = (
        select(models.FacturaElectronica.categoria_id, func.count(models.FacturaElectronica.id))
        .filter(models.FacturaElectronica.proyecto_id == proyecto_id)
        .filter(models.FacturaElectronica.categoria_id.is_not(None))
        .filter(or_(
            models.FacturaElectronica.categoria_id != cat.id,
            models.FacturaElectronica.categoria_id == None
        ))
        .group_by(models.FacturaElectronica.categoria_id)
    )
    result_electronica = await db.execute(query_electronica)
    for categoria_id, cantidad in result_electronica.all():
        cantidad_electronicas_por_batch[categoria_id] += cantidad
    
    # Consulta para sumar facturas electrónicas por batch
    
    
    query_electronica = (
        select(models.FacturaElectronica.categoria_id, func.sum(models.FacturaElectronica.monto_total))
        .filter(models.FacturaElectronica.proyecto_id == proyecto_id)
        .filter(models.FacturaElectronica.categoria_id.is_not(None))
        .filter(or_(
                models.FacturaElectronica.categoria_id != cat.id,
                models.FacturaElectronica.categoria_id == None
            ))
        .group_by(models.FacturaElectronica.categoria_id)
    )
    result_electronica = await db.execute(query_electronica)
    for categoria_id, suma in result_electronica.all():
        sumas_por_batch[categoria_id] += suma
    
    # Ahora, obtenemos los objetos completos de los batches para la respuesta
    if not sumas_por_batch:
        return []

    query_batches = select(models.Categoria).filter(models.Categoria.id.in_(sumas_por_batch.keys()))
    result_batches = await db.execute(query_batches)
    batches_obj = result_batches.scalars().all()

    # Combinamos los objetos Batch con sus sumas calculadas
    resumen_final = []
    for categoria in batches_obj:
        resumen_final.append({
            "categoria_info": categoria,
            "monto_total_categoria": sumas_por_batch.get(categoria.id, 0.0),
            "cantidad_electronicas": cantidad_electronicas_por_batch.get(categoria.id, 0),
            "cantidad_manuales": cantidad_manuales_por_batch.get(categoria.id, 0)
        })

    return resumen_final

async def get_resumen_empresa_por_proyecto(db: AsyncSession, proyecto_id: int,filtro_categoria="Invalidas") -> list:
    """
    Calcula la suma de los montos de las facturas para cada empresa
    dentro de un proyecto específico.
    """
    # Usaremos un diccionario para sumar los totales de ambas tablas de facturas
    # defaultdict es útil porque crea una entrada con 0.0 si la clave no existe
    sumas_por_batch = defaultdict(float)
    cantidad_electronicas_por_batch = defaultdict(int)
    cantidad_manuales_por_batch = defaultdict(int)

    query_manual = (
        select(models.FacturaManual.empresa_id, func.count(models.FacturaManual.id))
        .filter(models.FacturaManual.proyecto_id == proyecto_id)
        .filter(models.FacturaManual.empresa_id.is_not(None)) # Ignoramos las que no tienen batch
        .group_by(models.FacturaManual.empresa_id)
    )
    result_manual = await db.execute(query_manual)
    for empresa_id, cantidad in result_manual.all():
        cantidad_manuales_por_batch[empresa_id] += cantidad

    # Consulta para sumar facturas manuales por batch
    query_manual = (
        select(models.FacturaManual.empresa_id, func.sum(models.FacturaManual.monto_total))
        .filter(models.FacturaManual.proyecto_id == proyecto_id)
        .filter(models.FacturaManual.empresa_id.is_not(None)) # Ignoramos las que no tienen batch
        .group_by(models.FacturaManual.empresa_id)
    )
    result_manual = await db.execute(query_manual)
    for empresa_id, suma in result_manual.all():
        sumas_por_batch[empresa_id] += suma
    cat=await crud_categoria.get_or_create_categoria(db,filtro_categoria)
    query_electronica = (
        select(models.FacturaElectronica.empresa_id, func.count(models.FacturaElectronica.id))
        .filter(models.FacturaElectronica.proyecto_id == proyecto_id)
        .filter(models.FacturaElectronica.empresa_id.is_not(None))
        .filter(or_(
            models.FacturaElectronica.categoria_id != cat.id,
            models.FacturaElectronica.categoria_id == None
        ))
        .group_by(models.FacturaElectronica.empresa_id)
    )
    result_electronica = await db.execute(query_electronica)
    for empresa_id, cantidad in result_electronica.all():
        cantidad_electronicas_por_batch[empresa_id] += cantidad
    
    # Consulta para sumar facturas electrónicas por batch
    
    
    query_electronica = (
        select(models.FacturaElectronica.empresa_id, func.sum(models.FacturaElectronica.monto_total))
        .filter(models.FacturaElectronica.proyecto_id == proyecto_id)
        .filter(models.FacturaElectronica.empresa_id.is_not(None))
        .filter(or_(
                models.FacturaElectronica.categoria_id != cat.id,
                models.FacturaElectronica.categoria_id == None
            ))
        .group_by(models.FacturaElectronica.empresa_id)
    )
    result_electronica = await db.execute(query_electronica)
    for empresa_id, suma in result_electronica.all():
        sumas_por_batch[empresa_id] += suma
    
    # Ahora, obtenemos los objetos completos de los batches para la respuesta
    if not sumas_por_batch:
        return []

    query_batches = select(models.Empresa).filter(models.Empresa.id.in_(sumas_por_batch.keys()))
    result_batches = await db.execute(query_batches)
    batches_obj = result_batches.scalars().all()

    # Combinamos los objetos Batch con sus sumas calculadas
    resumen_final = []
    for empresa in batches_obj:
        resumen_final.append({
            "empresa_info": empresa,
            "monto_total_empresa": sumas_por_batch.get(empresa.id, 0.0),
            "cantidad_electronicas": cantidad_electronicas_por_batch.get(empresa.id, 0),
            "cantidad_manuales": cantidad_manuales_por_batch.get(empresa.id, 0)
        })

    return resumen_final

async def get_batches_por_proyecto(db: AsyncSession, proyecto_id: int) -> list:
    """
    Calcula la suma de los montos de las facturas para cada batch
    dentro de un proyecto específico.
    """
    

    return await crud_batch.get_batchs_by_proyect(db,proyecto_id)

async def delete_proyecto(db: AsyncSession, proyecto_id: int):
    """
    elimina proyecto
    """
    # Busca la factura que se va a eliminar
    db_proyecto = await get_proyecto(db, proyecto_id=proyecto_id)
    if not db_proyecto:
        return None # Retorna None si no se encontró

    await db.delete(db_proyecto) 
    await db.commit() 
    return await get_proyecto(db, proyecto_id=db_proyecto.id)


async def anadir_miembro_a_proyecto(db: AsyncSession, miembro_data: schemas.MiembroProyecto, proyecto_id: int,id_user:int):
    """Añade un nuevo miembro a un proyecto con un rol específico."""
    asociacion = models.ProyectoUsuario(
        proyecto_id=proyecto_id,
        usuario_id=id_user,
        rol=miembro_data.rol
    )
    db.add(asociacion)
    await db.commit()
    await db.refresh(asociacion)
    return asociacion

async def actualizar_rol_miembro(db: AsyncSession, proyecto_id: int, usuario_id: int, rol_update: schemas.MiembroProyectoUpdate):
    """Actualiza el rol de un miembro existente en un proyecto."""
    asociacion = await get_asociacion_usuario_proyecto(db, user_id=usuario_id, proyecto_id=proyecto_id)
    if not asociacion:
        return None
    asociacion.rol = rol_update.rol
    await db.commit()
    await db.refresh(asociacion)
    return asociacion

async def eliminar_miembro_de_proyecto(db: AsyncSession, proyecto_id: int, usuario_id: int):
    """Elimina a un miembro de un proyecto."""
    asociacion = await get_asociacion_usuario_proyecto(db, user_id=usuario_id, proyecto_id=proyecto_id)
    if not asociacion:
        return None
    await db.delete(asociacion)
    await db.commit()
    return asociacion


async def buscar_facturas_unificadas(db: AsyncSession, filtros: schemas.FiltrosFactura,user_id:int=None):
    """
    Busca, filtra, ordena y pagina facturas de forma unificada (manuales y electrónicas).
    """
    
    skip = (filtros.page - 1) * filtros.size
    limit = filtros.size
    # --- 1. Construcción dinámica de filtros ---
    # Filtros comunes para ambas tablas
    common_filters = []
    manual_filters = []
    electronica_filters = []
    # print("aquie 1 ",filtros)
    if filtros.proyecto_id:
        # Si se especifica un proyecto, filtramos por él.
        manual_filters.append(models.FacturaManual.proyecto_id == filtros.proyecto_id)
        electronica_filters.append(models.FacturaElectronica.proyecto_id == filtros.proyecto_id)
        # common_filters.append(models.FacturaElectronica.proyecto_id == filtros.proyecto_id)
    else:
        # SI NO se especifica un proyecto, buscamos en TODOS los proyectos del usuario.
        # Primero obtenemos los IDs de los proyectos del usuario.
    
        if user_id:
            proyectos_usuario_query = select(models.ProyectoUsuario.proyecto_id).filter(models.ProyectoUsuario.usuario_id == user_id)
        else:
            proyectos_usuario_query = select(models.ProyectoUsuario.proyecto_id)
            
    
        proyectos_usuario_result = await db.execute(proyectos_usuario_query)
        proyectos_ids = proyectos_usuario_result.scalars().all()
        
        # Filtramos facturas que pertenezcan a cualquiera de esos proyectos.
        manual_filters.append(models.FacturaManual.proyecto_id.in_(proyectos_ids))
        electronica_filters.append(models.FacturaElectronica.proyecto_id.in_(proyectos_ids))


    if filtros.fecha_inicio:
        start_datetime = datetime.combine(filtros.fecha_inicio, time.min)
        manual_filters.append(models.FacturaManual.fecha >= start_datetime)
        electronica_filters.append(models.FacturaElectronica.fecha >= start_datetime)


    if filtros.fecha_fin:
        end_datetime = datetime.combine(filtros.fecha_fin, time.max)
        manual_filters.append(models.FacturaManual.fecha <= end_datetime)
        electronica_filters.append(models.FacturaElectronica.fecha <= end_datetime)
    if filtros.monto_min is not None:
        manual_filters.append(models.FacturaManual.monto_total >= filtros.monto_min)
        electronica_filters.append(models.FacturaElectronica.monto_total >= filtros.monto_min)
    if filtros.monto_max is not None:
        manual_filters.append(models.FacturaManual.monto_total <= filtros.monto_max)
        electronica_filters.append(models.FacturaElectronica.monto_total <= filtros.monto_max)
    if filtros.categoria_id is not None:
        manual_filters.append(models.FacturaManual.categoria_id == filtros.categoria_id)
        electronica_filters.append(models.FacturaElectronica.categoria_id == filtros.categoria_id)
    if filtros.empresa_id is not None:
        manual_filters.append(models.FacturaManual.empresa_id == filtros.empresa_id)
        electronica_filters.append(models.FacturaElectronica.empresa_id == filtros.empresa_id)
    if filtros.batch_id is not None:
        manual_filters.append(models.FacturaManual.batch_id == filtros.batch_id)
        electronica_filters.append(models.FacturaElectronica.batch_id == filtros.batch_id)
    # Filtros solo para facturas electrónicas
    # electronica_filters = common_filters.copy()
    if filtros.complete is not None:
        electronica_filters.append(models.FacturaElectronica.complete == filtros.complete)
    if filtros.factura_especial is not None:
        electronica_filters.append(models.FacturaElectronica.factura_especial == filtros.factura_especial)
    if filtros.factura_virtual is not None:
        electronica_filters.append(models.FacturaElectronica.save_pdf == filtros.factura_virtual)
    
    # --- 2. Creación de las consultas SELECT ---
    select_statements = []

    # Se añaden columnas comunes para que el UNION funcione.
 # Se añade una columna 'tipo' para saber de qué tabla viene cada ID.
    if filtros.tipo_factura in ['todas', 'manual']:
        q_manual = (
            select(
                models.FacturaManual.id,
                models.FacturaManual.fecha,
                models.FacturaManual.monto_total,
                literal("manual").label("tipo"),
                # --- AÑADIMOS LAS COLUMNAS PARA ORDENAR ---
                models.Empresa.nombre.label("empresa_nombre"),
                models.Categoria.nombre.label("categoria_nombre"),
                models.Batch.nombre.label("batch_nombre")
            )
            .join(models.Empresa, models.FacturaManual.empresa_id == models.Empresa.id, isouter=True)
            .join(models.Categoria, models.FacturaManual.categoria_id == models.Categoria.id, isouter=True)
            .join(models.Batch, models.FacturaManual.batch_id == models.Batch.id, isouter=True)
            .filter(and_(*manual_filters))
        )
        select_statements.append(q_manual)

    if filtros.tipo_factura in ['todas', 'electronica']:
        q_electronica = (
            select(
                models.FacturaElectronica.id,
                models.FacturaElectronica.fecha,
                models.FacturaElectronica.monto_total,
                literal("electronica").label("tipo"),
                # --- AÑADIMOS LAS MISMAS COLUMNAS ---
                models.Empresa.nombre.label("empresa_nombre"),
                models.Categoria.nombre.label("categoria_nombre"),
                models.Batch.nombre.label("batch_nombre")
            )
            .join(models.Empresa, models.FacturaElectronica.empresa_id == models.Empresa.id, isouter=True)
            .join(models.Categoria, models.FacturaElectronica.categoria_id == models.Categoria.id, isouter=True)
            .join(models.Batch, models.FacturaElectronica.batch_id == models.Batch.id, isouter=True)
            .filter(and_(*electronica_filters))
        )
        select_statements.append(q_electronica)

    if not select_statements:
        return {"total": 0, "items": []}

    # --- 3. Unión de las consultas y paginación ---
    # Unimos las consultas y creamos una subconsulta (CTE)
    unified_cte = union_all(*select_statements).cte('unified_cte')
    # --- Contar el total de resultados ---
# Contar el total de resultados antes de paginar
    count_query = select(func.count()).select_from(unified_cte)
    total = (await db.execute(count_query)).scalar_one()
    if total == 0:
        total_pages = 0
    else:
        total_pages = math.ceil(total / filtros.size)
    # Lógica de Ordenamiento Dinámico
    sortable_columns = {
        "fecha": unified_cte.c.fecha,
        "monto_total": unified_cte.c.monto_total,
        "empresa": unified_cte.c.empresa_nombre,
        "categoria": unified_cte.c.categoria_nombre,
        "batch": unified_cte.c.batch_nombre,
    }
    sort_column = sortable_columns.get(filtros.sort_by, unified_cte.c.fecha)
    
    # order_logic = sort_column.desc() if filtros.sort_order == 'desc' else sort_column.asc()
    order_logic = sort_column.desc().nullslast() if filtros.sort_order == 'desc' else sort_column.asc().nullsfirst()
    # Obtener solo los IDs y tipos de la página actual
    paginated_ids_query = select(unified_cte.c.id, unified_cte.c.tipo).order_by(order_logic).offset(skip).limit(limit)
    paginated_ids_result = await db.execute(paginated_ids_query)
    
    manual_ids = []
    electronica_ids = []
    # Mantenemos el orden original para el paso final
    order_map = {}
    for i, (id, tipo) in enumerate(paginated_ids_result.all()):
        order_map[f"{tipo}_{id}"] = i
        if tipo == 'manual':
            manual_ids.append(id)
        else:
            electronica_ids.append(id)
            
    # --- 5. Obtener los objetos completos con Eager Loading ---
    items_map = {}
    if manual_ids:
        # (Aquí va tu consulta con eager loading para FacturaManual)
        manual_items_query = select(models.FacturaManual).options(
        # --- CARGA ANIDADA COMPLETA ---
        joinedload(models.FacturaManual.proyecto).options(
            joinedload(models.Proyecto.propietario),
            selectinload(models.Proyecto.asociaciones_usuario).joinedload(models.ProyectoUsuario.usuario),
            selectinload(models.Proyecto.batches) # <-- Añade la carga de batches
        ),
        joinedload(models.FacturaManual.categoria),
        joinedload(models.FacturaManual.batch),
        joinedload(models.FacturaManual.empresa)
    ).filter(models.FacturaManual.id.in_(manual_ids))
    


        manual_items_result = await db.execute(manual_items_query)
        for item in manual_items_result.unique().scalars().all():
            items_map[f"manual_{item.id}"] = item

    if electronica_ids:
        # (Aquí va tu consulta con eager loading para FacturaElectronica)
        electronica_items_query = select(models.FacturaElectronica).options(
        # --- CARGA ANIDADA COMPLETA (TAMBIÉN AQUÍ) ---
        joinedload(models.FacturaElectronica.proyecto).options(
            joinedload(models.Proyecto.propietario),
            selectinload(models.Proyecto.asociaciones_usuario).joinedload(models.ProyectoUsuario.usuario),
            selectinload(models.Proyecto.batches) # <-- Añade la carga de batches
        ),
        joinedload(models.FacturaElectronica.categoria),
        joinedload(models.FacturaElectronica.batch),
        joinedload(models.FacturaElectronica.empresa)
    ).filter(models.FacturaElectronica.id.in_(electronica_ids))
        
        electronica_items_result = await db.execute(electronica_items_query)
        for item in electronica_items_result.unique().scalars().all():
            items_map[f"electronica_{item.id}"] = item
            
    # Reconstruimos la lista final respetando el orden de la paginación
    final_items = sorted(items_map.values(), key=lambda x: order_map[f"{'manual' if isinstance(x, models.FacturaManual) else 'electronica'}_{x.id}"])
    
    items_con_tipo = []
    for item in final_items: # 'final_items' es la lista ordenada del paso anterior
        if isinstance(item, models.FacturaManual):
            # Convertimos el objeto a su schema Pydantic correspondiente.
            # Pydantic aplicará el valor por defecto 'tipo: manual'.
            schema_obj = schemas.FacturaManual.model_validate(item)
        elif isinstance(item, models.FacturaElectronica):
            schema_obj = schemas.FacturaElectronica.model_validate(item)
        else:
            continue # Ignorar tipos desconocidos si los hubiera

        # Convertimos el objeto Pydantic a un diccionario.
        # Ahora este diccionario SÍ tiene la clave 'tipo'.
        items_con_tipo.append(schema_obj.model_dump())
        
    # Devolvemos el total y la nueva lista de diccionarios.
    return {"total": total,
            "items": items_con_tipo,
            "page": filtros.page,
            "size": filtros.size,
            "total_pages": total_pages}
    # return {"total": total, "items": final_items}