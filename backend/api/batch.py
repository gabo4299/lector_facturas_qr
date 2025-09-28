from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import crud_batch
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.Batch, status_code=201)
async def crear_batch(batch: schemas.BatchCreate, db: AsyncSession = Depends(get_db)):
    # print("entro a post ",factura.model_dump())
    return await crud_batch.create_batch(db=db, batch=batch)

@router.get("/", response_model=List[schemas.Batch])
async def leer_batchs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    batchs = await crud_batch.get_batchs(db, skip=skip, limit=limit)
    return batchs

@router.get("/{batch_id}", response_model=schemas.Batch)
async def leer_batch(batch_id: int, db: AsyncSession = Depends(get_db)):
    db_batch = await crud_batch.get_batch(db, batch_id=batch_id)
    if db_batch is None:
        raise HTTPException(status_code=404, detail="batch no encontrado")
    return db_batch



@router.put("/{batch_id}", response_model=schemas.Batch, tags=["batch"])
async def actualizar_batch_manual(batch_id: int, batch: schemas.BatchBase, db: AsyncSession = Depends(get_db)):
    """
    Actualiza batch  por su ID. solo nombre y descripcion no id
    """
    db_batch = await crud_batch.update_batch(db, batch_id=batch_id, batch_update=batch)
    if db_batch is None:
        raise HTTPException(status_code=404, detail="batch no encontrado")
    return db_batch

@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["batch"])
async def eliminar_batch(batch_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina una factura electronica por su ID.
    """
    db_batch = await crud_batch.delete_batch(db, batch_id=batch_id)
    if db_batch is None:
        raise HTTPException(status_code=404, detail="batch no encontrado")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return