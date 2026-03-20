"""
Controlador: Platos/Menú
"""
from models.platos import PlatosModel
import config
from .base_controller import BaseController

class PlatosController(BaseController):
    """Controlador para Platos"""
    
    def __init__(self):
        self.model = PlatosModel()
    
    # Crear
    def crear_plato(self, nombre: str, precio: float, categoria: str,
                   descripcion: str = None, tiempo_preparacion: int = 15,
                   imagen_url: str = None):
        """Crear plato"""
        try:
            categoria_enum = config.PlatoCategoría(categoria)
            return self.model.crear_plato(nombre, precio, categoria_enum, descripcion, 
                                         tiempo_preparacion, imagen_url)
        except ValueError:
            return False, None, f"Categoría inválida: {categoria}"
    
    # Actualizar
    def actualizar_plato(self, plato_id: int, nombre: str = None, precio: float = None,
                        categoria: str = None, descripcion: str = None,
                        tiempo_preparacion: int = None):
        """Actualizar plato"""
        categoria_enum = None
        if categoria:
            try:
                categoria_enum = config.PlatoCategoría(categoria)
            except ValueError:
                return False, None, f"Categoría inválida: {categoria}"
        
        return self.model.actualizar_plato(plato_id, nombre, precio, categoria_enum, 
                                          descripcion, tiempo_preparacion)
    
    def cambiar_disponibilidad(self, plato_id: int, disponible: bool):
        """Cambiar disponibilidad"""
        return self.model.cambiar_disponibilidad_plato(plato_id, disponible)
    
    def agregar_ingrediente(self, plato_id: int, ingrediente_id: int,
                           cantidad_requerida: float = 1.0, unidad: str = "unidades"):
        """Agregar ingrediente a plato"""
        return self.model.agregar_ingrediente_plato(plato_id, ingrediente_id, 
                                                   cantidad_requerida, unidad)
    
    def remover_ingrediente(self, plato_id: int, ingrediente_id: int):
        """Remover ingrediente de plato"""
        return self.model.remover_ingrediente_plato(plato_id, ingrediente_id)
    
    # Leer
    def obtener_plato(self, plato_id: int):
        """Obtener plato"""
        return self.model.obtener_plato(plato_id)
    
    def obtener_platos_disponibles(self):
        """Obtener platos disponibles sin formatear (para UI)"""
        return self.model.obtener_platos_disponibles()
    
    def obtener_todos_platos_formateados(self):
        """Obtener todos formateados"""
        success, datos, msg = self.model.obtener_todos_platos_con_conteo()
        if not success or not datos:
            return success, [], msg
        
        datos_formateados = []
        for plato in datos:
            datos_formateados.append((
                plato[0],  # ID
                plato[1],  # nombre
                f"${plato[2]:.2f}",  # precio
                plato[3].value,  # categoria
                plato[4],  # tiempo_preparacion
                plato[5].value,  # estado
                plato[6]  # num_ingredientes
            ))
        return True, datos_formateados, msg
    
    def obtener_platos_disponibles_formateados(self):
        """Obtener platos disponibles"""
        success, platos, msg = self.model.obtener_platos_disponibles()
        if not success or not platos:
            return success, [], msg
        
        datos = []
        for plato in platos:
            datos.append((plato.id, plato.nombre, f"${plato.precio:.2f}", plato.categoria.value))
        return True, datos, msg
    
    def obtener_selectorlist(self):
        """Obtener lista para selector"""
        success, platos, msg = self.model.obtener_platos_disponibles()
        if not success or not platos:
            return [], []
        
        ids = [p.id for p in platos]
        labels = [f"{p.nombre} (${p.precio:.2f})" for p in platos]
        return ids, labels
    
    def obtener_categorias_disponibles(self):
        """Obtener lista de categorías"""
        return [c.value for c in config.PlatoCategoría]
    
    def obtener_ingredientes_plato_formateados(self, plato_id: int):
        """Obtener ingredientes de un plato"""
        success, ingredientes, msg = self.model.obtener_ingredientes_plato(plato_id)
        if not success or not ingredientes:
            return success, [], msg
        
        datos = []
        for ing in ingredientes:
            datos.append((ing.id, ing.nombre, f"${ing.precio_unitario:.2f}"))
        return True, datos, msg
    
    # Eliminar
    def eliminar_plato(self, plato_id: int):
        """Eliminar plato"""
        return self.model.eliminar_plato(plato_id)
