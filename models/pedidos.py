"""
Modelo de Negocio: Pedidos
Lógica más compleja: cálculos, estados, relaciones con platos
"""
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Pedido, DetallePedido, Plato, Cliente, Mesa, Pago
from database.queries import QueriesManager
import config
from utils.validators import validar_cantidad
from .base_model import BaseModel

class PedidosModel(BaseModel):
    """Lógica de negocio para Pedidos"""
    
    def crear_pedido(self, cliente_id: int, mesa_id: int,
                    empleado_id: int = None) -> Tuple[bool, Optional[Pedido], str]:
        """Crear nuevo pedido vacío"""
        def _crear(session):
            cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                raise ValueError(f"Cliente {cliente_id} no encontrado")
            
            mesa = session.query(Mesa).filter(Mesa.id == mesa_id).first()
            if not mesa:
                raise ValueError(f"Mesa {mesa_id} no encontrada")
            
            nuevo_pedido = Pedido(
                cliente_id=cliente_id,
                mesa_id=mesa_id,
                empleado_id=empleado_id,
                estado=config.PedidoEstado.PENDIENTE
            )
            session.add(nuevo_pedido)
            return nuevo_pedido
        
        return self._ejecutar_con_manejo_errores(_crear)
    
    def agregar_plato_pedido(self, pedido_id: int, plato_id: int,
                           cantidad: int = 1) -> Tuple[bool, Optional[DetallePedido], str]:
        """Agregar plato a un pedido"""
        es_valido, cantidad_validada, msg = validar_cantidad(str(cantidad))
        if not es_valido:
            return False, None, msg
        
        def _agregar(session):
            pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if not pedido:
                raise ValueError(f"Pedido {pedido_id} no encontrado")
            
            plato = session.query(Plato).filter(Plato.id == plato_id).first()
            if not plato:
                raise ValueError(f"Plato {plato_id} no encontrado")
            
            if plato.estado != config.PlatoEstado.DISPONIBLE:
                raise ValueError(f"Plato '{plato.nombre}' no disponible")
            
            # Verificar si plato ya está en pedido (actualizar cantidad)
            detalle_existente = session.query(DetallePedido).filter(
                DetallePedido.pedido_id == pedido_id,
                DetallePedido.plato_id == plato_id
            ).first()
            
            if detalle_existente:
                detalle_existente.cantidad += int(cantidad_validada)
                detalle_existente.subtotal = (
                    detalle_existente.cantidad * detalle_existente.precio_unitario
                )
                return detalle_existente
            else:
                detalle = DetallePedido(
                    pedido_id=pedido_id,
                    plato_id=plato_id,
                    cantidad=int(cantidad_validada),
                    precio_unitario=plato.precio,
                    subtotal=int(cantidad_validada) * plato.precio
                )
                session.add(detalle)
                return detalle
        
        return self._ejecutar_con_manejo_errores(_agregar)
    
    def remover_plato_pedido(self, pedido_id: int, plato_id: int) -> Tuple[bool, None, str]:
        """Remover plato de un pedido"""
        def _remover(session):
            detalle = session.query(DetallePedido).filter(
                DetallePedido.pedido_id == pedido_id,
                DetallePedido.plato_id == plato_id
            ).first()
            
            if not detalle:
                raise ValueError(f"Ítem no encontrado en pedido")
            
            session.delete(detalle)
            return None
        
        return self._ejecutar_con_manejo_errores(_remover)
    
    def actualizar_cantidad_item(self, detalle_id: int, cantidad: int) -> Tuple[bool, Optional[DetallePedido], str]:
        """Actualizar cantidad de un ítem en pedido"""
        es_valido, cantidad_validada, msg = validar_cantidad(str(cantidad))
        if not es_valido:
            return False, None, msg
        
        def _actualizar(session):
            detalle = session.query(DetallePedido).filter(DetallePedido.id == detalle_id).first()
            if not detalle:
                raise ValueError(f"Détalle {detalle_id} no encontrado")
            
            detalle.cantidad = int(cantidad_validada)
            detalle.subtotal = detalle.cantidad * detalle.precio_unitario
            return detalle
        
        return self._ejecutar_con_manejo_errores(_actualizar)
    
    def cambiar_estado_pedido(self, pedido_id: int, nuevo_estado: config.PedidoEstado) -> Tuple[bool, Optional[Pedido], str]:
        """Cambiar estado de un pedido"""
        def _cambiar(session):
            pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if not pedido:
                raise ValueError(f"Pedido {pedido_id} no encontrado")
            
            pedido.estado = nuevo_estado
            
            # Si se marca como entregado, registrar fecha
            if nuevo_estado == config.PedidoEstado.ENTREGADO:
                pedido.fecha_entrega = datetime.now()
            
            return pedido
        
        return self._ejecutar_con_manejo_errores(_cambiar)
    
    def aplicar_descuento(self, pedido_id: int, descuento: float) -> Tuple[bool, Optional[Pedido], str]:
        """Aplicar descuento a un pedido"""
        es_valido, descuento_validado, msg = validar_cantidad(str(descuento))
        if not es_valido:
            return False, None, msg
        
        def _aplicar(session):
            pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if not pedido:
                raise ValueError(f"Pedido {pedido_id} no encontrado")
            
            pedido.descuento = descuento_validado
            return pedido
        
        return self._ejecutar_con_manejo_errores(_aplicar)
    
    def obtener_pedido(self, pedido_id: int) -> Tuple[bool, Optional[Pedido], str]:
        """Obtener un pedido completo"""
        def _obtener(session):
            return session.query(Pedido).filter(Pedido.id == pedido_id).first()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_todos_pedidos(self) -> Tuple[bool, List[Pedido], str]:
        """Obtener todos los pedidos"""
        def _obtener(session):
            return session.query(Pedido).order_by(Pedido.fecha_creacion.desc()).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_pedidos_activos(self) -> Tuple[bool, List[Pedido], str]:
        """Obtener pedidos no completados ni cancelados"""
        def _obtener(session):
            return QueriesManager.obtener_pedidos_activos(session)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_pedidos_por_estado(self, estado: config.PedidoEstado) -> Tuple[bool, List[Pedido], str]:
        """Obtener pedidos por estado específico"""
        def _obtener(session):
            return QueriesManager.obtener_pedidos_por_estado(session, estado)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_pedidos_por_cliente(self, cliente_id: int) -> Tuple[bool, List[Pedido], str]:
        """Obtener todos los pedidos de un cliente"""
        def _obtener(session):
            return session.query(Pedido).filter(
                Pedido.cliente_id == cliente_id
            ).order_by(Pedido.fecha_creacion.desc()).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_pedidos_por_mesa(self, mesa_id: int) -> Tuple[bool, List[Pedido], str]:
        """Obtener pedidos de una mesa"""
        def _obtener(session):
            return QueriesManager.obtener_pedidos_por_mesa(session, mesa_id)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_detalles_pedido(self, pedido_id: int) -> Tuple[bool, List[DetallePedido], str]:
        """Obtener detalles de un pedido"""
        def _obtener(session):
            return QueriesManager.obtener_detalles_pedido(session, pedido_id)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def calcular_total_pedido(self, pedido_id: int) -> Tuple[bool, float, str]:
        """Calcular total de un pedido"""
        def _calcular(session):
            pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if not pedido:
                raise ValueError(f"Pedido {pedido_id} no encontrado")
            return pedido.calcular_total()
        
        return self._obtener_con_manejo_errores(_calcular)
    
    def obtener_ticket_completo(self, pedido_id: int) -> Tuple[bool, dict, str]:
        """Obtener información completa del pedido para imprimir"""
        def _obtener(session):
            return QueriesManager.obtener_ticket_completo(session, pedido_id)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def finalizar_pedido(self, pedido_id: int) -> Tuple[bool, Optional[Pedido], str]:
        """Finalizar pedido (entregado) y liberar mesa"""
        def _finalizar(session):
            pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if not pedido:
                raise ValueError(f"Pedido {pedido_id} no encontrado")
            
            # Cambiar estado a entregado
            pedido.estado = config.PedidoEstado.ENTREGADO
            pedido.fecha_entrega = datetime.now()
            
            # Cambiar estado del cliente
            pedido.cliente.estado = config.ClienteEstado.PAGADO
            
            # No liberar mesa aquí, esperar al pago
            
            return pedido
        
        return self._ejecutar_con_manejo_errores(_finalizar)
    
    def cancelar_pedido(self, pedido_id: int) -> Tuple[bool, Optional[Pedido], str]:
        """Cancelar un pedido"""
        def _cancelar(session):
            pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if not pedido:
                raise ValueError(f"Pedido {pedido_id} no encontrado")
            
            pedido.estado = config.PedidoEstado.CANCELADO
            
            # Liberar mesa
            if pedido.mesa:
                pedido.mesa.estado = config.MesaEstado.LIBRE
            
            return pedido
        
        return self._ejecutar_con_manejo_errores(_cancelar)
    
    def obtener_platos_mas_vendidos(self, limite: int = 10) -> Tuple[bool, List[Tuple], str]:
        """Obtener platos más vendidos"""
        def _obtener(session):
            return QueriesManager.obtener_platos_mas_vendidos(session, limite)
        
        return self._obtener_con_manejo_errores(_obtener)
