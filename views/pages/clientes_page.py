"""
Vista de Clientes - Gestión de comensales con diseño profesional
"""
import customtkinter as ctk
from datetime import datetime
from controllers.clientes_controller import ClientesController
from controllers.mesas_controller import MesasController
import config


class ClientesPage(ctk.CTkFrame):
    """Página de gestión de clientes - Diseño profesional"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=config.COLORS["light_bg"], **kwargs)
        
        self.controller = ClientesController()
        self.mesas_controller = MesasController()
        self.clientes_data = []
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz"""
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"], height=100)
        frame_header.pack(side="top", fill="x", padx=0, pady=0)
        frame_header.pack_propagate(False)
        
        # Contenedor para título y botones
        frame_header_content = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Lado izquierdo: Título
        frame_titulo = ctk.CTkFrame(frame_header_content, fg_color="transparent")
        frame_titulo.pack(side="left", fill="both", expand=True)
        
        titulo = ctk.CTkLabel(
            frame_titulo,
            text="👥 GESTIÓN DE CLIENTES",
            text_color="white",
            font=("Helvetica", 28, "bold")
        )
        titulo.pack(anchor="w")
        
        subtitulo = ctk.CTkLabel(
            frame_titulo,
            text="Gestiona comensales, mesas y clientes del restaurante",
            text_color="#E8EAED",
            font=("Helvetica", 11)
        )
        subtitulo.pack(anchor="w", pady=(3, 0))
        
        # Lado derecho: Botones de acción
        frame_botones = ctk.CTkFrame(frame_header_content, fg_color="transparent")
        frame_botones.pack(side="right")
        
        # Botón Nuevo Cliente
        btn_nuevo = ctk.CTkButton(
            frame_botones,
            text="➕ Nuevo Cliente",
            command=self._crear_dialogo_nuevo_cliente,
            fg_color=config.COLORS["success"],
            hover_color="#0E9F6E",
            text_color="white",
            font=("Helvetica", 12, "bold"),
            height=40
        )
        btn_nuevo.pack(side="left", padx=5)
        
        # Botón Refrescar
        btn_refrescar = ctk.CTkButton(
            frame_botones,
            text="🔄 Refrescar",
            command=self.refrescar_tabla,
            fg_color=config.COLORS["secondary"],
            hover_color=config.COLORS["primary"],
            text_color="white",
            font=("Helvetica", 12, "bold"),
            height=40
        )
        btn_refrescar.pack(side="left", padx=5)
        
        # === CONTENIDO PRINCIPAL ===
        frame_main = ctk.CTkFrame(self, fg_color=config.COLORS["light_bg"])
        frame_main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame para tabla
        self.frame_tabla = ctk.CTkFrame(frame_main, fg_color="transparent")
        self.frame_tabla.pack(fill="both", expand=True)
    
    def refrescar_tabla(self):
        """Refrescar tabla de clientes"""
        # Limpiar tabla anterior
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        
        # Obtener datos
        success, clientes_data, msg = self.controller.obtener_todos_clientes_formateados()
        
        if not success or not clientes_data:
            self._mostrar_empty_state()
            return
        
        self.clientes_data = clientes_data
        self._crear_tabla_visual(clientes_data)
    
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
        # Obtener mesas disponibles
        mesa_ids, mesa_labels = self.mesas_controller.obtener_selectorlist()
        
        # Crear ventana
        ventana = ctk.CTkToplevel(self)
        ventana.title("Nuevo Cliente")
        ventana.geometry("450x420")
        ventana.resizable(False, False)
        ventana.attributes('-topmost', True)
        
        # Frame principal
        frame = ctk.CTkFrame(ventana, fg_color=config.COLORS["light_bg"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(frame, fg_color=config.COLORS["info"], corner_radius=10)
        header.pack(fill="x", padx=0, pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="➕ Registrar Nuevo Cliente",
            font=("Helvetica", 16, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=15, padx=15)
        
        # Nombre
        ctk.CTkLabel(frame, text="Nombre Completo:", font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(10, 0))
        entry_nombre = ctk.CTkEntry(frame, placeholder_text="Juan García López", fg_color=config.COLORS["dark_bg"], text_color=config.COLORS["text_dark"], height=35)
        entry_nombre.pack(fill="x", pady=(5, 10))
        
        # Mesa
        ctk.CTkLabel(frame, text="Mesa Asignada:", font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(10, 0))
        combo_mesa = ctk.CTkComboBox(
            frame,
            values=mesa_labels if mesa_labels else ["Sin mesas disponibles"],
            fg_color=config.COLORS["dark_bg"],
            text_color=config.COLORS["text_dark"],
            button_color=config.COLORS["primary"],
            height=35
        )
        if mesa_labels:
            combo_mesa.set(mesa_labels[0])
        combo_mesa.pack(fill="x", pady=(5, 10))
        
        # Cantidad de personas
        ctk.CTkLabel(frame, text="Cantidad de Personas:", font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(10, 0))
        entry_personas = ctk.CTkEntry(frame, placeholder_text="2", fg_color=config.COLORS["dark_bg"], text_color=config.COLORS["text_dark"], height=35)
        entry_personas.insert(0, "1")
        entry_personas.pack(fill="x", pady=(5, 10))
        
        # Teléfono
        ctk.CTkLabel(frame, text="Teléfono (opcional):", font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(10, 0))
        entry_telefono = ctk.CTkEntry(frame, placeholder_text="+34 600 123 456", fg_color=config.COLORS["dark_bg"], text_color=config.COLORS["text_dark"], height=35)
        entry_telefono.pack(fill="x", pady=(5, 20))
        
        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        def guardar():
            nombre = entry_nombre.get()
            if not nombre:
                self._mostrar_error("Por favor ingresa un nombre")
                return
            
            try:
                personas = int(entry_personas.get())
            except:
                personas = 1
            
            telefono = entry_telefono.get() or None
            
            # Obtener ID de mesa del combo
            mesa_index = mesa_labels.index(combo_mesa.get()) if combo_mesa.get() in mesa_labels else None
            
            if mesa_index is not None:
                mesa_id = mesa_ids[mesa_index]
                success, cliente, msg = self.controller.crear_cliente(nombre, mesa_id, personas, telefono)
                if success:
                    self._mostrar_exito("Cliente creado exitosamente")
                    ventana.destroy()
                    self.refrescar_tabla()
                else:
                    self._mostrar_error(msg)
            else:
                self._mostrar_error("Por favor selecciona una mesa")
        
        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="✅ Guardar",
            fg_color=config.COLORS["success"],
            hover_color="#0E9F6E",
            text_color=config.COLORS["text_light"],
            command=guardar,
            height=40,
            font=("Helvetica", 12, "bold")
        )
        btn_guardar.pack(side="left", padx=5, fill="both", expand=True)
        
        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            fg_color="#6B7280",
            hover_color="#4B5563",
            text_color=config.COLORS["text_light"],
            command=ventana.destroy,
            height=40,
            font=("Helvetica", 12, "bold")
        )
        btn_cancelar.pack(side="left", padx=5, fill="both", expand=True)
    
    def _editar_cliente(self, cliente_id):
        """Editar cliente"""
        success, cliente, msg = self.controller.obtener_cliente(cliente_id)
        
        if not success:
            self._mostrar_error("No se pudo cargar el cliente")
            return
        
        # Crear ventana
        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar Cliente")
        ventana.geometry("450x380")
        ventana.resizable(False, False)
        ventana.attributes('-topmost', True)
        
        frame = ctk.CTkFrame(ventana, fg_color=config.COLORS["light_bg"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(frame, fg_color=config.COLORS["warning"], corner_radius=10)
        header.pack(fill="x", padx=0, pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="✏️ Editar Cliente",
            font=("Helvetica", 16, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=15, padx=15)
        
        # Nombre
        ctk.CTkLabel(frame, text="Nombre:", font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(10, 0))
        entry_nombre = ctk.CTkEntry(frame, fg_color=config.COLORS["dark_bg"], text_color=config.COLORS["text_dark"], height=35)
        entry_nombre.insert(0, cliente.nombre)
        entry_nombre.pack(fill="x", pady=(5, 10))
        
        # Personas
        ctk.CTkLabel(frame, text="Cantidad de Personas:", font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(10, 0))
        entry_personas = ctk.CTkEntry(frame, fg_color=config.COLORS["dark_bg"], text_color=config.COLORS["text_dark"], height=35)
        entry_personas.insert(0, str(cliente.cantidad_personas))
        entry_personas.pack(fill="x", pady=(5, 10))
        
        # Teléfono
        ctk.CTkLabel(frame, text="Teléfono:", font=("Helvetica", 11, "bold"), text_color=config.COLORS["text_dark"]).pack(anchor="w", pady=(10, 0))
        entry_telefono = ctk.CTkEntry(frame, fg_color=config.COLORS["dark_bg"], text_color=config.COLORS["text_dark"], height=35)
        entry_telefono.insert(0, cliente.telefono or "")
        entry_telefono.pack(fill="x", pady=(5, 20))
        
        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        def guardar():
            nombre = entry_nombre.get()
            try:
                personas = int(entry_personas.get())
            except:
                personas = cliente.cantidad_personas
            
            telefono = entry_telefono.get() or None
            
            success, _, msg = self.controller.actualizar_cliente(cliente_id, nombre, personas, telefono)
            if success:
                self._mostrar_exito("Cliente actualizado")
                ventana.destroy()
                self.refrescar_tabla()
            else:
                self._mostrar_error(msg)
        
        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="✅ Guardar",
            fg_color=config.COLORS["success"],
            hover_color="#0E9F6E",
            text_color=config.COLORS["text_light"],
            command=guardar,
            height=40,
            font=("Helvetica", 12, "bold")
        )
        btn_guardar.pack(side="left", padx=5, fill="both", expand=True)
        
        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            fg_color="#6B7280",
            hover_color="#4B5563",
            text_color=config.COLORS["text_light"],
            command=ventana.destroy,
            height=40,
            font=("Helvetica", 12, "bold")
        )
        btn_cancelar.pack(side="left", padx=5, fill="both", expand=True)
    
    def _eliminar_cliente(self, cliente_id):
        """Eliminar cliente con confirmación"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Confirmar Eliminación")
        ventana.geometry("400x200")
        ventana.resizable(False, False)
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
