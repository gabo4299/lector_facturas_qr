# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.models import  FacturaElectronica
from backend.schemas.schemas import FacturaElectronicaCreate,FacturaElectronicaUpdate
# from backend.services import 

# --- CRUD Factura electronica ---
async def get_factura_electronica(db: AsyncSession, factura_id: int):
    result = await db.execute(select(FacturaElectronica).filter(FacturaElectronica.id == factura_id))
    return result.scalar_one_or_none()

async def get_facturas_electronicas(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(FacturaElectronica).offset(skip).limit(limit))
    return result.scalars().all()

async def create_factura_electronica(db: AsyncSession, factura: FacturaElectronicaCreate):
    


    db_factura = FacturaElectronica(**factura.model_dump())
    db.add(db_factura)
    await db.commit()
    await db.refresh(db_factura)
    return db_factura


async def update_factura_electroncia(db: AsyncSession, factura_id: int, factura_update_data: FacturaElectronicaUpdate):
    '''Solo puede tener los parametros y debe tener todos los parametros  de FacturaElectronicaUpdate : 
    save_pdf
    categoria_id
    proyecto_id
    batch'''
    db_factura = await get_factura_electronica(db, factura_id=factura_id)
    if not db_factura:
        return None 

    # Actualiza los campos del modelo SQLAlchemy con los datos del schema Pydantic
    # print(f"el factura update es:{factura_update_data}")
    
    for key, value in factura_update_data.model_dump(exclude_unset=True).items():
        setattr(db_factura, key, value)

    db.add(db_factura) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_factura) # Refresca la instancia con los nuevos datos de la DB
    return db_factura



async def delete_factura_electronica(db: AsyncSession, factura_id: int):
    """
    Elimina una factura manual de la base de datos.
    """
    # Busca la factura que se va a eliminar
    db_factura = await get_factura_electronica(db, factura_id=factura_id)
    if not db_factura:
        return None # Retorna None si no se encontró

    await db.delete(db_factura) 
    await db.commit() 
    return db_factura 



