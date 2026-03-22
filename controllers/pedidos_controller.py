"""
Controlador: Pedidos
"""
from models.pedidos import PedidosModel
from models.pagos import PagosModel
import config
from .base_controller import BaseController

class PedidosController(BaseController):
    """Controlador para Pedidos"""
    
    def __init__(self):
        self.model = PedidosModel()
        self.pagos_model = PagosModel()
    
    # Crear
    def crear_pedido(self, cliente_id: int, mesa_id: int, empleado_id: int = None):
        """Crear pedido nuevo"""
        return self.model.crear_pedido(cliente_id, mesa_id, empleado_id)
    
    # Modificar
    def agregar_plato_pedido(self, pedido_id: int, plato_id: int, cantidad: int = 1):
        """Agregar plato a pedido"""
        return self.model.agregar_plato_pedido(pedido_id, plato_id, cantidad)
    
    def remover_plato_pedido(self, pedido_id: int, plato_id: int):
        """Remover plato de pedido"""
        return self.model.remover_plato_pedido(pedido_id, plato_id)
    
    def actualizar_cantidad_item(self, detalle_id: int, cantidad: int):
        """Actualizar cantidad de item"""
        return self.model.actualizar_cantidad_item(detalle_id, cantidad)
    
    def cambiar_estado_pedido(self, pedido_id: int, nuevo_estado: str):
        """Cambiar estado"""
        try:
            estado = config.PedidoEstado(nuevo_estado)
            success, pedido, msg = self.model.cambiar_estado_pedido(pedido_id, estado)
            
            if success and estado == config.PedidoEstado.ENTREGADO:
                # Al entregar, generar registro de pago pendiente automáticamente
                try:
                    self.pagos_model.registrar_pago(
                        pedido_id=pedido_id, 
                        monto=0.0, # 0.0 indica pendiente (saldo por cobrar)
                        metodo=config.PagoMetodo.EFECTIVO # Placeholder
                    )
                except ValueError:
                    # Ignorar si ya existe pago
                    pass
                except Exception as e:
                    print(f"Advertencia: No se pudo crear pago automático: {e}")
            
            return success, pedido, msg

        except ValueError:
            return False, None, f"Estado inválido: {nuevo_estado}"
    
    def aplicar_descuento(self, pedido_id: int, descuento: float):
        """Aplicar descuento"""
        return self.model.aplicar_descuento(pedido_id, descuento)
    
    def finalizar_pedido(self, pedido_id: int):
        """Finalizar pedido"""
        return self.model.finalizar_pedido(pedido_id)
    
    def cancelar_pedido(self, pedido_id: int):
        """Cancelar pedido"""
        return self.model.cancelar_pedido(pedido_id)
    
    # Leer
    def obtener_pedido(self, pedido_id: int):
        """Obtener pedido"""
        return self.model.obtener_pedido(pedido_id)
    
    def obtener_pedido_activo_mesa(self, mesa_id: int):
        """Obtener el pedido activo (no entregado ni cancelado) de una mesa"""
        success, pedidos, msg = self.model.obtener_todos_pedidos()
        if not success or not pedidos:
            return False, None, "No hay pedidos"
        
        # Filtrar pedidos de esta mesa que estén activos
        for pedido in pedidos:
            if pedido.mesa_id == mesa_id:
                # Considerar activo si no está ENTREGADO ni CANCELADO
                if pedido.estado.value not in [config.PedidoEstado.ENTREGADO.value, config.PedidoEstado.CANCELADO.value]:
                    return True, pedido, f"Pedido activo encontrado"
        
        return False, None, "No hay pedido activo para esta mesa"
    
    
    def obtener_todos_pedidos_formateados(self):
        """Obtener todos formateados"""
        success, pedidos, msg = self.model.obtener_todos_pedidos()
        if not success or not pedidos:
            return success, [], msg
        
        datos = []
        for pedido in pedidos:
            total = pedido.calcular_total()
            datos.append((
                pedido.id,
                pedido.cliente.nombre,
                f"Mesa {pedido.mesa.numero}",
                f"${total:.2f}",
                pedido.estado.value,
                pedido.fecha_creacion.strftime("%Y-%m-%d %H:%M")
            ))
        return True, datos, msg
    
    def obtener_pedidos_activos_formateados(self):
        """Obtener pedidos en progreso"""
        success, pedidos, msg = self.model.obtener_pedidos_activos()
        if not success or not pedidos:
            return success, [], msg
        
        datos = []
        for pedido in pedidos:
            total = pedido.calcular_total()
            datos.append((
                pedido.id,
                pedido.cliente.nombre,
                f"Mesa {pedido.mesa.numero}",
                f"${total:.2f}",
                pedido.estado.value
            ))
        return True, datos, msg
    
    def obtener_detalles_pedido_formateados(self, pedido_id: int):
        """Obtener detalles de un pedido formateados"""
        success, detalles, msg = self.model.obtener_detalles_pedido(pedido_id)
        if not success or not detalles:
            return success, [], msg
        
        datos = []
        for detalle in detalles:
            datos.append((
                detalle.id,
                detalle.plato.nombre,
                detalle.cantidad,
                f"${detalle.precio_unitario:.2f}",
                f"${detalle.subtotal:.2f}"
            ))
        return True, datos, msg
    
    def obtener_total_pedido(self, pedido_id: int):
        """Obtener total formateado"""
        success, total, msg = self.model.calcular_total_pedido(pedido_id)
        if success:
            return True, f"${total:.2f}", msg
        return success, "Error", msg
    
    def obtener_estados_disponibles(self):
        """Obtener lista de estados"""
        return [e.value for e in config.PedidoEstado]
    
    def obtener_ticket_completo(self, pedido_id: int):
        """Obtener ticket para imprimir"""
        return self.model.obtener_ticket_completo(pedido_id)
    
    # Estadísticas
    def obtener_platos_mas_vendidos(self, limite: int = 10):
        """Obtener platos más vendidos"""
        success, platos, msg = self.model.obtener_platos_mas_vendidos(limite)
        if not success or not platos:
            return success, [], msg
        
        # platos es lista de (nombre, total_vendido, ingresos)
        return True, platos, msg
