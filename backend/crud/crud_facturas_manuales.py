# crud_facturas_manuales.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.models import FacturaManual,Proyecto,ProyectoUsuario
from backend.schemas.schemas import FacturaManualCreate
from backend.crud import crud_empresa
from sqlalchemy.orm import joinedload, selectinload 
# --- CRUD Factura Manual ---
async def get_factura_manual(db: AsyncSession, factura_id: int):
    """
    Busca una factura manual por ID, cargando explícitamente sus relaciones.
    """
    query = select(FacturaManual).options(
        # Carga el proyecto y, DENTRO del proyecto, carga sus relaciones
        joinedload(FacturaManual.proyecto).options(
            joinedload(Proyecto.propietario),
            selectinload(Proyecto.asociaciones_usuario).joinedload(ProyectoUsuario.usuario),
            selectinload(Proyecto.batches)
        ),
        # Carga las otras relaciones directas de la factura
        joinedload(FacturaManual.categoria),
        joinedload(FacturaManual.batch),
        joinedload(FacturaManual.empresa)
    ).filter(FacturaManual.id == factura_id)
    
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()

async def get_facturas_manuales(db: AsyncSession, 
                                skip: int = 0, limit: int = 100):
    """Obtiene una lista de facturas manuales con sus relaciones cargadas."""
    query = select(FacturaManual).options(
        joinedload(FacturaManual.proyecto).options(
            joinedload(Proyecto.propietario),
            selectinload(Proyecto.asociaciones_usuario).joinedload(ProyectoUsuario.usuario),
            selectinload(Proyecto.batches)
        ),
        joinedload(FacturaManual.categoria),
        joinedload(FacturaManual.batch),
        joinedload(FacturaManual.empresa)
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.unique().scalars().all()

async def create_factura_manual(db: AsyncSession, factura: FacturaManualCreate):
    # print(f"llego la factura {factura.Nit_Beneficiario}")
    datos_factura = factura.model_dump()
    nit_empresa = datos_factura.pop("nit_emisor", None)
    nombre_empresa = datos_factura.pop("nombre_empresa", None)
    
    db_factura = FacturaManual(**datos_factura)
    if nit_empresa:
        empresa_obj = await crud_empresa.get_or_create_empresa(
            db, nit=nit_empresa, nombre=nombre_empresa
        )
        # Asociamos la factura con la empresa encontrada o creada
        db_factura.empresa_id = empresa_obj.id
    db.add(db_factura)
    await db.commit()
    await db.refresh(db_factura)
    return await get_factura_manual(db, factura_id=db_factura.id)

async def update_factura_manual(db: AsyncSession, factura_id: int, factura_update: FacturaManualCreate):
    """
    Actualiza una factura manual existente en la base de datos.
    """
    
    db_factura = await get_factura_manual(db, factura_id=factura_id)
    if not db_factura:
        return None 

    # Actualiza los campos del modelo SQLAlchemy con los datos del schema Pydantic
    print(f"el factura update es:{factura_update}")
    for key, value in factura_update.model_dump(exclude_unset=True).items():
        setattr(db_factura, key, value)

    db.add(db_factura) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_factura) # Refresca la instancia con los nuevos datos de la DB
    return await get_factura_manual(db, factura_id=db_factura.id)

async def delete_factura_manual(db: AsyncSession, factura_id: int):
    """
    Elimina una factura manual de la base de datos.
    """
    # Busca la factura que se va a eliminar
    db_factura = await get_factura_manual(db, factura_id=factura_id)
    if not db_factura:
        return None # Retorna None si no se encontró

    await db.delete(db_factura) 
    await db.commit() 
    return await get_factura_manual(db, factura_id=db_factura.id)

