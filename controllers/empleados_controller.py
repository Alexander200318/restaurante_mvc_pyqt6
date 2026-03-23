"""
Controlador: Empleados
"""
from models.empleados import EmpleadosModel
from models.turnos import TurnosModel
import config
from .base_controller import BaseController

class EmpleadosController(BaseController):
    """Controlador para Empleados"""
    
    def __init__(self):
        # Inicializamos el modelo primero para pasarlo al constructor base
        model = EmpleadosModel()
        super().__init__(model)
        
        # Modelo adicional para turnos
        self.turnos_model = TurnosModel()
    
    # Crear
    def crear_empleado(self, nombre: str, puesto: str, telefono: str = None, 
                      email: str = None, salario: float = None):
        """Crear nuevo empleado"""
        try:
            puesto_enum = config.EmpleadoPuesto(puesto)
            return self.model.crear_empleado(nombre, puesto_enum, telefono, email, salario)
        except ValueError:
            return False, None, f"Puesto inválido: {puesto}"
    
    # Actualizar
    def actualizar_empleado(self, empleado_id: int, nombre: str = None, puesto: str = None,
                           telefono: str = None, email: str = None, salario: float = None):
        """Actualizar empleado"""
        puesto_enum = None
        if puesto:
            try:
                puesto_enum = config.EmpleadoPuesto(puesto)
            except ValueError:
                return False, None, f"Puesto inválido: {puesto}"
        
        return self.model.actualizar_empleado(empleado_id, nombre, puesto_enum, telefono, email, salario)
    
    def cambiar_estado_empleado(self, empleado_id: int, nuevo_estado: str):
        """Cambiar estado"""
        try:
            estado = config.EmpleadoEstado(nuevo_estado)
            return self.model.cambiar_estado_empleado(empleado_id, estado)
        except ValueError:
            return False, None, f"Estado inválido: {nuevo_estado}"
    
    # Leer
    def obtener_empleado(self, empleado_id: int):
        """Obtener empleado"""
        return self.model.obtener_empleado(empleado_id)
    
    def obtener_todos_empleados_formateados(self):
        """Obtener todos formateados, incluyendo estado de turno activo"""
        success, empleados, msg = self.model.obtener_todos_empleados()
        if not success or not empleados:
            return success, [], msg

        # Obtener turnos activos
        _, turnos_activos, _ = self.turnos_model.obtener_turnos_activos()
        if not turnos_activos:
            turnos_activos = {}
        
        datos = []
        for emp in empleados:
            # Verificar si tiene turno activo
            inicio_turno = turnos_activos.get(emp.id)
            timestamp_inicio = inicio_turno.timestamp() if inicio_turno else None
            
            datos.append((
                emp.id,
                emp.nombre,
                emp.puesto.value,
                emp.telefono or "—",
                emp.email or "—",
                f"${emp.salario:.2f}" if emp.salario else "—",
                emp.estado.value,
                timestamp_inicio  # Dato extra para calcular tiempo o estado
            ))
        return True, datos, msg
    
    def obtener_puestos_disponibles(self):
        """Obtener lista de puestos"""
        puestos = [p.value for p in config.EmpleadoPuesto]
        return puestos
    
    def obtener_empleados_activos_formateados(self):
        """Obtener empleados activos"""
        success, empleados, msg = self.model.obtener_empleados_activos()
        if not success or not empleados:
            return success, [], msg
        
        datos = []
        for emp in empleados:
            datos.append((emp.id, emp.nombre, emp.puesto.value, emp.estado.value))
        return True, datos, msg
    
    def obtener_meseros_activos(self):
        """Obtener solo meseros (camareros) activos sin formatear"""
        success, empleados, msg = self.model.obtener_empleados_activos()
        if not success or not empleados:
            return False, [], msg
        
        # Filtrar solo camareros (meseros)
        meseros = [e for e in empleados if e.puesto.value.lower() == "camarero"]
        return True, meseros, msg
    
    def obtener_empleados_selectorlist(self):
        """Obtener lista para selector (camareros, chefs)"""
        success, empleados, msg = self.model.obtener_empleados_activos()
        if not success or not empleados:
            return [], []
        
        ids = [e.id for e in empleados]
        labels = [f"{e.nombre} ({e.puesto.value})" for e in empleados]
        return ids, labels
    
    # Eliminar (desactivar)
    def eliminar_empleado(self, empleado_id: int):
        """Desactivar empleado"""
        return self.model.eliminar_empleado(empleado_id)
