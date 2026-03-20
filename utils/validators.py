"""
Validadores para entrada de datos
Retornan tuplas (es_válido, valor_procesado, mensaje_error)
"""
from typing import Tuple, Any, Optional

def validar_numero_mesa(numero: str) -> Tuple[bool, Optional[int], str]:
    """Valida número de mesa (debe ser entero positivo)"""
    try:
        num = int(numero.strip())
        if num <= 0:
            return False, None, "El número de mesa debe ser positivo"
        return True, num, ""
    except ValueError:
        return False, None, "El número de mesa debe ser un número entero"

def validar_capacidad(capacidad: str) -> Tuple[bool, Optional[int], str]:
    """Valida capacidad de mesa (debe ser entero 1-20)"""
    try:
        cap = int(capacidad.strip())
        if cap < 1 or cap > 20:
            return False, None, "La capacidad debe estar entre 1 y 20"
        return True, cap, ""
    except ValueError:
        return False, None, "La capacidad debe ser un número entero"

def validar_nombre(nombre: str, min_length: int = 2, max_length: int = 100) -> Tuple[bool, Optional[str], str]:
    """Valida nombre (no vacío, longitud razonable)"""
    nombre = nombre.strip()
    if not nombre:
        return False, None, "El nombre no puede estar vacío"
    if len(nombre) < min_length:
        return False, None, f"El nombre debe tener al menos {min_length} caracteres"
    if len(nombre) > max_length:
        return False, None, f"El nombre no puede exceder {max_length} caracteres"
    # Bloquear caracteres especiales peligrosos
    caracteres_prohibidos = ['<', '>', '"', "'", ";", "--", "/*", "*/"]
    for char in caracteres_prohibidos:
        if char in nombre:
            return False, None, f"El nombre contiene caracteres prohibidos"
    return True, nombre, ""

def validar_precio(precio: str) -> Tuple[bool, Optional[float], str]:
    """Valida precio (debe ser positivo, máx 2 decimales)"""
    try:
        p = float(precio.strip())
        if p < 0:
            return False, None, "El precio no puede ser negativo"
        if p > 100000:
            return False, None, "El precio es demasiado alto"
        # Redondear a 2 decimales
        p = round(p, 2)
        return True, p, ""
    except ValueError:
        return False, None, "El precio debe ser un número (ej: 15.50)"

def validar_cantidad(cantidad: str) -> Tuple[bool, Optional[float], str]:
    """Valida cantidad (debe ser positiva)"""
    try:
        q = float(cantidad.strip())
        if q <= 0:
            return False, None, "La cantidad debe ser positiva"
        if q > 1000:
            return False, None, "La cantidad es demasiado alta"
        q = round(q, 2)
        return True, q, ""
    except ValueError:
        return False, None, "La cantidad debe ser un número (ej: 2.5)"

def validar_telefono(telefono: str) -> Tuple[bool, Optional[str], str]:
    """Valida teléfono (formato básico)"""
    telefono = telefono.strip()
    if not telefono:
        return True, None, ""  # Opcional
    if len(telefono) < 7 or len(telefono) > 20:
        return False, None, "El teléfono debe tener entre 7 y 20 caracteres"
    if not all(c.isdigit() or c in ['+', '-', ' ', '(', ')'] for c in telefono):
        return False, None, "El teléfono contiene caracteres inválidos"
    return True, telefono, ""

def validar_descripcion(descripcion: str, max_length: int = 500) -> Tuple[bool, Optional[str], str]:
    """Valida descripción (opcional, máx longitud)"""
    descripcion = descripcion.strip()
    if len(descripcion) > max_length:
        return False, None, f"La descripción no puede exceder {max_length} caracteres"
    return True, descripcion if descripcion else None, ""

def validar_unidad(unidad: str) -> Tuple[bool, Optional[str], str]:
    """Valida unidad de medida"""
    unidades_validas = ["kg", "L", "g", "ml", "unidades", "docenas", "botellas", "cajas"]
    unidad = unidad.strip().lower()
    if unidad not in unidades_validas:
        return False, None, f"Unidad inválida. Opciones: {', '.join(unidades_validas)}"
    return True, unidad, ""

def validar_porcentaje(porcentaje: str) -> Tuple[bool, Optional[float], str]:
    """Valida porcentaje (0-100)"""
    try:
        p = float(porcentaje.strip())
        if p < 0 or p > 100:
            return False, None, "El porcentaje debe estar entre 0 y 100"
        p = round(p, 2)
        return True, p, ""
    except ValueError:
        return False, None, "El porcentaje debe ser un número"

def validar_texto_largo(texto: str, min_length: int = 0, max_length: int = 5000) -> Tuple[bool, Optional[str], str]:
    """Valida texto largo (comentarios, descripciones)"""
    texto = texto.strip()
    if len(texto) < min_length:
        return False, None, f"El texto debe tener al menos {min_length} caracteres"
    if len(texto) > max_length:
        return False, None, f"El texto no puede exceder {max_length} caracteres"
    return True, texto if texto else None, ""
