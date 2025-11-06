# schemas.py
from pydantic import BaseModel,EmailStr, Field, computed_field

from datetime import date, datetime
from typing import Optional, List, Union,Annotated 

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
class CategoriaPaginada(BaseModel):
    items: list[Categoria]
    total: int
    page: int
    size: int
    pages: int
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

class EmpresasPaginada(BaseModel):
    items: list[Empresa]
    total: int
    page: int
    size: int
    pages: int



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
    cantidad_facturas:Optional[int]=0
    cantidad_manuales:Optional[int] =0
    cantidad_electronicas:Optional[int] =0

    class Config:
        from_attributes = True

class CategoriaResumen(BaseModel):
    # Usamos el schema 'Batch' existente para mostrar los datos del batch
    categoria_info: Categoria
    monto_total_categoria: float = 0.0
    cantidad_facturas:Optional[int]=0
    cantidad_manuales:Optional[int] =0
    cantidad_electronicas:Optional[int] =0

    class Config:
        from_attributes = True

class EmpresaResumen(BaseModel):
    # Usamos el schema 'Batch' existente para mostrar los datos del batch
    empresa_info: Empresa
    monto_total_empresa: float = 0.0
    cantidad_facturas:Optional[int]=0
    cantidad_manuales:Optional[int] =0
    cantidad_electronicas:Optional[int] =0

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

class UserPaginada(BaseModel):
    items: list[User]
    total: int
    page: int
    size: int
    pages: int
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

class ProyectoAdminInfo(Proyecto):
    """
    Hereda de Proyecto y añade campos calculados para vistas de administrador.
    """
    total_facturas: int = 0
    suma_total_facturas: float = 0.0

class PaginatedProyectosAdminResponse(BaseModel):
    items: List[ProyectoAdminInfo]
    total: int
    page: int
    size: int
    pages: int
class ProyectoInfo(Proyecto):
    suma_total:Optional[float] = None
    suma_fiscal:Optional[float] = None
    cantidad_facturas_electronicas:Optional[int] = None
    cantidad_facturas_manuales:Optional[int] = None
    suma_facturas_electronicas:Optional[float] = None
    suma_facturas_manuales:Optional[float] = None
    porcentajeGanado:Optional[float] = None
    batches: List[BatchResumen] = []
    empresas:Optional [List[EmpresaResumen]]=[]
    categorias:Optional [List[CategoriaResumen]]=[]

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
    tipo: Literal["manual"] = "manual" 
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
    tipo: Literal["electronica"] = "electronica"
    url: str
    monto_total: Optional[float] = None
    Nit_Beneficiario: Optional[str] = None
    fecha: Optional[datetime] = None
    detalles: Optional[List[DetalleItem]] = None
    n_factura: Optional[int] = None
    monto_fiscal: Optional[float] = None
    factura_especial: Optional[bool] = False
    save_pdf:Optional[bool]=False
    status: Optional[str] = "pendiente"
    complete:Optional[bool]=False
    pdfIO:Optional[str]=None
    #  aqui nos recomendaron 
    # empresa: Optional[str] = None
    # mejor solo un status mas limmpio 
    # status_Getrequest:Optional[bool]=False
    # status_Postrequest:Optional[bool]=False
    # status_PDFrequest:Optional[bool]=False
    # msg_get_request:Optional[str] = None
    # msg_post_request:Optional[str] = None
    # msg_pdf_request:Optional[dict] = None
    
    # #####################################################################
    # batch: Optional[int] = None
    # categoria_id: Optional[int] = None
    # proyecto_id: Optional[int] = None
    # class Config:
    #     from_attributes = True



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
    email:str
    # Usamos Literal para asegurar que el rol solo pueda ser 'editor' o 'lector'
    rol: Literal['editor', 'lector']

class MiembroProyectoUpdate(BaseModel):
    # Solo se puede actualizar el rol
    rol: Literal['editor', 'lector']



class FiltrosFactura(BaseModel):
    # Un flag para elegir el tipo de factura
    tipo_factura: Optional[Literal['todas', 'manual', 'electronica']] = 'todas'
    
    # Filtros comunes
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    monto_min: Optional[float] = None
    monto_max: Optional[float] = None
    categoria_id: Optional[int] = None
    empresa_id: Optional[int] = None
    batch_id: Optional[int] = None
    
    # Filtros específicos de FacturaElectronica
    complete: Optional[bool] = None
    factura_especial: Optional[bool] = None
    factura_virtual: Optional[bool] = None
        # Parámetros de Paginación
    page: int = 1
    size: int = 20
    
    # Parámetros de Ordenamiento
    sort_by: Literal['fecha', 'monto_total','empresa', 'categoria', 'batch','fecha_creacion'] = 'fecha'
    sort_order: Literal['asc', 'desc'] = 'desc'

    # Parámetro de Filtro de Proyecto (opcional)
    proyecto_id: Optional[int] = None


FacturaUnion = Union[FacturaManual, FacturaElectronica]
# --- Schema para la Respuesta Paginada ---
class PaginatedFacturasResponse(BaseModel):
    total: int
    items: List[Annotated[FacturaUnion, Field(discriminator='tipo')]]
    page:Optional [int]
    size: Optional[int]
    total_pages: Optional[int]

    
class GoogleLoginRequest(BaseModel):
    code: str
    
Proyecto.model_rebuild()
User.model_rebuild()
