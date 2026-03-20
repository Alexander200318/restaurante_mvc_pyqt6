"""
Página: Gestión de Pagos
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.pagos_controller import PagosController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils
import config

class PagosPage(ctk.CTkFrame):
    """Módulo de Pagos"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controller = PagosController()
        self.tabla_pendientes = None
        self.tabla_completados = None
        self.pago_seleccionado = None
        
        self._crear_ui()
        self.refrescar_tablas()
    
    def _crear_ui(self):
        """Crear interfaz"""
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"])
        frame_header.pack(fill="x", padx=10, pady=10)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text="💳 Gestión de Pagos",
            text_color=config.COLORS["text_light"],
            font=("Arial", 18, "bold")
        )
        titulo.pack(side="left", padx=10, pady=10)
        
        btn_registrar = ctk.CTkButton(
            frame_header,
            text="💰 Registrar Pago",
            command=self.registrar_pago,
            fg_color=config.COLORS["success"],
            hover_color="#45a049"
        )
        btn_registrar.pack(side="right", padx=5, pady=10)
        
        btn_completar = ctk.CTkButton(
            frame_header,
            text="✓ Completar",
            command=self.completar_pago,
            fg_color=config.COLORS["primary"],
            hover_color="#0d47a1"
        )
        btn_completar.pack(side="right", padx=5, pady=10)
        
        # Pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab: Pendientes
        tab_pendientes = self.tabview.add("⏳ Pendientes")
        frame_pendientes = ctk.CTkFrame(tab_pendientes)
        frame_pendientes.pack(fill="both", expand=True)
        
        self.tabla_pendientes = TreeViewWidget(
            frame_pendientes,
            columnas=["ID", "Cliente", "Mesa", "Monto", "Estado"],
            altura=20
        )
        self.tabla_pendientes.pack(fill="both", expand=True)
        self.tabla_pendientes.set_on_select(self._on_pago_select)
        
        # Tab: Todos
        tab_todos = self.tabview.add("Todos")
        frame_todos = ctk.CTkFrame(tab_todos)
        frame_todos.pack(fill="both", expand=True)
        
        self.tabla_completados = TreeViewWidget(
            frame_todos,
            columnas=["ID", "Cliente", "Monto", "Método", "Estado", "Fecha"],
            altura=20
        )
        self.tabla_completados.pack(fill="both", expand=True)
        
        # Info
        frame_info = ctk.CTkFrame(self, fg_color=config.COLORS["light_bg"])
        frame_info.pack(fill="x", padx=10, pady=10)
        
        self.label_info = ctk.CTkLabel(
            frame_info,
            text="Selecciona un pago pendiente",
            text_color=config.COLORS["text_dark"]
        )
        self.label_info.pack(padx=10, pady=10)
    
    def _on_pago_select(self, datos):
        self.pago_seleccionado = datos
        if datos:
            self.label_info.configure(text=f"Pago #{datos[0]} - {datos[1]}")
    
    def refrescar_tablas(self):
        # Tabla pendientes
        success, datos, msg = self.controller.obtener_pagos_pendientes_formateados()
        if success:
            self.tabla_pendientes.limpiar()
            self.tabla_pendientes.agregar_filas(datos)
        
        # Tabla todos
        success, datos, msg = self.controller.obtener_todos_pagos_formateados()
        if success:
            self.tabla_completados.limpiar()
            self.tabla_completados.agregar_filas(datos)
    
    def registrar_pago(self):
        DialogUtils.mostrar_exito("Funcionalidad", "Registración de pago en progreso")
    
    def completar_pago(self):
        if not self.pago_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un pago")
            return
        
        DialogUtils.mostrar_exito("Éxito", "Pago completado")
        self.refrescar_tablas()
