"""
Consultas complejas de base de datos con JOINs y filtros
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from .models import (
    Mesa, Cliente, Empleado, Ingrediente, Plato, 
    Pedido, DetallePedido, Pago, UsoIngrediente
)
import config

class QueriesManager:
    """Gestor de consultas complejas"""
    
    @staticmethod
    def obtener_pedidos_por_mesa(session: Session, mesa_id: int) -> List[Pedido]:
        """Obtener todos los pedidos de una mesa específica"""
        return session.query(Pedido).filter(Pedido.mesa_id == mesa_id).all()
    
    @staticmethod
    def obtener_pedidos_activos(session: Session) -> List[Pedido]:
        """Obtener pedidos no entregados ni cancelados"""
        estados_activos = [
            config.PedidoEstado.PENDIENTE,
            config.PedidoEstado.PREPARANDO,
            config.PedidoEstado.LISTO
        ]
        return session.query(Pedido).filter(Pedido.estado.in_(estados_activos)).all()
    
    @staticmethod
    def obtener_pedidos_por_fecha(session: Session, fecha_inicio: datetime, fecha_fin: datetime) -> List[Pedido]:
        """Obtener pedidos en un rango de fechas"""
        return session.query(Pedido).filter(
            and_(
                Pedido.fecha_creacion >= fecha_inicio,
                Pedido.fecha_creacion <= fecha_fin
            )
        ).all()
    
    @staticmethod
    def obtener_pedidos_por_estado(session: Session, estado: config.PedidoEstado) -> List[Pedido]:
        """Obtener pedidos por estado específico"""
        return session.query(Pedido).filter(Pedido.estado == estado).all()
    
    @staticmethod
    def obtener_mesas_disponibles(session: Session) -> List[Mesa]:
        """Obtener mesas libres"""
        return session.query(Mesa).filter(Mesa.estado == config.MesaEstado.LIBRE).all()
    
    @staticmethod
    def obtener_mesas_ocupadas(session: Session) -> List[Mesa]:
        """Obtener mesas ocupadas"""
        from sqlalchemy.orm import selectinload
        return session.query(Mesa).options(selectinload(Mesa.clientes)).filter(Mesa.estado == config.MesaEstado.OCUPADA).all()
    
    @staticmethod
    def obtener_empleados_activos(session: Session) -> List[Empleado]:
        """Obtener empleados activos"""
        return session.query(Empleado).filter(
            Empleado.estado == config.EmpleadoEstado.ACTIVO
        ).all()
    
    @staticmethod
    def obtener_ingredientes_bajo_stock(session: Session) -> List[Ingrediente]:
        """Obtener ingredientes con stock bajo (cantidad <= cantidad_minima)"""
        return session.query(Ingrediente).filter(
            Ingrediente.cantidad <= Ingrediente.cantidad_minima
        ).all()
    
    @staticmethod
    def obtener_platos_disponibles(session: Session) -> List[Plato]:
        """Obtener platos disponibles en el menú"""
        return session.query(Plato).filter(
            Plato.estado == config.PlatoEstado.DISPONIBLE
        ).all()
    
    @staticmethod
    def obtener_platos_por_categoria(session: Session, categoria: config.PlatoCategoría) -> List[Plato]:
        """Obtener platos de una categoría específica"""
        return session.query(Plato).filter(
            and_(
                Plato.categoria == categoria,
                Plato.estado == config.PlatoEstado.DISPONIBLE
            )
        ).all()
    
    @staticmethod
    def obtener_ingredientes_plato(session: Session, plato_id: int) -> List[Ingrediente]:
        """Obtener todos los ingredientes de un plato específico (JOIN)"""
        plato = session.query(Plato).filter(Plato.id == plato_id).first()
        if not plato:
            return []
        return plato.ingredientes
    
    @staticmethod
    def obtener_total_pedido(session: Session, pedido_id: int) -> float:
        """Obtener total de un pedido (con JOIN a detalles)"""
        pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            return 0.0
        return pedido.calcular_total()
    
    @staticmethod
    def obtener_detalles_pedido(session: Session, pedido_id: int) -> List[DetallePedido]:
        """Obtener detalles de un pedido específico"""
        return session.query(DetallePedido).filter(
            DetallePedido.pedido_id == pedido_id
        ).all()
    
    @staticmethod
    def obtener_pagos_pendientes(session: Session) -> List[Pago]:
        """Obtener pagos pendientes"""
        return session.query(Pago).filter(
            Pago.estado.in_([config.PagoEstado.PENDIENTE, config.PagoEstado.PARCIAL])
        ).all()
    
    @staticmethod
    def obtener_pago_por_pedido(session: Session, pedido_id: int) -> Optional[Pago]:
        """Obtener pago de un pedido específico"""
        return session.query(Pago).filter(Pago.pedido_id == pedido_id).first()
    
    @staticmethod
    def calcular_ingresos_por_fecha(session: Session, fecha_inicio: datetime, fecha_fin: datetime) -> float:
        """Calcular ingresos totales en un rango de fechas (pagos completados)"""
        result = session.query(func.sum(Pago.monto)).filter(
            and_(
                Pago.estado == config.PagoEstado.PAGADO,
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin
            )
        ).scalar()
        return float(result) if result else 0.0
    
    @staticmethod
    def calcular_ingresos_por_metodo(session: Session, 
                                     fecha_inicio: datetime, 
                                     fecha_fin: datetime) -> dict:
        """Calcular ingresos por método de pago"""
        resultados = session.query(
            Pago.metodo,
            func.sum(Pago.monto).label('total')
        ).filter(
            and_(
                Pago.estado == config.PagoEstado.PAGADO,
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin
            )
        ).group_by(Pago.metodo).all()
        
        return {str(metodo): total for metodo, total in resultados}
    
    @staticmethod
    def obtener_platos_mas_vendidos(session: Session, limite: int = 10) -> List[Tuple]:
        """Obtener platos más vendidos (con cantidad total vendida)"""
        resultados = session.query(
            Plato.nombre,
            func.sum(DetallePedido.cantidad).label('total_vendido'),
            func.sum(DetallePedido.subtotal).label('ingresos')
        ).join(
            DetallePedido, Plato.id == DetallePedido.plato_id
        ).join(
            Pedido, DetallePedido.pedido_id == Pedido.id
        ).filter(
            Pedido.estado.in_([
                config.PedidoEstado.ENTREGADO,
                config.PedidoEstado.LISTO
            ])
        ).group_by(
            Plato.id, Plato.nombre
        ).order_by(
            func.sum(DetallePedido.cantidad).desc()
        ).limit(limite).all()
        
        return resultados
    
    @staticmethod
    def obtener_ingredientes_mas_usados(session: Session, limite: int = 10) -> List[Tuple]:
        """Obtener ingredientes más usados"""
        resultados = session.query(
            Ingrediente.nombre,
            func.sum(UsoIngrediente.cantidad_usada).label('total_usado')
        ).join(
            UsoIngrediente, Ingrediente.id == UsoIngrediente.ingrediente_id
        ).group_by(
            Ingrediente.id, Ingrediente.nombre
        ).order_by(
            func.sum(UsoIngrediente.cantidad_usada).desc()
        ).limit(limite).all()
        
        return resultados
    
    @staticmethod
    def obtener_ingresos_por_categoria(session: Session, 
                                       fecha_inicio: datetime, 
                                       fecha_fin: datetime) -> dict:
        """Obtener ingresos por categoría de plato"""
        resultados = session.query(
            Plato.categoria,
            func.sum(DetallePedido.subtotal).label('ingresos')
        ).join(
            DetallePedido, Plato.id == DetallePedido.plato_id
        ).join(
            Pedido, DetallePedido.pedido_id == Pedido.id
        ).filter(
            and_(
                Pedido.fecha_creacion >= fecha_inicio,
                Pedido.fecha_creacion <= fecha_fin,
                Pedido.estado != config.PedidoEstado.CANCELADO
            )
        ).group_by(
            Plato.categoria
        ).all()
        
        return {str(categoria): ingresos for categoria, ingresos in resultados}
    
    @staticmethod
    def obtener_ticket_completo(session: Session, pedido_id: int) -> dict:
        """Obtener toda la información de un pedido para imprimir (ticket completo)"""
        pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            return {}
        
        detalles = session.query(DetallePedido).filter(
            DetallePedido.pedido_id == pedido_id
        ).all()
        
        pago = session.query(Pago).filter(Pago.pedido_id == pedido_id).first()
        
        return {
            'pedido': pedido,
            'detalles': detalles,
            'pago': pago,
            'total': pedido.calcular_total()
        }
    
    @staticmethod
    def obtener_cliente_con_mesa(session: Session, cliente_id: int) -> Optional[dict]:
        """Obtener cliente con su mesa asociada (JOIN)"""
        cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            return None
        
        return {
            'cliente': cliente,
            'mesa': cliente.mesa,
            'estado': cliente.estado
        }
    
    @staticmethod
    def estadisticas_diarias(session: Session, fecha: datetime) -> dict:
        """Obtener estadísticas del día"""
        inicio_dia = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        
        pedidos_dia = session.query(Pedido).filter(
            and_(
                Pedido.fecha_creacion >= inicio_dia,
                Pedido.fecha_creacion < fin_dia
            )
        ).count()
        
        ingresos_dia = QueriesManager.calcular_ingresos_por_fecha(
            session, inicio_dia, fin_dia
        )
        
        platos_vendidos = session.query(func.sum(DetallePedido.cantidad)).join(
            Pedido, DetallePedido.pedido_id == Pedido.id
        ).filter(
            and_(
                Pedido.fecha_creacion >= inicio_dia,
                Pedido.fecha_creacion < fin_dia
            )
        ).scalar() or 0
        
        return {
            'fecha': fecha.date(),
            'pedidos_totales': pedidos_dia,
            'ingresos': ingresos_dia,
            'items_vendidos': platos_vendidos
        }
