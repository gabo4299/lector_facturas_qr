# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- Factura Manual ---
class FacturaManualBase(BaseModel):
    Nit_Beneficiario: str
    monto_total: float
    fecha: Optional[datetime] = None
    empresa: Optional[str] = None

class FacturaManualCreate(FacturaManualBase):
    pass

class FacturaManual(FacturaManualBase):
    id: int
    class Config:
        from_attributes = True # Anteriormente orm_mode

# --- Factura Electrónica ---
class FacturaElectronicaBase(BaseModel):
    url: str
    monto_total: Optional[float] = None
    Nit_Beneficiario: Optional[str] = None
    fecha: Optional[datetime] = None
    empresa: Optional[str] = None
    detalles: Optional[List[str]] = None
    n_factura: Optional[int] = None
    monto_fiscal: Optional[float] = None
    nit_emisor: Optional[str] = None
    factura_especial: Optional[bool] = False
    pdfIO:Optional[bytes]=None
    status_Getrequest:Optional[bool]=False
    status_Postrequest:Optional[bool]=False
    status_PDFrequest:Optional[bool]=False

class FacturaElectronicaCreate(FacturaElectronicaBase):
    pass

class FacturaElectronica(FacturaElectronicaBase):
    id: int
    class Config:
        from_attributes = True