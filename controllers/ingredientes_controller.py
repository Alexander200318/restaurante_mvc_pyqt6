"""
Controlador: Ingredientes
"""
from models.ingredientes import IngredientesModel
import config
from .base_controller import BaseController

class IngredientesController(BaseController):
    """Controlador para Ingredientes"""
    
    def __init__(self):
        self.model = IngredientesModel()
    
    # Crear
    def crear_ingrediente(self, nombre: str, unidad: str, precio_unitario: float,
                         cantidad: float = 0.0, cantidad_minima: float = 5.0, 
                         proveedor: str = None):
        """Crear ingrediente"""
        return self.model.crear_ingrediente(nombre, unidad, precio_unitario, 
                                           cantidad, cantidad_minima, proveedor)
    
    # Actualizar
    def actualizar_ingrediente(self, ingrediente_id: int, nombre: str = None,
                              precio_unitario: float = None, cantidad_minima: float = None,
                              proveedor: str = None):
        """Actualizar ingrediente"""
        return self.model.actualizar_ingrediente(ingrediente_id, nombre, precio_unitario, 
                                                cantidad_minima, proveedor)
    
    def ajustar_cantidad(self, ingrediente_id: int, cantidad_nueva: float):
        """Ajustar stock"""
        return self.model.ajustar_cantidad(ingrediente_id, cantidad_nueva)
    
    def usar_ingrediente(self, ingrediente_id: int, cantidad: float):
        """Consumir ingrediente"""
        return self.model.usar_ingrediente(ingrediente_id, cantidad)
    
    # Leer
    def obtener_ingrediente(self, ingrediente_id: int):
        """Obtener ingrediente"""
        return self.model.obtener_ingrediente(ingrediente_id)
    
    def obtener_todos_ingredientes_formateados(self):
        """Obtener todos formateados"""
        success, ingredientes, msg = self.model.obtener_todos_ingredientes()
        if not success or not ingredientes:
            return success, [], msg
        
        datos = []
        for ing in ingredientes:
            datos.append((
                ing.id,
                ing.nombre,
                f"{ing.cantidad} {ing.unidad}",
                f"${ing.precio_unitario:.2f}",
                ing.proveedor or "—",
                ing.estado.value,
                "⚠️ BAJO STOCK" if ing.esta_bajo_stock() else "✓"
            ))
        return True, datos, msg
    
    def obtener_bajo_stock_formateados(self):
        """Obtener ingredientes bajo stock"""
        success, ingredientes, msg = self.model.obtener_ingredientes_bajo_stock()
        if not success or not ingredientes:
            return success, [], msg
        
        datos = []
        for ing in ingredientes:
            datos.append((
                ing.id,
                ing.nombre,
                f"{ing.cantidad}/{ing.cantidad_minima} {ing.unidad}",
                f"${ing.precio_unitario:.2f}",
                "AGOTADO"
            ))
        return True, datos, msg
    
    def obtener_unidades_disponibles(self):
        """Obtener lista de unidades"""
        return ["kg", "L", "g", "ml", "unidades", "docenas", "botellas", "cajas"]
    
    # Eliminar
    def eliminar_ingrediente(self, ingrediente_id: int):
        """Eliminar ingrediente"""
        return self.model.eliminar_ingrediente(ingrediente_id)
