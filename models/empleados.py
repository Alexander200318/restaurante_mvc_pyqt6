"""
Modelo de Negocio: Empleados
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from database.models import Empleado
import config
from utils.validators import validar_nombre, validar_telefono, validar_precio
from .base_model import BaseModel

class EmpleadosModel(BaseModel):
    """Lógica de negocio para Empleados"""
    
    def crear_empleado(self, nombre: str, puesto: config.EmpleadoPuesto,
                      telefono: str = None, email: str = None,
                      salario: float = None) -> Tuple[bool, Optional[Empleado], str]:
        """Crear nuevo empleado"""
        # Validar nombre
        es_valido, nombre_validado, msg = validar_nombre(nombre)
        if not es_valido:
            return False, None, msg
        
        # Validar teléfono
        if telefono:
            es_valido, telefono_validado, msg = validar_telefono(telefono)
            if not es_valido:
                return False, None, msg
        else:
            telefono_validado = None
        
        # Validar salario
        if salario is not None:
            es_valido, salario_validado, msg = validar_precio(str(salario))
            if not es_valido:
                return False, None, msg
        else:
            salario_validado = None
        
        def _crear(session):
            nuevo_empleado = Empleado(
                nombre=nombre_validado,
                puesto=puesto,
                telefono=telefono_validado,
                email=email,
                salario=salario_validado,
                estado=config.EmpleadoEstado.ACTIVO
            )
            session.add(nuevo_empleado)
            return nuevo_empleado
        
        return self._ejecutar_con_manejo_errores(_crear)
    
    def actualizar_empleado(self, empleado_id: int, nombre: Optional[str] = None,
                           puesto: Optional[config.EmpleadoPuesto] = None,
                           telefono: Optional[str] = None, email: Optional[str] = None,
                           salario: Optional[float] = None) -> Tuple[bool, Optional[Empleado], str]:
        """Actualizar datos de empleado"""
        if nombre:
            es_valido, nombre_validado, msg = validar_nombre(nombre)
            if not es_valido:
                return False, None, msg
        
        if telefono:
            es_valido, telefono_validado, msg = validar_telefono(telefono)
            if not es_valido:
                return False, None, msg
        else:
            telefono_validado = None
        
        if salario is not None:
            es_valido, salario_validado, msg = validar_precio(str(salario))
            if not es_valido:
                return False, None, msg
        else:
            salario_validado = None
        
        def _actualizar(session):
            empleado = session.query(Empleado).filter(Empleado.id == empleado_id).first()
            if not empleado:
                raise ValueError(f"Empleado {empleado_id} no encontrado")
            
            if nombre:
                empleado.nombre = nombre_validado
            if puesto:
                empleado.puesto = puesto
            if telefono:
                empleado.telefono = telefono_validado
            if email:
                empleado.email = email if email.strip() else None
            if salario is not None:
                empleado.salario = salario_validado
            
            return empleado
        
        return self._ejecutar_con_manejo_errores(_actualizar)
    
    def cambiar_estado_empleado(self, empleado_id: int, nuevo_estado: config.EmpleadoEstado) -> Tuple[bool, Optional[Empleado], str]:
        """Cambiar estado de empleado (activo/inactivo)"""
        def _cambiar(session):
            empleado = session.query(Empleado).filter(Empleado.id == empleado_id).first()
            if not empleado:
                raise ValueError(f"Empleado {empleado_id} no encontrado")
            
            empleado.estado = nuevo_estado
            return empleado
        
        return self._ejecutar_con_manejo_errores(_cambiar)
    
    def obtener_empleado(self, empleado_id: int) -> Tuple[bool, Optional[Empleado], str]:
        """Obtener un empleado por ID"""
        def _obtener(session):
            return session.query(Empleado).filter(Empleado.id == empleado_id).first()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_todos_empleados(self) -> Tuple[bool, List[Empleado], str]:
        """Obtener todos los empleados"""
        def _obtener(session):
            return session.query(Empleado).order_by(Empleado.nombre).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_empleados_activos(self) -> Tuple[bool, List[Empleado], str]:
        """Obtener solo empleados activos"""
        def _obtener(session):
            return session.query(Empleado).filter(
                Empleado.estado == config.EmpleadoEstado.ACTIVO
            ).order_by(Empleado.nombre).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_empleados_por_puesto(self, puesto: config.EmpleadoPuesto) -> Tuple[bool, List[Empleado], str]:
        """Obtener empleados de un puesto específico"""
        def _obtener(session):
            return session.query(Empleado).filter(
                Empleado.puesto == puesto
            ).order_by(Empleado.nombre).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def eliminar_empleado(self, empleado_id: int) -> Tuple[bool, None, str]:
        """Eliminar un empleado"""
        def _eliminar(session):
            empleado = session.query(Empleado).filter(Empleado.id == empleado_id).first()
            if not empleado:
                raise ValueError(f"Empleado {empleado_id} no encontrado")
            
            # Mejor: cambiar a inactivo en lugar de eliminar
            # Esto preserva histórico de pedidos
            empleado.estado = config.EmpleadoEstado.INACTIVO
            return None
        
        return self._ejecutar_con_manejo_errores(_eliminar)
