"""
Página: Reportes y Estadísticas
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.pagos_controller import PagosController
from controllers.pedidos_controller import PedidosController
from views.components.dialog_utils import DialogUtils
import config

class ReportesPage(ctk.CTkFrame):
    """Módulo de Reportes"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controller_pagos = PagosController()
        self.controller_pedidos = PedidosController()
        
        self._crear_ui()
    
    def _crear_ui(self):
        """Crear interfaz"""
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"])
        frame_header.pack(fill="x", padx=10, pady=10)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text="📊 Reportes y Estadísticas",
            text_color=config.COLORS["text_light"],
            font=("Arial", 18, "bold")
        )
        titulo.pack(side="left", padx=10, pady=10)
        
        btn_generar = ctk.CTkButton(
            frame_header,
            text="🔄 Refrescar",
            command=self.generar_reportes,
            fg_color=config.COLORS["primary"],
            hover_color="#0d47a1"
        )
        btn_generar.pack(side="right", padx=5, pady=10)
        
        # Pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab: Ingresos
        tab_ingresos = self.tabview.add("💰 Ingresos")
        self._crear_tab_ingresos(tab_ingresos)
        
        # Tab: Ventas
        tab_ventas = self.tabview.add("📈 Ventas")
        self._crear_tab_ventas(tab_ventas)
        
        # Tab: Resumen
        tab_resumen = self.tabview.add("📋 Resumen")
        self._crear_tab_resumen(tab_resumen)
    
    def _crear_tab_ingresos(self, parent):
        """Tab de ingresos"""
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Selector de fechas
        frame_fechas = ctk.CTkFrame(frame)
        frame_fechas.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(frame_fechas, text="Período:").pack(side="left", padx=5)
        
        opciones = ["Hoy", "Últimos 7 días", "Este mes", "Personalizado"]
        combo = ctk.CTkComboBox(frame_fechas, values=opciones, state="readonly")
        combo.pack(side="left", padx=5)
        combo.set("Últimos 7 días")
        
        # Info de ingresos
        self.label_ingresos_total = ctk.CTkLabel(
            frame,
            text="Ingresos Totales: —",
            font=("Arial", 16, "bold"),
            text_color=config.COLORS["success"]
        )
        self.label_ingresos_total.pack(pady=20)
        
        # Desglose por método
        ctk.CTkLabel(frame, text="Por Método de Pago:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(20, 10))
        
        self.label_metodos = ctk.CTkLabel(
            frame,
            text="Cargando...",
            justify="left"
        )
        self.label_metodos.pack(anchor="w", padx=20, pady=10)
        
        # Desglose por categoría
        ctk.CTkLabel(frame, text="Por Categoría de Plato:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(20, 10))
        
        self.label_categorias = ctk.CTkLabel(
            frame,
            text="Cargando...",
            justify="left"
        )
        self.label_categorias.pack(anchor="w", padx=20, pady=10)
    
    def _crear_tab_ventas(self, parent):
        """Tab de ventas"""
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Platos Más Vendidos:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 10))
        
        self.label_platos = ctk.CTkLabel(
            frame,
            text="Cargando...",
            justify="left"
        )
        self.label_platos.pack(anchor="w", padx=20, pady=10)
    
    def _crear_tab_resumen(self, parent):
        """Tab de resumen general"""
        frame = ctk.CTkScrollableFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.label_resumen = ctk.CTkLabel(
            frame,
            text="Resumen del día...",
            justify="left",
            wraplength=600
        )
        self.label_resumen.pack(anchor="w", padx=20, pady=20)
    
    def generar_reportes(self):
        """Generar datos de reportes"""
        fecha_inicio = datetime.now() - timedelta(days=7)
        fecha_fin = datetime.now()
        
        # Ingresos
        success, ingresos_str, msg = self.controller_pagos.obtener_ingresos_rango_fechas(fecha_inicio, fecha_fin)
        if success:
            self.label_ingresos_total.configure(text=f"Ingresos Totales (últimos 7 días): {ingresos_str}")
        
        # Por método
        success, por_metodo, msg = self.controller_pagos.obtener_ingresos_por_metodo(fecha_inicio, fecha_fin)
        if success:
            texto = "\n".join([f"  • {m}: {monto}" for m, monto in por_metodo.items()])
            self.label_metodos.configure(text=texto)
        
        # Por categoría
        success, por_categoria, msg = self.controller_pagos.obtener_ingresos_por_categoria(fecha_inicio, fecha_fin)
        if success:
            texto = "\n".join([f"  • {c}: {monto}" for c, monto in por_categoria.items()])
            self.label_categorias.configure(text=texto)
        
        # Platos más vendidos
        success, platos, msg = self.controller_pedidos.obtener_platos_mas_vendidos(10)
        if success:
            texto = "\n".join([f"  • {p[0]}: {p[1]} vendidos (${p[2]:.2f})" for p in platos])
            self.label_platos.configure(text=texto)
        
        DialogUtils.mostrar_exito("Éxito", "Reportes actualizados")
