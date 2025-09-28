from collections import defaultdict
from sqlalchemy import func, or_
from backend.crud import crud_categoria
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
    query = select(models.Proyecto).options(
        joinedload(models.Proyecto.propietario),
        selectinload(models.Proyecto.asociaciones_usuario).joinedload(models.ProyectoUsuario.usuario),
        selectinload(models.Proyecto.batches)
    ).filter(models.Proyecto.propietario_id == propietario_id).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.unique().scalars().all()




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


async def get_resumen_batches_por_proyecto(db: AsyncSession, proyecto_id: int,filtro_categoria="Invalidas") -> list:
    """
    Calcula la suma de los montos de las facturas para cada batch
    dentro de un proyecto específico.
    """
    # Usaremos un diccionario para sumar los totales de ambas tablas de facturas
    # defaultdict es útil porque crea una entrada con 0.0 si la clave no existe
    sumas_por_batch = defaultdict(float)

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
    # Consulta para sumar facturas electrónicas por batch
    # 🚩
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
            "monto_total_batch": sumas_por_batch.get(batch.id, 0.0)
        })

    return resumen_final

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


async def anadir_miembro_a_proyecto(db: AsyncSession, miembro_data: schemas.MiembroProyecto, proyecto_id: int):
    """Añade un nuevo miembro a un proyecto con un rol específico."""
    asociacion = models.ProyectoUsuario(
        proyecto_id=proyecto_id,
        usuario_id=miembro_data.usuario_id,
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