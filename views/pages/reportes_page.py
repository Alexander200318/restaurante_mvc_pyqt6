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
        super().__init__(parent, fg_color=config.COLORS["light_bg"], **kwargs)
        
        self.controller_pagos = PagosController()
        self.controller_pedidos = PedidosController()
        
        self._crear_ui()
    
    def _crear_ui(self):
        """Crear interfaz"""
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"], height=80)
        frame_header.pack(side="top", fill="x", padx=0, pady=0)
        frame_header.pack_propagate(False)
        
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

        ctk.CTkLabel(frame, text="Platos Más Vendidos", font=("Arial", 13, "bold")).pack(anchor="w", pady=(2, 4))

        self.label_platos_resumen = ctk.CTkLabel(
            frame,
            text="Top 5 de la semana",
            font=("Arial", 10),
            text_color=config.COLORS["secondary"]
        )
        self.label_platos_resumen.pack(anchor="w", padx=4, pady=(0, 6))

        self.lista_platos_card = ctk.CTkFrame(
            frame,
            fg_color=config.COLORS["dark_bg"],
            border_width=1,
            border_color=config.COLORS["border"],
            corner_radius=8
        )
        self.lista_platos_card.pack(fill="x", expand=False, pady=(0, 6))

        self.lista_platos_frame = ctk.CTkFrame(self.lista_platos_card, fg_color="transparent")
        self.lista_platos_frame.pack(fill="x", padx=8, pady=8)

    def _nombre_corto(self, nombre: str, max_len: int = 22) -> str:
        """Acortar nombre para reportes compactos."""
        if len(nombre) <= max_len:
            return nombre
        return nombre[:max_len - 1] + "…"

    def _actualizar_lista_platos(self, platos: list):
        """Actualizar lista compacta de platos más vendidos."""
        for widget in self.lista_platos_frame.winfo_children():
            widget.destroy()

        if not platos:
            ctk.CTkLabel(
                self.lista_platos_frame,
                text="Sin ventas registradas",
                font=("Arial", 10),
                text_color=config.COLORS["secondary"]
            ).pack(anchor="w", padx=4, pady=4)
            return

        for i, p in enumerate(platos, start=1):
            nombre = self._nombre_corto(str(p[0]), 24)
            vendidos = int(p[1])
            total = float(p[2])

            fila = ctk.CTkFrame(
                self.lista_platos_frame,
                fg_color=config.COLORS["light_bg"],
                corner_radius=6,
                border_width=1,
                border_color=config.COLORS["border"]
            )
            fila.pack(fill="x", pady=2)

            ctk.CTkLabel(
                fila,
                text=f"{i}",
                width=24,
                font=("Arial", 10, "bold"),
                text_color=config.COLORS["primary"]
            ).pack(side="left", padx=(8, 4), pady=4)

            ctk.CTkLabel(
                fila,
                text=nombre,
                font=("Arial", 10, "bold"),
                text_color=config.COLORS["text_dark"]
            ).pack(side="left", padx=(0, 6), pady=4)

            ctk.CTkLabel(
                fila,
                text=f"{vendidos} uds",
                font=("Arial", 10),
                text_color=config.COLORS["secondary"]
            ).pack(side="right", padx=(6, 10), pady=4)

            ctk.CTkLabel(
                fila,
                text=f"${total:.2f}",
                font=("Arial", 10, "bold"),
                text_color=config.COLORS["success"]
            ).pack(side="right", padx=(0, 6), pady=4)
    
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
        success, platos, msg = self.controller_pedidos.obtener_platos_mas_vendidos(4)
        if success:
            self._actualizar_lista_platos(platos)

            total_unidades = sum(p[1] for p in platos)
            total_monto = sum(p[2] for p in platos)
            self.label_platos_resumen.configure(
                text=f"Top {len(platos)} • {total_unidades} uds • ${total_monto:.2f}"
            )
        else:
            self.label_platos_resumen.configure(text="Sin datos de ventas")
            self._actualizar_lista_platos([])
        
        DialogUtils.mostrar_exito("Éxito", "Reportes actualizados")
