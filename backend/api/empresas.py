from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import crud_empresa
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.Empresa, status_code=201)
async def crear_empresa(empresa: schemas.EmpresaCreate, db: AsyncSession = Depends(get_db)):
    # print("entro a post ",factura.model_dump())
    return await crud_empresa.create_empresa(db=db, empresa=empresa)

@router.get("/", response_model=List[schemas.Empresa])
async def leer_empresas(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    empresas = await crud_empresa.get_empresas(db, skip=skip, limit=limit)
    return empresas

@router.get("/{empresa_id}", response_model=schemas.Empresa)
async def leer_empresa(empresa_id: int, db: AsyncSession = Depends(get_db)):
    db_empresa = await crud_empresa.get_empresa(db, empresa_id=empresa_id)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="empresa no encontrado")
    return db_empresa



@router.put("/{empresa_id}", response_model=schemas.Empresa, tags=["empresa"])
async def actualizar_empresa_manual(empresa_id: int, empresa: schemas.Empresa, db: AsyncSession = Depends(get_db)):
    """
    Actualiza empresa  por su ID.
    """
    db_empresa = await crud_empresa.update_empresa(db, empresa_id=empresa_id, empresa_update=empresa)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="empresa no encontrado")
    return db_empresa

@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["empresa"])
async def eliminar_empresa(empresa_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina una factura electronica por su ID.
    """
    db_empresa = await crud_empresa.delete_empresa(db, empresa_id=empresa_id)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="empresa no encontrado")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return