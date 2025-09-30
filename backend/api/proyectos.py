from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import crud_categoria, crud_facturas_electronicas, crud_facturas_manuales, crud_proyecto
from backend.schemas import schemas
from backend.db import models
from backend.api import auth
from backend.db.database import engine, AsyncSessionLocal
from backend.services import factura_service

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
    
# --- DEPENDENCIA DE PERMISOS ---
def require_role(allowed_roles: List[str]):
    async def role_checker(
        proyecto_id: int, 
        db: AsyncSession = Depends(get_db), 
        current_user: models.User = Depends(auth.get_current_active_user)
    )->models.Proyecto:
        # Buscamos la asociación específica para este usuario y proyecto
        proyecto_obj = await crud_proyecto.get_proyecto(db=db, proyecto_id=proyecto_id)
        if not proyecto_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
        
        if proyecto_obj.propietario_id == current_user.id:
            # Si es el dueño, tiene todos los permisos. Le devolvemos el proyecto.
            return proyecto_obj
        asociacion = await crud_proyecto.get_asociacion_usuario_proyecto(db, user_id=current_user.id, proyecto_id=proyecto_id)
        if not asociacion:
            raise HTTPException(status_code=403, detail="No eres miembro de este proyecto.")
        
        if asociacion.rol not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"No tienes los permisos necesarios. Se requiere rol: {', '.join(allowed_roles)}")
        
        # Si tiene permiso, devolvemos el proyecto para no tener que buscarlo de nuevo
        return asociacion.proyecto
        
    return role_checker


@router.post("/", response_model=schemas.Proyecto, status_code=201)
async def crear_proyecto(proyecto: schemas.ProyectoCreate,
                          db: AsyncSession = Depends(get_db),
                          current_user: models.User = Depends(auth.get_current_active_user)
                          ):
    db_proyecto = await crud_proyecto.get_proyecto_by_name(db, proyecto_name=proyecto.nombre)
    if db_proyecto :
        raise HTTPException(status_code=409, detail="Proyecto existente")
    return await crud_proyecto.create_proyecto(db=db, proyecto=proyecto, propietario_id=current_user.id)


@router.get("/", response_model=List[schemas.Proyecto])
async def leer_proyectos_del_usuario(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
    
):
    return await crud_proyecto.get_proyectos_by_user(db, propietario_id=current_user.id)


@router.get("/{proyecto_id}", response_model=schemas.Proyecto)
async def leer_proyecto(
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño", "editor", "lector"]))
):
    """Obtiene un proyecto específico si el usuario es miembro (cualquier rol)."""
    return proyecto




@router.get("/{proyecto_id}/resume",response_model=schemas.ProyectoResumen)
async def sumar_proyecto(
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño", "editor", "lector"]))
    ,db: AsyncSession = Depends(get_db)
):
    """devuelve la suma de las facturas"""
    monto_total= await crud_proyecto.get_suma_total_proyecto(db=db,proyecto_id=proyecto.id)
    return  {"monto_total": monto_total}

@router.get("/{proyecto_id}/detalle_batch", response_model=List[schemas.BatchResumen], tags=["Análisis de Proyectos"])
async def obtener_detalle_de_batches(
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño", "editor", "lector"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Devuelve una lista de todos los batches dentro de un proyecto,
    cada uno con la suma total de sus facturas asociadas.
    """
    resumen_batches = await crud_proyecto.get_resumen_batches_por_proyecto(db=db, proyecto_id=proyecto.id)
    return resumen_batches

@router.get("/{proyecto_id}/batch", response_model=List[schemas.Batch], tags=["lista de batch por proyecto"])
async def obtener_batchs(
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño", "editor", "lector"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Devuelve una lista de todos los batches dentro de un proyecto,
    
    """
    resumen_batches = await crud_proyecto.get_batches_por_proyecto(db=db, proyecto_id=proyecto.id)
    return resumen_batches


@router.get("/{proyecto_id}/facturas",response_model=schemas.FacturasDelProyectoResponse, tags=["Proyectos"])
async def obtener_detalle_facturas(
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño", "editor", "lector"])),
    db: AsyncSession = Depends(get_db)
):
    """
        Devuelve dos listas separadas: una con las facturas manuales y otra con las electrónicas
        que pertenecen a un proyecto específico.
        """
    # 1. Obtenemos las facturas manuales usando la nueva función CRUD
    facturas_manuales = await crud_facturas_manuales.get_facturas_manuales_por_proyecto(db=db, proyecto_id=proyecto.id)

    # 2. Obtenemos las facturas electrónicas
    facturas_electronicas = await crud_facturas_electronicas.get_facturas_electronicas_por_proyecto(
        db=db, proyecto_id=proyecto.id
    )

    # 3. Devolvemos el diccionario con la estructura que espera el response_model
    return {
        "facturas_manuales": facturas_manuales,
        "facturas_electronicas": facturas_electronicas
    }

@router.get("/{proyecto_id}/check_facturas")
async def hacerCheckfacturas(
    background_tasks: BackgroundTasks,
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño", "editor", "lector"])),
    db: AsyncSession = Depends(get_db),
   # Inyectamos la dependencia
):
    """
        hace un check a todas las facturas electronicas que no sean invalidas y no esten completas
        """
    facturas_encoladas = await crud_facturas_electronicas.obtener_y_bloquear_facturas_para_procesar(
        db=db, 
        proyecto_id=proyecto.id
    )
    for i in facturas_encoladas:
            background_tasks.add_task(
                factura_service.tarea_de_scraping_y_actualizacion, # La función a ejecutar AQUI SE DA LOS ERRORES DE FECHA Y ETC
                factura_id=i.id, # Argumentos para la función
                url=i.url,
                proyect_id=i.proyecto_id,
                savePdf=i.save_pdf
            )
            



    
    return {
        "mensaje": f"Se han puesto en cola {len(facturas_encoladas)} facturas para su verificación.",
        "facturas_en_cola": [f.id for f in facturas_encoladas]
    }

@router.get("/{proyecto_id}/check_facturas_forced")
async def hacerCheckForcedfacturas(
    background_tasks: BackgroundTasks,
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño"])),
    db: AsyncSession = Depends(get_db),
   # Inyectamos la dependencia
):
    """
        hace un check a todas las facturas electronicas que no sean invalidas y no esten completas
        """
    facturas_encoladas = await crud_facturas_electronicas.get_facturas_electronicas_por_proyecto(
        db=db, 
        proyecto_id=proyecto.id
    )
    lista_f=[models.FacturaElectronica]
    for i in facturas_encoladas:
            if i.complete!=True:

                new_fac=await crud_facturas_electronicas.bloquear_factura(db=db,factura_id=i.id)
                lista_f.append(new_fac)
                background_tasks.add_task(
                    factura_service.tarea_de_scraping_y_actualizacion, # La función a ejecutar AQUI SE DA LOS ERRORES DE FECHA Y ETC
                    factura_id=i.id, # Argumentos para la función
                    url=i.url,
                    proyect_id=i.proyecto_id,
                    savePdf=i.save_pdf
                )
            



    
    return {
        "mensaje": f"Se han puesto en cola {len(lista_f)} facturas para su verificación.",
        "facturas_en_cola": [f.id for f in lista_f]
    }

@router.put("/{proyecto_id}", response_model=schemas.Proyecto)
async def actualizar_proyecto(
    proyecto_update: schemas.ProyectoUpdate,
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño", "editor"])),
    db: AsyncSession = Depends(get_db)
):
    if proyecto_update.nombre:
        db_proyecto = await crud_proyecto.get_proyecto_by_name(db, proyecto_name=proyecto.nombre)
        if db_proyecto :
            raise HTTPException(status_code=409, detail="Proyecto existente")
    """Actualiza un proyecto. Solo para dueños o editores."""
    return await crud_proyecto.update_proyecto(db=db, db_proyecto=proyecto, proyecto_update=proyecto_update)


@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_proyecto(
    proyecto_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Elimina un proyecto.
    Solo permite la eliminación si el proyecto pertenece al usuario autenticado.
    """
    db_proyecto = await crud_proyecto.get_proyecto(db, proyecto_id=proyecto_id)
    if db_proyecto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
    
    # --- Verificación de Pertenencia ---
    if db_proyecto.propietario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar este proyecto")
        
    await crud_proyecto.delete_proyecto(db=db, proyecto_id=proyecto_id)
    return

@router.post("/{proyecto_id}/miembros", status_code=status.HTTP_201_CREATED, tags=["Gestión de Miembros"])
async def anadir_miembro(
    miembro_data: schemas.MiembroProyecto,
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño","editor"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Añade un nuevo colaborador (miembro) a un proyecto.
    Solo el dueño del proyecto puede realizar esta acción.
    """
    # Verificar que el usuario a añadir no sea el propio dueño
    if miembro_data.usuario_id == proyecto.propietario_id:
        raise HTTPException(status_code=400, detail="El dueño del proyecto no puede ser añadido como miembro.")
    
    # Verificar que el usuario no sea ya miembro
    miembro_existente = await crud_proyecto.get_asociacion_usuario_proyecto(db, user_id=miembro_data.usuario_id, proyecto_id=proyecto.id)
    if miembro_existente:
        raise HTTPException(status_code=409, detail="Este usuario ya es miembro del proyecto.")

    await crud_proyecto.anadir_miembro_a_proyecto(db=db, miembro_data=miembro_data, proyecto_id=proyecto.id)
    return {"detail": "Miembro añadido exitosamente."}


@router.put("/{proyecto_id}/miembros/{usuario_id}", tags=["Gestión de Miembros"])
async def cambiar_rol_miembro(
    usuario_id: int,
    rol_update: schemas.MiembroProyectoUpdate,
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Cambia el rol de un colaborador existente en un proyecto.
    Solo el dueño del proyecto puede realizar esta acción.
    """
    asociacion_actualizada = await crud_proyecto.actualizar_rol_miembro(db, proyecto_id=proyecto.id, usuario_id=usuario_id, rol_update=rol_update)
    if not asociacion_actualizada:
        raise HTTPException(status_code=404, detail="El usuario no es miembro de este proyecto.")
    return {"detail": f"Rol del usuario {usuario_id} actualizado a '{rol_update.rol}'."}


@router.delete("/{proyecto_id}/miembros/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Gestión de Miembros"])
async def quitar_miembro(
    usuario_id: int,
    proyecto: models.Proyecto = Depends(require_role(allowed_roles=["dueño"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Quita a un colaborador de un proyecto.
    Solo el dueño del proyecto puede realizar esta acción.
    """
    asociacion_eliminada = await crud_proyecto.eliminar_miembro_de_proyecto(db, proyecto_id=proyecto.id, usuario_id=usuario_id)
    if not asociacion_eliminada:
        raise HTTPException(status_code=404, detail="El usuario no es miembro de este proyecto.")
    return