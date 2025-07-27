from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import crud_proyecto
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.Proyecto, status_code=201)
async def crear_proyecto(proyecto: schemas.ProyectoCreate, db: AsyncSession = Depends(get_db)):
    # print("entro a post ",factura.model_dump())
    return await crud_proyecto.create_proyecto(db=db, proyecto=proyecto)

@router.get("/", response_model=List[schemas.Proyecto])
async def leer_proyectos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    proyectos = await crud_proyecto.get_proyectos(db, skip=skip, limit=limit)
    return proyectos

@router.get("/{proyecto_id}", response_model=schemas.Proyecto)
async def leer_proyecto(proyecto_id: int, db: AsyncSession = Depends(get_db)):
    db_proyecto = await crud_proyecto.get_proyecto(db, proyecto_id=proyecto_id)
    if db_proyecto is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return db_proyecto



@router.put("/{proyecto_id}", response_model=schemas.Proyecto, tags=["Proyecto"])
async def actualizar_proyecto_manual(proyecto_id: int, proyecto: schemas.Proyecto, db: AsyncSession = Depends(get_db)):
    """
    Actualiza Proyecto  por su ID.
    """
    db_proyecto = await crud_proyecto.update_proyecto(db, proyecto_id=proyecto_id, proyecto_update=proyecto)
    if db_proyecto is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return db_proyecto

@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Proyecto"])
async def eliminar_proyecto(proyecto_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina una factura electronica por su ID.
    """
    db_proyecto = await crud_proyecto.delete_proyecto(db, proyecto_id=proyecto_id)
    if db_proyecto is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return