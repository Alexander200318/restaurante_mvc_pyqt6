"""
Modelo de Negocio: Platos/Menú
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import delete, insert, select
from database.models import Plato, Ingrediente, plato_ingrediente_association
import config
from utils.validators import validar_nombre, validar_precio, validar_descripcion
from .base_model import BaseModel

class PlatosModel(BaseModel):
    """Lógica de negocio para Platos del Menú"""
    
    def crear_plato(self, nombre: str, precio: float, categoria: config.PlatoCategoría,
                   descripcion: str = None, tiempo_preparacion: int = 15,
                   imagen_url: str = None) -> Tuple[bool, Optional[Plato], str]:
        """Crear nuevo plato"""
        # Validar nombre
        es_valido, nombre_validado, msg = validar_nombre(nombre)
        if not es_valido:
            return False, None, msg
        
        # Validar precio
        es_valido, precio_validado, msg = validar_precio(str(precio))
        if not es_valido:
            return False, None, msg
        
        # Validar descripción
        if descripcion:
            es_valido, descripcion_validada, msg = validar_descripcion(descripcion)
            if not es_valido:
                return False, None, msg
        else:
            descripcion_validada = None
        
        def _crear(session):
            # Verificar que no exista
            existente = session.query(Plato).filter(Plato.nombre == nombre_validado).first()
            if existente:
                raise ValueError(f"Plato '{nombre_validado}' ya existe")
            
            nuevo_plato = Plato(
                nombre=nombre_validado,
                precio=precio_validado,
                categoria=categoria,
                descripcion=descripcion_validada,
                tiempo_preparacion=tiempo_preparacion,
                imagen_url=imagen_url,
                estado=config.PlatoEstado.DISPONIBLE
            )
            session.add(nuevo_plato)
            return nuevo_plato
        
        return self._ejecutar_con_manejo_errores(_crear)
    
    def actualizar_plato(self, plato_id: int, nombre: Optional[str] = None,
                        precio: Optional[float] = None,
                        categoria: Optional[config.PlatoCategoría] = None,
                        descripcion: Optional[str] = None,
                        tiempo_preparacion: Optional[int] = None) -> Tuple[bool, Optional[Plato], str]:
        """Actualizar datos de plato"""
        if nombre:
            es_valido, nombre_validado, msg = validar_nombre(nombre)
            if not es_valido:
                return False, None, msg
        
        if precio is not None:
            es_valido, precio_validado, msg = validar_precio(str(precio))
            if not es_valido:
                return False, None, msg
        else:
            precio_validado = None
        
        if descripcion:
            es_valido, descripcion_validada, msg = validar_descripcion(descripcion)
            if not es_valido:
                return False, None, msg
        else:
            descripcion_validada = None
        
        def _actualizar(session):
            plato = session.query(Plato).filter(Plato.id == plato_id).first()
            if not plato:
                raise ValueError(f"Plato {plato_id} no encontrado")
            
            if nombre:
                otro = session.query(Plato).filter(
                    Plato.nombre == nombre_validado,
                    Plato.id != plato_id
                ).first()
                if otro:
                    raise ValueError(f"Ya existe plato '{nombre_validado}'")
                plato.nombre = nombre_validado
            
            if precio_validado is not None:
                plato.precio = precio_validado
            
            if categoria:
                plato.categoria = categoria
            
            if descripcion:
                plato.descripcion = descripcion_validada
            
            if tiempo_preparacion is not None:
                plato.tiempo_preparacion = tiempo_preparacion
            
            return plato
        
        return self._ejecutar_con_manejo_errores(_actualizar)
    
    def agregar_ingrediente_plato(self, plato_id: int, ingrediente_id: int,
                                 cantidad_requerida: float = 1.0,
                                 unidad: str = "unidades") -> Tuple[bool, Optional[Plato], str]:
        """Agregar ingrediente a un plato"""
        def _agregar(session):
            plato = session.query(Plato).filter(Plato.id == plato_id).first()
            if not plato:
                raise ValueError(f"Plato {plato_id} no encontrado")
            
            ingrediente = session.query(Ingrediente).filter(
                Ingrediente.id == ingrediente_id
            ).first()
            if not ingrediente:
                raise ValueError(f"Ingrediente {ingrediente_id} no encontrado")
            
            # Verificar que no esté ya agregado
            if ingrediente in plato.ingredientes:
                raise ValueError(f"Ingrediente ya está en este plato")
            
            plato.ingredientes.append(ingrediente)
            return plato
        
        return self._ejecutar_con_manejo_errores(_agregar)
    
    def remover_ingrediente_plato(self, plato_id: int, ingrediente_id: int) -> Tuple[bool, Optional[Plato], str]:
        """Remover ingrediente de un plato"""
        def _remover(session):
            plato = session.query(Plato).filter(Plato.id == plato_id).first()
            if not plato:
                raise ValueError(f"Plato {plato_id} no encontrado")
            
            ingrediente = session.query(Ingrediente).filter(
                Ingrediente.id == ingrediente_id
            ).first()
            if not ingrediente:
                raise ValueError(f"Ingrediente {ingrediente_id} no encontrado")
            
            if ingrediente in plato.ingredientes:
                plato.ingredientes.remove(ingrediente)
            else:
                raise ValueError(f"Ingrediente no está en este plato")
            
            return plato
        
        return self._ejecutar_con_manejo_errores(_remover)
    
    def cambiar_disponibilidad_plato(self, plato_id: int, 
                                    disponible: bool) -> Tuple[bool, Optional[Plato], str]:
        """Cambiar disponibilidad de un plato"""
        def _cambiar(session):
            plato = session.query(Plato).filter(Plato.id == plato_id).first()
            if not plato:
                raise ValueError(f"Plato {plato_id} no encontrado")
            
            plato.estado = (config.PlatoEstado.DISPONIBLE if disponible 
                           else config.PlatoEstado.NO_DISPONIBLE)
            return plato
        
        return self._ejecutar_con_manejo_errores(_cambiar)
    
    def obtener_plato(self, plato_id: int) -> Tuple[bool, Optional[Plato], str]:
        """Obtener un plato por ID"""
        def _obtener(session):
            return session.query(Plato).options(joinedload(Plato.ingredientes)).filter(Plato.id == plato_id).first()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_todos_platos(self) -> Tuple[bool, List[Plato], str]:
        """Obtener todos los platos"""
        def _obtener(session):
            return session.query(Plato).order_by(Plato.nombre).all()
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_platos_disponibles(self) -> Tuple[bool, List[Plato], str]:
        """Obtener solo platos disponibles"""
        def _obtener(session):
            from database.queries import QueriesManager
            return QueriesManager.obtener_platos_disponibles(session)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_platos_por_categoria(self, categoria: config.PlatoCategoría) -> Tuple[bool, List[Plato], str]:
        """Obtener platos de una categoría"""
        def _obtener(session):
            from database.queries import QueriesManager
            return QueriesManager.obtener_platos_por_categoria(session, categoria)
        
        return self._obtener_con_manejo_errores(_obtener)
    
    def obtener_ingredientes_plato(self, plato_id: int) -> Tuple[bool, List[Ingrediente], str]:
        """Obtener ingredientes de un plato"""
        def _obtener(session):
            from database.queries import QueriesManager
            return QueriesManager.obtener_ingredientes_plato(session, plato_id)
        
        return self._obtener_con_manejo_errores(_obtener)

    def obtener_ingredientes_plato_completo(self, plato_id: int) -> Tuple[bool, List[Tuple[Ingrediente, float, str]], str]:
        """Obtener ingredientes con cantidad y unidad"""
        def _obtener(session):
            # Select explícito sobre la tabla de asociación + ingrediente
            stmt = select(
                Ingrediente, 
                plato_ingrediente_association.c.cantidad_requerida,
                plato_ingrediente_association.c.unidad
            ).select_from(
                plato_ingrediente_association
            ).join(
                Ingrediente, 
                Ingrediente.id == plato_ingrediente_association.c.ingrediente_id
            ).where(
                plato_ingrediente_association.c.plato_id == plato_id
            )
            
            result = session.execute(stmt).all()
            return [(row[0], row[1], row[2]) for row in result]
        
        return self._obtener_con_manejo_errores(_obtener)

    def actualizar_ingredientes_plato(self, plato_id: int, ingredientes: List[dict]) -> Tuple[bool, None, str]:
        """Actualizar ingredientes (reemplazar todos) -> List[{'id': int, 'cantidad': float}]"""
        def _actualizar(session):
            # 1. Eliminar relaciones existentes
            stmt_del = delete(plato_ingrediente_association).where(
                plato_ingrediente_association.c.plato_id == plato_id
            )
            session.execute(stmt_del)
            
            # 2. Insertar nuevos
            if ingredientes:
                values = []
                for item in ingredientes:
                    # Validar existencia de ingrediente (opcional pero recomendado)
                    ing_id = item['id']
                    cant = float(item['cantidad'])
                    # La unidad la tomamos del ingrediente original o la pasamos
                    # Asumimos que la unidad es la del ingrediente base por simplicidad
                    # O podemos pasarla explícitamente si el UI lo permite
                    
                    ing_obj = session.query(Ingrediente).get(ing_id)
                    if not ing_obj:
                        continue 
                    
                    unid = ing_obj.unidad # Usar unidad base del ingrediente
                        
                    values.append({
                        'plato_id': plato_id,
                        'ingrediente_id': ing_id,
                        'cantidad_requerida': cant,
                        'unidad': unid
                    })
                
                if values:
                    stmt_ins = insert(plato_ingrediente_association).values(values)
                    session.execute(stmt_ins)
            
            return None
            
        return self._ejecutar_con_manejo_errores(_actualizar)
    
    def eliminar_plato(self, plato_id: int) -> Tuple[bool, None, str]:
        """Eliminar un plato"""
        def _eliminar(session):
            plato = session.query(Plato).filter(Plato.id == plato_id).first()
            if not plato:
                raise ValueError(f"Plato {plato_id} no encontrado")
            
            # Verificar que no esté en pedidos
            if plato.detalles_pedido:
                raise ValueError(f"No se puede eliminar, está en {len(plato.detalles_pedido)} pedidos")
            
            session.delete(plato)
            return None
        
        return self._ejecutar_con_manejo_errores(_eliminar)
    
    def obtener_todos_platos_con_conteo(self) -> Tuple[bool, List[tuple], str]:
        """Obtener todos los platos con conteo de ingredientes en una sola sesión"""
        def _obtener(session):
            platos = session.query(Plato).order_by(Plato.nombre).all()
            datos = []
            for plato in platos:
                # Contar ingredientes dentro de la sesión para evitar problemas con lazy loading
                num_ingredientes = len(plato.ingredientes) if plato.ingredientes else 0
                datos.append((
                    plato.id,
                    plato.nombre,
                    plato.precio,
                    plato.categoria,
                    plato.tiempo_preparacion,
                    plato.estado,
                    num_ingredientes
                ))
            return datos
        
        return self._obtener_con_manejo_errores(_obtener)
