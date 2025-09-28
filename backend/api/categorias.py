from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import crud_categoria
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.Categoria, status_code=201)
async def crear_categoria(categoria: schemas.CategoriaCreate, db: AsyncSession = Depends(get_db)):
    # print("entro a post ",factura.model_dump())
    return await crud_categoria.create_categoria(db=db, categoria=categoria)

@router.get("/", response_model=List[schemas.Categoria])
async def leer_categorias(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categorias = await crud_categoria.get_categorias(db, skip=skip, limit=limit)
    return categorias

@router.get("/{categoria_id}", response_model=schemas.Categoria)
async def leer_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    db_categoria = await crud_categoria.get_categoria(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="categoria no encontrado")
    return db_categoria



@router.put("/{categoria_id}", response_model=schemas.Categoria, tags=["categoria"])
async def actualizar_categoria_manual(categoria_id: int, categoria: schemas.CategoriaCreate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza categoria  por su ID.
    """
    db_categoria = await crud_categoria.update_categoria(db, categoria_id=categoria_id, categoria_update=categoria)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="categoria no encontrado")
    return db_categoria

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["categoria"])
async def eliminar_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina una factura electronica por su ID.
    """
    db_categoria = await crud_categoria.delete_categoria(db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="categoria no encontrado")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return