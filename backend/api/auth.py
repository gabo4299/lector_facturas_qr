# backend/api/auth.py
import asyncio
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import google_auth_oauthlib
from google.oauth2.id_token import verify_oauth2_token
from google.auth.transport.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError,jwt


from backend.crud import crud_users
from backend.schemas import schemas
from backend import auth
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal

from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Le decimos a FastAPI dónde está el endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await crud_users.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email,"fullName":user.name,"is_su":user.is_superuser})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await crud_users.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


async def get_current_superuser(current_user: models.User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Se requieren permisos de administrador para esta acción."
        )
    return current_user


@router.post("/google", response_model=schemas.Token)
async def login_with_google(
    request: schemas.GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Recibe el código de autorización de Google, lo verifica,
    obtiene/crea el usuario y devuelve un token JWT de nuestra aplicación.
    """
    try:
        # 1. Intercambia el código de autorización por un token de ID
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'client_secret.json', # Debes crear este archivo JSON con tus credenciales
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
        )
        # flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        
        
        # Esta llamada es síncrona, la ejecutamos en un hilo para no bloquear
        flow.redirect_uri = 'postmessage'
        # print(f"llegando el codigo {request.code}")
        await asyncio.to_thread(
            flow.fetch_token,
            code=request.code
        )
        credentials = flow.credentials
        # print(f"credentials {credentials}")
        id_info = verify_oauth2_token(
            credentials.id_token, Request(), os.getenv("GOOGLE_CLIENT_ID")
        )
        

        # El email es la pieza clave
        user_email = id_info.get("email")
        # print(f"user :{id_info}")
        if not user_email:
            raise HTTPException(status_code=400, detail="No se pudo obtener el email de Google.")

        # 3. Busca o crea el usuario en tu propia base de datos
        user = await crud_users.get_or_create_user_by_google(db, google_user_info=id_info)

        # 4. Crea un token JWT para TU aplicación
        access_token = auth.create_access_token(data={"sub": user.email,"fullName":user.name,"is_su":user.is_superuser})
        
        # 5. Devuelve TU token JWT, no el de Google
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print(f"No se pudo validar con Google: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo validar con Google: {e}"
        )