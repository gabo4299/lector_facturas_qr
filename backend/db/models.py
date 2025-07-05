# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from .database import Base
import datetime

class FacturaManual(Base):
    __tablename__ = "facturas_manuales"

    id = Column(Integer, primary_key=True, index=True)
    Nit_Beneficiario = Column(String, nullable=False)
    monto_total = Column(Float, nullable=False)
    fecha = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    empresa = Column(String, nullable=True)

class FacturaElectronica(Base):
    __tablename__ = "facturas_electronicas"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    monto_total = Column(Float, nullable=False)
    Nit_Beneficiario = Column(String, nullable=True)
    fecha = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    empresa = Column(String, nullable=True)
    # detalles: lo manejaremos como un string simple, o podrías usar JSON
    detalles = Column(String, nullable=True) 
    n_factura = Column(Integer, nullable=True)
    monto_fiscal = Column(Float, nullable=True)
    nit_emisor = Column(String, nullable=True)
    factura_especial = Column(Boolean, default=False)