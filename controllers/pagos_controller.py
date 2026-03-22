"""
Controlador: Pagos
"""
from models.pagos import PagosModel
import config
from datetime import datetime
from .base_controller import BaseController
from models.clientes import ClientesModel

class PagosController(BaseController):
    """Controlador para Pagos"""
    
    def __init__(self):
        self.model = PagosModel()
        self.clientes_model = ClientesModel()
    
    # Crear/Registrar
    def registrar_pago(self, pedido_id: int, monto: float, metodo: str,
                      referencia: str = None, cambio: float = 0.0):



        """Registrar nuevo pago"""
        try:
            metodo_enum = config.PagoMetodo(metodo)
            return self.model.registrar_pago(pedido_id, monto, metodo_enum, referencia, cambio)
        except ValueError:
            return False, None, f"Método de pago inválido: {metodo}"
    
    # Actualizar
    def actualizar_pago(self, pago_id: int, monto: float = None,
                       metodo: str = None, referencia: str = None):
        """Actualizar pago"""
        metodo_enum = None
        if metodo:
            try:
                metodo_enum = config.PagoMetodo(metodo)
            except ValueError:
                return False, None, f"Método inválido: {metodo}"
        
        return self.model.actualizar_pago(pago_id, monto, metodo_enum, referencia)
    
    def completar_pago(self, pago_id: int, cambio: float = 0.0):
        """Marcar como completado"""
        return self.model.completar_pago(pago_id, cambio)
    
    def anular_pago(self, pago_id: int):
        """Anular pago"""
        return self.model.anular_pago(pago_id)
    
    # Leer
    def obtener_pago(self, pago_id: int):
        """Obtener pago"""
        return self.model.obtener_pago(pago_id)
    
    def obtener_todos_pagos_formateados(self):
        """Obtener todos formateados"""
        success, pagos, msg = self.model.obtener_todos_pagos()
        if not success or not pagos:
            return success, [], msg
        
        datos = []
        for pago in pagos:
            fecha = pago.fecha_pago.strftime("%Y-%m-%d %H:%M") if pago.fecha_pago else "—"
            cliente_nombre = pago.pedido.cliente.nombre if pago.pedido else "—"
            datos.append((
                pago.id,
                cliente_nombre,
                f"${pago.monto:.2f}",
                pago.metodo.value,
                pago.estado.value,
                fecha
            ))
        return True, datos, msg
    
    def obtener_pagos_pendientes_formateados(self):
        """Obtener pagos pendientes"""
        success, pagos, msg = self.model.obtener_pagos_pendientes()
        if not success or not pagos:
            return success, [], msg
        
        datos = []
        for pago in pagos:
            cliente_nombre = pago.pedido.cliente.nombre if pago.pedido else "—"
            mesa_num = f"Mesa {pago.pedido.mesa.numero}" if pago.pedido else "—"
            datos.append((
                pago.id,
                cliente_nombre,
                mesa_num,
                f"${pago.monto:.2f}",
                pago.estado.value
            ))
        return True, datos, msg
    
    def obtener_metodos_disponibles(self):
        """Obtener lista de métodos de pago"""
        return [m.value for m in config.PagoMetodo]
    
    def obtener_pago_por_pedido(self, pedido_id: int):
        """Obtener pago de un pedido"""
        return self.model.obtener_pago_por_pedido(pedido_id)
    


    # Reportes
    def obtener_ingresos_rango_fechas(self, fecha_inicio: datetime, fecha_fin: datetime):
        """Obtener ingresos en rango"""
        success, ingresos, msg = self.model.calcular_ingresos_por_fecha(fecha_inicio, fecha_fin)
        if success:
            return True, f"${ingresos:.2f}", msg
        return success, "Error", msg
    


    def obtener_ingresos_por_metodo(self, fecha_inicio: datetime, fecha_fin: datetime):
        """Obtener desglose de ingresos por método"""
        success, desglose, msg = self.model.calcular_ingresos_por_metodo(fecha_inicio, fecha_fin)
        if not success:
            return success, {}, msg
        
        # Convertir dict a formato display-friendly
        datos_formateados = {
            metodo: f"${monto:.2f}" for metodo, monto in desglose.items()
        }
        return True, datos_formateados, msg
    


    def obtener_ingresos_por_categoria(self, fecha_inicio: datetime, fecha_fin: datetime):
        """Obtener ingresos por categoría de plato"""
        success, ingresos, msg = self.model.calcular_ingresos_por_categoria(fecha_inicio, fecha_fin)
        if not success:
            return success, {}, msg
        
        # Convertir a formato display
        datos_formateados = {
            categoria: f"${monto:.2f}" for categoria, monto in ingresos.items()
        }
        return True, datos_formateados, msg
    



    def calcular_propina_sugerida(self, monto: float) -> float:
        """
        Calcula la propina sugerida (10% del monto).
        """
        return round(monto * 0.10, 2)
    
    def buscar_cliente_por_cedula(self, cedula: str):
        if not cedula:
            return False, None, "Cédula vacía"
        
        return self.clientes_model.obtener_cliente_por_cedula(cedula)