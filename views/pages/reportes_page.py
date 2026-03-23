"""
Página: Reportes y Estadísticas - Vista Única (Dashboard Consolidado)
"""
import customtkinter as ctk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

# Controladores
from controllers.pagos_controller import PagosController
from controllers.pedidos_controller import PedidosController

class ReportesPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#F3F4F6", **kwargs)
        
        self.controller_pagos = PagosController()
        self.controller_pedidos = PedidosController()
        
        self._crear_ui()
        self.after(500, self.generar_reportes)

    def _limpiar_monto(self, valor):
        if isinstance(valor, (int, float)): return float(valor)
        if isinstance(valor, str):
            limpio = re.sub(r'[^\d.]', '', valor)
            try: return float(limpio) if limpio else 0.0
            except: return 0.0
        return 0.0

    def _crear_ui(self):
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color="#EA580C", height=80, corner_radius=0)
        frame_header.pack(side="top", fill="x")
        frame_header.pack_propagate(False)
        
        ctk.CTkLabel(frame_header, text="📊 Panel de Control General", font=("Helvetica", 22, "bold"), text_color="white").pack(side="left", padx=30)
        
        self.btn_refrescar = ctk.CTkButton(
            frame_header, text="🔄 Actualizar Todo", command=self.generar_reportes,
            fg_color="white", text_color="#EA580C", hover_color="#FEE2E2",
            font=("Helvetica", 12, "bold"), height=35, width=150
        )
        self.btn_refrescar.pack(side="right", padx=30)

        # === ÁREA DE SCROLL (Dashboard Completo) ===
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- SECCIÓN 1: KPI TOTAL ---
        self.card_total = ctk.CTkFrame(self.main_scroll, fg_color="white", corner_radius=15)
        self.card_total.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.card_total, text="INGRESOS ÚLTIMOS 7 DÍAS", font=("Helvetica", 13, "bold"), text_color="#6B7280").pack(pady=(15, 0))
        self.label_total = ctk.CTkLabel(self.card_total, text="$ 0.00", font=("Helvetica", 42, "bold"), text_color="#10B981")
        self.label_total.pack(pady=(5, 15))

        # --- SECCIÓN 2: GRID DE ESTADÍSTICAS RÁPIDAS (2 Columnas) ---
        self.grid_stats = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.grid_stats.pack(fill="x", pady=5)
        self.grid_stats.grid_columnconfigure((0, 1), weight=1)

        # Métodos de Pago
        self.f_metodos = ctk.CTkFrame(self.grid_stats, fg_color="white", corner_radius=15)
        self.f_metodos.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        ctk.CTkLabel(self.f_metodos, text="💳 Métodos de Pago", font=("Helvetica", 14, "bold"), text_color="#242629").pack(pady=10)
        self.list_metodos = ctk.CTkFrame(self.f_metodos, fg_color="transparent")
        self.list_metodos.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Categorías
        self.f_cats = ctk.CTkFrame(self.grid_stats, fg_color="white", corner_radius=15)
        self.f_cats.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        ctk.CTkLabel(self.f_cats, text="🍴 Ventas por Categoría", font=("Helvetica", 14, "bold"), text_color="#242629").pack(pady=10)
        self.list_cats = ctk.CTkFrame(self.f_cats, fg_color="transparent")
        self.list_cats.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # --- SECCIÓN 3: GRÁFICOS (2 Columnas) ---
        self.grid_plots = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.grid_plots.pack(fill="x", pady=10)
        self.grid_plots.grid_columnconfigure((0, 1), weight=1)

        self.container_pie = ctk.CTkFrame(self.grid_plots, fg_color="white", corner_radius=15, height=300)
        self.container_pie.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        
        self.container_bar = ctk.CTkFrame(self.grid_plots, fg_color="white", corner_radius=15, height=300)
        self.container_bar.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        # --- SECCIÓN 4: TABLA PRODUCTOS (Ancho completo) ---
        self.f_tabla = ctk.CTkFrame(self.main_scroll, fg_color="white", corner_radius=15)
        self.f_tabla.pack(fill="x", pady=10)
        ctk.CTkLabel(self.f_tabla, text="🏆 Ranking de Productos Más Vendidos", font=("Helvetica", 15, "bold"), text_color="#242629").pack(pady=15)
        
        # Header de tabla simple
        h_table = ctk.CTkFrame(self.f_tabla, fg_color="#F9FAFB", height=35)
        h_table.pack(fill="x", padx=15)
        ctk.CTkLabel(h_table, text="RANK", width=50, font=("Arial", 10, "bold"), text_color="#242629").pack(side="left", padx=10)
        ctk.CTkLabel(h_table, text="PRODUCTO", font=("Arial", 10, "bold"), text_color="#242629").pack(side="left", padx=20)
        ctk.CTkLabel(h_table, text="VENTA TOTAL", font=("Arial", 10, "bold"), text_color="#242629").pack(side="right", padx=20)
        ctk.CTkLabel(h_table, text="CANTIDAD", font=("Arial", 10, "bold"), text_color="#242629").pack(side="right", padx=20)

        self.list_platos = ctk.CTkFrame(self.f_tabla, fg_color="transparent")
        self.list_platos.pack(fill="x", padx=15, pady=10)

    def generar_reportes(self):
        inicio = datetime.now() - timedelta(days=7)
        fin = datetime.now()

        try:
            # 1. KPI
            _, monto, _ = self.controller_pagos.obtener_ingresos_rango_fechas(inicio, fin)
            self.label_total.configure(text=f"$ {self._limpiar_monto(monto):,.2f}")

            # 2. Listas de Texto
            _, metodos, _ = self.controller_pagos.obtener_ingresos_por_metodo(inicio, fin)
            self._render_mini_list(self.list_metodos, metodos)

            _, cats, _ = self.controller_pagos.obtener_ingresos_por_categoria(inicio, fin)
            self._render_mini_list(self.list_cats, cats)

            # 3. Gráficos
            cats_limpias = {k: self._limpiar_monto(v) for k, v in cats.items()} if cats else {"N/A": 1}
            self._plot_pie(cats_limpias)

            _, platos, _ = self.controller_pedidos.obtener_platos_mas_vendidos(5)
            self._plot_bars(platos[:5] if platos else [("N/A", 0, 0)])

            # 4. Tabla Inferior
            self._render_table(platos)

        except Exception as e:
            print(f"Error Dashboard: {e}")

    def _render_mini_list(self, parent, data):
        for w in parent.winfo_children(): w.destroy()
        if not data:
            ctk.CTkLabel(parent, text="Sin datos", text_color="gray").pack()
            return
        for k, v in data.items():
            row = ctk.CTkFrame(parent, fg_color="#F9FAFB", height=30)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=str(k), font=("Arial", 11)).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"$ {self._limpiar_monto(v):,.2f}", font=("Arial", 11, "bold"), text_color="#10B981").pack(side="right", padx=10)

    def _render_table(self, platos):
        for w in self.list_platos.winfo_children(): w.destroy()
        if not platos: return
        for i, p in enumerate(platos, 1):
            fila = ctk.CTkFrame(self.list_platos, fg_color="transparent", height=40)
            fila.pack(fill="x")
            ctk.CTkLabel(fila, text=f"#{i}", width=50, text_color="#EA580C", font=("Arial", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(fila, text=p[0], font=("Arial", 12)).pack(side="left", padx=20)
            ctk.CTkLabel(fila, text=f"$ {self._limpiar_monto(p[2]):,.2f}", font=("Arial", 12, "bold"), text_color="#10B981").pack(side="right", padx=20)
            ctk.CTkLabel(fila, text=f"{p[1]} uds", font=("Arial", 11)).pack(side="right", padx=20)
            ctk.CTkFrame(self.list_platos, fg_color="#F3F4F6", height=1).pack(fill="x")

    def _plot_pie(self, data):
        for w in self.container_pie.winfo_children(): w.destroy()
        fig, ax = plt.subplots(figsize=(3, 3), dpi=90)
        fig.patch.set_facecolor('none')
        ax.pie(data.values(), labels=data.keys(), autopct='%1.0f%%', colors=["#3B82F6", "#10B981", "#F59E0B", "#EF4444"], textprops={'fontsize': 7})
        canvas = FigureCanvasTkAgg(fig, master=self.container_pie)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
        plt.close(fig)

    def _plot_bars(self, data):
        for w in self.container_bar.winfo_children(): w.destroy()
        fig, ax = plt.subplots(figsize=(3, 3), dpi=90)
        fig.patch.set_facecolor('none')
        nombres = [p[0][:8] for p in data]
        unidades = [float(p[1]) for p in data]
        ax.bar(nombres, unidades, color="#EA580C")
        ax.tick_params(axis='x', labelsize=7, rotation=20)
        ax.spines[['top', 'right']].set_visible(False)
        canvas = FigureCanvasTkAgg(fig, master=self.container_bar)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
        plt.close(fig)