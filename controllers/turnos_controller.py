"""
Controlador de Turnos
"""
from typing import List, Tuple, Optional
from datetime import datetime, date
from models.turnos import TurnosModel
from controllers.base_controller import BaseController

class TurnosController(BaseController):
    """Controlador para la gestión de turnos de empleados"""
    
    def __init__(self):
        self.model = TurnosModel()
        # No llamar a super().__init__(self.model) si BaseController no usa model
        # O si BaseController.__init__ espera model, pasarselo:
        # super().__init__(self.model)
        # Segun vimos antes, BaseController espera un modelo.
        super().__init__(self.model)
    
    def iniciar_turno(self, empleado_id: int) -> Tuple[bool, Optional[object], str]:
        """Iniciar un turno para un empleado"""
        return self.model.iniciar_turno(empleado_id)
        
    def finalizar_turno(self, empleado_id: int) -> Tuple[bool, Optional[object], str]:
        """Finalizar el turno actual de un empleado"""
        return self.model.finalizar_turno(empleado_id)
    
    def obtener_turno_actual(self, empleado_id: int) -> Tuple[bool, Optional[object], str]:
        """Obtener el turno actual de un empleado si está abierto"""
        return self.model.obtener_turno_actual(empleado_id)
        
    def obtener_historial_formateado(self, 
                                    fecha_inicio: Optional[date] = None,
                                    fecha_fin: Optional[date] = None,
                                    empleado_id: Optional[int] = None,
                                    nombre_empleado: Optional[str] = None,
                                    duracion_min_horas: Optional[float] = None,
                                    duracion_max_horas: Optional[float] = None) -> Tuple[bool, List[tuple], str]:
        """
        Obtener historial de turnos formateado y filtrado
        
        Args:
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            empleado_id: ID exacto del empleado
            nombre_empleado: Búsqueda parcial por nombre
            duracion_min_horas: Duración mínima en horas
            duracion_max_horas: Duración máxima en horas
        """
        
        # Validar consistencia de fechas si ambas están presentes
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
             return False, [], "La fecha de inicio no puede ser mayor que la fecha final."

        # Llamar al modelo
        # NOTA: Ajusta fecha_inicio y fecha_fin en el modelo de turnos.py para que acepten estos argumentos 
        # si cambiaste la firma en el modelo. Asumo que el modelo ya soporta fecha_inicio/fin o los maneja.
        # Si el modelo espera 'fecha_filtro', necesitamos adaptar.
        # Revision rapida: El modelo fue actualizado a obtener_historial_turnos(fecha_inicio, fecha_fin, ...)
        
        success, turnos, msg = self.model.obtener_historial_turnos(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            empleado_id=empleado_id,
            nombre_empleado=nombre_empleado
        )
        
        if not success or not turnos:
            return False, [], msg
            
        datos = []
        for turno in turnos:
            # Calcular duración
            if turno.fecha_fin:
                duracion = turno.fecha_fin - turno.fecha_inicio
            else:
                duracion = datetime.now() - turno.fecha_inicio
            
            duracion_horas = duracion.total_seconds() / 3600
            
            # FILTRO: Duración Mínima
            if duracion_min_horas is not None and duracion_horas < duracion_min_horas:
                continue
                
            # FILTRO: Duración Máxima
            if duracion_max_horas is not None and duracion_horas > duracion_max_horas:
                continue

            empleado_nombre = turno.empleado.nombre if turno.empleado else "Desconocido"
            
            # Formato de Fechas y Hora
            inicio_fmt = turno.fecha_inicio.strftime("%d/%m/%Y %H:%M")
            fin_fmt = turno.fecha_fin.strftime("%d/%m/%Y %H:%M") if turno.fecha_fin else "En curso"
            
            # Formatear duración bonita
            total_seconds = int(duracion.total_seconds())
            horas, remainder = divmod(total_seconds, 3600)
            minutos, _ = divmod(remainder, 60)
            
            if turno.fecha_fin:
                duracion_str = f"{horas}h {minutos}m"
            else:
                duracion_str = f"{horas}h {minutos}m (Actual)"
            
            datos.append((
                turno.id,
                empleado_nombre,
                inicio_fmt,
                fin_fmt,
                duracion_str
            ))
            
        return True, datos, msg
