"""
Base para todos los modelos de negocio
Proporciona métodos comunes y manejo de errores centralizado
"""
from typing import List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from database.db_manager import db_manager

class BaseModel:
    """Clase base para todos los modelos de negocio"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def _ejecutar_con_manejo_errores(self, operacion, *args, **kwargs) -> Tuple[bool, Any, str]:
        """
        Ejecutar operación con manejo centralizado de errores
        Retorna: (success, resultado, mensaje)
        """
        session = None
        try:
            session = self.db_manager.get_session()
            resultado = operacion(session, *args, **kwargs)
            session.commit()
            return True, resultado, "Operación exitosa"
        except ValueError as e:
            if session:
                session.rollback()
            return False, None, f"Error de validación: {str(e)}"
        except Exception as e:
            if session:
                session.rollback()
            return False, None, f"Error en la operación: {str(e)}"
        finally:
            if session:
                self.db_manager.close_session(session)
    
    def _obtener_con_manejo_errores(self, operacion, *args, **kwargs) -> Tuple[bool, Any, str]:
        """
        Ejecutar operación de lectura (sin commit)
        Retorna: (success, resultado, mensaje)
        """
        session = None
        try:
            session = self.db_manager.get_session()
            resultado = operacion(session, *args, **kwargs)
            return True, resultado, ""
        except Exception as e:
            return False, None, f"Error al obtener datos: {str(e)}"
        finally:
            if session:
                self.db_manager.close_session(session)
