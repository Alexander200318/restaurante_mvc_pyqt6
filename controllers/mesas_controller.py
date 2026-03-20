"""
Controlador: Mesas
Orquesta interacciones entre UI y modelo de Mesas
"""
from models.mesas import MesasModel
import config
from .base_controller import BaseController

class MesasController(BaseController):
    """Controlador para Mesas"""
    
    def __init__(self):
        self.model = MesasModel()
    
    # Crear
    def crear_mesa(self, numero: int, capacidad: int):
        """Crear nueva mesa - retorna (success, mesa, mensaje)"""
        return self.model.crear_mesa(numero, capacidad)
    
    # Actualizar
    def actualizar_mesa(self, mesa_id: int, numero: int = None, capacidad: int = None):
        """Actualizar mesa"""
        return self.model.actualizar_mesa(mesa_id, numero, capacidad)
    
    def cambiar_estado_mesa(self, mesa_id: int, nuevo_estado: str):
        """Cambiar estado de mesa"""
        try:
            estado = config.MesaEstado(nuevo_estado)
            return self.model.cambiar_estado_mesa(mesa_id, estado)
        except ValueError:
            return False, None, f"Estado inválido: {nuevo_estado}"
    
    # Leer
    def obtener_mesa(self, mesa_id: int):
        """Obtener mesa por ID"""
        return self.model.obtener_mesa(mesa_id)
    
    def obtener_todas_mesas(self):
        """Obtener todas las mesas como objetos (no formateados)"""
        return self.model.obtener_todas_mesas()
    
    def obtener_todas_mesas_formateadas(self):
        """Obtener todas las mesas formateadas para tabla"""
        success, mesas, msg = self.model.obtener_todas_mesas()
        if not success or not mesas:
            return success, [], msg
        
        # Formatear para TreeView (lista de tuplas)
        datos = []
        for mesa in mesas:
            cliente_nombre = mesa.clientes[0].nombre if mesa.clientes else "—"
            datos.append((
                mesa.id,
                mesa.numero,
                mesa.capacidad,
                cliente_nombre,
                mesa.estado.value
            ))
        return True, datos, msg
    
    def obtener_selectorlist(self):
        """Obtener lista formatada para selector (ComboBox, etc)"""
        success, mesas, msg = self.model.obtener_todas_mesas()
        if not success or not mesas:
            return [], []
        
        ids = [m.id for m in mesas]
        labels = [f"Mesa {m.numero} (Cap: {m.capacidad})" for m in mesas]
        return ids, labels
    
    def obtener_mesas_disponibles_formateadas(self):
        """Obtener mesas libres formateadas"""
        success, mesas, msg = self.model.obtener_mesas_disponibles()
        if not success or not mesas:
            return success, [], msg
        
        datos = []
        for mesa in mesas:
            datos.append((mesa.id, mesa.numero, mesa.capacidad, "—", "libre"))
        return True, datos, msg
    
    def obtener_mesas_ocupadas_formateadas(self):
        """Obtener mesas ocupadas formateadas"""
        success, mesas, msg = self.model.obtener_mesas_ocupadas()
        if not success or not mesas:
            return success, [], msg
        
        datos = []
        for mesa in mesas:
            cliente_nombre = mesa.clientes[0].nombre if mesa.clientes else "—"
            datos.append((mesa.id, mesa.numero, mesa.capacidad, cliente_nombre, "ocupada"))
        return True, datos, msg
    
    # Asignar/Liberar
    def asignar_cliente_mesa(self, mesa_id: int, cliente_id: int):
        """Asignar cliente a mesa"""
        return self.model.asignar_cliente_mesa(mesa_id, cliente_id)
    
    def liberar_mesa(self, mesa_id: int):
        """Liberar mesa"""
        return self.model.liberar_mesa(mesa_id)
    
    # Eliminar
    def eliminar_mesa(self, mesa_id: int):
        """Eliminar mesa"""
        return self.model.eliminar_mesa(mesa_id)
