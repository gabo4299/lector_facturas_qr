# crud.py
from typing import List
import asyncio
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.database import AsyncSessionLocal
from backend.db.models import  FacturaElectronica,ProyectoUsuario,Proyecto
from backend.schemas.schemas import FacturaElectronicaCreate,FacturaElectronicaUpdate,FacturaElectronicaInicial
import backend.schemas.schemas as schemas
from backend.crud import crud_empresa,crud_proyecto,crud_categoria
from sqlalchemy.orm import joinedload,selectinload
from datetime import timezone,datetime
# from backend.services import 
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
# --- CRUD Factura electronica ---
async def get_factura_electronica(db: AsyncSession, factura_id: int) ->FacturaElectronica:
    query = select(FacturaElectronica).options(
        joinedload(FacturaElectronica.proyecto).options(
            joinedload(Proyecto.propietario),
            # Carga la lista de asociaciones y, dentro de cada una, el usuario.
            selectinload(Proyecto.asociaciones_usuario).joinedload(ProyectoUsuario.usuario),
            selectinload(Proyecto.batches) #
            
            ),
        joinedload(FacturaElectronica.categoria),
        joinedload(FacturaElectronica.batch),
        joinedload(FacturaElectronica.empresa)
    ).filter(FacturaElectronica.id == factura_id)
    
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()

async def get_facturas_electronicas(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(FacturaElectronica).options(
            
            joinedload(FacturaElectronica.proyecto).options(
            joinedload(Proyecto.propietario),
            # Carga la lista de asociaciones y, dentro de cada una, el usuario.
            selectinload(Proyecto.asociaciones_usuario).joinedload(ProyectoUsuario.usuario),
            selectinload(Proyecto.batches) #
            
            ),
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
    return await get_factura_electronica(db, factura_id=db_factura.id)


async def update_status_factura_electronica(db: AsyncSession, factura_id: int,
                                             Msg:str=None,status:bool=None) -> FacturaElectronica | None:
    
    if not Msg :
        return None
    db_factura = await get_factura_electronica(db, factura_id=factura_id)
    if not db_factura :
        return None 
    if status != None:
        db_factura.complete=status
    db_factura.status=Msg
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_factura) # Refresca la instancia con los nuevos datos de la DB
    return await get_factura_electronica(db, factura_id=db_factura.id)

async def update_rute_factura_electronica(db: AsyncSession, factura_id: int,
                                             ruta:str=None) -> FacturaElectronica | None:
    

    db_factura = await get_factura_electronica(db, factura_id=factura_id)
    if not db_factura :
        return None 

    db_factura.pdfIO=ruta   
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_factura) # Refresca la instancia con los nuevos datos de la DB
    return await get_factura_electronica(db, factura_id=db_factura.id)



async def update_factura_electroncia(db: AsyncSession, factura_id: int, factura_update: FacturaElectronicaUpdate) -> FacturaElectronica | None:
    '''Solo puede tener los parametros y debe tener todos los parametros  de FacturaElectronicaUpdate : 
    save_pdf
    categoria_id
    proyecto_id
    batch_id'''
    db_factura = await get_factura_electronica(db, factura_id=factura_id)
    if not db_factura:
        print("\n\n\n  no hay factura aa aa a \n")
        return None 

    # Actualiza los campos del modelo SQLAlchemy con los datos del schema Pydantic
    # print(f"el factura update es:{factura_update_data}")
    
    for key, value in factura_update.model_dump(exclude_unset=True).items():
        setattr(db_factura, key, value)

    db.add(db_factura) # Añade el objeto actualizado a la sesión
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_factura) # Refresca la instancia con los nuevos datos de la DB
    return await get_factura_electronica(db, factura_id=db_factura.id)



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
    


async def get_facturas_incompletas(db: AsyncSession,proyect_id:int,filtro_categoria:str="Invalidas") -> list[FacturaElectronica] | None:
    # 🚩
    """Busca  facturas electrónica incompletas y no validas."""
    cat= await   crud_categoria.get_or_create_categoria(db,filtro_categoria)
    query = select(FacturaElectronica).options(
            
            joinedload(FacturaElectronica.proyecto).options(
            joinedload(Proyecto.propietario),
            # Carga la lista de asociaciones y, dentro de cada una, el usuario.
            selectinload(Proyecto.asociaciones_usuario).joinedload(ProyectoUsuario.usuario),
            selectinload(Proyecto.batches) #
            
            ),
            joinedload(FacturaElectronica.categoria),
            joinedload(FacturaElectronica.batch),
            joinedload(FacturaElectronica.empresa)
        ).filter(FacturaElectronica.complete == False,
                 FacturaElectronica.proyecto_id == proyect_id,
                or_(
                    FacturaElectronica.categoria_id != cat.id,
                    FacturaElectronica.categoria_id == None
                    )
                )
    
    result = await db.execute(query)
    return result.unique().scalars().all()

async def set_error_Factura_Electronica(db:AsyncSession,facturaModel:FacturaElectronica,msg:str="error",tipo_error:int=1,categoria_name:str="Invalidas",categoria_desc:str="Facturas Invalidas"):
    
    if tipo_error ==1 :
        new_msg="ERROR_CRITICO: "+msg   
    else:
        new_msg=msg   
    
    categoria=await crud_categoria.get_or_create_categoria(db=db,name=categoria_name,description=categoria_desc)
    update_data=schemas.FacturaElectronicaCreate(url=facturaModel.url,proyecto_id=facturaModel.proyecto_id,
                                                 categoria_id=categoria.id,fecha=facturaModel.fecha,status=new_msg,monto_total=0.0,monto_fiscal=0.0).model_dump()
    update_data.pop("nit_emisor")
    for key, value in update_data.items():
        # print("los valores a actulizar \n",key , value)
        setattr(facturaModel, key, value)
    # guardando
    print("guardando factura empty")
    await db.commit()
    await db.refresh(facturaModel) # Refresca la instancia con los nuevos datos de la DB
    return await get_factura_electronica(db, factura_id=facturaModel.id)

async def get_facturas_electronicas_por_proyecto(db: AsyncSession, proyecto_id: int) -> List[FacturaElectronica]:
    """Obtiene todas las facturas electrónicas de un proyecto, con sus relaciones."""
    query = select(FacturaElectronica).options(
        joinedload(FacturaElectronica.categoria),
        joinedload(FacturaElectronica.batch),
        joinedload(FacturaElectronica.empresa)
    ).filter(FacturaElectronica.proyecto_id == proyecto_id)
    
    result = await db.execute(query)
    return result.unique().scalars().all()
async def update_factura_desde_scraping(db: AsyncSession, factura_id: int, datos_completos: schemas.FacturaElectronicaCreateScrapping):
    """Actualiza una factura con los datos obtenidos del scraping."""

    db_factura = await get_factura_electronica(db, factura_id=factura_id)
    proyecto = await crud_proyecto.get_proyecto(db, proyecto_id=db_factura.proyecto_id)
    if not db_factura:
        return None


    update_data = datos_completos.model_dump(exclude_unset=True)
    if update_data["Nit_Beneficiario"] != proyecto.nit_beneficiario:
        print("error de NITS")
        return await set_error_Factura_Electronica(db,db_factura,msg=f"nit beneficiario ({update_data['Nit_Beneficiario'] }) diferente a nit de proyecto {proyecto.nit_beneficiario} se recomienda eliminar")
    if update_data["fecha"] != None:
        
        if not (proyecto.fecha_inicio <= parse_fecha(update_data["fecha"].isoformat()) <= proyecto.fecha_fin):
            msg=f"La fecha de la factura ({update_data['fecha'].date()}) está fuera del rango del proyecto ({proyecto.fecha_inicio.date()} al {proyecto.fecha_fin.date()} se recomienda eliminar)."
            return await set_error_Factura_Electronica(db,db_factura,msg)
        
    else:
        print("error de fecha no hay ")
        return await set_error_Factura_Electronica(db,db_factura,msg=f"ERROR: No se introdujo fecha")

    nit_empresa = update_data.pop("nit_emisor", None)
    nombre_empresa = update_data.pop("empresa", None)
    
    for key, value in update_data.items():
        # print("los valores a actulizar \n",key , value)
        setattr(db_factura, key, value)
    if nit_empresa:
        empresa_obj = await crud_empresa.get_or_create_empresa(
            db, nit=nit_empresa, nombre=nombre_empresa
        )
        # Asociamos la factura con la empresa encontrada o creada
        db_factura.empresa_id = empresa_obj.id

    # print("factura nueva \n\n\n\n",db_factura)
    await db.commit()
    await db.refresh(db_factura) # Refresca la instancia con los nuevos datos de la DB
    return await get_factura_electronica(db, factura_id=db_factura.id)




async def bloquear_factura(db: AsyncSession, factura_id: int):
    db_factura = await get_factura_electronica(db, factura_id=factura_id)
    if not db_factura :
        return None 
    db_factura.status="procesando"
    await db.commit() # Confirma los cambios en la base de datos
    await db.refresh(db_factura) # Refresca la instancia con los nuevos datos de la DB
    return await get_factura_electronica(db, factura_id=db_factura.id)
    
async def obtener_y_bloquear_facturas_para_procesar(db: AsyncSession, proyecto_id: int,filtro_categoria:str="Invalidas") -> List[FacturaElectronica]:
    """
    Busca todas las facturas de un proyecto que necesitan ser procesadas ('pendiente' o 'error'),
    las actualiza atómicamente a 'procesando' y las devuelve.
    """
    # 1. Identificamos las facturas candidatas
    cat_x=await crud_categoria.get_or_create_categoria(db,filtro_categoria)
    query = select(FacturaElectronica).where(
        and_(
            FacturaElectronica.proyecto_id == proyecto_id,
            FacturaElectronica.complete!= True,
            or_(
                FacturaElectronica.categoria_id != cat_x.id,
                FacturaElectronica.categoria_id == None
            ),
            FacturaElectronica.status!="procesando"

        )
    ).with_for_update() # Bloquea las filas para evitar que otro proceso las toque

    result = await db.execute(query)
    facturas_para_procesar = result.scalars().all()

    if not facturas_para_procesar:
        return []

    # 2. Cambiamos su estado a 'procesando'
    for factura in facturas_para_procesar:
        factura.status = "procesando"
    
    # 3. Guardamos los cambios en la base de datos
    await db.commit()

    # Devolvemos la lista de facturas que acabamos de bloquear
    return facturas_para_procesar




