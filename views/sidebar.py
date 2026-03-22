"""
Barra lateral de navegación - Sidebar en customtkinter
"""
import customtkinter as ctk
from typing import Callable, Dict
import config

class Sidebar(ctk.CTkFrame):
    """Barra lateral con navegación moderna y estilo Dashboard"""
    
    def __init__(self, parent, on_module_change: Callable, **kwargs):
        # Fondo Beige suave para distinguir del contenido blanco
        # Usamos #FFF7ED (un beige muy claro parecedio a blanco hueso)
        super().__init__(parent, fg_color="#FFF7ED", corner_radius=0, **kwargs)
        
        self.on_module_change = on_module_change
        self.botones = {}
        
        # Paleta de colores interna sidebar (Tema Beige)
        self.colors = {
            "bg": "#FFF7ED",        # Fondo beige
            "active": config.COLORS.get("primary", "#EA580C"), 
            "hover": "#FFEDD5",     # Beige un poco más oscuro para hover
            "text": "#7C2D12",      # Texto marrón rojizo suave para contraste con beige
            "text_active": "#FFFFFF", 
            "text_header": "#1E293B", 
            "border": "#FED7AA"     # Borde naranja muy suave
        }
        
        self._crear_sidebar()
    
    def _crear_sidebar(self):
        """Construir interfaz"""
        # 1. HEADER (Logo + Titulo)
        self._crear_header()
        
        # 2. NAVEGACIÓN (Lista de módulos)
        self._crear_navegacion()
        
        # Estado inicial
        self._set_active("dashboard")
    
    def _crear_header(self):
        # Header con fondo color primario (Tomate)
        header = ctk.CTkFrame(self, fg_color=self.colors["active"], height=90, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        content = ctk.CTkFrame(header, fg_color="transparent")
        content.pack(expand=True, fill="x", padx=10, pady=0) # Menos padding horizontal
        
        # Logo Icon (Más pequeño)
        icon_bg = ctk.CTkFrame(content, width=36, height=36, corner_radius=8, fg_color="white")
        icon_bg.pack(side="left")
        
        icon_label = ctk.CTkLabel(icon_bg, text="🍽️", font=("Segoe UI Emoji", 20))
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Textos
        text_box = ctk.CTkFrame(content, fg_color="transparent")
        text_box.pack(side="left", padx=8, fill="x", expand=True)
        
        ctk.CTkLabel(
            text_box, 
            text="RESTAURANTE", 
            font=("Segoe UI", 14, "bold"), # Fuente ligeramente ajustada
            text_color="white",
            anchor="w"
        ).pack(anchor="w", pady=(0, 0), fill="x")
        
        ctk.CTkLabel(
            text_box, 
            text="SYSTEM V2.0", # Texto más corto para entrar mejor
            font=("Segoe UI", 10, "bold"), 
            text_color="#FFF7ED",
            anchor="w"
        ).pack(anchor="w", fill="x")

    def _crear_navegacion(self):
        # Contenedor de navegación (sin scroll) - Agregamos padding superior
        self.nav_frame = ctk.CTkFrame(
            self, 
            fg_color="transparent", 
            corner_radius=0
        )
        self.nav_frame.pack(fill="both", expand=True, padx=12, pady=(20, 20))
        
        # Lista de Módulos (ID, Etiqueta con Icono)
        items = [
            ("dashboard", "📊  Dashboard"),
            ("clientes", "👤  Clientes"),
            ("mesas", "🪑  Mesas"),
            ("pedidos", "📋  Pedidos"),
            ("empleados", "👥  Empleados"),
            ("ingredientes", "📦  Inventario"),
            ("menu", "🍔  Menú"),
            ("pagos", "💳  Caja y Pagos"),
            ("reportes", "📈  Reportes")
        ]
        
        for key, label in items:
            self._crear_boton(key, label)

    def _crear_boton(self, key, text):
        btn = ctk.CTkButton(
            self.nav_frame,
            text=text,
            font=("Segoe UI", 13, "bold"),
            anchor="w",
            height=46,
            corner_radius=8,
            fg_color="transparent",
            text_color=self.colors["text"],
            hover_color=self.colors["hover"],
            command=lambda k=key: self._on_click(k)
        )
        btn.pack(fill="x", pady=4)
        self.botones[key] = btn

    def _crear_footer(self):
        pass


    def _on_click(self, key):
        self._set_active(key)
        if self.on_module_change:
            self.on_module_change(key)
            
    def _set_active(self, active_key):
        # Restaurar todos
        for key, btn in self.botones.items():
            btn.configure(
                fg_color="transparent", 
                text_color=self.colors["text"]
            )
            
        # Activar seleccionado
        if active_key in self.botones:
            self.botones[active_key].configure(
                fg_color=self.colors["active"], 
                text_color=self.colors["text_active"]
            )

    def resaltar_modulo(self, modulo_id: str):
        """Método público para resaltar un botón externamente"""
        self._set_active(modulo_id)
