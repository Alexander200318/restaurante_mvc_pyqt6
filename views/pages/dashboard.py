"""
Dashboard Principal - Resumen de todo el Restaurante
Versión mejorada con CustomTkinter
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from database.models import (
    Mesa, Cliente, Empleado, Ingrediente, 
    Plato, Pedido, DetallePedido, Pago
)
from sqlalchemy import func
import config


class DashboardPage:
    """Página de Dashboard con resumen ejecutivo"""
    
    def __init__(self, frame_contenido, db_manager: DatabaseManager):
        self.frame_contenido = frame_contenido
        self.db_manager = db_manager
        self.frame = None
        self.widgets = {}
        
    def crear(self):
        """Crear la página del dashboard"""
        # Limpiar frame
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()
        
        # Frame principal scrollable
        self.frame = ctk.CTkScrollableFrame(
            self.frame_contenido, 
            fg_color=config.COLORS["light_bg"]
        )
        self.frame.pack(fill="both", expand=True)
        
        # Header con gradiente visual (naranja)
        self._crear_header()
        
        # Métricas principales
        self._crear_metricas_principales()
        
        # Sección de Mesas
        self._crear_seccion_mesas_mejorada()
        
        # Sección de Pedidos
        self._crear_seccion_pedidos_mejorada()
        
        # Sección de Ingresos
        self._crear_seccion_ingresos_mejorada()
        
        # Sección de Empleados
        self._crear_seccion_empleados_mejorada()
        
        # Sección de Ingredientes
        self._crear_seccion_ingredientes_mejorada()
    
    def _crear_header(self):
        """Crear cabecera decorativa"""
        header = ctk.CTkFrame(self.frame, fg_color=config.COLORS["primary"], height=140)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        ctk.CTkLabel(
            header_content,
            text="🍽️ DASHBOARD RESTAURANTE",
            font=("Helvetica", 28, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(anchor="w", pady=(0, 8))
        
        fecha_text = f"📅 {datetime.now().strftime('%A, %d de %B')} | 🕐 {datetime.now().strftime('%H:%M')}"
        ctk.CTkLabel(header_content, text=fecha_text, font=("Helvetica", 11), text_color=config.COLORS["text_light"]).pack(anchor="w")
    
    def _crear_metricas_principales(self):
        """Crear tarjetas de métricas principales"""
        container = ctk.CTkFrame(self.frame, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=20)
        
        session = self.db_manager.get_session()
        try:
            total_mesas = session.query(func.count(Mesa.id)).scalar() or 0
            mesas_libres = session.query(func.count(Mesa.id)).filter(
                Mesa.estado == config.MesaEstado.LIBRE
            ).scalar() or 0
            mesas_ocupadas = session.query(func.count(Mesa.id)).filter(
                Mesa.estado == config.MesaEstado.OCUPADA
            ).scalar() or 0
            
            total_empleados = session.query(func.count(Empleado.id)).scalar() or 0
            empleados_activos = session.query(func.count(Empleado.id)).filter(
                Empleado.estado == config.EmpleadoEstado.ACTIVO
            ).scalar() or 0
            
            hoy = datetime.now().date()
            ingresos_hoy = session.query(func.sum(Pago.monto)).filter(
                func.date(Pago.fecha_pago) == hoy
            ).scalar() or 0
            
            pedidos_pendientes = session.query(func.count(Pedido.id)).filter(
                Pedido.estado == config.PedidoEstado.PENDIENTE
            ).scalar() or 0
            
        finally:
            self.db_manager.close_session(session)
        
        # Crear 4 metric cards en grid
        cards_data = [
            ("🪑", "MESAS", f"{mesas_ocupadas}/{total_mesas}", f"{mesas_libres} libres", config.COLORS["info"], 0),
            ("📋", "PEDIDOS", str(pedidos_pendientes), "pendientes entrega", config.COLORS["warning"], 1),
            ("💰", "INGRESOS", f"${ingresos_hoy:.2f}", "en el día", config.COLORS["success"], 2),
            ("👥", "EMPLEADOS", str(empleados_activos), f"de {total_empleados}", config.COLORS["primary"], 3),
        ]
        
        for icon, titulo, valor, subtitulo, color, col in cards_data:
            self._crear_metric_card(container, icon, titulo, valor, subtitulo, color, col)
    
    def _crear_metric_card(self, parent, icon, title, value, subtitle, color, column):
        """Crear una tarjeta de métrica mejorada"""
        card = ctk.CTkFrame(parent, fg_color=config.COLORS["dark_bg"], corner_radius=12)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)
        
        # Borde lateral
        border = ctk.CTkFrame(card, fg_color=color, width=6, corner_radius=12)
        border.pack(side="left", fill="y")
        border.pack_propagate(False)
        
        # Contenido
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        # Icono y título
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text=icon, font=("Helvetica", 24), text_color=color).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(header_frame, text=title, font=("Helvetica", 10, "bold"), text_color=config.COLORS["secondary"]).pack(side="left")
        
        # Valor principal
        ctk.CTkLabel(content, text=value, font=("Helvetica", 22, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(5, 2))
        
        # Subtítulo
        ctk.CTkLabel(content, text=subtitle, font=("Helvetica", 9), text_color=config.COLORS["secondary"]).pack(anchor="w")
    
    def _crear_seccion_mesas_mejorada(self):
        """Crear sección de mesas mejorada"""
        self._crear_titulo_seccion(self.frame, "🪑 Estado de Mesas")
        
        session = self.db_manager.get_session()
        try:
            mesas = session.query(Mesa).order_by(Mesa.numero).all()
            
            if not mesas:
                self._crear_empty_state(self.frame, "No hay mesas registradas")
                return
            
            container = ctk.CTkFrame(self.frame, fg_color="transparent")
            container.pack(fill="x", padx=20, pady=(0, 20))
            
            for idx, mesa in enumerate(mesas):
                if mesa.estado == config.MesaEstado.LIBRE:
                    bg, txt, emoji = config.COLORS["mesa_libre"], config.COLORS["texto_libre"], "✓"
                elif mesa.estado == config.MesaEstado.OCUPADA:
                    bg, txt, emoji = config.COLORS["mesa_ocupada"], config.COLORS["texto_ocupada"], "🍽️"
                else:
                    bg, txt, emoji = config.COLORS["mesa_reservada"], config.COLORS["texto_reservada"], "🔒"
                
                btn = ctk.CTkButton(
                    container,
                    text=f"{emoji}\nMesa {mesa.numero}\n{mesa.capacidad} pax",
                    fg_color=bg,
                    hover_color=bg,
                    text_color=txt,
                    corner_radius=10,
                    height=90,
                    font=("Helvetica", 10, "bold"),
                    state="disabled"
                )
                btn.grid(row=idx // 8, column=idx % 8, padx=5, pady=5, sticky="nsew")
                container.grid_columnconfigure(idx % 8, weight=1)
        
        finally:
            self.db_manager.close_session(session)
    
    def _crear_seccion_pedidos_mejorada(self):
        """Crear sección de pedidos mejorada"""
        self._crear_titulo_seccion(self.frame, "📋 Pedidos Activos")
        
        session = self.db_manager.get_session()
        try:
            pedidos = session.query(Pedido).filter(
                Pedido.estado == config.PedidoEstado.PENDIENTE
            ).order_by(Pedido.fecha_creacion.desc()).limit(6).all()
            
            if not pedidos:
                self._crear_empty_state(self.frame, "✅ No hay pedidos pendientes", success=True)
                return
            
            tabla = ctk.CTkFrame(self.frame, fg_color=config.COLORS["dark_bg"], corner_radius=10)
            tabla.pack(fill="both", padx=20, pady=(0, 20))
            
            # Encabezado
            header = ctk.CTkFrame(tabla, fg_color=config.COLORS["primary"], corner_radius=10)
            header.pack(fill="x", padx=0, pady=0)
            
            for col, text in enumerate(["ID", "Mesa", "Cliente", "Empleado", "Hora", "Estado"]):
                ctk.CTkLabel(header, text=text, font=("Helvetica", 10, "bold"), text_color=config.COLORS["text_light"]).grid(row=0, column=col, padx=12, pady=10, sticky="w")
                header.grid_columnconfigure(col, weight=1)
            
            # Filas
            for row, pedido in enumerate(pedidos, 1):
                bg = config.COLORS["light_bg"] if row % 2 else config.COLORS["dark_bg"]
                row_frame = ctk.CTkFrame(tabla, fg_color=bg)
                row_frame.pack(fill="x", padx=10, pady=3)
                
                datos = [
                    str(pedido.id),
                    f"Mesa {pedido.mesa.numero}" if pedido.mesa else "-",
                    (pedido.cliente.nombre if pedido.cliente else "-")[:15],
                    (pedido.empleado.nombre if pedido.empleado else "-")[:15],
                    pedido.fecha_creacion.strftime("%H:%M") if pedido.fecha_creacion else "-",
                    "⏳"
                ]
                
                for col, dato in enumerate(datos):
                    ctk.CTkLabel(row_frame, text=dato, font=("Helvetica", 9), text_color=config.COLORS["text_dark"]).grid(row=0, column=col, padx=12, pady=8, sticky="w")
                    row_frame.grid_columnconfigure(col, weight=1)
        
        finally:
            self.db_manager.close_session(session)
    
    def _crear_seccion_ingresos_mejorada(self):
        """Crear sección de ingresos mejorada"""
        self._crear_titulo_seccion(self.frame, "💵 Ingresos del Día")
        
        session = self.db_manager.get_session()
        try:
            hoy = datetime.now().date()
            total = session.query(func.sum(Pago.monto)).filter(func.date(Pago.fecha_pago) == hoy).scalar() or 0
            cantidad = session.query(func.count(Pago.id)).filter(func.date(Pago.fecha_pago) == hoy).scalar() or 0
            promedio = total / cantidad if cantidad > 0 else 0
            pagos = session.query(Pago.metodo, func.sum(Pago.monto).label('total')).filter(func.date(Pago.fecha_pago) == hoy).group_by(Pago.metodo).all()
        finally:
            self.db_manager.close_session(session)
        
        container = ctk.CTkFrame(self.frame, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Tres cards principales
        for i, (titulo, valor, color) in enumerate([("Total", f"${total:.2f}", config.COLORS["success"]), ("Transacciones", str(cantidad), config.COLORS["info"]), ("Promedio", f"${promedio:.2f}", config.COLORS["warning"])]):
            card = ctk.CTkFrame(container, fg_color=color, corner_radius=12)
            card.grid(row=0, column=i, padx=8, pady=0, sticky="nsew")
            container.grid_columnconfigure(i, weight=1)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=15, pady=12)
            ctk.CTkLabel(content, text=titulo, font=("Helvetica", 10), text_color=config.COLORS["text_light"]).pack(anchor="w")
            ctk.CTkLabel(content, text=valor, font=("Helvetica", 20, "bold"), text_color=config.COLORS["text_light"]).pack(anchor="w", pady=(3, 0))
        
        # Desglose
        if pagos:
            ctk.CTkLabel(self.frame, text="Desglose por Método", font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 10))
            
            for metodo, total_metodo in pagos:
                card = ctk.CTkFrame(self.frame, fg_color=config.COLORS["dark_bg"], corner_radius=8)
                card.pack(fill="x", padx=20, pady=3)
                
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=15, pady=8)
                
                ctk.CTkLabel(content, text=metodo.capitalize(), font=("Helvetica", 10, "bold"), text_color=config.COLORS["text_dark"]).pack(side="left")
                ctk.CTkLabel(content, text=f"${total_metodo:.2f}", font=("Helvetica", 10), text_color=config.COLORS["success"]).pack(side="right")
    
    def _crear_seccion_empleados_mejorada(self):
        """Crear sección de empleados mejorada"""
        self._crear_titulo_seccion(self.frame, "👥 Empleados Activos")
        
        session = self.db_manager.get_session()
        try:
            empleados = session.query(Empleado).filter(Empleado.estado == config.EmpleadoEstado.ACTIVO).limit(6).all()
            
            if not empleados:
                self._crear_empty_state(self.frame, "No hay empleados activos")
                return
            
            container = ctk.CTkFrame(self.frame, fg_color="transparent")
            container.pack(fill="x", padx=20, pady=(0, 20))
            
            for idx, emp in enumerate(empleados):
                card = ctk.CTkFrame(container, fg_color=config.COLORS["dark_bg"], corner_radius=10)
                card.grid(row=idx // 3, column=idx % 3, padx=10, pady=10, sticky="nsew")
                container.grid_columnconfigure(idx % 3, weight=1)
                
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=15, pady=15)
                
                ctk.CTkLabel(content, text=emp.nombre, font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(0, 4))
                ctk.CTkLabel(content, text=emp.puesto.value.capitalize() if emp.puesto else "-", font=("Helvetica", 9), text_color=config.COLORS["primary"]).pack(anchor="w", pady=(0, 10))
                
                sep = ctk.CTkFrame(content, fg_color=config.COLORS["border"], height=1)
                sep.pack(fill="x", pady=(0, 10))
                
                if emp.fecha_ingreso:
                    ctk.CTkLabel(content, text=f"📅 {emp.fecha_ingreso.strftime('%d/%m/%Y')}", font=("Helvetica", 8), text_color=config.COLORS["secondary"]).pack(anchor="w")
        
        finally:
            self.db_manager.close_session(session)
    
    def _crear_seccion_ingredientes_mejorada(self):
        """Crear sección de ingredientes mejorada"""
        self._crear_titulo_seccion(self.frame, "⚠️ Ingredientes Bajo Stock")
        
        session = self.db_manager.get_session()
        try:
            ingredientes = session.query(Ingrediente).filter(Ingrediente.cantidad <= Ingrediente.cantidad_minima).order_by(Ingrediente.cantidad).limit(8).all()
            
            if not ingredientes:
                self._crear_empty_state(self.frame, "✅ Stock suficiente en todos los ingredientes", success=True)
                return
            
            container = ctk.CTkFrame(self.frame, fg_color="transparent")
            container.pack(fill="x", padx=20, pady=(0, 20))
            
            for ing in ingredientes:
                porcentaje = (ing.cantidad / ing.cantidad_minima * 100) if ing.cantidad_minima > 0 else 0
                
                card = ctk.CTkFrame(container, fg_color=config.COLORS["mesa_ocupada"], corner_radius=10)
                card.pack(fill="x", pady=5)
                
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=15, pady=12)
                
                ctk.CTkLabel(content, text=f"🔴 {ing.nombre}", font=("Helvetica", 10, "bold"), text_color=config.COLORS["texto_ocupada"]).pack(anchor="w", pady=(0, 8))
                
                # Barra de progreso
                bar_frame = ctk.CTkFrame(content, fg_color=config.COLORS["light_bg"], corner_radius=4, height=6)
                bar_frame.pack(fill="x", pady=(0, 8))
                bar_frame.pack_propagate(False)
                
                bar_filled = ctk.CTkFrame(bar_frame, fg_color=config.COLORS["danger"], corner_radius=4, width=int(porcentaje * 2))
                bar_filled.pack(side="left", fill="y")
                bar_filled.pack_propagate(False)
                
                detalles = f"{ing.cantidad:.1f} {ing.unidad} / {ing.cantidad_minima} {ing.unidad} ({porcentaje:.0f}%)"
                ctk.CTkLabel(content, text=detalles, font=("Helvetica", 8), text_color=config.COLORS["texto_ocupada"]).pack(anchor="w")
        
        finally:
            self.db_manager.close_session(session)
    
    def _crear_titulo_seccion(self, parent, texto):
        """Crear titulo de sección"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(15, 10))
        
        line = ctk.CTkFrame(frame, fg_color=config.COLORS["primary"], width=5, height=2)
        line.pack(side="left", padx=(0, 10))
        line.pack_propagate(False)
        
        ctk.CTkLabel(frame, text=texto, font=("Helvetica", 14, "bold"), text_color=config.COLORS["text_dark"]).pack(side="left", anchor="w")
    
    def _crear_empty_state(self, parent, mensaje, success=False):
        """Crear estado vacío"""
        card = ctk.CTkFrame(parent, fg_color=config.COLORS["dark_bg"], corner_radius=10)
        card.pack(fill="x", padx=20, pady=(0, 20))
        
        color = config.COLORS["success"] if success else config.COLORS["secondary"]
        ctk.CTkLabel(card, text=mensaje, font=("Helvetica", 11), text_color=color).pack(pady=20)
    
    
    def refrescar(self):
        """Refrescar los datos del dashboard"""
        self.crear()
