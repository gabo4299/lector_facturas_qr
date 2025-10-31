# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, LargeBinary,ForeignKey,Table, func
from .database import Base
from sqlalchemy.orm import relationship 
from sqlalchemy.dialects.postgresql import JSONB
import datetime
#antes 
# proyecto_usuarios_association = Table('proyecto_usuarios', Base.metadata,
#     Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), primary_key=True),
#     Column('proyecto_id', Integer, ForeignKey('proyectos.id', ondelete="CASCADE"), primary_key=True)
# )

# despues 

class ProyectoUsuario(Base):
    __tablename__ = 'proyecto_usuarios'
    proyecto_id = Column(Integer, ForeignKey('proyectos.id', ondelete="CASCADE"), primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), primary_key=True)
    rol = Column(String, nullable=False, default='lector') # Roles: 'dueño', 'editor', 'lector'
    
    # Relaciones para navegar desde esta tabla
    proyecto = relationship("Proyecto", back_populates="asociaciones_usuario")
    usuario = relationship("User", back_populates="asociaciones_proyecto")


class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email=Column(String, nullable=False,unique=True)
    password=Column(String, nullable=False)
    name=Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False) # <-- NUEVO CAMPO
    # Relación para los proyectos que ESTE usuario posee
    proyectos_propios = relationship("Proyecto", back_populates="propietario")
    # antes    
    # # --- NUEVA RELACIÓN MUCHOS-A-MUCHOS ---
    # # Relación para los proyectos en los que ESTE usuario colabora
    # proyectos_colabora = relationship(
    #     "Proyecto",
    #     secondary=proyecto_usuarios_association, # Usa la tabla de asociación
    #     back_populates="miembros"
    # )
    # despues
    asociaciones_proyecto = relationship("ProyectoUsuario", back_populates="usuario")


    
class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    fecha_inicio=Column(DateTime(timezone=True), nullable=False)
    fecha_fin=Column(DateTime(timezone=True), nullable=False)
    propietario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nit_beneficiario=Column(String, nullable=True)
    # Relación con el único dueño del proyecto
    propietario = relationship("User", back_populates="proyectos_propios")
    batches = relationship("Batch", back_populates="proyecto", cascade="all, delete-orphan", passive_deletes=True)
    # --- NUEVA RELACIÓN MUCHOS-A-MUCHOS ---
    # Relación para los miembros (colaboradores) de ESTE proyecto
    asociaciones_usuario = relationship("ProyectoUsuario", back_populates="proyecto", cascade="all, delete-orphan")
    
    
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
class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    descripcion = Column(String, nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"), nullable=False)

    proyecto = relationship("Proyecto", back_populates="batches")
    facturas_manuales = relationship("FacturaManual", back_populates="batch")
    facturas_electronicas = relationship("FacturaElectronica", back_populates="batch")


class FacturaManual(Base):
    __tablename__ = "facturas_manuales"

    id = Column(Integer, primary_key=True, index=True)
    Nit_Beneficiario = Column(String, nullable=False)
    monto_total = Column(Float, nullable=False)
    fecha = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    
    
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"), nullable=False)

    empresa = relationship("Empresa", back_populates="facturas_manuales")
    batch = relationship("Batch", back_populates="facturas_manuales")
    categoria = relationship("Categoria", back_populates="facturas_manuales")
    proyecto = relationship("Proyecto", back_populates="facturas_manuales")
    fecha_creacion = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=True
    )

class FacturaElectronica(Base):
    __tablename__ = "facturas_electronicas"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False,unique=True, index=True)
    monto_total = Column(Float, nullable=False)
    Nit_Beneficiario = Column(String, nullable=True)
    fecha = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    detalles = Column(JSONB, nullable=True,default=None) 
    n_factura = Column(Integer, nullable=True)
    monto_fiscal = Column(Float, nullable=True)
    # empresa = Column(String, nullable=True)
    # nit_emisor = Column(String, nullable=True)
    factura_especial = Column(Boolean, default=False)
    status = Column(String, default="pendiente")
    complete= Column(Boolean, default=False)
    pdfIO=Column(String,nullable=True)
    save_pdf=Column(Boolean,default=False)
    # batch = Column(Integer, nullable=True, index=True)

    categoria_id = Column(Integer, ForeignKey("categorias.id",ondelete="SET NULL"), nullable=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id",ondelete="CASCADE"), nullable=True)

    categoria = relationship("Categoria", back_populates="facturas_electronicas")
    proyecto = relationship("Proyecto", back_populates="facturas_electronicas")
    # NUEVOS CAMBIOS
    batch = relationship("Batch", back_populates="facturas_electronicas")
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    empresa = relationship("Empresa", back_populates="facturas_electronicas")
    fecha_creacion = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=True
    )

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    nombre=Column(String, index=True, nullable=False)
    nit=Column(String, unique=True, index=True, nullable=False)
    rubro = Column(String, nullable=True)
    facturas_manuales = relationship("FacturaManual", back_populates="empresa")
    facturas_electronicas = relationship("FacturaElectronica", back_populates="empresa")


class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    descripcion = Column(String, nullable=True)
    # Relación inversa: una categoría puede tener muchas facturas
    facturas_manuales = relationship("FacturaManual", back_populates="categoria")
    facturas_electronicas = relationship("FacturaElectronica", back_populates="categoria")


