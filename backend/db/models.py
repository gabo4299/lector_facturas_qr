# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, LargeBinary,ForeignKey
from .database import Base
from sqlalchemy.orm import relationship 
from sqlalchemy.dialects.postgresql import JSONB
import datetime

class FacturaManual(Base):
    __tablename__ = "facturas_manuales"

    id = Column(Integer, primary_key=True, index=True)
    Nit_Beneficiario = Column(String, nullable=False)
    monto_total = Column(Float, nullable=False)
    fecha = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    empresa = Column(String, nullable=True)
    
    batch = Column(String, nullable=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id",ondelete="SET NULL"), nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id",ondelete="CASCADE"), nullable=True)
    
    # Relaciones que permiten acceder a los objetos completos
    # ej: mi_factura.categoria.nombre
    categoria = relationship("Categoria", back_populates="facturas_manuales")
    proyecto = relationship("Proyecto", back_populates="facturas_manuales")

class FacturaElectronica(Base):
    __tablename__ = "facturas_electronicas"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False,unique=True, index=True)
    monto_total = Column(Float, nullable=False)
    Nit_Beneficiario = Column(String, nullable=True)
    fecha = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    empresa = Column(String, nullable=True)
    detalles = Column(JSONB, nullable=True,default=None) 
    n_factura = Column(Integer, nullable=True)
    monto_fiscal = Column(Float, nullable=True)
    nit_emisor = Column(String, nullable=True)
    factura_especial = Column(Boolean, default=False)
    status_Getrequest=Column(Boolean,default=False)
    status_Postrequest=Column(Boolean,default=False)
    status_PDFrequest=Column(Boolean,default=False)
    msg_get_request=Column(String,nullable=True)
    msg_post_request=Column(String,nullable=True)
    msg_pdf_request=Column(JSONB,nullable=True)
    pdfIO=Column(String,nullable=True)
    save_pdf=Column(Boolean,default=False)
    batch = Column(Integer, nullable=True, index=True)

    categoria_id = Column(Integer, ForeignKey("categorias.id",ondelete="SET NULL"), nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id",ondelete="CASCADE"), nullable=True)

    categoria = relationship("Categoria", back_populates="facturas_electronicas")
    proyecto = relationship("Proyecto", back_populates="facturas_electronicas")

class User(Base):
     __tablename__ = "usuarios"
     id = Column(Integer, primary_key=True, index=True)
     email=Column(String, nullable=False)
     password=Column(String, nullable=False)
     name=Column(String, nullable=False)
     is_active = Column(Boolean, default=True)




class Empresa(Base):
     __tablename__ = "empresas"
     id = Column(Integer, primary_key=True, index=True)
     nombre=Column(String, index=True, nullable=False)
     nit=Column(String, unique=True, index=True, nullable=False)



class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)

    # Relación inversa: una categoría puede tener muchas facturas
    facturas_manuales = relationship("FacturaManual", back_populates="categoria")
    facturas_electronicas = relationship("FacturaElectronica", back_populates="categoria")

class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    fecha_inicio=Column(DateTime(timezone=True), nullable=False)
    fecha_fin=Column(DateTime(timezone=True), nullable=False)
    # Relación inversa: un proyecto puede tener muchas facturas
    facturas_manuales = relationship(
        "FacturaManual", 
        back_populates="proyecto",
        # Le dice a SQLAlchemy que aplique operaciones (como delete) a los hijos
        cascade="all, delete-orphan",
        # Le dice a SQLAlchemy que confíe en la DB para las eliminaciones en cascada
        passive_deletes=True,
    )
    facturas_electronicas = relationship(
        "FacturaElectronica", 
        back_populates="proyecto",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )