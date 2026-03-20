"""
Barra lateral de navegación - Sidebar en customtkinter
"""
import customtkinter as ctk
from typing import Callable, Dict
import config

class Sidebar(ctk.CTkFrame):
    """Barra lateral con navegación entre módulos"""
    
    def __init__(self, parent, on_module_change: Callable, **kwargs):
        """
        parent: ventana padre
        on_module_change: callback(modulo_nombre) cuando se cambia módulo
        """
        super().__init__(parent, fg_color=config.COLORS["dark_bg"], **kwargs)
        
        self.on_module_change = on_module_change
        self.boton_activo = None
        self.botones = {}
        
        self._crear_sidebar()
    
    def _crear_sidebar(self):
        """Crear elementos de sidebar"""
        # Header con color naranja restaurante
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"])
        frame_header.pack(fill="x", padx=0, pady=0)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text="🍽️ RESTAURANTE PRO",
            text_color=config.COLORS["text_light"],
            font=("Arial", 14, "bold")
        )
        titulo.pack(pady=15, padx=10)
        
        # Divisor
        divisor = ctk.CTkFrame(self, fg_color=config.COLORS["accent"], height=2)
        divisor.pack(fill="x", padx=0, pady=0)
        
        # Frame para botones (scrollable si es necesario)
        self.frame_botones = ctk.CTkScrollableFrame(
            self,
            fg_color=config.COLORS["dark_bg"],
            label_text="Módulos",
            label_text_color=config.COLORS["text_light"]
        )
        self.frame_botones.pack(fill="both", expand=True, padx=0, pady=10)
        
        # Definir módulos
        modulos = [
            ("mesas", "🪑 Mesas"),
            ("pedidos", "📋 Pedidos"),
            ("empleados", "👥 Empleados"),
            ("ingredientes", "📦 Ingredientes"),
            ("menu", "🍖 Menú"),
            ("pagos", "💳 Pagos"),
            ("reportes", "📊 Reportes"),
        ]
        
        # Crear botones
        for modulo_id, etiqueta in modulos:
            btn = ctk.CTkButton(
                self.frame_botones,
                text=etiqueta,
                height=50,
                corner_radius=8,
                fg_color=config.COLORS["secondary"],
                hover_color=config.COLORS["primary"],
                text_color=config.COLORS["text_light"],
                font=("Arial", 12, "bold"),
                command=lambda m=modulo_id: self._cambiar_modulo(m)
            )
            btn.pack(fill="x", padx=10, pady=8)
            self.botones[modulo_id] = btn
        
        # Divisor inferior
        divisor2 = ctk.CTkFrame(self, fg_color=config.COLORS["border"], height=1)
        divisor2.pack(fill="x", padx=0, pady=10)
        
        # Info
        frame_info = ctk.CTkFrame(self, fg_color="transparent")
        frame_info.pack(fill="x", padx=10, pady=10)
        
        info_texto = ctk.CTkLabel(
            frame_info,
            text="Sistema de Gestión\nRestaurante v2.0",
            text_color=config.COLORS["border"],
            font=("Arial", 9),
            justify="center"
        )
        info_texto.pack()
        
        # Activar módulo inicial (mesas)
        self._cambiar_modulo("mesas")
    
    def _cambiar_modulo(self, modulo_id: str):
        """Cambiar módulo activo"""
        # Cambiar estilo de botón activo
        if self.boton_activo:
            self.boton_activo.configure(
                fg_color=config.COLORS["secondary"],
                hover_color=config.COLORS["primary"]
            )
        
        # Activar nuevo botón
        btn = self.botones.get(modulo_id)
        if btn:
            btn.configure(
                fg_color=config.COLORS["primary"],
                hover_color=config.COLORS["accent"]
            )
            self.boton_activo = btn
        
        # Llamar callback
        self.on_module_change(modulo_id)
    
    def resaltar_modulo(self, modulo_id: str):
        """Resaltar un módulo (sin callback)"""
        if modulo_id in self.botones:
            self._cambiar_modulo(modulo_id)
