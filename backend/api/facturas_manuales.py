from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.api import auth
from backend.crud import crud_facturas_manuales,crud_proyecto
from backend.schemas import schemas
from backend.db import models
from backend.db.database import engine, AsyncSessionLocal
from datetime import timezone ,datetime
router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def parse_fecha(fecha_str):
    # Intentamos analizar la fecha en varios formatos posibles
    try:
        # Fecha sin hora (solo "2025-06-27")
        return datetime.strptime(fecha_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    
    try:
        # Fecha con hora en formato ISO (ej. "2025-06-27T04:00:00")
        return datetime.fromisoformat(fecha_str).astimezone(timezone.utc)
    except ValueError:
        pass
    
    try:
        # Fecha con zona horaria explícita (ej. "2025-06-27T04:00:00+02:00")
        return datetime.fromisoformat(fecha_str).astimezone(timezone.utc)
    except ValueError:
        pass
@router.post("/manuales/", response_model=schemas.FacturaManual, status_code=201)
async def crear_factura_manual(factura: schemas.FacturaManualCreate, 
                               db: AsyncSession = Depends(get_db),
                               current_user: models.User = Depends(auth.get_current_active_user)):
    proyecto = await crud_proyecto.get_proyecto(db, proyecto_id=factura.proyecto_id)
    if not proyecto or proyecto.propietario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para añadir facturas a este proyecto."
        )

    if factura.Nit_Beneficiario != proyecto.nit_beneficiario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El NIT de la factura ({factura.Nit_Beneficiario}) no coincide con el NIT del proyecto ({proyecto.nit_beneficiario})."
        )
    if not factura.fecha:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La factura debe tener una fecha para ser registrada en un proyecto."
        )
    
    if not (proyecto.fecha_inicio <= factura.fecha.replace(tzinfo=timezone.utc) <= proyecto.fecha_fin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La fecha de la factura ({factura.fecha.date()}) está fuera del rango del proyecto ({proyecto.fecha_inicio.date()} al {proyecto.fecha_fin.date()})."
        )

    # print("entro a post ",factura.model_dump())
    return await crud_facturas_manuales.create_factura_manual(db=db, factura=factura)

@router.get("/manuales/", response_model=List[schemas.FacturaManual])
async def leer_facturas_manuales(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    facturas = await crud_facturas_manuales.get_facturas_manuales(db, skip=skip, limit=limit)
    return facturas

@router.get("/manuales/{factura_id}", response_model=schemas.FacturaManual)
async def leer_factura_manual(factura_id: int, db: AsyncSession = Depends(get_db)):
    db_factura = await crud_facturas_manuales.get_factura_manual(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return db_factura

@router.put("/manuales/{factura_id}", response_model=schemas.FacturaManual,
             tags=["Facturas Manuales"],
             )
async def actualizar_factura_manual(factura_id: int, 
                                    factura: schemas.FacturaManualUpdate, 
                                    db: AsyncSession = Depends(get_db),
                                    current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Actualiza una factura manual por su ID.
    """
    db_factura = await crud_facturas_manuales.get_factura_manual(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura manual no encontrada")
    proyecto = await crud_proyecto.get_proyecto(db, proyecto_id=db_factura.proyecto_id)
    if not proyecto or proyecto.propietario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para añadir facturas a este proyecto."
        )

    if factura.fecha != None:
        
        if not (proyecto.fecha_inicio <= parse_fecha(factura.fecha.isoformat()) <= proyecto.fecha_fin):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La fecha de la factura ({factura.fecha.date()}) está fuera del rango del proyecto ({proyecto.fecha_inicio.date()} al {proyecto.fecha_fin.date()})."
            )
    
    db_factura = await crud_facturas_manuales.update_factura_manual(db, factura_id=factura_id, factura_update=factura)
    
    return db_factura

@router.delete("/manuales/{factura_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Facturas Manuales"])
async def eliminar_factura_manual(factura_id: int, db: AsyncSession = Depends(get_db),
                                  current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Elimina una factura manual por su ID.
    """
    db_factura = await crud_facturas_manuales.delete_factura_manual(db, factura_id=factura_id)
    if db_factura is None:
        raise HTTPException(status_code=404, detail="Factura manual no encontrada")
    # Para DELETE, no se devuelve contenido, solo un código de éxito 204.
    return
