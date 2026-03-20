"""
Configuración global de la aplicación
"""
import os
from enum import Enum
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "restaurante.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Tema de customtkinter
APPEARANCE = "dark"  # "light" | "dark"

# Colores customtkinter (tema restaurante React)
COLORS = {
    "primary": "#EA580C",       # Naranja React (#EA580C ≈ orange-600)
    "secondary": "#374151",     # Gris oscuro
    "success": "#10B981",       # Verde
    "warning": "#F59E0B",       # Amarillo
    "danger": "#EF4444",        # Rojo
    "light_bg": "#F3F4F6",      # Gris muy claro (bg-gray-50)
    "dark_bg": "#FFFFFF",       # Blanco para cards
    "text_light": "#FFFFFF",    # Blanco
    "text_dark": "#1F2937",     # Gris oscuro texto
    "border": "#D1D5DB",        # Gris borde (border-gray-300)
    "accent": "#F97316",        # Naranja más oscuro
    "info": "#3B82F6",          # Azul información
    
    # Estados mesas
    "mesa_libre": "#DCFCE7",      # Verde claro
    "mesa_ocupada": "#FEE2E2",    # Rojo claro
    "mesa_reservada": "#FEF3C7",  # Amarillo claro
    
    "texto_libre": "#15803D",     # Verde texto
    "texto_ocupada": "#991B1B",   # Rojo texto
    "texto_reservada": "#92400E", # Amarillo texto
}

# Enums para Estados
class MesaEstado(str, Enum):
    LIBRE = "libre"
    OCUPADA = "ocupada"
    RESERVADA = "reservada"

class ClienteEstado(str, Enum):
    COMIENDO = "comiendo"
    PAGADO = "pagado"
    CANCELADO = "cancelado"

class EmpleadoPuesto(str, Enum):
    CAMARERO = "camarero"
    CHEF = "chef"
    GERENTE = "gerente"
    COCINERO = "cocinero"

class EmpleadoEstado(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"

class IngredienteEstado(str, Enum):
    DISPONIBLE = "disponible"
    AGOTADO = "agotado"

class PlatoEstado(str, Enum):
    DISPONIBLE = "disponible"
    NO_DISPONIBLE = "no_disponible"

class PlatoCategoría(str, Enum):
    ENTRADA = "entrada"
    PLATO_FUERTE = "plato_fuerte"
    POSTRE = "postre"
    BEBIDA = "bebida"
    ACOMPAÑAMIENTO = "acompañamiento"

class PedidoEstado(str, Enum):
    PENDIENTE = "pendiente"
    PREPARANDO = "preparando"
    LISTO = "listo"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"

class PagoEstado(str, Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    PARCIAL = "parcial"

class PagoMetodo(str, Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    FONDO_COMUN = "fondo_común"

# Dimensiones de ventana
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Tamaño de fuentes
FONT_SIZES = {
    "xs": 10,
    "sm": 12,
    "md": 14,
    "lg": 16,
    "xl": 18,
    "2xl": 24,
}

# Padding estándar
PADDING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
}

# Configuración de BD
DB_ECHO = False  # Cambiar a True para ver queries SQL en consola
