"""
Modelo de Negocio: Turnos
"""
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import desc, func
from sqlalchemy.orm import joinedload
from database.models import Turno, Empleado
from .base_model import BaseModel

class TurnosModel(BaseModel):
    """Lógica de negocio para Turnos"""
    
    def iniciar_turno(self, empleado_id: int) -> Tuple[bool, Optional[Turno], str]:
        """Registrar el inicio de un turno para un empleado"""
        def _iniciar(session):
            # Verificar si ya tiene un turno abierto
            turno_abierto = session.query(Turno).filter(
                Turno.empleado_id == empleado_id,
                Turno.fecha_fin.is_(None)
            ).first()
            
            if turno_abierto:
                raise ValueError(f"El empleado ya tiene un turno abierto desde {turno_abierto.fecha_inicio}")
            
            # Verificar existencia de empleado
            empleado = session.query(Empleado).filter(Empleado.id == empleado_id).first()
            if not empleado:
                raise ValueError(f"Empleado con ID {empleado_id} no encontrado")
                
            nuevo_turno = Turno(
                empleado_id=empleado_id,
                fecha_inicio=datetime.now()
            )
            session.add(nuevo_turno)
            return nuevo_turno
            
        return self._ejecutar_con_manejo_errores(_iniciar)
    
    def finalizar_turno(self, empleado_id: int) -> Tuple[bool, Optional[Turno], str]:
        """Registrar el fin de un turno"""
        def _finalizar(session):
            turno_abierto = session.query(Turno).filter(
                Turno.empleado_id == empleado_id,
                Turno.fecha_fin.is_(None)
            ).order_by(desc(Turno.fecha_inicio)).first()
            
            if not turno_abierto:
                raise ValueError("El empleado no tiene un turno abierto para cerrar")
            
            turno_abierto.fecha_fin = datetime.now()
            return turno_abierto
            
        return self._ejecutar_con_manejo_errores(_finalizar)
    
    def obtener_turno_actual(self, empleado_id: int) -> Tuple[bool, Optional[Turno], str]:
        """Obtener el turno actual abierto si existe"""
        def _obtener(session):
            return session.query(Turno).filter(
                Turno.empleado_id == empleado_id,
                Turno.fecha_fin.is_(None)
            ).first()
            
        return self._ejecutar_con_manejo_errores(_obtener)

    def obtener_historial_turnos(self, 
                               fecha_inicio: Optional[datetime.date] = None,
                               fecha_fin: Optional[datetime.date] = None,
                               empleado_id: Optional[int] = None,
                               nombre_empleado: Optional[str] = None) -> Tuple[bool, List[Turno], str]:
        """Obtener historial de turnos con filtros avanzados"""
        def _listar(session):
            query = session.query(Turno)\
                .join(Empleado)\
                .options(joinedload(Turno.empleado))\
                .order_by(desc(Turno.fecha_inicio))
            
            if empleado_id:
                query = query.filter(Turno.empleado_id == empleado_id)
            
            if nombre_empleado:
                # Filtrado insensible a mayúsculas/minúsculas y acentos (básico)
                search_term = f"%{nombre_empleado}%"
                query = query.filter(Empleado.nombre.ilike(search_term))
            
            # Filtro fechas robusto (usando rangos de datetime)
            if fecha_inicio:
                dt_inicio = datetime.combine(fecha_inicio, datetime.min.time())
                query = query.filter(Turno.fecha_inicio >= dt_inicio)
            
            if fecha_fin:
                dt_fin = datetime.combine(fecha_fin, datetime.max.time())
                query = query.filter(Turno.fecha_inicio <= dt_fin)
                
            return query.all()
            
        return self._ejecutar_con_manejo_errores(_listar)

    def obtener_turnos_activos(self) -> Tuple[bool, dict, str]:
        """Obtiene un diccionario {empleado_id: fecha_inicio} para turnos sin cerrar"""
        def _obtener(session):
            turnos = session.query(Turno).filter(Turno.fecha_fin.is_(None)).all()
            return {t.empleado_id: t.fecha_inicio for t in turnos}
        
        return self._ejecutar_con_manejo_errores(_obtener)
