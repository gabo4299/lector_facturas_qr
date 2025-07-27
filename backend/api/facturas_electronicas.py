from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import crud_facturas_electronicas
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/electronicas/", response_model=schemas.FacturaManual, status_code=201)
async def crear_factura_manual(factura: schemas.FacturaManualCreate, db: AsyncSession = Depends(get_db)):
    # print("entro a post ",factura.model_dump())
    return await crud_facturas_electronicas.create_factura_electronica(db=db, factura=factura)

@router.get("/electronicas/", response_model=List[schemas.FacturaManual])
async def leer_facturas_electronicas(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    facturas = await crud_facturas_electronicas.get_facturas_electronicas(db, skip=skip, limit=limit)
    return facturas

@router.get("/electronicas/{factura_id}", response_model=schemas.FacturaManual)
async def leer_factura_elctronica(factura_id: int, db: AsyncSession = Depends(get_db)):
    db_factura = await crud_facturas_electronicas.get_factura_electronica(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return db_factura



@router.put("/electronicas/{factura_id}", response_model=schemas.FacturaManual, tags=["Facturas electronicas"])
async def actualizar_factura_manual(factura_id: int, factura: schemas.FacturaManualCreate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza una factura electronica  por su ID.
    """
    db_factura = await crud_facturas_electronicas.update_factura_manual(db, factura_id=factura_id, factura_update=factura)
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
        raise HTTPException(status_code=404, detail="Factura manual no encontrada")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return
