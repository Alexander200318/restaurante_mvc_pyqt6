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
                              unidad: str = None,
                              precio_unitario: float = None, cantidad_minima: float = None,
                              proveedor: str = None):
        """Actualizar ingrediente"""
        return self.model.actualizar_ingrediente(ingrediente_id, nombre, unidad, precio_unitario, 
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
    
    
    def obtener_todos_ingredientes(self):
        success, ingredientes, msg = self.model.obtener_todos_ingredientes()
        if not success or not ingredientes:
            return success, [], msg
    
        datos = []
        for ing in ingredientes:
            datos.append((
                ing.id,
                ing.nombre,
                f"{ing.cantidad} {ing.unidad}", # Cantidad Total formateada (ej: 50.0 Kilogramos)
                f"${ing.precio_unitario:.2f}",
                ing.cantidad_minima,
                ing.proveedor or "Sin proveedor",
                ing.estado.value
            ))
        return True, datos, msg
    

    def obtener_bajo_stock_formateados(self):
        """Obtener ingredientes bajo stock"""
        success, ingredientes, msg = self.model.obtener_ingredientes_bajo_stock()
        if not success or not ingredientes:
            return success, [], msg
        
        datos = []
        for ing in ingredientes:
            faltante = ing.cantidad_minima - ing.cantidad
            if ing.cantidad == 0:
                mensaje = f"SIN STOCK (Pedir {ing.cantidad_minima})"
            else:
                mensaje = f"BAJO: Faltan {faltante:.1f} {ing.unidad} para el mínimo"
            
            # Formato amigable para el usuario:
            # En lugar de solo números, le decimos "Tienes X, necesitas mínimo Y"
            datos.append((
                ing.id,
                ing.nombre,
                f"Tienes: {ing.cantidad} {ing.unidad} | Mínimo: {ing.cantidad_minima}",
                f"${ing.precio_unitario:.2f}",
                mensaje 
            ))
        return True, datos, msg
    
    def obtener_unidades_disponibles(self):
        """Obtener lista de unidades"""
        return ["Kilogramos", "Litros", "Gramos", "Mililitros", "Libras", "Onzas", "Piezas", "Unidades", "Docenas", "Paquetes", "Sobres", "Latas", "Botellas", "Cajas", "Bolsas", "Frascos"]
    
    # Eliminar
    def eliminar_ingrediente(self, ingrediente_id: int):
        """Eliminar ingrediente"""
        return self.model.eliminar_ingrediente(ingrediente_id)
