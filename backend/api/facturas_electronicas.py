from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException,status,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from typing import List
from backend.services import factura_service
from fastapi.responses import JSONResponse
from backend.crud import crud_categoria, crud_facturas_electronicas,crud_proyecto
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal
from backend.api import auth
router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def verificar_permiso_en_factura(allowed_roles: List[str]):
    async def checker(
        factura_id: int, 
        db: AsyncSession = Depends(get_db), 
        current_user: models.User = Depends(auth.get_current_active_user)
    ) -> models.FacturaElectronica: # Devuelve el objeto de la factura para reutilizarlo

        db_factura = await crud_facturas_electronicas.get_factura_electronica(db, factura_id=factura_id)

        if not db_factura:
            raise HTTPException(status_code=404, detail="Factura no encontrada.")

        # Obtenemos el proyecto al que pertenece la factura
        proyecto = db_factura.proyecto
        if not proyecto:
             raise HTTPException(status_code=404, detail="La factura no está asociada a ningún proyecto.")

        # Verificamos si el usuario actual es el propietario del proyecto
        if proyecto.propietario_id == current_user.id:
            return db_factura # El dueño siempre tiene permiso

        # Si no, buscamos si es un miembro con el rol adecuado
        asociacion = await crud_proyecto.get_asociacion_usuario_proyecto(
            db, user_id=current_user.id, proyecto_id=proyecto.id
        )
        
        if not asociacion:
            raise HTTPException(status_code=403, detail="No eres miembro del proyecto al que pertenece esta factura.")
        
        if asociacion.rol not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tienes los permisos necesarios para esta acción.")
        
        return db_factura
        
    return checker
def verificar_permiso_en_proyecto_electronica(allowed_roles: List[str]):
    async def checker(
        # La única diferencia clave es que depende de FacturaElectronicaInicial
        factura_inicial: schemas.FacturaElectronicaInicial,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
    ) -> models.Proyecto:

        proyecto_id = factura_inicial.proyecto_id
        # ... (el resto de la lógica de verificación es exactamente la misma)
        # ... (busca el proyecto, comprueba el propietario, busca la asociación, comprueba el rol)
        
        # (código de verificación omitido por brevedad, es idéntico al anterior)
        proyecto_obj = await crud_proyecto.get_proyecto(db=db, proyecto_id=proyecto_id)
        if not proyecto_obj:
            raise HTTPException(status_code=404, detail=f"Proyecto con id {proyecto_id} no encontrado.")

        if proyecto_obj.propietario_id == current_user.id:
            return proyecto_obj

        asociacion = await crud_proyecto.get_asociacion_usuario_proyecto(db, user_id=current_user.id, proyecto_id=proyecto_id)
        if not asociacion:
            raise HTTPException(status_code=403, detail="No eres miembro de este proyecto.")
        if asociacion.rol not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tienes los permisos necesarios para añadir facturas a este proyecto.")
        
        return proyecto_obj
        
    return checker
def require_role(allowed_roles: List[str]):
    async def role_checker(
        datos_iniciales: schemas.FacturaElectronicaInicial,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
    )->models.Proyecto:
        # Buscamos la asociación específica para este usuario y proyecto
        print("estamos aqui ",datos_iniciales)
        if not datos_iniciales.proyecto_id:
            
            raise HTTPException(status_code=422, detail="Se requiere un proyecto_id.")

        proyecto_id = datos_iniciales.proyecto_id
        proyecto_obj = await crud_proyecto.get_proyecto(db=db, proyecto_id=proyecto_id)
        if not proyecto_obj:
            raise HTTPException(status_code=404, detail=f"Proyecto con id {proyecto_id} no encontrado.")
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

#💃 fatla el check  y check force  talvez eliminar checkforce
# ✅ se elimino el checkforce y funciona el check
#💃 endpoint para descarga pdf
# ✅
# 💃falta poner la logica de download al save_pdf  en update 
# ✅ creo q si porque osea  ?? q mrd era esto xd

# .💃  .🚩 (falta la validacion de la categoria Invalidas o por su msg en que lugar ?)  falta rehacer las que faltan o las que tienen error
# .✅ aqui y en proyectos.py hay  Invalidas con ese texto buscamos la funcion de checkfacturas 

#✅(cada proyecto tiene sus batches y categoria es mas global) ver pertenencias es decir cada proyecto tiene sus propios batches y categorias ?? ? ? ? ? ? 
# ✅falta sumar proyectos .......
# ✅falta categorias 
# ✅falta batches
# ✅sumar batches que son las bolsas 
#✅  ver esto que no funciona # .filter(models.FacturaElectronica.categoria_id!=cat.id )




@router.post("/electronicas/", response_model=schemas.FacturaElectronica, status_code=202)
async def crear_factura_electronica(
    factura_inicial: schemas.FacturaElectronicaInicial, # Un nuevo schema solo con la URL
    background_tasks: BackgroundTasks, # Inyectamos la dependencia
    db: AsyncSession = Depends(get_db),
    proyecto_validado: models.Proyecto = Depends(verificar_permiso_en_proyecto_electronica(allowed_roles=["dueño", "editor","lector"]))):
    # print("entro a post ",factura.model_dump())

    db_factura = await crud_facturas_electronicas.get_factura_electronica_by_url(db, url=factura_inicial.url)
    if db_factura:
        # Si la factura ya existe, devuelve un error 409 Conflict
        msg_detail={
                "msg":"Ya existe una factura registrada con esta URL.",
                'id_factura':db_factura.id,
                'num_fact':db_factura.n_factura
        }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg_detail
           
        )
    

    # todo esto es por verse envez de esto vamos a 
    # if not proyecto or proyecto.propietario_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No tienes permiso para añadir facturas a este proyecto."
    #     )

    factura_creada = await crud_facturas_electronicas.create_factura_electronica_inicial(db=db, factura=factura_inicial)
    # 2. Añade la tarea de larga duración al segundo plano.
    #    Esta función se ejecutará DESPUÉS de que la respuesta haya sido enviada.

    background_tasks.add_task(
        factura_service.tarea_de_scraping_y_actualizacion, # La función a ejecutar AQUI SE DA LOS ERRORES DE FECHA Y ETC
        factura_id=factura_creada.id, # Argumentos para la función
        url=factura_creada.url,
        proyect_id=factura_inicial.proyecto_id,
        savePdf=factura_creada.save_pdf
    )
    return factura_creada
    # return await crud_facturas_electronicas.create_factura_electronica(db=db, factura=factura)

@router.get("/electronicas/", response_model=List[schemas.FacturaElectronica])
async def leer_facturas_electronicas(skip: int = 0, limit: int = 100,
                                      db: AsyncSession = Depends(get_db)):
    facturas = await crud_facturas_electronicas.get_facturas_electronicas(db, skip=skip, limit=limit)
    return facturas

@router.get("/electronicas/{factura_id}", response_model=schemas.FacturaElectronica)
async def leer_factura_elctronica(factura_id: int, db: AsyncSession = Depends(get_db)):
    db_factura = await crud_facturas_electronicas.get_factura_electronica(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return db_factura




@router.put("/electronicas/{factura_id}", response_model=schemas.FacturaElectronica , tags=["Facturas electronicas"])
async def actualizar_factura_electronica(factura_id: int,
                                     factura: schemas.FacturaElectronicaUpdate, 
                                     background_tasks: BackgroundTasks, 
                                     db: AsyncSession = Depends(get_db),
                                     factura_cuestion: models.Proyecto = Depends(verificar_permiso_en_factura(allowed_roles=["dueño", "editor"]))):
    """
    Actualiza una factura electronica  por su ID.
    Solo puede tener los parametros y debe tener todos los parametros  de FacturaElectronicaUpdate : 
    save_pdf
    categoria_id
    batch
    """
    db_factura_inicial= await crud_facturas_electronicas.get_factura_electronica(db, factura_id=factura_id)
    
    if db_factura_inicial is None:
        raise HTTPException(status_code=404, detail="Factura electronica no encontrada")
    
    

    
    
    if factura.save_pdf != None:
        print("existe savepdf \n\n\n\n\n\n\n\n ")
        print("factura inicial ",db_factura_inicial.save_pdf)
        print("factura en curso ",factura.save_pdf)
        if db_factura_inicial.save_pdf != factura.save_pdf and factura.save_pdf== True: 
                print("iniciando facturaaaa scraping")
                # db_factura = await crud_facturas_electronicas.update_factura_electroncia(db, factura_id=factura_id, factura_update=factura)
                # db_factura =await crud_facturas_electronicas.update_status_factura_electronica(db=db,factura_id=factura_id,Msg="Esperando descarga Servidor",status=False)
                db_factura= await crud_facturas_electronicas.bloquear_factura(db=db,factura_id=factura_id)
                background_tasks.add_task(
                factura_service.tarea_de_scraping_y_actualizacion, # La función a ejecutar AQUI SE DA LOS ERRORES DE FECHA Y ETC
                factura_id=factura_id, # Argumentos para la función
                url=db_factura_inicial.url,
                proyect_id=db_factura_inicial.proyecto_id,
                savePdf=factura.save_pdf
            )
        else:
            print("no se cumplio cond ")
            # db_factura = await crud_facturas_electronicas.update_factura_electroncia(db, factura_id=factura_id, factura_update=factura)
            db_factura=await crud_facturas_electronicas.update_rute_factura_electronica(db=db,factura_id=factura_id)
    # else:
    db_factura = await crud_facturas_electronicas.update_factura_electroncia(db, factura_id=factura_id, factura_update=factura)
    return db_factura

@router.delete("/electronicas/{factura_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Facturas electronicas"])
async def eliminar_factura_electronica(
                                        db: AsyncSession = Depends(get_db),
                                        factura: models.Proyecto = Depends(verificar_permiso_en_factura(allowed_roles=["dueño", "editor"]))):
    """
    Elimina una factura electronica por su ID.
    """

    db_factura = await crud_facturas_electronicas.delete_factura_electronica(db, factura_id=factura.id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura Electronica no encontrada")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return



@router.get("/electronicas/check/{factura_id}",response_model=schemas.FacturaElectronica , tags=["Facturas electronicas"])
async def check_factura_electronica(factura_id: int,
                                    db:AsyncSession=Depends(get_db),
                                    factura_cuestion: models.FacturaElectronica = Depends(verificar_permiso_en_factura(allowed_roles=["dueño", "editor"]))):
    db_factura=factura_cuestion
    categoria_x=await crud_categoria.get_or_create_categoria(db=db,name="Invalidas")
    
    
    if categoria_x.id != db_factura.categoria_id:
        if db_factura.complete == True:
            try:
                factura_schema = schemas.FacturaElectronica.model_validate(db_factura)
                # intentar serealizar para no ahcer un schema nuevo
                contenido_serializable = {
                        "msg": "factura ya completada",
                        "factura": factura_schema.model_dump(mode="python") # o .dict() en Pydantic v1
                    }
                print("\n\n\n\n\n\n\n\n\n\n la facuta es ",contenido_serializable["factura"])
                contenido_serializable["factura"]['fecha']=contenido_serializable["factura"]['fecha'].isoformat()
                contenido_serializable["factura"].pop("proyecto")
                return JSONResponse(content=contenido_serializable)
            except:
                print("error al desearilizar la factura\n")
                contenido_serializable = {
                        "msg": "factura ya completada"}

                return JSONResponse(content=contenido_serializable)
    #  te falta poner en ele service proyect_id=factura_inicial.proyecto_id,
        db_fact= await factura_service.tarea_de_scraping_y_actualizacion(factura_id,db_factura.url,db_factura.save_pdf)
        return db_fact
    else:
        contenido_serializable = {
                "msg": "Error la factura es invalida "}

        return JSONResponse(status_code=500,content=contenido_serializable)





@router.get("/electronicas/download/{factura_id}",response_model=schemas.FacturaElectronica , tags=["Facturas electronicas"])
async def download_factura(factura_id: int,
                            db:AsyncSession=Depends(get_db),
                            proyecto_validado: models.Proyecto = Depends(verificar_permiso_en_factura(allowed_roles=["dueño", "editor"]))):
    
    db_factura= await crud_facturas_electronicas.get_factura_electronica(db,factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura Electronica no encontrada")
    if not db_factura.pdfIO:
        raise HTTPException(status_code=404, detail="Esta factura no tiene un PDF asociado.")
    try:
        ruta_archivo = Path(db_factura.pdfIO)
        if not ruta_archivo.is_file():
            raise HTTPException(status_code=404, detail="El archivo PDF no existe en el servidor.")

    # 4. Devolvemos la respuesta del archivo
        nombre_descarga = f"factura_{db_factura.n_factura or db_factura.id}.pdf"
        return FileResponse(
            path=ruta_archivo, 
            media_type='application/pdf', 
            filename=nombre_descarga
        )

    except Exception as e :
        print ("error al descargar factura: \n",e )
        raise HTTPException(status_code=404, detail="PDF de Factura Electronica no encontrada")
    