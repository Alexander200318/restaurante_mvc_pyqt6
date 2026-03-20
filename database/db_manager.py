"""
Gestor de Base de Datos - Inicialización y manejo de conexiones SQLAlchemy
"""
from typing import Optional, Generator
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import config
from .models import Base

class DatabaseManager:
    """Gestor centralizado de la base de datos"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._init_db()
    
    def _init_db(self):
        """Inicializar engine y sessionmaker"""
        # Usar StaticPool para evitar problemas con SQLite en threading
        self.engine = create_engine(
            config.DATABASE_URL,
            echo=config.DB_ECHO,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False
        )
        # Crear todas las tablas
        self.create_tables()
    
    def create_tables(self):
        """Crear todas las tablas desde los modelos"""
        try:
            Base.metadata.create_all(bind=self.engine)
            print(f"✓ Base de datos inicializada: {config.DATABASE_PATH}")
        except Exception as e:
            print(f"✗ Error al crear tablas: {e}")
            raise
    
    def get_session(self) -> Session:
        """Obtener una sesión nueva"""
        if self.SessionLocal is None:
            self._init_db()
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Cerrar sesión"""
        if session:
            session.close()
    
    def reset_database(self):
        """PELIGRO: Eliminar todas las tablas y recrearlas (para testing)"""
        Base.metadata.drop_all(bind=self.engine)
        self.create_tables()
        print("✓ Base de datos reiniciada")
    
    def check_connection(self) -> bool:
        """Verificar conexión a BD"""
        try:
            with self.engine.connect() as conn:
                return True
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Obtener cantidad de registros en una tabla"""
        session = self.get_session()
        try:
            from .models import (
                Mesa, Cliente, Empleado, Ingrediente, 
                Plato, Pedido, DetallePedido, Pago
            )
            
            models = {
                "mesas": Mesa,
                "clientes": Cliente,
                "empleados": Empleado,
                "ingredientes": Ingrediente,
                "platos": Plato,
                "pedidos": Pedido,
                "detalles_pedido": DetallePedido,
                "pagos": Pago,
            }
            
            if table_name in models:
                count = session.query(models[table_name]).count()
                return count
            return 0
        except Exception as e:
            print(f"Error al contar registros: {e}")
            return 0
        finally:
            self.close_session(session)

# Instancia global (singleton)
db_manager = DatabaseManager()
