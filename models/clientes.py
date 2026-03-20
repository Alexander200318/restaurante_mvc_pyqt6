"""
Modelo de Negocio: Clientes/Comensales
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from database.models import Cliente
from database.queries import QueriesManager
import config
from utils.validators import validar_nombre, validar_telefono
from .base_model import BaseModel

class ClientesModel(BaseModel):
    """Lógica de negocio para Clientes"""
    
    def crear_cliente(self, nombre: str, mesa_id: int, 
                     cantidad_personas: int = 1, telefono: str = None) -> Tuple[bool, Optional[Cliente], str]:
        """Crear nuevo cliente con validaciones"""
        # Validar nombre
        es_valido, nombre_validado, msg = validar_nombre(nombre)
        if not es_valido:
            return False, None, msg
        
        # Validar teléfono si se proporciona
        if telefono:
            es_valido, telefono_validado, msg = validar_telefono(telefono)
            if not es_valido:
                return False, None, msg
        else:
            telefono_validado = None
        
        def _crear(session):
            from database.models import Mesa
            # Verificar que mesa existe
            mesa = session.query(Mesa).filter(Mesa.id == mesa_id).first()
            if not mesa:
                raise ValueError(f"Mesa {mesa_id} no encontrada")
            
            nuevo_cliente = Cliente(
                nombre=nombre_validado,
                mesa_id=mesa_id,
                cantidad_personas=cantidad_personas,
                telefono=telefono_validado,
                estado=config.ClienteEstado.COMIENDO
            )
            session.add(nuevo_cliente)
            return nuevo_cliente
        
        return self._ejecutar_con_manejo_errores(_crear)
    
    def actualizar_cliente(self, cliente_id: int, nombre: Optional[str] = None,
                          cantidad_personas: Optional[int] = None,
                          telefono: Optional[str] = None) -> Tuple[bool, Optional[Cliente], str]:
        """Actualizar datos de un cliente"""
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
        
        def _actualizar(session):
            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                raise ValueError(f"Cliente {cliente_id} no encontrado")
            
            if nombre:
                cliente.nombre = nombre_validado
            if cantidad_personas is not None:
                cliente.cantidad_personas = cantidad_personas
            if telefono:
                cliente.telefono = telefono_validado
            
            return cliente
        
        return self._ejecutar_con_manejo_errores(_actualizar)
    
    def cambiar_estado_cliente(self, cliente_id: int, nuevo_estado: config.ClienteEstado) -> Tuple[bool, Optional[Cliente], str]:
        """Cambiar estado de cliente (comiendo/pagado/cancelado)"""
        def _cambiar(session):
            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                raise ValueError(f"Cliente {cliente_id} no encontrado")
            
            cliente.estado = nuevo_estado
            return cliente
        
        return self._ejecutar_con_manejo_errores(_cambiar)
    
    def obtener_cliente(self, cliente_id: int) -> Tuple[bool, Optional[Cliente], str]:
        """Obtener un cliente por ID"""
        def _obtener(session):
            return session.query(Cliente).filter(Cliente.id == cliente_id).first()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_todos_clientes(self) -> Tuple[bool, List[Cliente], str]:
        """Obtener todos los clientes"""
        def _obtener(session):
            return session.query(Cliente).order_by(Cliente.fecha_llegada.desc()).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_clientes_por_mesa(self, mesa_id: int) -> Tuple[bool, List[Cliente], str]:
        """Obtener clientes de una mesa específica"""
        def _obtener(session):
            return session.query(Cliente).filter(Cliente.mesa_id == mesa_id).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_clientes_comiendo(self) -> Tuple[bool, List[Cliente], str]:
        """Obtener clientes activos (comiendo)"""
        def _obtener(session):
            return session.query(Cliente).filter(
                Cliente.estado == config.ClienteEstado.COMIENDO
            ).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def eliminar_cliente(self, cliente_id: int) -> Tuple[bool, None, str]:
        """Eliminar un cliente"""
        def _eliminar(session):
            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                raise ValueError(f"Cliente {cliente_id} no encontrado")
            
            # Verificar que no tenga pedidos activos
            from database.models import Pedido
            pedidos_activos = session.query(Pedido).filter(
                Pedido.cliente_id == cliente_id,
                Pedido.estado.in_([
                    config.PedidoEstado.PENDIENTE,
                    config.PedidoEstado.PREPARANDO,
                    config.PedidoEstado.LISTO
                ])
            ).count()
            
            if pedidos_activos > 0:
                raise ValueError(f"No se puede eliminar cliente con pedidos activos")
            
            # Liberar la mesa
            if cliente.mesa:
                cliente.mesa.estado = config.MesaEstado.LIBRE
            
            cliente.mesa_id = None
            session.delete(cliente)
            return None
        
        return self._ejecutar_con_manejo_errores(_eliminar)
