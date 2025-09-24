from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import crud_users
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.User, status_code=201)
async def crear_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # print("entro a post ",factura.model_dump())
    return await crud_users.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=schemas.User)
async def leer_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud_users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User no encontrado")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
async def eliminar_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina user ID.
    """
    db_proyecto = await crud_users.delete_user(db, user_id=user_id)
    if db_proyecto is None:
        raise HTTPException(status_code=404, detail="User no encontrado")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return