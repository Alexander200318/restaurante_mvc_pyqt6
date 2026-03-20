"""
Controlador: Clientes
"""
from models.clientes import ClientesModel
import config
from .base_controller import BaseController

class ClientesController(BaseController):
    """Controlador para Clientes"""
    
    def __init__(self):
        self.model = ClientesModel()
    
    # Crear
    def crear_cliente(self, nombre: str, mesa_id: int, cantidad_personas: int = 1, telefono: str = None):
        """Crear nuevo cliente"""
        return self.model.crear_cliente(nombre, mesa_id, cantidad_personas, telefono)
    
    # Actualizar
    def actualizar_cliente(self, cliente_id: int, nombre: str = None, cantidad_personas: int = None, telefono: str = None):
        """Actualizar cliente"""
        return self.model.actualizar_cliente(cliente_id, nombre, cantidad_personas, telefono)
    
    def cambiar_estado_cliente(self, cliente_id: int, nuevo_estado: str):
        """Cambiar estado"""
        try:
            estado = config.ClienteEstado(nuevo_estado)
            return self.model.cambiar_estado_cliente(cliente_id, estado)
        except ValueError:
            return False, None, f"Estado inválido: {nuevo_estado}"
    
    # Leer
    def obtener_cliente(self, cliente_id: int):
        """Obtener cliente por ID"""
        return self.model.obtener_cliente(cliente_id)
    
    def obtener_todos_clientes_formateados(self):
        """Obtener todos los clientes formateados para tabla"""
        success, clientes, msg = self.model.obtener_todos_clientes()
        if not success or not clientes:
            return success, [], msg
        
        datos = []
        for cliente in clientes:
            mesa_num = cliente.mesa.numero if cliente.mesa else "—"
            datos.append((
                cliente.id,
                cliente.nombre,
                mesa_num,
                cliente.cantidad_personas,
                cliente.telefono or "—",
                cliente.estado.value
            ))
        return True, datos, msg
    
    def obtener_selectorlist(self):
        """Obtener lista para selector"""
        success, clientes, msg = self.model.obtener_clientes_comiendo()
        if not success or not clientes:
            return [], []
        
        ids = [c.id for c in clientes]
        labels = [f"Mesa {c.mesa.numero} - {c.nombre}" for c in clientes]
        return ids, labels
    
    def obtener_clientes_comiendo_formateados(self):
        """Obtener clientes activos"""
        success, clientes, msg = self.model.obtener_clientes_comiendo()
        if not success or not clientes:
            return success, [], msg
        
        datos = []
        for cliente in clientes:
            mesa_num = cliente.mesa.numero if cliente.mesa else "—"
            datos.append((cliente.id, cliente.nombre, mesa_num, cliente.cantidad_personas, cliente.estado.value))
        return True, datos, msg
    
    # Eliminar
    def eliminar_cliente(self, cliente_id: int):
        """Eliminar cliente"""
        return self.model.eliminar_cliente(cliente_id)
