from fastapi import APIRouter, Depends, HTTPException,status,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.services import factura_service

from backend.crud import crud_facturas_electronicas
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/electronicas/", response_model=schemas.FacturaElectronica, status_code=202)
async def crear_factura_electronica(
    factura_inicial: schemas.FacturaElectronicaInicial, # Un nuevo schema solo con la URL
    background_tasks: BackgroundTasks, # Inyectamos la dependencia
    db: AsyncSession = Depends(get_db)):
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
    factura_creada = await crud_facturas_electronicas.create_factura_electronica_inicial(db=db, factura=factura_inicial)
    # 2. Añade la tarea de larga duración al segundo plano.
    #    Esta función se ejecutará DESPUÉS de que la respuesta haya sido enviada.
    background_tasks.add_task(
        factura_service.tarea_de_scraping_y_actualizacion, # La función a ejecutar
        factura_id=factura_creada.id, # Argumentos para la función
        url=factura_creada.url
    )
    return factura_creada
    # return await crud_facturas_electronicas.create_factura_electronica(db=db, factura=factura)

@router.get("/electronicas/", response_model=List[schemas.FacturaElectronica])
async def leer_facturas_electronicas(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    facturas = await crud_facturas_electronicas.get_facturas_electronicas(db, skip=skip, limit=limit)
    return facturas

@router.get("/electronicas/{factura_id}", response_model=schemas.FacturaElectronica)
async def leer_factura_elctronica(factura_id: int, db: AsyncSession = Depends(get_db)):
    db_factura = await crud_facturas_electronicas.get_factura_electronica(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return db_factura



@router.put("/electronicas/{factura_id}", response_model=schemas.FacturaElectronica , tags=["Facturas electronicas"])
async def actualizar_factura_manual(factura_id: int, factura: schemas.FacturaElectronicaUpdate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza una factura electronica  por su ID.
    Solo puede tener los parametros y debe tener todos los parametros  de FacturaElectronicaUpdate : 
    save_pdf
    categoria_id
    proyecto_id
    batch
    """
    db_factura = await crud_facturas_electronicas.update_factura_electroncia(db, factura_id=factura_id, factura_update=factura)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura manual no encontrada")
    return db_factura

@router.delete("/electronicas/{factura_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Facturas electronicas"])
async def eliminar_factura_electronica(factura_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina una factura electronica por su ID.
    """
    db_factura = await crud_facturas_electronicas.delete_factura_electronica(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura Electronica no encontrada")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return


@router.get("/electronicas/check/{factura_id}",response_model=schemas.FacturaElectronica , tags=["Facturas electronicas"])
async def check_factura_electronica(factura_id: int,db:AsyncSession=Depends(get_db)):
    db_factura= await crud_facturas_electronicas.get_factura_electronica(db,factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura Electronica no encontrada")
    
    if db_factura.status_Getrequest == True and db_factura.status_PDFrequest == True and db_factura.status_Postrequest == True:
        
        return db_factura

    db_fact= await factura_service.tarea_de_scraping_y_actualizacion(factura_id,db_factura.url)
    return db_fact