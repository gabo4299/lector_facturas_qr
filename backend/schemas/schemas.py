# schemas.py
from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional, List

from typing import Literal 



class ProyectoResumen(BaseModel):
    monto_total: float
    # En el futuro, podrías añadir más campos aquí:
    # cantidad_facturas: int
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int
    class Config:
        from_attributes = True

class EmpresaBase(BaseModel):
    nombre: str
    nit:str
    rubro: Optional[str] = None

class EmpresaUpdate(BaseModel):
    nombre: Optional[str]=None
    rubro: Optional[str] = None
class EmpresaCreate(EmpresaBase):
    pass

class Empresa(EmpresaBase):
    id: int
    class Config:
        from_attributes = True

class BatchBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
class BatchCreate(BatchBase):
    proyecto_id: int
class Batch(BatchBase):
    id: int
    proyecto_id: int
    class Config: from_attributes = True

class BatchResumen(BaseModel):
    # Usamos el schema 'Batch' existente para mostrar los datos del batch
    batch_info: Batch
    monto_total_batch: float = 0.0

    class Config:
        from_attributes = True
        
class UserBase(BaseModel):
    email: EmailStr
    name:Optional[str]=None

class UserUpdate(BaseModel):
    name:Optional[str]=None
class UserCreate(UserBase):
    # La contraseña solo se requiere al crear el usuario
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool #

    class Config:
        from_attributes = True

class MiembroSchema(BaseModel):
    rol: str
    usuario: User # Anidamos el schema de User completo

    class Config:
        from_attributes = True

class ProyectoBase(BaseModel):
    nombre: str
    fecha_inicio: datetime
    fecha_fin: datetime
    nit_beneficiario: str
class ProyectoCreate(ProyectoBase):
    # propietario_id: int por jwt ya no se necesita

    pass

class ProyectoUpdate(BaseModel):
    # Todos los campos son opcionales
    nombre: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    nit_beneficiario: Optional[str] = None
class Proyecto(ProyectoBase):
    id: int
    propietario: User # Relación anidada
    asociaciones_usuario: List[MiembroSchema] = []
    batches: List[Batch] = [] # Lista de batches
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str



class DetalleItem(BaseModel):
    detalle: str
    precio_unitario: Optional[float]=None
    cantidad: Optional[float]=None
    descuento:Optional[float]=None
    total: Optional[float]=None

# --- Factura Manual ---
class FacturaManualBase(BaseModel):
    Nit_Beneficiario: str
    monto_total: float
    fecha: Optional[datetime] = None
   

class FacturaManualCreate(FacturaManualBase):
    nit_emisor: Optional[str] = None
    nombre_empresa: Optional[str] = None
    proyecto_id: int
    categoria_id: Optional[int] = None
    batch_id: Optional[int] = None

class FacturaManualUpdate(BaseModel):
    monto_total: Optional[float] = None
    fecha: Optional[datetime] = None
    nit_emisor: Optional[str] = None # Para cambiar/asignar la empresa
    categoria_id: Optional[int] = None ## ver esto para despues
    batch_id: Optional[int] = None




class FacturaManual(FacturaManualBase):
    id: int
    fecha: Optional[datetime] = None
    empresa: Optional[Empresa] = None
    proyecto: Optional[Proyecto] = None
    categoria: Optional[Categoria] = None
    batch: Optional[Batch] = None
    class Config: from_attributes = True



class FacturaElectronicaInicial(BaseModel):
    url: str
    # Podrías añadir aquí los campos que el usuario sí puede definir al inicio
    # como proyecto_id o categoria_id si los conoce de antemano.
    save_pdf:Optional[bool]=False
    proyecto_id: int
    categoria_id: Optional[int] = None
    batch_id: Optional[int] = None

# --- Factura Electrónica ---
class FacturaElectronicaBase(BaseModel):
    url: str
    monto_total: Optional[float] = None
    Nit_Beneficiario: Optional[str] = None
    fecha: Optional[datetime] = None
    detalles: Optional[List[DetalleItem]] = None
    n_factura: Optional[int] = None
    monto_fiscal: Optional[float] = None
    factura_especial: Optional[bool] = False
    save_pdf:Optional[bool]=False
    #  aqui nos recomendaron 
    # empresa: Optional[str] = None
    # mejor solo un status mas limmpio 
    status: Optional[str] = "pendiente"
    complete:Optional[bool]=False
    # status_Getrequest:Optional[bool]=False
    # status_Postrequest:Optional[bool]=False
    # status_PDFrequest:Optional[bool]=False
    # msg_get_request:Optional[str] = None
    # msg_post_request:Optional[str] = None
    # msg_pdf_request:Optional[dict] = None
    pdfIO:Optional[str]=None
    # #####################################################################
    # batch: Optional[int] = None
    # categoria_id: Optional[int] = None
    # proyecto_id: Optional[int] = None
    class Config:
        from_attributes = True



class FacturaElectronicaCreate(FacturaElectronicaBase):
    nit_emisor: Optional[str] = None
    proyecto_id: int
    categoria_id: Optional[int] = None
    batch_id: Optional[int] = None
    
class FacturaElectronicaCreateScrapping(FacturaElectronicaBase):
    nit_emisor: Optional[str] = None
    empresa:Optional[str] = None
    proyecto_id: int
    categoria_id: Optional[int] = None
    batch_id: Optional[int] = None
    

class FacturaElectronica(FacturaElectronicaBase):
    id: int
    empresa: Optional[Empresa] = None
    fecha: Optional[datetime] = None
    proyecto: Optional[Proyecto] = None
    categoria: Optional[Categoria] = None
    batch: Optional[Batch] = None
    class Config:
        from_attributes = True


class FacturaElectronicaUpdate(BaseModel):
    # Solo incluye los campos que se pueden modificar.
    # Todos son opcionales para permitir actualizaciones parciales.
    save_pdf: Optional[bool] = None
    categoria_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    batch_id: Optional[int] = None



class FacturasDelProyectoResponse(BaseModel):
    """
    Schema para la respuesta que agrupa las facturas de un proyecto.
    """
    facturas_manuales: List[FacturaManual]
    facturas_electronicas: List[FacturaElectronica]


# Nuevo schema para la gestión de miembros
class MiembroProyecto(BaseModel):
    usuario_id: int
    # Usamos Literal para asegurar que el rol solo pueda ser 'editor' o 'lector'
    rol: Literal['editor', 'lector']

class MiembroProyectoUpdate(BaseModel):
    # Solo se puede actualizar el rol
    rol: Literal['editor', 'lector']


Proyecto.model_rebuild()
User.model_rebuild()
