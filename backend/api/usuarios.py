from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.crud import crud_users
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal
from backend.db import models
from backend.api import auth
router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.User, status_code=201)
async def crear_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # print("entro a post ",factura.model_dump())
    return await crud_users.create_user(db=db, user=user)


@router.get("/paginated", response_model=schemas.UserPaginada)
async def leer_usuarios_paginados(
                     db: AsyncSession = Depends(get_db),
                     current_user: models.User = Depends(auth.get_current_active_user),
                     search: str | None = None,
                    page: int = 1,
                    size: int = 10,
                    sort_by: str = "id", # Por defecto ordena por id
                    sort_order: str = "asc"):
    
    if current_user.is_superuser:
        usuarios=await crud_users.get_users_paginacion(db,search=search,page=page,size=size,sort_by=sort_by,sort_order=sort_order)
        return usuarios

    else:
        raise HTTPException(status_code=403, detail="No eres Admin")
    
    

@router.get("/{user_id}", response_model=schemas.User)
async def leer_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud_users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User no encontrado")
    return db_user


@router.put("/{user_id}", response_model=schemas.User, tags=["User"])
async def editar(user_id: int,
                 usuarioUpdate:schemas.UserUpdate, db: AsyncSession = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_active_user)):
    """
    editar user .
    """
    print("editanodoooooo")
    if int(current_user.id) == user_id or current_user.is_superuser == True:
        db_user = await crud_users.update_user(db, user_id=user_id,user_update_data=usuarioUpdate)
        
        if db_user is None:
            raise HTTPException(status_code=404, detail="User no encontrado")
        return db_user
    
    raise HTTPException(status_code=403, detail="No tienes permisos")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
async def eliminar_user(user_id: int, db: AsyncSession = Depends(get_db),
                        current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Elimina user ID.
    """
    if int(current_user.id) == user_id or current_user.is_superuser == True:
        db_user = await crud_users.delete_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User no encontrado")
        return
    
    raise HTTPException(status_code=403, detail="No tienes permisos")