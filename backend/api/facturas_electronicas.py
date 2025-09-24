from fastapi import APIRouter, Depends, HTTPException,status,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.services import factura_service
from fastapi.responses import JSONResponse
from backend.crud import crud_facturas_electronicas,crud_proyecto
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal
from backend.api import auth
router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/electronicas/", response_model=schemas.FacturaElectronica, status_code=202)
async def crear_factura_electronica(
    factura_inicial: schemas.FacturaElectronicaInicial, # Un nuevo schema solo con la URL
    background_tasks: BackgroundTasks, # Inyectamos la dependencia
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)):
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
    proyecto = await crud_proyecto.get_proyecto(db, proyecto_id=factura_inicial.proyecto_id)
    if not proyecto or proyecto.propietario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para añadir facturas a este proyecto."
        )

    factura_creada = await crud_facturas_electronicas.create_factura_electronica_inicial(db=db, factura=factura_inicial)
    # 2. Añade la tarea de larga duración al segundo plano.
    #    Esta función se ejecutará DESPUÉS de que la respuesta haya sido enviada.
    background_tasks.add_task(
        factura_service.tarea_de_scraping_y_actualizacion, # La función a ejecutar AQUI SE DA LOS ERRORES DE FECHA Y ETC
        factura_id=factura_creada.id, # Argumentos para la función
        url=factura_creada.url,
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
#  lo que hay que hacer devolver la factura sin el pdf siempre, y tener un endpoint para 
#  descargarlo en caso que sea save_false pues no devuelve nada 
#  otra opcion es que siempre siempre se guarde el pdf pero talvez mejor que un db
#  en una carpeta o otra forma de almacenar para posterior a esto descargarlo 
#  siempre guardarlo ?? ? ?? ? ? y cuando sea necesario descarga de acuerdo al save???
#  


@router.put("/electronicas/{factura_id}", response_model=schemas.FacturaElectronica , tags=["Facturas electronicas"])
async def actualizar_factura_manual(factura_id: int,
                                     factura: schemas.FacturaElectronicaUpdate, 
                                     db: AsyncSession = Depends(get_db),
                                     current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Actualiza una factura electronica  por su ID.
    Solo puede tener los parametros y debe tener todos los parametros  de FacturaElectronicaUpdate : 
    save_pdf
    categoria_id
    proyecto_id
    batch
    """
    db_factura = await crud_facturas_electronicas.get_factura_electronica(db, factura_id=factura_id,)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura manual no encontrada")
    
    proyecto = await crud_proyecto.get_proyecto(db, proyecto_id=db_factura.proyecto_id)
    if not proyecto or proyecto.propietario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para añadir facturas a este proyecto."
        )
    db_factura = await crud_facturas_electronicas.update_factura_electroncia(db, factura_id=factura_id, factura_update=factura)

    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura manual no encontrada")
    return db_factura

@router.delete("/electronicas/{factura_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Facturas electronicas"])
async def eliminar_factura_electronica(factura_id: int,
                                        db: AsyncSession = Depends(get_db),
                                        current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Elimina una factura electronica por su ID.
    """
    db_factura = await crud_facturas_electronicas.get_factura_electronica(db, factura_id=factura_id,)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura manual no encontrada")
    
    proyecto = await crud_proyecto.get_proyecto(db, proyecto_id=db_factura.proyecto_id)
    if not proyecto or proyecto.propietario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para añadir facturas a este proyecto."
        )
    db_factura = await crud_facturas_electronicas.delete_factura_electronica(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura Electronica no encontrada")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return

# faltaaaa

@router.get("/electronicas/check/{factura_id}",response_model=schemas.FacturaElectronica , tags=["Facturas electronicas"])
async def check_factura_electronica(factura_id: int,db:AsyncSession=Depends(get_db)):
    db_factura= await crud_facturas_electronicas.get_factura_electronica(db,factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura Electronica no encontrada")
    
    if db_factura.status_Getrequest == True and db_factura.status_PDFrequest == True and db_factura.status_Postrequest == True:
        print(f"tipo de dato de factura es {type(db_factura)}")
        factura_schema = schemas.FacturaElectronica.model_validate(db_factura)
        try:
            # intentar serealizar para no ahcer un schema nuevo
            contenido_serializable = {
                    "msg": "factura ya completada",
                    "factura": factura_schema.model_dump(mode="python") # o .dict() en Pydantic v1
                }
            
            contenido_serializable["factura"]['fecha']=contenido_serializable["factura"]['fecha'].isoformat()
        except:
            print("error al desearilizar la factura\n")
            contenido_serializable = {
                    "msg": "factura ya completada"}

        return JSONResponse(content=contenido_serializable)

    db_fact= await factura_service.tarea_de_scraping_y_actualizacion(factura_id,db_factura.url,db_factura.save_pdf)
    return db_fact


@router.get("/electronicas/checkforce/{factura_id}",response_model=schemas.FacturaElectronica , tags=["Facturas electronicas"])
async def check_factura_electronica(factura_id: int,db:AsyncSession=Depends(get_db)):

    db_factura= await crud_facturas_electronicas.get_factura_electronica(db,factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura Electronica no encontrada")


    db_fact= await factura_service.tarea_de_scraping_y_actualizacion(factura_id,db_factura.url,db_factura.save_pdf)

    return db_fact