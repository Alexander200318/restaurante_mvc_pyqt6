"""
Modelo de Negocio: Mesas
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from database.models import Mesa
from database.queries import QueriesManager
import config
from utils.validators import validar_numero_mesa, validar_capacidad
from .base_model import BaseModel

class MesasModel(BaseModel):
    """Lógica de negocio para Mesas"""
    
    def crear_mesa(self, numero: int, capacidad: int) -> Tuple[bool, Optional[Mesa], str]:
        """Crear nueva mesa con validaciones"""
        # Validar entrada
        es_valido, numero_validado, msg = validar_numero_mesa(str(numero))
        if not es_valido:
            return False, None, msg
        
        es_valido, capacidad_validada, msg = validar_capacidad(str(capacidad))
        if not es_valido:
            return False, None, msg
        
        def _crear(session):
            # Verificar si número ya existe
            existente = session.query(Mesa).filter(Mesa.numero == numero_validado).first()
            if existente:
                raise ValueError(f"Mesa número {numero_validado} ya existe")
            
            nueva_mesa = Mesa(
                numero=numero_validado,
                capacidad=capacidad_validada,
                estado=config.MesaEstado.LIBRE
            )
            session.add(nueva_mesa)
            return nueva_mesa
        
        return self._ejecutar_con_manejo_errores(_crear)
    
    def actualizar_mesa(self, mesa_id: int, numero: Optional[int] = None, 
                       capacidad: Optional[int] = None) -> Tuple[bool, Optional[Mesa], str]:
        """Actualizar datos de una mesa"""
        if numero is not None:
            es_valido, numero_validado, msg = validar_numero_mesa(str(numero))
            if not es_valido:
                return False, None, msg
        
        if capacidad is not None:
            es_valido, capacidad_validada, msg = validar_capacidad(str(capacidad))
            if not es_valido:
                return False, None, msg
        
        def _actualizar(session):
            mesa = session.query(Mesa).filter(Mesa.id == mesa_id).first()
            if not mesa:
                raise ValueError(f"Mesa {mesa_id} no encontrada")
            
            if numero is not None:
                # Verificar que no exista otra mesa con ese número
                otra_mesa = session.query(Mesa).filter(
                    Mesa.numero == numero_validado,
                    Mesa.id != mesa_id
                ).first()
                if otra_mesa:
                    raise ValueError(f"Ya existe otra mesa con número {numero_validado}")
                mesa.numero = numero_validado
            
            if capacidad is not None:
                mesa.capacidad = capacidad_validada
            
            return mesa
        
        return self._ejecutar_con_manejo_errores(_actualizar)
    
    def cambiar_estado_mesa(self, mesa_id: int, nuevo_estado: config.MesaEstado) -> Tuple[bool, Optional[Mesa], str]:
        """Cambiar estado de una mesa (libre/ocupada/reservada)"""
        def _cambiar(session):
            mesa = session.query(Mesa).filter(Mesa.id == mesa_id).first()
            if not mesa:
                raise ValueError(f"Mesa {mesa_id} no encontrada")
            
            mesa.estado = nuevo_estado
            return mesa
        
        return self._ejecutar_con_manejo_errores(_cambiar)
    
    def obtener_mesa(self, mesa_id: int) -> Tuple[bool, Optional[Mesa], str]:
        """Obtener una mesa por ID"""
        def _obtener(session):
            return session.query(Mesa).filter(Mesa.id == mesa_id).first()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_todas_mesas(self) -> Tuple[bool, List[Mesa], str]:
        """Obtener todas las mesas"""
        def _obtener(session):
            from sqlalchemy.orm import selectinload
            return session.query(Mesa).options(selectinload(Mesa.clientes)).order_by(Mesa.numero).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_mesas_disponibles(self) -> Tuple[bool, List[Mesa], str]:
        """Obtener solo mesas libres"""
        def _obtener(session):
            return QueriesManager.obtener_mesas_disponibles(session)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_mesas_ocupadas(self) -> Tuple[bool, List[Mesa], str]:
        """Obtener solo mesas ocupadas"""
        def _obtener(session):
            return QueriesManager.obtener_mesas_ocupadas(session)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def eliminar_mesa(self, mesa_id: int) -> Tuple[bool, None, str]:
        """Eliminar una mesa"""
        def _eliminar(session):
            mesa = session.query(Mesa).filter(Mesa.id == mesa_id).first()
            if not mesa:
                raise ValueError(f"Mesa {mesa_id} no encontrada")
            
            # Verificar que no tenga clientes
            if mesa.clientes:
                raise ValueError(f"No se puede eliminar mesa con clientes")
            
            session.delete(mesa)
            return None
        
        return self._ejecutar_con_manejo_errores(_eliminar)
    
    def asignar_cliente_mesa(self, mesa_id: int, cliente_id: int) -> Tuple[bool, Optional[Mesa], str]:
        """Asignar cliente a una mesa"""
        def _asignar(session):
            mesa = session.query(Mesa).filter(Mesa.id == mesa_id).first()
            if not mesa:
                raise ValueError(f"Mesa {mesa_id} no encontrada")
            
            from database.models import Cliente
            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                raise ValueError(f"Cliente {cliente_id} no encontrado")
            
            cliente.mesa_id = mesa_id
            mesa.estado = config.MesaEstado.OCUPADA
            return mesa
        
        return self._ejecutar_con_manejo_errores(_asignar)
    
    def liberar_mesa(self, mesa_id: int) -> Tuple[bool, Optional[Mesa], str]:
        """Liberar una mesa (dejar libre)"""
        def _liberar(session):
            mesa = session.query(Mesa).filter(Mesa.id == mesa_id).first()
            if not mesa:
                raise ValueError(f"Mesa {mesa_id} no encontrada")
            
            mesa.estado = config.MesaEstado.LIBRE
            # Los clientes se desasignan en el modelo Cliente
            return mesa
        
        return self._ejecutar_con_manejo_errores(_liberar)
