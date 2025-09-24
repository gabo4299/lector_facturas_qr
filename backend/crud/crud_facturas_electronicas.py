# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.models import  FacturaElectronica
from backend.schemas.schemas import FacturaElectronicaCreate,FacturaElectronicaUpdate,FacturaElectronicaInicial
from sqlalchemy.orm import joinedload
# from backend.services import 

# --- CRUD Factura electronica ---
async def get_factura_electronica(db: AsyncSession, factura_id: int) ->FacturaElectronicaCreate:
    query = select(FacturaElectronica).options(
        joinedload(FacturaElectronica.proyecto),
        joinedload(FacturaElectronica.categoria),
        joinedload(FacturaElectronica.batch),
        joinedload(FacturaElectronica.empresa)
    ).filter(FacturaElectronica.id == factura_id)
    
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()

async def get_facturas_electronicas(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(FacturaElectronica).options(
            joinedload(FacturaElectronica.proyecto),
            joinedload(FacturaElectronica.categoria),
            joinedload(FacturaElectronica.batch),
            joinedload(FacturaElectronica.empresa)
        ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.unique().scalars().all()

async def create_factura_electronica(db: AsyncSession, factura: FacturaElectronicaCreate):
    


    db_factura = FacturaElectronica(**factura.model_dump())
    db.add(db_factura)
    await db.commit()
    await db.refresh(db_factura)
    return await get_factura_electronica(db, factura_id=db_factura.id)


async def create_factura_electronica_inicial(db: AsyncSession, factura: FacturaElectronicaInicial):
    """Crea la factura con datos mínimos y un estado 'procesando'."""
    db_factura = FacturaElectronica(
        **factura.model_dump(),
        monto_total=0.0 
    )
    db.add(db_factura)
    await db.commit()
    await db.refresh(db_factura)
    print("\n \n \n \n  se creoo la factura en dvb s \n \n \n \n")
    await get_factura_electronica(db, factura_id=db_factura.id)


async def update_factura_electroncia(db: AsyncSession, factura_id: int, factura_update: FacturaElectronicaUpdate):
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
    
    for key, value in factura_update.model_dump(exclude_unset=True).items():
        setattr(db_factura, key, value)

    db.add(db_factura) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_factura) # Refresca la instancia con los nuevos datos de la DB
    await get_factura_electronica(db, factura_id=db_factura.id)



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



async def get_factura_electronica_by_url(db: AsyncSession, url: str):
    """Busca una factura electrónica por su URL."""
    query = select(FacturaElectronica).options(
        joinedload(FacturaElectronica.proyecto),
        joinedload(FacturaElectronica.categoria),
        joinedload(FacturaElectronica.batch),
        joinedload(FacturaElectronica.empresa)
    ).filter(FacturaElectronica.url == url)
    
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()
    

async def update_factura_desde_scraping(db: AsyncSession, factura_id: int, datos_completos: FacturaElectronicaCreate):
    """Actualiza una factura con los datos obtenidos del scraping."""
    db_factura = await get_factura_electronica(db, factura_id=factura_id)
    if not db_factura:
        return None

    update_data = datos_completos.model_dump()
    for key, value in update_data.items():
        setattr(db_factura, key, value)
    
    await db.commit()
    return await get_factura_electronica(db, factura_id=db_factura.id)
