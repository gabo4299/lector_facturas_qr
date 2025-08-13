# schemas.py
from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional, List


class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int
    class Config:
        from_attributes = True

class ProyectoBase(BaseModel):
    nombre: str
    fecha_inicio:Optional[datetime] = None
    fecha_fin:Optional[datetime] = None


class ProyectoCreate(ProyectoBase):
    pass

class Proyecto(ProyectoBase):
    id: int
    class Config:
        from_attributes = True


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
    empresa: Optional[str] = None
    batch: Optional[int] = None
    # Al crear, esperamos recibir los IDs de la categoría y el proyecto
    categoria_id: Optional[int] = None
    proyecto_id: Optional[int] = None

class FacturaManualCreate(FacturaManualBase):
    pass

class FacturaManual(FacturaManualBase):
    id: int
    # #ver si da esto de fecha
    # fecha: datetime
    # Al leer, devolvemos los objetos completos anidados
    categoria: Optional[Categoria] = None
    proyecto: Optional[Proyecto] = None
    class Config:
        from_attributes = True # Anteriormente orm_mode


# --- Factura Electrónica ---
class FacturaElectronicaBase(BaseModel):
    url: str
    monto_total: Optional[float] = None
    Nit_Beneficiario: Optional[str] = None
    fecha: Optional[datetime] = None
    empresa: Optional[str] = None
    detalles: Optional[List[DetalleItem]] = None
    n_factura: Optional[int] = None
    monto_fiscal: Optional[float] = None
    nit_emisor: Optional[str] = None
    factura_especial: Optional[bool] = False
    save_pdf:Optional[bool]=False
    status_Getrequest:Optional[bool]=False
    status_Postrequest:Optional[bool]=False
    status_PDFrequest:Optional[bool]=False
    msg_get_request:Optional[str] = None
    msg_post_request:Optional[str] = None
    msg_pdf_request:Optional[dict] = None
    pdfIO:Optional[bytes]=None
    # #####################################################################
    batch: Optional[int] = None
    categoria_id: Optional[int] = None
    proyecto_id: Optional[int] = None

class FacturaElectronicaInicial(BaseModel):
    url: str
    # Podrías añadir aquí los campos que el usuario sí puede definir al inicio
    # como proyecto_id o categoria_id si los conoce de antemano.
    save_pdf:Optional[bool]=False
    proyecto_id: Optional[int] = None
    categoria_id: Optional[int] = None
class FacturaElectronicaCreate(FacturaElectronicaBase):
    pass

class FacturaElectronica(FacturaElectronicaBase):
    id: int
    class Config:
        from_attributes = True


class FacturaElectronicaUpdate(BaseModel):
    # Solo incluye los campos que se pueden modificar.
    # Todos son opcionales para permitir actualizaciones parciales.
    save_pdf: Optional[bool] = None
    categoria_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    batch: Optional[int] = None





class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    # La contraseña solo se requiere al crear el usuario
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True



class EmpresaBase(BaseModel):
    nombre: str
    nit:str

class EmpresaCreate(EmpresaBase):
    pass

class Empresa(EmpresaBase):
    id: int
    class Config:
        from_attributes = True