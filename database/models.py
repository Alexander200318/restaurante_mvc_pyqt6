"""
Modelos de Base de Datos - Definición de tablas con SQLAlchemy ORM
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean, JSON, Table
from sqlalchemy.orm import declarative_base, relationship
import config

Base = declarative_base()

# Tabla de relación muchos-a-muchos: Platos - Ingredientes
plato_ingrediente_association = Table(
    'plato_ingrediente',
    Base.metadata,
    Column('plato_id', Integer, ForeignKey('platos.id'), primary_key=True),
    Column('ingrediente_id', Integer, ForeignKey('ingredientes.id'), primary_key=True),
    Column('cantidad_requerida', Float, default=1.0),  # Cantidad del ingrediente por plato
    Column('unidad', String(50), default='unidades')
)

class Mesa(Base):
    """Modelo de Mesa del restaurante"""
    __tablename__ = "mesas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, unique=True, nullable=False, index=True)
    capacidad = Column(Integer, nullable=False)
    estado = Column(SQLEnum(config.MesaEstado), default=config.MesaEstado.LIBRE)
    fecha_creacion = Column(DateTime, default=datetime.now)
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    clientes = relationship("Cliente", back_populates="mesa")
    pedidos = relationship("Pedido", back_populates="mesa")
    
    def __repr__(self):
        return f"<Mesa {self.numero} (Cap: {self.capacidad})>"

class Cliente(Base):
    """Modelo de Cliente/Comensal"""
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(255), nullable=True)
    mesa_id = Column(Integer, ForeignKey('mesas.id'), nullable=True)
    estado = Column(SQLEnum(config.ClienteEstado), default=config.ClienteEstado.COMIENDO)
    fecha_llegada = Column(DateTime, default=datetime.now)
    
    # Relaciones
    mesa = relationship("Mesa", back_populates="clientes")
    pedidos = relationship("Pedido", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente {self.nombre} {self.apellido}>"

class Empleado(Base):
    """Modelo de Empleado"""
    __tablename__ = "empleados"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    puesto = Column(SQLEnum(config.EmpleadoPuesto), nullable=False)
    estado = Column(SQLEnum(config.EmpleadoEstado), default=config.EmpleadoEstado.ACTIVO)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    fecha_ingreso = Column(DateTime, default=datetime.now)
    salario = Column(Float, nullable=True)
    
    # Relaciones
    pedidos = relationship("Pedido", back_populates="empleado")
    
    def __repr__(self):
        return f"<Empleado {self.nombre} ({self.puesto})>"

class Ingrediente(Base):
    """Modelo de Ingrediente"""
    __tablename__ = "ingredientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    cantidad = Column(Float, default=0.0)
    unidad = Column(String(50), nullable=False)
    precio_unitario = Column(Float, nullable=False)
    estado = Column(SQLEnum(config.IngredienteEstado), default=config.IngredienteEstado.DISPONIBLE)
    cantidad_minima = Column(Float, default=5.0)  # Para alertas de bajo stock
    proveedor = Column(String(100), nullable=True)
    fecha_ultimo_ingreso = Column(DateTime, nullable=True)
    
    # Relaciones
    usos = relationship("UsoIngrediente", back_populates="ingrediente")
    platos = relationship(
        "Plato",
        secondary=plato_ingrediente_association,
        back_populates="ingredientes"
    )
    
    def __repr__(self):
        return f"<Ingrediente {self.nombre} ({self.cantidad}{self.unidad})>"
    
    def esta_bajo_stock(self) -> bool:
        """Verificar si está bajo de stock"""
        return self.cantidad <= self.cantidad_minima

class Plato(Base):
    """Modelo de Plato/Producto del Menú"""
    __tablename__ = "platos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    categoria = Column(SQLEnum(config.PlatoCategoría), nullable=False)
    estado = Column(SQLEnum(config.PlatoEstado), default=config.PlatoEstado.DISPONIBLE)
    tiempo_preparacion = Column(Integer, default=15)  # minutos
    fecha_creacion = Column(DateTime, default=datetime.now)
    imagen_url = Column(String(500), nullable=True)
    
    # Relaciones
    ingredientes = relationship(
        "Ingrediente",
        secondary=plato_ingrediente_association,
        back_populates="platos"
    )
    detalles_pedido = relationship("DetallePedido", back_populates="plato")
    
    def __repr__(self):
        return f"<Plato {self.nombre} (${self.precio})>"

class Pedido(Base):
    """Modelo de Pedido"""
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    mesa_id = Column(Integer, ForeignKey('mesas.id'), nullable=False)
    empleado_id = Column(Integer, ForeignKey('empleados.id'), nullable=True)
    estado = Column(SQLEnum(config.PedidoEstado), default=config.PedidoEstado.PENDIENTE)
    fecha_creacion = Column(DateTime, default=datetime.now, index=True)
    fecha_entrega = Column(DateTime, nullable=True)
    observaciones = Column(Text, nullable=True)
    descuento = Column(Float, default=0.0)  # Porcentaje o monto
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="pedidos")
    mesa = relationship("Mesa", back_populates="pedidos")
    empleado = relationship("Empleado", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")
    pago = relationship("Pago", back_populates="pedido", uselist=False, cascade="all, delete-orphan")
    usos_ingredientes = relationship("UsoIngrediente", back_populates="pedido")
    
    def __repr__(self):
        return f"<Pedido {self.id} - Cliente {self.cliente_id} (${self.calcular_total():.2f})>"
    
    def calcular_total(self) -> float:
        """Calcular total del pedido"""
        subtotal = sum(detalle.subtotal for detalle in self.detalles)
        return max(0, subtotal - self.descuento)
    
    def cantidad_items(self) -> int:
        """Cantidad de items en el pedido"""
        return sum(detalle.cantidad for detalle in self.detalles)

class DetallePedido(Base):
    """Modelo de Línea de Pedido"""
    __tablename__ = "detalles_pedido"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=False)
    plato_id = Column(Integer, ForeignKey('platos.id'), nullable=False)
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)  # cantidad * precio_unitario
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="detalles")
    plato = relationship("Plato", back_populates="detalles_pedido")
    
    def __repr__(self):
        return f"<DetallePedido {self.plato_id} x{self.cantidad}>"

class Pago(Base):
    """Modelo de Pago"""
    __tablename__ = "pagos"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), unique=True, nullable=False)
    monto = Column(Float, nullable=False)
    metodo = Column(SQLEnum(config.PagoMetodo), nullable=False)
    estado = Column(SQLEnum(config.PagoEstado), default=config.PagoEstado.PENDIENTE)
    fecha_pago = Column(DateTime, nullable=True)
    referencia = Column(String(100), nullable=True)  # Número de transacción, ticket, etc
    cambio = Column(Float, default=0.0)
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="pago")
    
    def __repr__(self):
        return f"<Pago {self.id} - ${self.monto} ({self.estado})>"

class UsoIngrediente(Base):
    """Modelo de Auditoría - Registro de uso de ingredientes"""
    __tablename__ = "usos_ingredientes"
    
    id = Column(Integer, primary_key=True, index=True)
    ingrediente_id = Column(Integer, ForeignKey('ingredientes.id'), nullable=False)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=True)
    cantidad_usada = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.now, index=True)
    notas = Column(Text, nullable=True)
    
    # Relaciones
    ingrediente = relationship("Ingrediente", back_populates="usos")
    pedido = relationship("Pedido", back_populates="usos_ingredientes")
    
    def __repr__(self):
        return f"<UsoIngrediente {self.ingrediente_id} x{self.cantidad_usada}>"
