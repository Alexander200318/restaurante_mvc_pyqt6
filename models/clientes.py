"""
Modelo de Negocio: Clientes/Comensales
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from database.models import Cliente
from database.queries import QueriesManager
import config
from utils.validators import validar_nombre, validar_telefono
from .base_model import BaseModel

class ClientesModel(BaseModel):
    """Lógica de negocio para Clientes"""
    
    def crear_cliente(self, cedula: str, nombre: str, apellido: str, 
                     telefono: str = None, direccion: str = None, correo: str = None) -> Tuple[bool, Optional[Cliente], str]:
        """Crear nuevo cliente con validaciones"""
        # Validar cédula
        if not cedula or len(cedula.strip()) < 3:
            return False, None, "La cédula es requerida"
        
        # Validar nombre
        es_valido, nombre_validado, msg = validar_nombre(nombre)
        if not es_valido:
            return False, None, msg
        
        # Validar apellido
        es_valido, apellido_validado, msg = validar_nombre(apellido)
        if not es_valido:
            return False, None, "Apellido inválido"
        
        # Validar teléfono si se proporciona
        if telefono:
            es_valido, telefono_validado, msg = validar_telefono(telefono)
            if not es_valido:
                return False, None, msg
        else:
            telefono_validado = None
        
        def _crear(session):
            # Verificar que cédula sea única
            cliente_existente = session.query(Cliente).filter(Cliente.cedula == cedula).first()
            if cliente_existente:
                raise ValueError(f"Ya existe un cliente con cédula {cedula}")
            
            nuevo_cliente = Cliente(
                cedula=cedula,
                nombre=nombre_validado,
                apellido=apellido_validado,
                telefono=telefono_validado,
                direccion=direccion or None,
                correo=correo or None,
                mesa_id=None,
                estado=config.ClienteEstado.COMIENDO
            )
            session.add(nuevo_cliente)
            return nuevo_cliente
        
        return self._ejecutar_con_manejo_errores(_crear)
    
    def actualizar_cliente(self, cliente_id: int, nombre: Optional[str] = None,
                          apellido: Optional[str] = None,
                          telefono: Optional[str] = None,
                          direccion: Optional[str] = None,
                          correo: Optional[str] = None,
                          mesa_id: Optional[int] = None) -> Tuple[bool, Optional[Cliente], str]:
        """Actualizar datos de un cliente"""
        if nombre:
            es_valido, nombre_validado, msg = validar_nombre(nombre)
            if not es_valido:
                return False, None, msg
        else:
            nombre_validado = None
        
        if apellido:
            es_valido, apellido_validado, msg = validar_nombre(apellido)
            if not es_valido:
                return False, None, "Apellido inválido"
        else:
            apellido_validado = None
        
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
            
            if nombre_validado:
                cliente.nombre = nombre_validado
            if apellido_validado:
                cliente.apellido = apellido_validado
            if telefono_validado:
                cliente.telefono = telefono_validado
            if direccion is not None:
                cliente.direccion = direccion
            if correo is not None:
                cliente.correo = correo
            if mesa_id is not None:
                cliente.mesa_id = mesa_id
            
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
            return session.query(Cliente).options(joinedload(Cliente.mesa)).filter(Cliente.id == cliente_id).first()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_todos_clientes(self) -> Tuple[bool, List[Cliente], str]:
        """Obtener todos los clientes"""
        def _obtener(session):
            return session.query(Cliente).options(joinedload(Cliente.mesa)).order_by(Cliente.fecha_llegada.desc()).all()
        
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

    def buscar_cliente_por_cedula(self, cedula: str) -> Tuple[bool, Optional[Cliente], str]:
        """Buscar cliente por número de cédula"""
        def _buscar(session):
            return session.query(Cliente).filter(Cliente.cedula == cedula).first()
        
        return self._obtener_con_manejo_errores(_buscar)
        
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













    def obtener_cliente_por_cedula(self, cedula: str):
        """Buscar cliente por cédula"""
        def _obtener(session):
            return session.query(Cliente).filter(Cliente.cedula == cedula).first()
        
        return self._obtener_con_manejo_errores(_obtener)