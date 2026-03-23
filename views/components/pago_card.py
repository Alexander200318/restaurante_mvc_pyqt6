"""
Componente: Tarjeta de Pago
"""
import customtkinter as ctk
import config
from datetime import datetime

class PagoCard(ctk.CTkFrame):
    def __init__(self, parent, pago, on_action=None, **kwargs):
        super().__init__(
            parent, 
            fg_color="white", 
            corner_radius=16,
            border_width=0,
            **kwargs
        )
        self.pago = pago
        self.on_action = on_action
        self._crear_ui()

    def _crear_ui(self):
        # Layout principal
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=12, pady=12)

        # --- HEADER ---
        header = ctk.CTkFrame(main_layout, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        # ID y Mesa
        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack(side="left")
        
        titulo_mesa = "MESA ?"
        if self.pago.pedido and self.pago.pedido.mesa:
            titulo_mesa = f"MESA {self.pago.pedido.mesa.numero}"
            
        ctk.CTkLabel(
            info_frame,
            text=f"#{self.pago.id} • {titulo_mesa}",
            font=("Segoe UI", 12, "bold"),
            text_color="#94A3B8"
        ).pack(anchor="w")

        # Estado Badge
        estado_color = self._get_estado_color(self.pago.estado)
        bg_color = self._get_estado_bg_color(self.pago.estado)
        
        badge = ctk.CTkFrame(header, fg_color=bg_color, corner_radius=100, height=24)
        badge.pack(side="right", anchor="n")
        
        ctk.CTkLabel(
            badge,
            text=self.pago.estado.value.upper(),
            font=("Segoe UI", 10, "bold"),
            text_color=estado_color
        ).pack(padx=10, pady=2)

        # --- CONTENIDO ---
        # Si el pago es PENDIENTE y el monto es 0, intentamos mostrar el total del pedido
        monto_mostrar = self.pago.monto
        
        if self.pago.estado == config.PagoEstado.PENDIENTE and monto_mostrar == 0:
            if self.pago.pedido:
                # OJO: Aquí asumimos que los detalles ya vienen cargados gracias a selectinload en el modelo
                # Si no vinieran cargados, esto podría fallar o devolver 0.
                try:
                    monto_mostrar = self.pago.pedido.calcular_total()
                except:
                    pass

        # Monto Grande
        ctk.CTkLabel(
            main_layout,
            text=f"${monto_mostrar:.2f}",
            font=("Segoe UI Display", 28, "bold"),
            text_color=config.COLORS["primary"]
        ).pack(anchor="w", pady=(5, 0))
        
        # Cliente
        cliente_nombre = "Cliente Genérico"
        if self.pago.pedido and self.pago.pedido.cliente:
            cliente_nombre = f"{self.pago.pedido.cliente.nombre} {self.pago.pedido.cliente.apellido}"
            
        ctk.CTkLabel(
            main_layout,
            text=cliente_nombre,
            font=("Segoe UI", 14),
            text_color="#1E293B"
        ).pack(anchor="w", pady=(0, 10))

        # Detalles Meta
        meta_frame = ctk.CTkFrame(main_layout, fg_color="#F8FAFC", corner_radius=8)
        meta_frame.pack(fill="x", pady=(0, 10))
        
        # Fecha
        fecha_str = self.pago.fecha_pago.strftime("%d/%m %H:%M") if self.pago.fecha_pago else "Pendiente"
        self._crear_meta_row(meta_frame, "📅 Fecha:", fecha_str)
        
        # Método (Solo mostrar si está pagado)
        if self.pago.estado == config.PagoEstado.PAGADO:
            metodo_str = self.pago.metodo.value if self.pago.metodo else "—"
            self._crear_meta_row(meta_frame, "💳 Método:", metodo_str)

        # --- BOTÓN ACCIÓN ---
        btn_text = "Ver Comprobante" if self.pago.estado == config.PagoEstado.PAGADO else "Procesar Pago"
        btn_color = config.COLORS["success"] if self.pago.estado == config.PagoEstado.PAGADO else config.COLORS["primary"]
        
        btn_action = ctk.CTkButton(
            main_layout,
            text=btn_text,
            fg_color=btn_color,
            hover_color=self._darken_color(btn_color),
            height=32,
            font=("Segoe UI", 12, "bold"),
            command=lambda: self.on_action(self.pago) if self.on_action else None
        )
        btn_action.pack(fill="x", pady=(5, 0))

    def _crear_meta_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=4)
        
        ctk.CTkLabel(
            row, text=label, 
            font=("Segoe UI", 11), 
            text_color="#64748B", 
            width=60, 
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            row, text=value, 
            font=("Segoe UI", 11, "bold"), 
            text_color="#334155"
        ).pack(side="left")

    def _get_estado_color(self, estado):
        if estado == config.PagoEstado.PAGADO:
            return "#15803d" # Green 700
        elif estado == config.PagoEstado.PENDIENTE:
            return "#b45309" # Amber 700
        return "#1d4ed8" # Blue 700

    def _get_estado_bg_color(self, estado):
        if estado == config.PagoEstado.PAGADO:
            return "#dcfce7" # Green 100
        elif estado == config.PagoEstado.PENDIENTE:
            return "#fef3c7" # Amber 100
        return "#dbeafe" # Blue 100

    def _darken_color(self, hex_color, factor=0.8):
        # Función simple para oscurecer color hex (simulado)
        # En producción usaría lib externa o algo más robusto, 
        # aquí retorno un hardcoded si es primary/success de config
        if hex_color == config.COLORS["primary"]: return "#0d47a1"
        if hex_color == config.COLORS["success"]: return "#14532d"
        return "gray"