"""
Componente: Tarjeta de Pedido Ultra-Moderna
"""
import customtkinter as ctk
import config

class PedidoCard(ctk.CTkFrame):
    def __init__(self, parent, pedido, on_status_change=None, **kwargs):
        # Card container styling - Clean White Card
        super().__init__(
            parent, 
            fg_color="white", 
            corner_radius=16, 
            border_width=0, # Sin borde para look más limpio
            **kwargs
        )
        self.pedido = pedido
        self.on_status_change = on_status_change

        # Sombra sutil simulada con un frame interno si fuera necesario, 
        # pero CTK no soporta sombras reales. Usaremos contraste.
        self._crear_ui()

    def _crear_ui(self):
        # CONTENEDOR PRINCIPAL CON PADDING INTERNO
        # Usamos un frame transparente para el padding reducido
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=12, pady=12)

        # --- HEADER (MESA + TIME AGO) ---
        header = ctk.CTkFrame(main_layout, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        # Mesa (Izquierda) - Grande y claro
        mesa_frame = ctk.CTkFrame(header, fg_color="transparent")
        mesa_frame.pack(side="left")
        
        ctk.CTkLabel(
            mesa_frame, 
            text="MESA", 
            font=("Segoe UI", 10, "bold"),
            text_color="#94A3B8" # Slate-400
        ).pack(anchor="w", pady=(0,0))
        
        ctk.CTkLabel(
            mesa_frame, 
            text=f"{self.pedido.mesa.numero}", 
            font=("Segoe UI Display", 22, "bold"),
            text_color="#1E293B" # Slate-800
        ).pack(anchor="w", pady=(0,0))

        # Estado (Derecha) - Pill Style
        estado_color = self._get_estado_color(self.pedido.estado)
        bg_color = self._get_estado_bg_color(self.pedido.estado)
        
        badge = ctk.CTkFrame(
            header, 
            fg_color=bg_color, 
            corner_radius=100, 
            height=26
        )
        badge.pack(side="right", anchor="n")
        
        ctk.CTkLabel(
            badge,
            text=self.pedido.estado.value.upper(),
            font=("Segoe UI", 10, "bold"),
            text_color=estado_color,
        ).pack(padx=12, pady=3)

        # --- INFO META (MESERO + HORA) ---
        meta_frame = ctk.CTkFrame(main_layout, fg_color="#F8FAFC", corner_radius=6)
        meta_frame.pack(fill="x", pady=(0, 10))
        
        icon = "👤" if self.pedido.empleado else "❓"
        nombre = self.pedido.empleado.nombre if self.pedido.empleado else "Sin asignar"
        hora = self.pedido.fecha_creacion.strftime("%H:%M")
        
        ctk.CTkLabel(
            meta_frame,
            text=f"{icon} {nombre}   •   🕒 {hora}",
            font=("Segoe UI", 11),
            text_color="#64748B",
            height=24
        ).pack(padx=8, anchor="w")

        # --- LISTA PRODUCTOS (SCROLLABLE SI SON MUCHOS) ---
        # Solo mostraremos los primeros 4-5 items y un indicador si hay más, o scroll
        # Para mantener cards uniformes, usaremos un frame fijo
        
        items_container = ctk.CTkFrame(main_layout, fg_color="transparent")
        items_container.pack(fill="both", expand=True, pady=(0, 10))
        
        if not self.pedido.detalles:
             ctk.CTkLabel(items_container, text="Sin productos", text_color="#CBD5E1", font=("Segoe UI", 11)).pack()
        else:
            for detalle in self.pedido.detalles:
                row = ctk.CTkFrame(items_container, fg_color="transparent", height=20)
                row.pack(fill="x", pady=1)
                
                # Cantidad (Círculo pequeño o solo número bold)
                ctk.CTkLabel(
                    row,
                    text=f"{detalle.cantidad}x",
                    font=("Segoe UI", 12, "bold"),
                    text_color=config.COLORS["primary"],
                    width=20,
                    anchor="w"
                ).pack(side="left")
                
                # Nombre Plato
                ctk.CTkLabel(
                    row,
                    text=detalle.plato.nombre,
                    font=("Segoe UI", 12),
                    text_color="#334155",
                    anchor="w"
                ).pack(side="left", fill="x", expand=True)

        # Separador Dotted
        canvas = ctk.CTkCanvas(main_layout, height=2, bg="white", highlightthickness=0)
        canvas.pack(fill="x", pady=(0, 10))
        canvas.create_line(0, 1, 500, 1, fill="#E2E8F0", dash=(2, 2))
        
        # --- FOOTER (TOTAL) ---
        footer = ctk.CTkFrame(main_layout, fg_color="transparent")
        footer.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            footer,
            text="TOTAL",
            font=("Segoe UI", 10, "bold"),
            text_color="#94A3B8"
        ).pack(side="left", anchor="s", pady=(0, 2))
        
        ctk.CTkLabel(
            footer,
            text=f"${self.pedido.calcular_total():.2f}",
            font=("Segoe UI", 18, "bold"),
            text_color="#0F172A"
        ).pack(side="right")

        # --- BOTÓN ACCIÓN ---
        btn = self._get_action_button(main_layout)
        if btn:
            btn.pack(fill="x")

    def _get_estado_color(self, estado):
        colors = {
            config.PedidoEstado.PENDIENTE: "#B45309", # Amber 700
            config.PedidoEstado.PREPARANDO: "#1D4ED8", # Blue 700
            config.PedidoEstado.LISTO: "#047857", # Emerald 700
            config.PedidoEstado.ENTREGADO: "#374151", # Gray 700
            config.PedidoEstado.CANCELADO: "#B91C1C"  # Red 700
        }
        return colors.get(estado, "#000000")

    def _get_estado_bg_color(self, estado):
        colors = {
            config.PedidoEstado.PENDIENTE: "#FEF3C7", # Amber 100
            config.PedidoEstado.PREPARANDO: "#DBEAFE", # Blue 100
            config.PedidoEstado.LISTO: "#D1FAE5", # Emerald 100
            config.PedidoEstado.ENTREGADO: "#F3F4F6", # Gray 100
            config.PedidoEstado.CANCELADO: "#FEE2E2"  # Red 100
        }
        return colors.get(estado, "#FFFFFF")

    def _get_action_button(self, parent):
        estado = self.pedido.estado
        
        # Configuración común de botones grandes
        btn_kwargs = {
            "height": 45,
            "corner_radius": 12,
            "font": ("Segoe UI", 13, "bold"),
            "fg_color": "#F1F5F9", # Default Gray
            "text_color": "#475569"
        }
        
        if estado == config.PedidoEstado.PENDIENTE:
            return ctk.CTkButton(
                parent,
                text="🔥 PASAR A COCINA",
                fg_color=config.COLORS["primary"],
                hover_color=config.COLORS["accent"],
                text_color="white",
                command=lambda: self._cambiar_estado(config.PedidoEstado.PREPARANDO),
                height=36, corner_radius=10, font=("Segoe UI", 11, "bold")
            )
        elif estado == config.PedidoEstado.PREPARANDO:
            return ctk.CTkButton(
                parent,
                text="✅ TERMINAR ORDEN",
                fg_color="#10B981", # Emerald
                hover_color="#059669",
                text_color="white",
                command=lambda: self._cambiar_estado(config.PedidoEstado.LISTO),
                height=36, corner_radius=10, font=("Segoe UI", 11, "bold")
            )
        elif estado == config.PedidoEstado.LISTO:
            return ctk.CTkButton(
                parent,
                text="🍽️ ENTREGAR",
                fg_color="#3B82F6", # Blue
                hover_color="#2563EB",
                text_color="white",
                command=lambda: self._cambiar_estado(config.PedidoEstado.ENTREGADO),
                height=36, corner_radius=10, font=("Segoe UI", 11, "bold")
            )
        
        return None # Sin botón para entregados/cancelados

    def _cambiar_estado(self, nuevo_estado):
        if self.on_status_change:
            self.on_status_change(self.pedido.id, nuevo_estado)
