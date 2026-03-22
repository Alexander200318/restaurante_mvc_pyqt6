"""
Modelo de Negocio: Ingredientes
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from database.models import Ingrediente
import config
from utils.validators import validar_nombre, validar_cantidad, validar_precio, validar_unidad
from .base_model import BaseModel

class IngredientesModel(BaseModel):
    """Lógica de negocio para Ingredientes"""
    
    # Lista de caracteres prohibidos para prevenir inyecciones básicas o formatos inválidos
    CARACTERES_PROHIBIDOS = ["<", ">", "{", "}", "[", "]", "*", ";"]

    def _contiene_prohibidos(self, texto: str) -> bool:
        if not texto: return False
        return any(c in texto for c in self.CARACTERES_PROHIBIDOS)
    def crear_ingrediente(self, nombre: str, unidad: str, precio_unitario: float,
                         cantidad: float = 0.0, cantidad_minima: float = 5.0,
                         proveedor: str = None) -> Tuple[bool, Optional[Ingrediente], str]:
        """Crear nuevo ingrediente"""
        # Validación de seguridad del backend (para datos inyectados)
        if self._contiene_prohibidos(nombre) or self._contiene_prohibidos(proveedor) or self._contiene_prohibidos(unidad):
             return False, None, "Se han detectado caracteres no permitidos (<, >, {, }, *, ;)"
             
        def _crear(session):
            # Verificar que no exista
            existente = session.query(Ingrediente).filter(
                Ingrediente.nombre == nombre
            ).first()
            if existente:
                raise ValueError(f"Ingrediente '{nombre}' ya existe")
            
            nuevo_ingrediente = Ingrediente(
                nombre=nombre.strip(),
                unidad=unidad.strip(),
                precio_unitario=precio_unitario,
                cantidad=cantidad,
                cantidad_minima=cantidad_minima,
                proveedor=proveedor,
                estado=config.IngredienteEstado.DISPONIBLE
            )
            session.add(nuevo_ingrediente)
            return nuevo_ingrediente
        
        return self._ejecutar_con_manejo_errores(_crear)
    
    def actualizar_ingrediente(self, ingrediente_id: int, nombre: Optional[str] = None,
                              unidad: Optional[str] = None,
                              precio_unitario: Optional[float] = None,
                              cantidad_minima: Optional[float] = None,
                              proveedor: Optional[str] = None) -> Tuple[bool, Optional[Ingrediente], str]:
        """Actualizar datos de ingrediente"""
        
        if self._contiene_prohibidos(nombre) or self._contiene_prohibidos(proveedor) or self._contiene_prohibidos(unidad):
             return False, None, "Se han detectado caracteres no permitidos (<, >, {, }, *, ;)"
             
        def _actualizar(session):
            ingrediente = session.query(Ingrediente).filter(
                Ingrediente.id == ingrediente_id
            ).first()
            if not ingrediente:
                raise ValueError(f"Ingrediente {ingrediente_id} no encontrado")
            
            if nombre:
                nombre_limpio = nombre.strip()
                # Verificar no exista otro con ese nombre
                otro = session.query(Ingrediente).filter(
                    Ingrediente.nombre == nombre_limpio,
                    Ingrediente.id != ingrediente_id
                ).first()
                if otro:
                    raise ValueError(f"Ya existe ingrediente '{nombre_limpio}'")
                ingrediente.nombre = nombre_limpio
            
            if unidad:
                ingrediente.unidad = unidad.strip()
            
            if precio_unitario is not None:
                ingrediente.precio_unitario = precio_unitario
            
            if cantidad_minima is not None:
                ingrediente.cantidad_minima = cantidad_minima
            
            if proveedor:
                ingrediente.proveedor = proveedor
            
            return ingrediente
        
        return self._ejecutar_con_manejo_errores(_actualizar)
    
    def ajustar_cantidad(self, ingrediente_id: int, cantidad_nueva: float) -> Tuple[bool, Optional[Ingrediente], str]:
        """Ajustar cantidad en stock"""
        es_valido, cantidad_validada, msg = validar_cantidad(str(cantidad_nueva))
        if not es_valido:
            return False, None, msg
        
        def _ajustar(session):
            ingrediente = session.query(Ingrediente).filter(
                Ingrediente.id == ingrediente_id
            ).first()
            if not ingrediente:
                raise ValueError(f"Ingrediente {ingrediente_id} no encontrado")
            
            ingrediente.cantidad = cantidad_validada
            
            # Actualizar estado según stock
            if cantidad_validada <= ingrediente.cantidad_minima:
                ingrediente.estado = config.IngredienteEstado.AGOTADO
            else:
                ingrediente.estado = config.IngredienteEstado.DISPONIBLE
            
            return ingrediente
        
        return self._ejecutar_con_manejo_errores(_ajustar)
    
    def usar_ingrediente(self, ingrediente_id: int, cantidad: float) -> Tuple[bool, None, str]:
        """Consumir ingrediente (restar de stock)"""
        es_valido, cantidad_validada, msg = validar_cantidad(str(cantidad))
        if not es_valido:
            return False, None, msg
        
        def _usar(session):
            ingrediente = session.query(Ingrediente).filter(
                Ingrediente.id == ingrediente_id
            ).first()
            if not ingrediente:
                raise ValueError(f"Ingrediente {ingrediente_id} no encontrado")
            
            if ingrediente.cantidad < cantidad_validada:
                raise ValueError(f"Stock insuficiente de {ingrediente.nombre}")
            
            ingrediente.cantidad -= cantidad_validada
            
            # Actualizar estado
            if ingrediente.cantidad <= ingrediente.cantidad_minima:
                ingrediente.estado = config.IngredienteEstado.AGOTADO
            else:
                ingrediente.estado = config.IngredienteEstado.DISPONIBLE
            
            return None
        
        return self._ejecutar_con_manejo_errores(_usar)
    
    def obtener_ingrediente(self, ingrediente_id: int) -> Tuple[bool, Optional[Ingrediente], str]:
        """Obtener un ingrediente por ID"""
        def _obtener(session):
            return session.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_todos_ingredientes(self) -> Tuple[bool, List[Ingrediente], str]:
        """Obtener todos los ingredientes"""
        def _obtener(session):
            return session.query(Ingrediente).order_by(Ingrediente.nombre).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_ingredientes_bajo_stock(self) -> Tuple[bool, List[Ingrediente], str]:
        """Obtener ingredientes con bajo stock"""
        def _obtener(session):
            from database.queries import QueriesManager
            return QueriesManager.obtener_ingredientes_bajo_stock(session)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_ingredientes_disponibles(self) -> Tuple[bool, List[Ingrediente], str]:
        """Obtener solo ingredientes disponibles"""
        def _obtener(session):
            return session.query(Ingrediente).filter(
                Ingrediente.estado == config.IngredienteEstado.DISPONIBLE
            ).order_by(Ingrediente.nombre).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def eliminar_ingrediente(self, ingrediente_id: int) -> Tuple[bool, None, str]:
        """Eliminar un ingrediente"""
        def _eliminar(session):
            ingrediente = session.query(Ingrediente).filter(
                Ingrediente.id == ingrediente_id
            ).first()
            if not ingrediente:
                raise ValueError(f"Ingrediente {ingrediente_id} no encontrado")
            
            # Verificar que no esté en uso en platos
            if ingrediente.platos:
                raise ValueError(f"No se puede eliminar, está en {len(ingrediente.platos)} platos")
            
            session.delete(ingrediente)
            return None
        
        return self._ejecutar_con_manejo_errores(_eliminar)
