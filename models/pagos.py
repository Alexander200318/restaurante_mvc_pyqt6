"""
Modelo de Negocio: Pagos
"""
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from database.models import Pago, Pedido, Mesa
from database.queries import QueriesManager
import config
from utils.validators import validar_precio
from .base_model import BaseModel

class PagosModel(BaseModel):
    """Lógica de negocio para Pagos"""
    
    def registrar_pago(self, pedido_id: int, monto: float, metodo: config.PagoMetodo,
                      referencia: str = None, cambio: float = 0.0) -> Tuple[bool, Optional[Pago], str]:
        """Registrar un pago para un pedido"""
        # Validar monto
        es_valido, monto_validado, msg = validar_precio(str(monto))
        if not es_valido:
            return False, None, msg
        
        def _registrar(session):
            pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if not pedido:
                raise ValueError(f"Pedido {pedido_id} no encontrado")
            
            # Verificar que no tenga pago registrado
            pago_existente = session.query(Pago).filter(Pago.pedido_id == pedido_id).first()
            if pago_existente:
                raise ValueError(f"Pedido ya tiene pago registrado")
            
            # Calcular total del pedido
            total_pedido = pedido.calcular_total()
            
            # Determinar estado según monto
            if monto_validado >= total_pedido:
                estado_pago = config.PagoEstado.PAGADO
            elif monto_validado > 0:
                estado_pago = config.PagoEstado.PARCIAL
            else:
                estado_pago = config.PagoEstado.PENDIENTE
            
            nuevo_pago = Pago(
                pedido_id=pedido_id,
                monto=monto_validado,
                metodo=metodo,
                referencia=referencia,
                cambio=cambio,
                estado=estado_pago,
                fecha_pago=datetime.now() if estado_pago != config.PagoEstado.PENDIENTE else None
            )
            session.add(nuevo_pago)
            
            # Si pago está completo, liberar mesa
            if estado_pago == config.PagoEstado.PAGADO:
                if pedido.mesa:
                    pedido.mesa.estado = config.MesaEstado.LIBRE
                
                # Cambiar estado del cliente
                pedido.cliente.estado = config.ClienteEstado.PAGADO
            
            return nuevo_pago
        
        return self._ejecutar_con_manejo_errores(_registrar)
    
    def actualizar_pago(self, pago_id: int, monto: Optional[float] = None,
                       metodo: Optional[config.PagoMetodo] = None,
                       referencia: Optional[str] = None) -> Tuple[bool, Optional[Pago], str]:
        """Actualizar datos de pago"""
        if monto is not None:
            es_valido, monto_validado, msg = validar_precio(str(monto))
            if not es_valido:
                return False, None, msg
        else:
            monto_validado = None
        
        def _actualizar(session):
            pago = session.query(Pago).filter(Pago.id == pago_id).first()
            if not pago:
                raise ValueError(f"Pago {pago_id} no encontrado")
            
            if monto_validado is not None:
                pago.monto = monto_validado
            
            if metodo:
                pago.metodo = metodo
            
            if referencia:
                pago.referencia = referencia
            
            return pago
        
        return self._ejecutar_con_manejo_errores(_actualizar)
    
    def completar_pago(self, pago_id: int, cambio: float = 0.0) -> Tuple[bool, Optional[Pago], str]:
        """Marcar pago como completado"""
        def _completar(session):
            pago = session.query(Pago).filter(Pago.id == pago_id).first()
            if not pago:
                raise ValueError(f"Pago {pago_id} no encontrado")
            
            pago.estado = config.PagoEstado.PAGADO
            pago.fecha_pago = datetime.now()
            if cambio:
                pago.cambio = cambio
            
            # Liberar mesa
            pedido = pago.pedido
            if pedido and pedido.mesa:
                pedido.mesa.estado = config.MesaEstado.LIBRE
            
            # Cambiar estado del cliente
            if pedido and pedido.cliente:
                pedido.cliente.estado = config.ClienteEstado.PAGADO
            
            return pago
        
        return self._ejecutar_con_manejo_errores(_completar)
    
    def anular_pago(self, pago_id: int) -> Tuple[bool, None, str]:
        """Anular un pago (volver a PENDIENTE)"""
        def _anular(session):
            pago = session.query(Pago).filter(Pago.id == pago_id).first()
            if not pago:
                raise ValueError(f"Pago {pago_id} no encontrado")
            
            pago.estado = config.PagoEstado.PENDIENTE
            pago.fecha_pago = None
            
            # Volver a ocupar mesa
            pedido = pago.pedido
            if pedido and pedido.mesa:
                pedido.mesa.estado = config.MesaEstado.OCUPADA
            
            return None
        
        return self._ejecutar_con_manejo_errores(_anular)
    
    def obtener_pago(self, pago_id: int) -> Tuple[bool, Optional[Pago], str]:
        """Obtener un pago por ID"""
        def _obtener(session):
            return session.query(Pago).filter(Pago.id == pago_id).first()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_pago_por_pedido(self, pedido_id: int) -> Tuple[bool, Optional[Pago], str]:
        """Obtener pago de un pedido específico"""
        def _obtener(session):
            return QueriesManager.obtener_pago_por_pedido(session, pedido_id)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_todos_pagos(self) -> Tuple[bool, List[Pago], str]:
        """Obtener todos los pagos"""
        def _obtener(session):
            return session.query(Pago).options(
                joinedload(Pago.pedido).joinedload(Pedido.cliente),
                joinedload(Pago.pedido).joinedload(Pedido.mesa)
            ).order_by(Pago.fecha_pago.desc()).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_pagos_pendientes(self) -> Tuple[bool, List[Pago], str]:
        """Obtener pagos que no están completados"""
        def _obtener(session):
            return session.query(Pago).options(
                joinedload(Pago.pedido).joinedload(Pedido.cliente),
                joinedload(Pago.pedido).joinedload(Pedido.mesa)
            ).filter(
                Pago.estado.in_([config.PagoEstado.PENDIENTE, config.PagoEstado.PARCIAL])
            ).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_pagos_por_estado(self, estado: config.PagoEstado) -> Tuple[bool, List[Pago], str]:
        """Obtener pagos por estado específico"""
        def _obtener(session):
            return session.query(Pago).filter(Pago.estado == estado).order_by(
                Pago.fecha_pago.desc()
            ).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_pagos_por_metodo(self, metodo: config.PagoMetodo) -> Tuple[bool, List[Pago], str]:
        """Obtener pagos por método de pago"""
        def _obtener(session):
            return session.query(Pago).filter(
                Pago.metodo == metodo,
                Pago.estado == config.PagoEstado.PAGADO
            ).order_by(Pago.fecha_pago.desc()).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def calcular_ingresos_por_fecha(self, fecha_inicio, fecha_fin) -> Tuple[bool, float, str]:
        """Calcular ingresos totales en un rango de fechas"""
        def _calcular(session):
            return QueriesManager.calcular_ingresos_por_fecha(session, fecha_inicio, fecha_fin)
        
        return self._obtener_con_manejo_errores(_calcular)
    
    def calcular_ingresos_por_metodo(self, fecha_inicio, fecha_fin) -> Tuple[bool, dict, str]:
        """Calcular ingresos por método de pago"""
        def _calcular(session):
            return QueriesManager.calcular_ingresos_por_metodo(session, fecha_inicio, fecha_fin)
        
        return self._obtener_con_manejo_errores(_calcular)
    
    def calcular_ingresos_por_categoria(self, fecha_inicio, fecha_fin) -> Tuple[bool, dict, str]:
        """Calcular ingresos por categoría de plato"""
        def _calcular(session):
            return QueriesManager.obtener_ingresos_por_categoria(session, fecha_inicio, fecha_fin)
        
        return self._obtener_con_manejo_errores(_calcular)
