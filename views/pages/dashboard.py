"""
Dashboard Principal - Diseño Moderno & Premium
Actualizado: 2026-03-20
"""
import customtkinter as ctk
from datetime import datetime
from database.db_manager import DatabaseManager
from database.models import (
    Mesa, Cliente, Empleado, Ingrediente, 
    Plato, Pedido, Pago
)
from sqlalchemy import func
import config

class DashboardPage:
    """Dashboard con diseño moderno y métricas en tiempo real"""
    
    def __init__(self, frame_contenido, db_manager: DatabaseManager):
        self.frame_contenido = frame_contenido
        self.db_manager = db_manager
        self.frame = None
        
        # Paleta de Colores Moderna (Tema Tomate/Naranja)
        self.colors = {
            "primary": "#EA580C",       # Orange 600
            "primary_hover": "#C2410C", # Orange 700
            "secondary": "#64748B",     # Slate 500
            "success": "#10B981",       # Emerald 500
            "danger": "#EF4444",        # Red 500
            "warning": "#F59E0B",       # Amber 500
            "info": "#3B82F6",          # Blue 500
            "dark": "#1F2937",          # Gray 800
            "surface": "#FFFFFF",       # White
            "background": "#F3F4F6",    # Gray 100
            "text": "#111827",          # Gray 900
            "text_light": "#6B7280",    # Gray 500
            "border": "#E5E7EB"         # Gray 200
        }

    def crear(self):
        """Construir el dashboard"""
        # Limpiar frame anterior
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()
            
        # Frame principal con scroll
        self.frame = ctk.CTkScrollableFrame(
            self.frame_contenido,
            fg_color=self.colors["background"],
            corner_radius=0
        )
        self.frame.pack(fill="both", expand=True)
        
        # Smooth scrolling workaround para Windows
        self._bind_mouse_wheel(self.frame)

        # 1. Header Hero (Estilo Banner)
        self._render_hero_header()
        
        # 2. Key Metrics Row (Tarjetas de KPI)
        self._render_kpi_cards()
        
        # 3. Contenido Principal (Grid Responsive)
        main_grid = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_grid.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        
        # Grid configuración: Columna 0 flexible, Columna 1 fija
        main_grid.grid_columnconfigure(0, weight=1) 
        main_grid.grid_columnconfigure(1, weight=0, minsize=420) # Sidebar fijo de 420px para máxima visibilidad

        # Columna Izquierda (Tablas y Pedidos)
        left_col = ctk.CTkFrame(main_grid, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 25))
        
        self._render_live_tables(left_col)
        self._render_recent_orders(left_col)
        
        # Columna Derecha (Resúmenes y Alertas)
        # Importante: Usar width explícito para evitar colapso visual inicial
        right_col = ctk.CTkFrame(main_grid, fg_color="transparent", width=420)
        right_col.grid(row=0, column=1, sticky="nw") # Alineado arriba-izquierda
        
        self._render_financial_summary(right_col)
        ctk.CTkFrame(right_col, fg_color="transparent", height=20).pack() # Espaciador
        self._render_stock_alerts(right_col)
        ctk.CTkFrame(right_col, fg_color="transparent", height=20).pack() # Espaciador
        self._render_active_staff(right_col)

    def _bind_mouse_wheel(self, widget):
        # Aumentamos la velocidad del scroll (ajustado a x8 para mayor fluidez)
        # event.delta suele ser 120 (arriba) o -120 (abajo) en Windows
        def _on_mousewheel(event):
            widget._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)) * 8, "units")
            
        widget.bind("<Enter>", lambda e: widget._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        widget.bind("<Leave>", lambda e: widget._parent_canvas.unbind_all("<MouseWheel>"))

    def _render_hero_header(self):
        """Header moderno con gradiente simulado"""
        hero = ctk.CTkFrame(self.frame, fg_color=self.colors["primary"], height=160, corner_radius=0)
        hero.pack(fill="x", pady=(0, 20))
        hero.pack_propagate(False)
        
        content = ctk.CTkFrame(hero, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Saludo y Fecha
        info_box = ctk.CTkFrame(content, fg_color="transparent")
        info_box.pack(side="left", fill="y")
        
        hora = datetime.now().hour
        saludo = "Buenos días" if 5 <= hora < 12 else "Buenas tardes" if 12 <= hora < 19 else "Buenas noches"
        
        ctk.CTkLabel(
            info_box, 
            text=f"{saludo} 👋", 
            font=("Segoe UI", 32, "bold"), 
            text_color="white"
        ).pack(anchor="w")
        
        fecha = datetime.now().strftime("Hoy es %A, %d de %B del %Y")
        ctk.CTkLabel(
            info_box, 
            text=fecha, 
            font=("Segoe UI", 14), 
            text_color="#E0E7FF" # Indigo 100
        ).pack(anchor="w", pady=(5, 0))

        # Botones de Acción (Pills Flotantes) - Eliminado por solicitud
        # actions = ctk.CTkFrame(content, fg_color="transparent")
        # actions.pack(side="right", anchor="center")

    def _render_kpi_cards(self):
        """Tarjetas de métricas clave con estilo moderno"""
        kpi_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        kpi_container.pack(fill="x", padx=30, pady=(0, 20))
        
        # Queries Database
        session = self.db_manager.get_session()
        try:
            hoy = datetime.now().date()
            ventas_hoy = session.query(func.sum(Pago.monto)).filter(func.date(Pago.fecha_pago) == hoy).scalar() or 0.0
            pedidos_hoy = session.query(func.count(Pedido.id)).filter(func.date(Pedido.fecha_creacion) == hoy).scalar() or 0
            
            # Total Clientes Registrados
            clientes_hoy = session.query(func.count(Cliente.id)).scalar() or 0
            
            # Ocupacion
            total_mesas = session.query(func.count(Mesa.id)).scalar() or 1
            mesas_ocupadas = session.query(func.count(Mesa.id)).filter(Mesa.estado == config.MesaEstado.OCUPADA).scalar() or 0
            ocupacion_pct = int((mesas_ocupadas / total_mesas) * 100)
            
        finally:
            self.db_manager.close_session(session)

        metrics = [
            {"title": "Ventas Hoy", "value": f"${ventas_hoy:,.2f}", "icon": "💰", "color": self.colors["success"], "trend": "+12%"},
            {"title": "Pedidos", "value": str(pedidos_hoy), "icon": "🧾", "color": self.colors["info"], "trend": "+5%"},
            {"title": "Ocupación", "value": f"{ocupacion_pct}%", "icon": "🪑", "color": self.colors["warning"], "trend": f"{mesas_ocupadas}/{total_mesas}"},
            {"title": "Clientes", "value": str(clientes_hoy), "icon": "👥", "color": self.colors["primary"], "trend": "Registrados"}
        ]

        for idx, m in enumerate(metrics):
            self._create_kpi_card(kpi_container, m, idx)

    def _create_kpi_card(self, parent, data, idx):
        # Diseño "Glassmorphism" sutil con borde suave y más padding
        card = ctk.CTkFrame(
            parent, 
            fg_color="white", 
            corner_radius=20, # Más redondeado
            border_width=1, 
            border_color="#E2E8F0"
        )
        # Usamos PACK porque el contenedor padre usa PACK (en el código revisado arriba puede ser pack o grid dependiendo del contexto, 
        # pero en _render_kpi_cards original se usaba pack o grid según la sección.
        # Revisando _render_kpi_cards: usa `kpi_container.grid_columnconfigure`? NO, usa PACK en la versión leída.
        # ERROR: En la versión leída arriba, `_render_kpi_cards` usa `self._create_kpi_card` dentro de un loop.
        # Vamos a asumir grid si el contenedor padre fue configurado con grid columns, pero en el código LEIDO usa pack:
        # `kpi_container.pack(fill="x", padx=30, pady=(0, 20))`
        # Y dentro del loop hace: `self._create_kpi_card(kpi_container, m, idx)`
        # Y dentro de `_create_kpi_card` leido usa PACK: `card.pack(side="left", fill="both", expand=True, padx=10 if idx > 0 else (0, 10))`
        
        # Vamos a mantener PACK para compatibilidad pero con estilo moderno
        card.pack(side="left", fill="both", expand=True, padx=10 if idx > 0 else (0, 10))
        
        # Efecto de "top border" de color
        ctk.CTkFrame(card, height=4, fg_color=data["color"], corner_radius=20).pack(fill="x", padx=1, pady=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)
        
        # Header (Icon + Trend)
        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        # Icono con fondo suave
        icon_bg = ctk.CTkFrame(header, fg_color=data["color"], width=48, height=48, corner_radius=24) # Circular
        icon_bg.pack(side="left")
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=data["icon"], font=("Segoe UI Emoji", 24)).place(relx=0.5, rely=0.5, anchor="center")
        
        # Trend badge
        trend_bg = ctk.CTkFrame(header, fg_color="#F8FAFC", corner_radius=12)
        trend_bg.pack(side="right", anchor="ne")
        ctk.CTkLabel(trend_bg, text=data["trend"], font=("Segoe UI", 11, "bold"), text_color=data["color"]).pack(padx=10, pady=4)
        
        # Value & Title
        ctk.CTkLabel(inner, text=data["value"], font=("Segoe UI Display", 32, "bold"), text_color="#0F172A").pack(anchor="w", pady=(5,0))
        ctk.CTkLabel(inner, text=data["title"], font=("Segoe UI", 14), text_color="#64748B").pack(anchor="w")

    def _render_live_tables(self, parent):
        """Mapa Visual de Mesas"""
        container = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=16, border_width=1, border_color=self.colors["border"])
        container.pack(fill="x", pady=(0, 20))
        
        # Title
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="Estado de Sala", font=("Segoe UI", 16, "bold"), text_color=self.colors["text"]).pack(side="left")
        
        # Legend
        legend = ctk.CTkFrame(header, fg_color="transparent")
        legend.pack(side="right")
        for label, color in [("Libre", self.colors["success"]), ("Ocupada", self.colors["danger"]), ("Reservada", self.colors["warning"])]:
            self._add_legend_item(legend, label, color)
            
        # Grid
        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        session = self.db_manager.get_session()
        try:
            mesas = session.query(Mesa).order_by(Mesa.numero).all()
            if not mesas:
                ctk.CTkLabel(grid, text="No hay mesas configuradas", text_color=self.colors["text_light"]).pack(pady=20)
                return
            
            # Dynamic Grid
            cols = 5
            for i in range(cols): grid.grid_columnconfigure(i, weight=1)
            
            for idx, mesa in enumerate(mesas):
                color = self.colors["success"]
                status_icon = "✓"
                if mesa.estado == config.MesaEstado.OCUPADA: 
                    color = self.colors["danger"]
                    status_icon = "🍽️"
                elif mesa.estado == config.MesaEstado.RESERVADA: 
                    color = self.colors["warning"]
                    status_icon = "🔒"
                
                # Card Wrapper
                m_card = ctk.CTkFrame(grid, fg_color=self.colors["background"], corner_radius=12, border_width=1, border_color=self.colors["border"])
                m_card.grid(row=idx//cols, column=idx%cols, padx=5, pady=5, sticky="nsew")
                
                # Status Bar
                ctk.CTkFrame(m_card, fg_color=color, height=4, corner_radius=4).pack(fill="x", padx=2, pady=2)
                
                # Content
                ctk.CTkLabel(m_card, text=f"Mesa {mesa.numero}", font=("Segoe UI", 12, "bold"), text_color=self.colors["text"]).pack(pady=(8, 0))
                ctk.CTkLabel(m_card, text=f"{mesa.capacidad} pax", font=("Segoe UI", 10), text_color=self.colors["text_light"]).pack(pady=(0, 8))
                
        finally:
            self.db_manager.close_session(session)

    def _add_legend_item(self, parent, text, color):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(side="left", padx=8)
        ctk.CTkFrame(item, width=8, height=8, corner_radius=4, fg_color=color).pack(side="left")
        ctk.CTkLabel(item, text=text, font=("Segoe UI", 11), text_color=self.colors["text_light"]).pack(side="left", padx=(5,0))

    def _render_recent_orders(self, parent):
        """Lista de Últimos Pedidos"""
        container = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=16, border_width=1, border_color=self.colors["border"])
        container.pack(fill="x")
        
        # Header
        ctk.CTkLabel(container, text="Pedidos Recientes", font=("Segoe UI", 16, "bold"), text_color=self.colors["text"]).pack(anchor="w", padx=20, pady=20)
        
        session = self.db_manager.get_session()
        try:
            pedidos = session.query(Pedido).order_by(Pedido.fecha_creacion.desc()).limit(5).all()
            
            if not pedidos:
                ctk.CTkLabel(container, text="Sin actividad reciente", text_color=self.colors["text_light"]).pack(pady=20)
                return
            
            # Headers row
            headers = ctk.CTkFrame(container, fg_color=self.colors["background"], height=35, corner_radius=8)
            headers.pack(fill="x", padx=15)
            
            cols = [("HORA", 80), ("MESA", 80), ("CLIENTE", 150), ("TOTAL", 80), ("ESTADO", 100)]
            for txt, width in cols:
                ctk.CTkLabel(headers, text=txt, font=("Segoe UI", 10, "bold"), text_color=self.colors["text_light"], width=width, anchor="w").pack(side="left", padx=5)
            
            # Rows
            for p in pedidos:
                row = ctk.CTkFrame(container, fg_color="transparent", height=45)
                row.pack(fill="x", padx=15, pady=2)
                
                # Logic
                total = sum(d.precio_unitario * d.cantidad for d in p.detalles) if p.detalles else 0
                cliente_nombre = (p.cliente.nombre if p.cliente else "Anonimo")
                mesa_txt = f"Mesa {p.mesa.numero}" if p.mesa else "Delivery"
                
                # State color
                state_color = self.colors["primary"]
                if p.estado == config.PedidoEstado.ENTREGADO: state_color = self.colors["success"]
                elif p.estado == config.PedidoEstado.CANCELADO: state_color = self.colors["danger"]
                
                # Columns
                values = [
                    (p.fecha_creacion.strftime("%H:%M"), 80),
                    (mesa_txt, 80),
                    (cliente_nombre[:15], 150),
                    (f"${total:.2f}", 80)
                ]
                
                for txt, width in values:
                    ctk.CTkLabel(row, text=txt, font=("Segoe UI", 11), text_color=self.colors["text"], width=width, anchor="w").pack(side="left", padx=5)
                
                # State Chip
                chip = ctk.CTkFrame(row, fg_color=state_color, width=90, height=24, corner_radius=12)
                chip.pack(side="left", padx=5)
                chip.pack_propagate(False)
                ctk.CTkLabel(chip, text=p.estado.value.upper(), font=("Segoe UI", 9, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
                
                # Divider
                ctk.CTkFrame(container, height=1, fg_color=self.colors["border"]).pack(fill="x", padx=20)

        finally:
            self.db_manager.close_session(session)

    def _render_financial_summary(self, parent):
        """Resumen Financiero"""
        self._create_sidebar_card(parent, "Finanzas", "💰", self._content_financial)

    def _content_financial(self, parent):
        session = self.db_manager.get_session()
        try:
            hoy = datetime.now().date()
            pagos = session.query(Pago.metodo, func.sum(Pago.monto)).filter(func.date(Pago.fecha_pago) == hoy).group_by(Pago.metodo).all()
            total = sum(m for _, m in pagos)
        finally:
            self.db_manager.close_session(session)
            
        if not pagos:
            ctk.CTkLabel(parent, text="Sin transacciones hoy", font=("Segoe UI", 11), text_color=self.colors["text_light"]).pack(pady=10)
            return

        for metodo, monto in pagos:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=metodo.capitalize(), font=("Segoe UI", 11), text_color=self.colors["text"]).pack(side="left")
            ctk.CTkLabel(row, text=f"${monto:.2f}", font=("Segoe UI", 11, "bold"), text_color=self.colors["success"]).pack(side="right")
            
            # Bar
            pct = (monto/total) if total else 0
            bar_bg = ctk.CTkFrame(parent, fg_color=self.colors["background"], height=6, corner_radius=3)
            bar_bg.pack(fill="x", pady=(0, 5))
            ctk.CTkFrame(bar_bg, fg_color=self.colors["success"], width=max(4, int(pct*200)), height=6, corner_radius=3).place(x=0, y=0)

    def _render_stock_alerts(self, parent):
        """Alertas de Stock"""
        self._create_sidebar_card(parent, "Alertas Stock", "⚠️", self._content_stock)

    def _content_stock(self, parent):
        session = self.db_manager.get_session()
        try:
            low_stock = session.query(Ingrediente).filter(Ingrediente.cantidad <= Ingrediente.cantidad_minima).limit(3).all()
            
            if not low_stock:
                ctk.CTkLabel(parent, text="Stock Saludaoble ✅", text_color=self.colors["success"]).pack(pady=10)
                return

            for ing in low_stock:
                row = ctk.CTkFrame(parent, fg_color="#FEF2F2", corner_radius=8, border_width=1, border_color="#FECACA")
                row.pack(fill="x", pady=4)
                
                content = ctk.CTkFrame(row, fg_color="transparent")
                content.pack(fill="both", padx=10, pady=8)
                
                ctk.CTkLabel(content, text=ing.nombre, font=("Segoe UI", 11, "bold"), text_color="#991B1B").pack(anchor="w")
                ctk.CTkLabel(content, text=f"Queda: {ing.cantidad} {ing.unidad}", font=("Segoe UI", 10), text_color="#B91C1C").pack(anchor="w")

        finally:
            self.db_manager.close_session(session)

    def _render_active_staff(self, parent):
        """Staff Activo"""
        self._create_sidebar_card(parent, "Equipo Activo", "👥", self._content_staff)

    def _content_staff(self, parent):
        session = self.db_manager.get_session()
        try:
            staff = session.query(Empleado).filter(Empleado.estado == config.EmpleadoEstado.ACTIVO).limit(4).all()
            
            if not staff:
                ctk.CTkLabel(parent, text="Sin personal activo", text_color=self.colors["text_light"]).pack(pady=10)
                return

            for emp in staff:
                row = ctk.CTkFrame(parent, fg_color="transparent")
                row.pack(fill="x", pady=6)
                
                initials = emp.nombre[:2].upper()
                avatar = ctk.CTkFrame(row, width=32, height=32, corner_radius=16, fg_color="#EEF2FF")
                avatar.pack(side="left")
                ctk.CTkLabel(avatar, text=initials, font=("Segoe UI", 10, "bold"), text_color=self.colors["primary"]).place(relx=0.5, rely=0.5, anchor="center")
                
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", padx=10)
                ctk.CTkLabel(info, text=emp.nombre, font=("Segoe UI", 11, "bold"), text_color=self.colors["text"]).pack(anchor="w")
                
                ctk.CTkFrame(row, width=8, height=8, corner_radius=4, fg_color=self.colors["success"]).pack(side="right")

        finally:
            self.db_manager.close_session(session)

    def _create_sidebar_card(self, parent, title, icon, content_callback):
        card = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=16, border_width=1, border_color=self.colors["border"])
        card.pack(fill="x", pady=(0, 20))
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header, text=title, font=("Segoe UI", 14, "bold"), text_color=self.colors["dark"]).pack(side="left")
        ctk.CTkLabel(header, text=icon, font=("Segoe UI Emoji", 14)).pack(side="right")
        
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", padx=15, pady=(0, 15))
        content_callback(body)

    def refrescar(self):
        """Recargar dashboard"""
        self.crear()
