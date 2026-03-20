"""
Página: Gestión de Clientes - Diseño Grid Visual
"""
import customtkinter as ctk
from controllers.clientes_controller import ClientesController
from controllers.mesas_controller import MesasController
from views.components.dialog_utils import DialogUtils
import config

class ClientesPage(ctk.CTkFrame):
    """Módulo de Clientes con Grid Visual"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#F9FAFB", **kwargs)
        
        self.controller = ClientesController()
        self.mesas_controller = MesasController()
        self.cliente_seleccionado = None
        self.grid_frame = None
        self.cliente_cards = {}
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz"""
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color="#FFFFFF", height=100)
        frame_header.pack(side="top", fill="x", padx=0, pady=0)
        frame_header.pack_propagate(False)
        
        # Separador sutil
        separator = ctk.CTkFrame(frame_header, fg_color="#E5E7EB", height=1)
        separator.pack(fill="x", pady=(0, 0))
        
        # Contenedor para título y botones
        frame_header_content = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Lado izquierdo: Título
        frame_titulo = ctk.CTkFrame(frame_header_content, fg_color="transparent")
        frame_titulo.pack(side="left", fill="both", expand=True)
        
        titulo = ctk.CTkLabel(
            frame_titulo,
            text="Gestión de Clientes",
            text_color="#1F2937",
            font=("Helvetica", 32, "bold")
        )
        titulo.pack(anchor="w")
        
        subtitulo = ctk.CTkLabel(
            frame_titulo,
            text="Administra y organiza la información de tus clientes",
            text_color="#6B7280",
            font=("Helvetica", 12)
        )
        subtitulo.pack(anchor="w", pady=(6, 0))
        
        # Lado derecho: Botón Nuevo Cliente
        btn_nuevo = ctk.CTkButton(
            frame_header_content,
            text="+ Nuevo Cliente",
            command=self._crear_dialogo_nuevo_cliente,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="white",
            font=("Helvetica", 13, "bold"),
            height=45,
            width=180,
            corner_radius=8
        )
        btn_nuevo.pack(side="right", padx=0)
        
        # === CONTENIDO PRINCIPAL ===
        frame_main = ctk.CTkFrame(self, fg_color="#F9FAFB")
        frame_main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame scrollable para el grid
        self.canvas = ctk.CTkCanvas(
            frame_main,
            bg="#F9FAFB",
            highlightthickness=0,
            height=400
        )
        scrollbar = ctk.CTkScrollbar(frame_main, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(
            self.canvas,
            fg_color="#F9FAFB"
        )
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Grid frame para los clientes (4 columnas)
        self.grid_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
    
    
    def refrescar_tabla(self):
        """Refrescar grid de clientes"""
        # Limpiar grid anterior
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.cliente_cards = {}
        
        # Obtener todos los clientes
        success, clientes, msg = self.controller.obtener_todos_clientes()
        if not success or not clientes:
            label_vacio = ctk.CTkLabel(
                self.grid_frame,
                text="No hay clientes disponibles",
                text_color=config.COLORS["text_dark"],
                font=("Helvetica", 14)
            )
            label_vacio.pack(pady=40)
            return
        
        # Crear lista de clientes en filas
        for idx, cliente in enumerate(clientes):
            self._crear_fila_cliente(cliente, idx)
    
    def _crear_fila_cliente(self, cliente, idx):
        """Crear fila cliente estilo lista"""
        # Fila principal con diseño profesional
        row_frame = ctk.CTkFrame(self.grid_frame, fg_color="white", corner_radius=12)
        row_frame.pack(fill="x", pady=12, padx=0)
        
        # Línea izquierda decorativa
        left_border = ctk.CTkFrame(row_frame, fg_color="#10B981", width=4, corner_radius=2)
        left_border.pack(side="left", fill="y", padx=(0, 0))
        
        # Contenedor con padding generoso
        content_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=18)
        
        # Lado izquierdo: Nombre e info
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Nombre (más grande y prominente)
        nombre_completo = f"{cliente.nombre} {cliente.apellido}"
        ctk.CTkLabel(
            left_frame,
            text=nombre_completo,
            text_color="#1F2937",
            font=("Helvetica", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Información secundaria (Cédula, Teléfono)
        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(anchor="w", fill="x")
        
        ctk.CTkLabel(
            info_frame,
            text=f"ID: {cliente.cedula}",
            text_color="#9CA3AF",
            font=("Helvetica", 11)
        ).pack(side="left", padx=(0, 24))
        
        if cliente.telefono:
            ctk.CTkLabel(
                info_frame,
                text=f"Teléfono: {cliente.telefono}",
                text_color="#9CA3AF",
                font=("Helvetica", 11)
            ).pack(side="left", padx=(0, 24))
        
        # Lado derecho: Botones
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=(30, 0))
        
        # Botones con mayor espacio
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        btn_ver = ctk.CTkButton(
            btn_frame,
            text="Ver",
            command=lambda: self._mostrar_detalles_cliente(cliente),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            text_color="white",
            font=("Helvetica", 11, "bold"),
            height=36,
            width=85,
            corner_radius=7
        )
        btn_ver.pack(side="left", padx=8)
        
        btn_editar = ctk.CTkButton(
            btn_frame,
            text="Editar",
            command=lambda: self._editar_cliente(cliente.id),
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="white",
            font=("Helvetica", 11, "bold"),
            height=36,
            width=85,
            corner_radius=7
        )
        btn_editar.pack(side="left", padx=8)
        
        btn_eliminar = ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            command=lambda: self._eliminar_cliente(cliente.id),
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="white",
            font=("Helvetica", 11, "bold"),
            height=36,
            width=95,
            corner_radius=7
        )
        btn_eliminar.pack(side="left", padx=8)
        
        # Efecto hover
        self.cliente_cards[cliente.id] = {'frame': row_frame, 'cliente': cliente}
        row_frame.bind("<Enter>", lambda e: self._on_row_hover_enter(cliente.id))
        row_frame.bind("<Leave>", lambda e: self._on_row_hover_leave(cliente.id))
        
        # Propagar eventos a children
        for child in row_frame.winfo_children():
            child.bind("<Enter>", lambda e: self._on_row_hover_enter(cliente.id))
            child.bind("<Leave>", lambda e: self._on_row_hover_leave(cliente.id))
    
    def _on_row_hover_enter(self, cliente_id):
        """Efecto hover en fila"""
        if cliente_id not in self.cliente_cards:
            return
        row_frame = self.cliente_cards[cliente_id]['frame']
        row_frame.configure(fg_color="#ECEFF1")
    
    def _on_row_hover_leave(self, cliente_id):
        """Restaurar color de fila"""
        if cliente_id not in self.cliente_cards:
            return
        row_frame = self.cliente_cards[cliente_id]['frame']
        idx = list(self.cliente_cards.keys()).index(cliente_id)
        bg_color = "#F9FAFB" if idx % 2 == 0 else "white"
        row_frame.configure(fg_color=bg_color)
    
    def _crear_card_cliente(self, cliente, row, col):
        """Crear tarjeta visual para un cliente - DEPRECATED"""
        pass
    
    def _on_hover_enter(self, cliente_id):
        """Efecto hover al pasar ratón - DEPRECATED"""
        pass
    
    def _on_hover_leave(self, cliente_id):
        """Restaurar color original - DEPRECATED"""
        pass
    
    def _on_cliente_click(self, cliente):
        """Click en un cliente"""
        self.cliente_seleccionado = cliente
        # Ya no se usa, los botones llaman directamente
    
    def _mostrar_detalles_cliente(self, cliente):
        """Mostrar diálogo con detalles del cliente"""
        dialog = ctk.CTkToplevel()
        dialog.configure(fg_color="#FFFFFF")
        dialog.title(f"Cliente: {cliente.nombre} {cliente.apellido}")
        dialog.geometry("480x600")
        dialog.resizable(False, False)
        dialog.update_idletasks()
        # Centrar ventana en la pantalla
        x = (dialog.winfo_screenwidth() // 2) - (240)
        y = (dialog.winfo_screenheight() // 2) - (300)
        dialog.geometry(f"480x600+{x}+{y}")
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        # Header del diálogo
        header_frame = ctk.CTkFrame(dialog, fg_color="#FFFFFF", height=65)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Información del Cliente",
            text_color="#1F2937",
            font=("Helvetica", 18, "bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        # Frame principal scrollable
        scrollable_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color="#FFFFFF"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Contenedor de campos
        fields_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        fields_container.pack(fill="both", expand=True, padx=24, pady=28)
        
        # Cédula
        ctk.CTkLabel(fields_container, text="Cédula", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        ctk.CTkLabel(fields_container, text=cliente.cedula, text_color="#6B7280", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 18), padx=0)
        
        # Nombre
        ctk.CTkLabel(fields_container, text="Nombre", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        ctk.CTkLabel(fields_container, text=cliente.nombre, text_color="#6B7280", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 18), padx=0)
        
        # Apellido
        ctk.CTkLabel(fields_container, text="Apellido", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        ctk.CTkLabel(fields_container, text=cliente.apellido, text_color="#6B7280", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 18), padx=0)
        
        # Teléfono
        if cliente.telefono:
            ctk.CTkLabel(fields_container, text="Teléfono", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
            ctk.CTkLabel(fields_container, text=cliente.telefono, text_color="#6B7280", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 18), padx=0)
        
        # Correo
        if cliente.correo:
            ctk.CTkLabel(fields_container, text="Correo", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
            ctk.CTkLabel(fields_container, text=cliente.correo, text_color="#6B7280", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 18), padx=0)
        
        # Dirección
        if cliente.direccion:
            ctk.CTkLabel(fields_container, text="Dirección", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
            ctk.CTkLabel(fields_container, text=cliente.direccion, text_color="#6B7280", font=("Helvetica", 12), wraplength=350).pack(anchor="w", pady=(0, 18), padx=0)
        
        # Separador
        ctk.CTkFrame(dialog, fg_color="#F0F0F0", height=1).pack(fill="x")
        
        # Botones con diseño profesional
        frame_botones = ctk.CTkFrame(dialog, fg_color="#FFFFFF")
        frame_botones.pack(fill="x", padx=20, pady=16)
        
        btn_editar = ctk.CTkButton(
            frame_botones,
            text="Editar",
            command=lambda: self._editar_cliente(cliente.id, dialog),
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="white",
            height=44,
            font=("Helvetica", 12, "bold"),
            corner_radius=8
        )
        btn_editar.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        btn_eliminar = ctk.CTkButton(
            frame_botones,
            text="Eliminar",
            command=lambda: self._eliminar_cliente(cliente.id),
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="white",
            height=44,
            font=("Helvetica", 12, "bold"),
            corner_radius=8
        )
        btn_eliminar.pack(side="left", padx=(10, 0), expand=True, fill="x")
    
    def _mostrar_empty_state(self):
        """Mostrar estado vacío"""
        empty_frame = ctk.CTkFrame(self.frame_tabla, fg_color=config.COLORS["info"], corner_radius=10)
        empty_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Contenedor centrado
        center = ctk.CTkFrame(empty_frame, fg_color="transparent")
        center.pack(expand=True)
        
        ctk.CTkLabel(
            center,
            text="👥",
            font=("Helvetica", 64),
            text_color=config.COLORS["text_light"]
        ).pack(pady=(0, 15))
        
        ctk.CTkLabel(
            center,
            text="No hay clientes registrados",
            font=("Helvetica", 18, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            center,
            text="Haz clic en '➕ Nuevo Cliente' para crear uno",
            font=("Helvetica", 13),
            text_color=config.COLORS["text_light"]
        ).pack()
    
    def _crear_tabla_visual(self, clientes_data):
        """Crear tabla visual de clientes"""
        # Container de la tabla
        tabla_container = ctk.CTkFrame(self.frame_tabla, fg_color=config.COLORS["dark_bg"], corner_radius=10)
        tabla_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # === ENCABEZADO DE TABLA ===
        header_frame = ctk.CTkFrame(tabla_container, fg_color=config.COLORS["info"], corner_radius=10)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        columns = ["ID", "Nombre", "Mesa", "Personas", "Teléfono", "Estado", "Acciones"]
        column_widths = [50, 150, 80, 100, 120, 100, 120]
        
        for col, (header_text, width) in enumerate(zip(columns, column_widths)):
            ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=("Helvetica", 11, "bold"),
                text_color=config.COLORS["text_light"]
            ).grid(row=0, column=col, padx=12, pady=12, sticky="w", width=width)
        
        # === FILAS DE DATOS ===
        for row_idx, cliente_data in enumerate(clientes_data, 1):
            cliente_id, nombre, mesa, personas, telefono, estado = cliente_data
            
            # Alternancia de colores
            bg_color = config.COLORS["light_bg"] if row_idx % 2 == 0 else config.COLORS["dark_bg"]
            row_frame = ctk.CTkFrame(tabla_container, fg_color=bg_color)
            row_frame.pack(fill="x", padx=10, pady=3, ipady=8)
            
            # ID
            ctk.CTkLabel(
                row_frame,
                text=str(cliente_id),
                font=("Helvetica", 10),
                text_color=config.COLORS["secondary"]
            ).grid(row=0, column=0, padx=12, sticky="w", width=50)
            
            # Nombre
            ctk.CTkLabel(
                row_frame,
                text=nombre,
                font=("Helvetica", 11, "bold"),
                text_color=config.COLORS["text_dark"]
            ).grid(row=0, column=1, padx=12, sticky="w", width=150)
            
            # Mesa
            mesa_text = f"Mesa {mesa}" if isinstance(mesa, int) else str(mesa)
            ctk.CTkLabel(
                row_frame,
                text=mesa_text,
                font=("Helvetica", 10),
                text_color=config.COLORS["secondary"]
            ).grid(row=0, column=2, padx=12, sticky="w", width=80)
            
            # Personas
            personas_text = f"{personas} pax"
            ctk.CTkLabel(
                row_frame,
                text=personas_text,
                font=("Helvetica", 10),
                text_color=config.COLORS["secondary"]
            ).grid(row=0, column=3, padx=12, sticky="w", width=100)
            
            # Teléfono
            ctk.CTkLabel(
                row_frame,
                text=telefono if telefono != "—" else "—",
                font=("Helvetica", 10),
                text_color=config.COLORS["secondary"]
            ).grid(row=0, column=4, padx=12, sticky="w", width=120)
            
            # Estado (badge)
            estado_color = self._get_color_estado(estado)
            estado_frame = ctk.CTkFrame(row_frame, fg_color=estado_color, corner_radius=6)
            estado_frame.grid(row=0, column=5, padx=12, sticky="w", width=100)
            
            ctk.CTkLabel(
                estado_frame,
                text=estado.capitalize(),
                font=("Helvetica", 9, "bold"),
                text_color=config.COLORS["text_light"]
            ).pack(padx=8, pady=3)
            
            # Botones de acción
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=6, padx=12, sticky="w", width=120)
            
            # Botón Editar
            btn_edit = ctk.CTkButton(
                actions_frame,
                text="✏️ Editar",
                font=("Helvetica", 9),
                fg_color=config.COLORS["warning"],
                hover_color=config.COLORS["accent"],
                text_color=config.COLORS["text_light"],
                height=28,
                width=60,
                command=lambda cid=cliente_id: self._editar_cliente(cid)
            )
            btn_edit.pack(side="left", padx=2)
            
            # Botón Eliminar
            btn_delete = ctk.CTkButton(
                actions_frame,
                text="🗑️ Borrar",
                font=("Helvetica", 9),
                fg_color=config.COLORS["danger"],
                hover_color=config.COLORS["primary"],
                text_color=config.COLORS["text_light"],
                height=28,
                width=60,
                command=lambda cid=cliente_id: self._eliminar_cliente(cid)
            )
            btn_delete.pack(side="left", padx=2)
    
    def _get_color_estado(self, estado):
        """Obtener color según estado"""
        if estado.lower() == "comiendo":
            return config.COLORS["success"]
        elif estado.lower() == "pagado":
            return config.COLORS["info"]
        else:  # cancelado
            return config.COLORS["secondary"]
    
    def _crear_dialogo_nuevo_cliente(self):
        """Crear diálogo para nuevo cliente"""
        # Crear ventana
        dialog = ctk.CTkToplevel()
        dialog.configure(fg_color="#FFFFFF")
        dialog.title("Agregar Nuevo Cliente")
        dialog.geometry("480x620")
        dialog.resizable(False, False)
        dialog.update_idletasks()
        # Centrar ventana en la pantalla
        x = (dialog.winfo_screenwidth() // 2) - (240)
        y = (dialog.winfo_screenheight() // 2) - (310)
        dialog.geometry(f"480x620+{x}+{y}")
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        # Header del diálogo
        header_frame = ctk.CTkFrame(dialog, fg_color="#FFFFFF", height=65)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Información del Cliente",
            text_color="#1F2937",
            font=("Helvetica", 18, "bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        # Frame principal scrollable
        scrollable_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color="#FFFFFF"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Contenedor de campos con padding
        fields_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        fields_container.pack(fill="both", expand=True, padx=24, pady=28)
        
        # Cédula
        ctk.CTkLabel(fields_container, text="Cédula", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_cedula = ctk.CTkEntry(fields_container, placeholder_text="Ej: 1234567890", height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_cedula.pack(fill="x", pady=(0, 16), padx=0)
        
        # Nombre
        ctk.CTkLabel(fields_container, text="Nombre", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_nombre = ctk.CTkEntry(fields_container, placeholder_text="Ej: Jose", height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_nombre.pack(fill="x", pady=(0, 16), padx=0)
        
        # Apellido
        ctk.CTkLabel(fields_container, text="Apellido", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_apellido = ctk.CTkEntry(fields_container, placeholder_text="Ej: García López", height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_apellido.pack(fill="x", pady=(0, 16), padx=0)
        
        # Teléfono
        ctk.CTkLabel(fields_container, text="Teléfono (opcional)", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_telefono = ctk.CTkEntry(fields_container, placeholder_text="Ej: 0999999999", height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_telefono.pack(fill="x", pady=(0, 16), padx=0)
        
        # Correo
        ctk.CTkLabel(fields_container, text="Correo (opcional)", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_correo = ctk.CTkEntry(fields_container, placeholder_text="Ej: juan@email.com", height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_correo.pack(fill="x", pady=(0, 16), padx=0)
        
        # Dirección
        ctk.CTkLabel(fields_container, text="Dirección (opcional)", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_direccion = ctk.CTkEntry(fields_container, placeholder_text="Ej: Calle Principal 123", height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_direccion.pack(fill="x", pady=(0, 16), padx=0)
        
        # Separador sutil
        ctk.CTkFrame(dialog, fg_color="#F0F0F0", height=1).pack(fill="x")
        
        # Botones con diseño profesional
        frame_botones = ctk.CTkFrame(dialog, fg_color="#FFFFFF")
        frame_botones.pack(fill="x", padx=20, pady=16)
        
        def guardar():
            try:
                cedula = entry_cedula.get()
                nombre = entry_nombre.get()
                apellido = entry_apellido.get()
                
                if not cedula:
                    DialogUtils.mostrar_error("Error", "La cédula es requerida")
                    return
                if not nombre:
                    DialogUtils.mostrar_error("Error", "El nombre es requerido")
                    return
                if not apellido:
                    DialogUtils.mostrar_error("Error", "El apellido es requerido")
                    return
                
                telefono = entry_telefono.get() or None
                correo = entry_correo.get() or None
                direccion = entry_direccion.get() or None
                
                # Crear cliente sin mesa asignada
                success, cliente, msg = self.controller.crear_cliente(cedula, nombre, apellido, telefono, direccion, correo)
                if success:
                    DialogUtils.mostrar_exito("Éxito", "Cliente creado correctamente", parent=dialog)
                    dialog.destroy()
                    self.refrescar_tabla()
                else:
                    DialogUtils.mostrar_error("Error", msg, parent=dialog)
            except Exception as e:
                DialogUtils.mostrar_error("Error", str(e), parent=dialog)
        
        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="Guardar Cliente",
            command=guardar,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="white",
            height=44,
            font=("Helvetica", 12, "bold"),
            corner_radius=8
        )
        btn_guardar.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color="#374151",
            height=44,
            font=("Helvetica", 12, "bold"),
            corner_radius=8
        )
        btn_cancelar.pack(side="left", padx=(10, 0), expand=True, fill="x")
    
    def _editar_cliente(self, cliente_id, dialog=None):
        """Editar cliente"""
        success, cliente, msg = self.controller.obtener_cliente(cliente_id)
        
        if not success:
            DialogUtils.mostrar_error("Error", "No se pudo cargar el cliente")
            return
        
        if dialog:
            dialog.destroy()
        
        # Crear ventana
        ventana = ctk.CTkToplevel()
        ventana.configure(fg_color="#FFFFFF")
        ventana.title("Editar Cliente")
        ventana.geometry("480x620")
        ventana.resizable(False, False)
        ventana.update_idletasks()
        # Centrar ventana en la pantalla
        x = (ventana.winfo_screenwidth() // 2) - (240)
        y = (ventana.winfo_screenheight() // 2) - (310)
        ventana.geometry(f"480x620+{x}+{y}")
        ventana.attributes('-topmost', True)
        ventana.grab_set()
        
        # Header del diálogo
        header_frame = ctk.CTkFrame(ventana, fg_color="#FFFFFF", height=65)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Editar Información del Cliente",
            text_color="#1F2937",
            font=("Helvetica", 18, "bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        # Frame principal scrollable
        scrollable_frame = ctk.CTkScrollableFrame(
            ventana,
            fg_color="#FFFFFF"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Contenedor de campos
        fields_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        fields_container.pack(fill="both", expand=True, padx=24, pady=28)
        
        # Cédula (no editable)
        ctk.CTkLabel(fields_container, text="Cédula", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_cedula = ctk.CTkEntry(fields_container, placeholder_text="", height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_cedula.insert(0, cliente.cedula)
        entry_cedula.configure(state="disabled")
        entry_cedula.pack(fill="x", pady=(0, 16), padx=0)
        
        # Nombre
        ctk.CTkLabel(fields_container, text="Nombre", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_nombre = ctk.CTkEntry(fields_container, height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_nombre.insert(0, cliente.nombre)
        entry_nombre.pack(fill="x", pady=(0, 16), padx=0)
        
        # Apellido
        ctk.CTkLabel(fields_container, text="Apellido", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_apellido = ctk.CTkEntry(fields_container, height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_apellido.insert(0, cliente.apellido)
        entry_apellido.pack(fill="x", pady=(0, 16), padx=0)
        
        # Teléfono
        ctk.CTkLabel(fields_container, text="Teléfono", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_telefono = ctk.CTkEntry(fields_container, height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_telefono.insert(0, cliente.telefono or "")
        entry_telefono.pack(fill="x", pady=(0, 16), padx=0)
        
        # Correo
        ctk.CTkLabel(fields_container, text="Correo", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_correo = ctk.CTkEntry(fields_container, height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_correo.insert(0, cliente.correo or "")
        entry_correo.pack(fill="x", pady=(0, 16), padx=0)
        
        # Dirección
        ctk.CTkLabel(fields_container, text="Dirección", text_color="#1F2937", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 8), padx=0)
        entry_direccion = ctk.CTkEntry(fields_container, height=42, font=("Helvetica", 12), border_width=2, border_color="#E5E7EB", corner_radius=8, fg_color="#FFFFFF", text_color="#1F2937")
        entry_direccion.insert(0, cliente.direccion or "")
        entry_direccion.pack(fill="x", pady=(0, 16), padx=0)
        
        # Separador sutil
        ctk.CTkFrame(ventana, fg_color="#F0F0F0", height=1).pack(fill="x")
        
        # Botones con diseño profesional
        frame_botones = ctk.CTkFrame(ventana, fg_color="#FFFFFF")
        frame_botones.pack(fill="x", padx=20, pady=16)
        
        def guardar():
            nombre = entry_nombre.get()
            apellido = entry_apellido.get()
            telefono = entry_telefono.get() or None
            correo = entry_correo.get() or None
            direccion = entry_direccion.get() or None
            
            if not nombre:
                DialogUtils.mostrar_error("Error", "El nombre es requerido")
                return
            if not apellido:
                DialogUtils.mostrar_error("Error", "El apellido es requerido")
                return
            
            success, _, msg = self.controller.actualizar_cliente(cliente_id, nombre, apellido, telefono, direccion, correo)
            if success:
                DialogUtils.mostrar_exito("Éxito", "Cliente actualizado correctamente", parent=ventana)
                ventana.destroy()
                self.refrescar_tabla()
            else:
                DialogUtils.mostrar_error("Error", msg, parent=ventana)
        
        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="Guardar Cambios",
            fg_color="#10B981",
            hover_color="#059669",
            text_color="white",
            command=guardar,
            height=44,
            font=("Helvetica", 12, "bold"),
            corner_radius=8
        )
        btn_guardar.pack(side="left", padx=(0, 10), fill="both", expand=True)
        
        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color="#374151",
            command=ventana.destroy,
            height=44,
            font=("Helvetica", 12, "bold"),
            corner_radius=8
        )
        btn_cancelar.pack(side="left", padx=(10, 0), fill="both", expand=True)
    
    def _eliminar_cliente(self, cliente_id):
        """Eliminar cliente con confirmación"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Confirmar Eliminación")
        ventana.geometry("400x200")
        ventana.resizable(False, False)
        ventana.update_idletasks()
        # Centrar ventana en la pantalla
        x = (ventana.winfo_screenwidth() // 2) - (200)
        y = (ventana.winfo_screenheight() // 2) - (100)
        ventana.geometry(f"400x200+{x}+{y}")
        ventana.attributes('-topmost', True)
        
        frame = ctk.CTkFrame(ventana, fg_color=config.COLORS["light_bg"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(frame, fg_color=config.COLORS["danger"], corner_radius=10)
        header.pack(fill="x", padx=0, pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="🗑️ ¿Eliminar este cliente?",
            font=("Helvetica", 16, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=15, padx=15)
        
        ctk.CTkLabel(
            frame,
            text="Esta acción no se puede deshacer",
            font=("Helvetica", 12),
            text_color=config.COLORS["secondary"]
        ).pack(pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        def confirmar():
            success, _, msg = self.controller.eliminar_cliente(cliente_id)
            if success:
                self._mostrar_exito("Cliente eliminado")
                ventana.destroy()
                self.refrescar_tabla()
            else:
                self._mostrar_error(msg)
        
        btn_eliminar = ctk.CTkButton(
            btn_frame,
            text="✓ Eliminar",
            fg_color=config.COLORS["danger"],
            hover_color="#C91C1C",
            text_color=config.COLORS["text_light"],
            command=confirmar,
            height=40,
            font=("Helvetica", 12, "bold")
        )
        btn_eliminar.pack(side="left", padx=5, fill="both", expand=True)
        
        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="✕ Cancelar",
            fg_color="#6B7280",
            hover_color="#4B5563",
            text_color=config.COLORS["text_light"],
            command=ventana.destroy,
            height=40,
            font=("Helvetica", 12, "bold")
        )
        btn_cancelar.pack(side="left", padx=5, fill="both", expand=True)
    
    def _mostrar_exito(self, mensaje):
        """Mostrar mensaje de éxito"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Éxito")
        ventana.geometry("350x120")
        ventana.resizable(False, False)
        ventana.update_idletasks()
        # Centrar ventana en la pantalla
        x = (ventana.winfo_screenwidth() // 2) - (175)
        y = (ventana.winfo_screenheight() // 2) - (60)
        ventana.geometry(f"350x120+{x}+{y}")
        ventana.attributes('-topmost', True)
        
        frame = ctk.CTkFrame(ventana, fg_color=config.COLORS["success"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"✓ {mensaje}",
            font=("Helvetica", 13, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=20)
        
        ventana.after(2000, ventana.destroy)
    
    def _mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Error")
        ventana.geometry("350x120")
        ventana.resizable(False, False)
        ventana.update_idletasks()
        # Centrar ventana en la pantalla
        x = (ventana.winfo_screenwidth() // 2) - (175)
        y = (ventana.winfo_screenheight() // 2) - (60)
        ventana.geometry(f"350x120+{x}+{y}")
        ventana.attributes('-topmost', True)
        
        frame = ctk.CTkFrame(ventana, fg_color=config.COLORS["danger"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"✗ {mensaje}",
            font=("Helvetica", 13, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=20)
        
        ventana.after(3000, ventana.destroy)
