"""
Página: Gestión de Mesas - Diseño Grid Visual React
"""
import customtkinter as ctk
from controllers.mesas_controller import MesasController
from controllers.clientes_controller import ClientesController
from views.components.dialog_utils import DialogUtils
import config
import datetime 

class MesasPage(ctk.CTkFrame):
    """Módulo de Mesas con Grid Visual"""
    
    def __init__(self, parent, **kwargs):
            super().__init__(parent, fg_color="#F3F4F6", **kwargs)
            
            self.controller = MesasController()
            self.controller_clientes = ClientesController()
            self.mesa_seleccionada = None
            self.grid_frame = None
            self.mesa_cards = {}
            self.mesa_pedido_actual = {}
            self.carrito_actual = {}
            
            # Crear cliente genérico
            self.cliente_generico = self._crear_cliente_generico_global()
            
            self._crear_ui()
            self.after(100, self.refrescar_tabla)

    def _crear_cliente_generico_global(self):
        """Crear un cliente genérico global para todos los pedidos"""
        from controllers.clientes_controller import ClientesController
        
        controller_clientes = ClientesController()
        
        try:
            # Buscar si ya existe
            success, clientes, _ = controller_clientes.obtener_todos_clientes()
            if success and clientes:
                for cliente in clientes:
                    if hasattr(cliente, 'nombre') and cliente.nombre == "CLIENTE_GENERICO":
                        print(f"✓ Cliente genérico ya existe: ID {cliente.id}")
                        return cliente
            
            # Crear cliente genérico
            print("📝 Creando cliente genérico...")
            success, nuevo_cliente, msg = controller_clientes.crear_cliente(
                cedula="9999999999",
                nombre="CLIENTE_GENERICO",
                apellido="Sistema",
                telefono="0000000000",
                direccion="Pedidos sin cliente",
                correo="sistema@restaurante.com"
            )
            
            if success:
                print(f"✓ Cliente genérico creado: ID {nuevo_cliente.id}")
                return nuevo_cliente
            else:
                print(f"❌ Error al crear cliente genérico: {msg}")
                return None
                
        except Exception as e:
            print(f"❌ Error en _crear_cliente_generico_global: {e}")
            return None
   
    def _crear_ui(self):
            """Crear interfaz"""
            # === HEADER ===
            frame_header = ctk.CTkFrame(self, fg_color="#EA580C", height=80)
            frame_header.pack(side="top", fill="x")
            frame_header.pack_propagate(False)
            
            frame_header_content = ctk.CTkFrame(frame_header, fg_color="transparent")
            frame_header_content.pack(fill="both", expand=True, padx=30, pady=15)
            
            # Título
            frame_titulo = ctk.CTkFrame(frame_header_content, fg_color="transparent")
            frame_titulo.pack(side="left")
            
            titulo = ctk.CTkLabel(
                frame_titulo,
                text="🗺️ Mapa de Mesas",
                text_color="white",
                font=("Helvetica", 28, "bold")
            )
            titulo.pack(anchor="w")
            
            subtitulo = ctk.CTkLabel(
                frame_titulo,
                text="Gestiona el estado de las mesas y crea nuevos pedidos",
                text_color="#FFEDD5",
                font=("Helvetica", 11)
            )
            subtitulo.pack(anchor="w", pady=(3, 0))
            
            # Botón Nueva Mesa
            btn_nueva = ctk.CTkButton(
                frame_header_content,
                text="➕ Nueva Mesa",
                command=self.crear_mesa,
                fg_color="#10B981",
                hover_color="#059669",
                text_color="white",
                font=("Helvetica", 12, "bold"),
                height=40,
                width=120
            )
            btn_nueva.pack(side="right")
            
            # === CONTENIDO PRINCIPAL SCROLLABLE ===
            self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
            self.scroll_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Grid para mesas
            self.grid_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            self.grid_frame.pack(fill="both", expand=True)
        
    def refrescar_tabla(self):
        """Refrescar grid de mesas"""
        # Limpiar grid anterior
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.mesa_cards = {}
        
        # Obtener todas las mesas
        success, mesas, msg = self.controller.obtener_todas_mesas()
        if not success or not mesas:
            label_vacio = ctk.CTkLabel(
                self.grid_frame,
                text="No hay mesas disponibles",
                text_color=config.COLORS["text_dark"],
                font=("Helvetica", 14)
            )
            label_vacio.pack(pady=40)
            return
        
        # Crear grid de 4 columnas
        columnas = 4
        for idx, mesa in enumerate(mesas):
            row = idx // columnas
            col = idx % columnas
            self._crear_card_mesa(mesa, row, col)
    
    def _crear_card_mesa(self, mesa, row, col):
        """Crear tarjeta visual para una mesa"""
        # Determinar colores según estado
        if mesa.estado.value == "libre":
            color_fondo = config.COLORS["mesa_libre"]
            color_borde = "#86EFAC"
            color_texto = config.COLORS["texto_libre"]
        elif mesa.estado.value == "ocupada":
            color_fondo = config.COLORS["mesa_ocupada"]
            color_borde = "#FECACA"
            color_texto = config.COLORS["texto_ocupada"]
        elif mesa.estado.value == "reservada":
            color_fondo = config.COLORS["mesa_reservada"]
            color_borde = "#FCD34D"
            color_texto = config.COLORS["texto_reservada"]
        else:
            color_fondo = "#F3F4F6"
            color_borde = "#D1D5DB"
            color_texto = "#6B7280"
        
        # Crear grid con columnas de igual ancho
        if row == 0 and col == 0:
            for c in range(4):
                self.grid_frame.grid_columnconfigure(c, weight=1)
        
        # Frame de la tarjeta
        card_frame = ctk.CTkFrame(
            self.grid_frame,
            fg_color=color_fondo,
            border_width=2,
            border_color=color_borde,
            cursor="hand2"  # Cambiar cursor a mano para indicar que es clickeable
        )
        card_frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        # Crear función de click para toda la tarjeta
        def on_card_click(event=None):
            self._on_mesa_click(mesa)
        
        # Bindear click en el frame principal
        card_frame.bind("<Button-1>", on_card_click)
        
        # Contenido de la tarjeta
        frame_content = ctk.CTkFrame(card_frame, fg_color="transparent")
        frame_content.pack(fill="both", expand=True, padx=15, pady=15)
        # Hacer clickeable también el frame de contenido
        frame_content.bind("<Button-1>", on_card_click)
        
        # === NÚMERO EN CÍRCULO ===
        circle_frame = ctk.CTkFrame(frame_content, fg_color="white", width=70, height=70)
        circle_frame.pack(pady=(0, 10))
        circle_frame.pack_propagate(False)
        # Hacer clickeable el círculo
        circle_frame.bind("<Button-1>", on_card_click)
        
        label_numero = ctk.CTkLabel(
            circle_frame,
            text=str(mesa.numero),
            text_color="#1F2937",
            font=("Helvetica", 24, "bold")
        )
        label_numero.pack(expand=True)
        # Hacer clickeable el número
        label_numero.bind("<Button-1>", on_card_click)
        
        # === ESTADO ===
        label_estado = ctk.CTkLabel(
            frame_content,
            text=mesa.estado.value.capitalize(),
            text_color=color_texto,
            font=("Helvetica", 13, "bold")
        )
        label_estado.pack(pady=5)
        # Hacer clickeable el estado
        label_estado.bind("<Button-1>", on_card_click)
        
        # === CAPACIDAD CON ICONO ===
        frame_capacidad = ctk.CTkFrame(frame_content, fg_color="transparent")
        frame_capacidad.pack(pady=(5, 0))
        # Hacer clickeable el frame de capacidad
        frame_capacidad.bind("<Button-1>", on_card_click)
        
        label_capacidad = ctk.CTkLabel(
            frame_capacidad,
            text=f"👥 {mesa.capacidad} personas",
            text_color="#6B7280",
            font=("Helvetica", 11)
        )
        label_capacidad.pack()
        # Hacer clickeable la etiqueta de capacidad
        label_capacidad.bind("<Button-1>", on_card_click)
        
        # Almacenar referencia
        self.mesa_cards[mesa.id] = {
            'frame': card_frame,
            'mesa': mesa,
            'color_original': (color_fondo, color_borde)
        }
        
        # Añadir efecto hover
        card_frame.bind("<Enter>", lambda e: self._on_hover_enter(mesa.id))
        card_frame.bind("<Leave>", lambda e: self._on_hover_leave(mesa.id))

    def _on_hover_enter(self, mesa_id):
        """Efecto hover al pasar ratón"""
        if mesa_id not in self.mesa_cards:
            return
        card_data = self.mesa_cards[mesa_id]
        card_frame = card_data['frame']
        
        # Oscurecer ligeramente el color
        card_frame.configure(
            border_color="#EA580C"
        )
        card_frame.configure(border_width=3)
    
    def _on_hover_leave(self, mesa_id):
        """Restaurar color original"""
        if mesa_id not in self.mesa_cards:
            return
        card_data = self.mesa_cards[mesa_id]
        card_frame = card_data['frame']
        color_fondo, color_borde = card_data['color_original']
        
        card_frame.configure(
            border_color=color_borde,
            border_width=2
        )
    
    def _on_mesa_click(self, mesa):
        """Click en una mesa"""
        self.mesa_seleccionada = mesa
        
        if mesa.estado.value.lower() == "libre":
            self._mostrar_nuevo_pedido(mesa)
        else:
            self._mostrar_detalles_mesa(mesa)
    
    def _mostrar_detalles_mesa(self, mesa):
        """Mostrar diálogo con detalles de la mesa con estilo moderno"""
        dialog = ctk.CTkToplevel()
        dialog.title(f"Detalles - Mesa {mesa.numero}")
        dialog.geometry("400x520")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        dialog.configure(fg_color="#F3F4F6") # Fondo claro estilo React

        # === HEADER NARANJA (Consistente con Crear Mesa) ===
        header_frame = ctk.CTkFrame(dialog, fg_color="#EA580C", corner_radius=15, height=120)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)

        ctk.CTkLabel(header_frame, text="📋", font=("Helvetica", 40)).pack(pady=(10, 0))
        ctk.CTkLabel(
            header_frame, 
            text=f"Mesa {mesa.numero}", 
            text_color="white", 
            font=("Helvetica", 22, "bold")
        ).pack()

        # === CUERPO DE INFORMACIÓN ===
        body_frame = ctk.CTkFrame(dialog, fg_color="white", corner_radius=15)
        body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Determinar color según estado para el texto
        estado_map = {
            "libre": {"color": "#10B981", "icon": "🟢"},
            "ocupada": {"color": "#EF4444", "icon": "🔴"},
            "reservada": {"color": "#F59E0B", "icon": "🟠"}
        }
        info_estado = estado_map.get(mesa.estado.value.lower(), {"color": "#6B7280", "icon": "⚪"})

        # --- Card de Estado ---
        label_est_title = ctk.CTkLabel(body_frame, text="Estado Actual", font=("Helvetica", 12, "bold"), text_color="#374151")
        label_est_title.pack(anchor="w", padx=25, pady=(20, 0))
        
        estado_display = ctk.CTkLabel(
            body_frame, 
            text=f"{info_estado['icon']} {mesa.estado.value.capitalize()}",
            font=("Helvetica", 16, "bold"),
            text_color=info_estado['color'],
            fg_color="#F9FAFB",
            height=45,
            corner_radius=8
        )
        estado_display.pack(fill="x", padx=20, pady=5)

        # --- Card de Capacidad ---
        label_cap_title = ctk.CTkLabel(body_frame, text="Capacidad de Mesa", font=("Helvetica", 12, "bold"), text_color="#374151")
        label_cap_title.pack(anchor="w", padx=25, pady=(15, 0))
        
        capacidad_display = ctk.CTkLabel(
            body_frame, 
            text=f"👥 {mesa.capacidad} Personas",
            font=("Helvetica", 14),
            text_color="#4B5563",
            fg_color="#F9FAFB",
            height=40,
            corner_radius=8
        )
        capacidad_display.pack(fill="x", padx=20, pady=5)

        # === BOTONES DE ACCIÓN ===
        acciones_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        acciones_frame.pack(fill="x", padx=20, pady=(10, 20))

        if mesa.estado.value.lower() in ["ocupada", "reservada"]:
            # Botón Agregar Platos (Naranja)
            btn_agregar = ctk.CTkButton(
                acciones_frame,
                text="➕ Agregar Platos",
                command=lambda: self._agregar_platos_pedido_existente(mesa),
                fg_color="#EA580C",
                hover_color="#C2410C",
                text_color="white",
                font=("Helvetica", 13, "bold"),
                height=45
            )
            btn_agregar.pack(fill="x", pady=5)
            
            # Botón Liberar (Rojo suave)
            btn_liberar = ctk.CTkButton(
                acciones_frame,
                text="🔓 Liberar Mesa",
                command=lambda: self._liberar_mesa(mesa, dialog),
                fg_color="#FEE2E2",
                hover_color="#FCA5A5",
                text_color="#DC2626",
                font=("Helvetica", 13, "bold"),
                height=45
            )
            btn_liberar.pack(fill="x", pady=5)
        
        # Botón Cerrar siempre visible
        btn_cerrar = ctk.CTkButton(
            acciones_frame,
            text="Cerrar",
            command=dialog.destroy,
            fg_color="transparent",
            text_color="#6B7280",
            hover_color="#E5E7EB",
            height=35
        )
        btn_cerrar.pack(fill="x", pady=(5, 0))
        
    def _liberar_mesa(self, mesa, dialog):
        """Liberar una mesa - solo cambiar estado, mantener cliente genérico"""
        success, _, msg = self.controller.liberar_mesa(mesa.id)
        if success:
            # Limpiar referencia local del pedido
            if hasattr(self, 'mesa_pedido_actual') and mesa.id in self.mesa_pedido_actual:
                del self.mesa_pedido_actual[mesa.id]
            
            DialogUtils.mostrar_exito("Éxito", "Mesa liberada correctamente")
            dialog.destroy()
            self.refrescar_tabla()
        else:
            DialogUtils.mostrar_error("Error", msg)
    
    def _mostrar_nuevo_pedido(self, mesa):
        """Mostrar dialog con sistema completo de nuevo pedido (React-like)"""
        from controllers.empleados_controller import EmpleadosController
        from controllers.platos_controller import PlatosController
        
        # Cargar datos
        controller_empleados = EmpleadosController()
        controller_platos = PlatosController()
        
        success_emp, meseros, _ = controller_empleados.obtener_meseros_activos()
        success_platos, platos, _ = controller_platos.obtener_platos_disponibles()
        
        if not success_platos or not platos:
            DialogUtils.mostrar_error("Error", "No hay platos disponibles")
            return
        
        # Crear dialog
        dialog = ctk.CTkToplevel()
        dialog.title(f"Nuevo Pedido - Mesa {mesa.numero}")
        dialog.geometry("900x550")
        dialog.resizable(True, True)
        dialog.attributes('-topmost', True)  # Mantener en el frente
        dialog.grab_set()  # Hacerla modal
        
        # === HEADER ===
        frame_header = ctk.CTkFrame(dialog, fg_color=config.COLORS["primary"], height=60)
        frame_header.pack(side="top", fill="x", padx=0, pady=0)
        frame_header.pack_propagate(False)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text=f"Nuevo Pedido - Mesa {mesa.numero}",
            text_color="white",
            font=("Helvetica", 20, "bold")
        )
        titulo.pack(side="left", padx=20, pady=15)
        
        # === CONTENIDO PRINCIPAL ===
        frame_main = ctk.CTkFrame(dialog, fg_color=config.COLORS["light_bg"])
        frame_main.pack(fill="both", expand=True, padx=0, pady=0)
        
        # === PANEL IZQUIERDO (Productos) ===
        frame_left = ctk.CTkFrame(frame_main, fg_color=config.COLORS["light_bg"])
        frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Selector de mesero
        label_mesero = ctk.CTkLabel(
            frame_left,
            text="👨‍💼 Selecciona un mesero:",
            text_color=config.COLORS["text_dark"],
            font=("Helvetica", 11, "bold")
        )
        label_mesero.pack(anchor="w", pady=(0, 8))
        
        mesero_labels = [m.nombre for m in meseros] if success_emp and meseros else ["No hay meseros"]
        combo_mesero = ctk.CTkComboBox(
            frame_left,
            values=mesero_labels,
            state="readonly",
            font=("Helvetica", 10)
        )
        combo_mesero.pack(fill="x", pady=(0, 15))
        if mesero_labels and mesero_labels[0] != "No hay meseros":
            combo_mesero.set(mesero_labels[0])
        
        # Variable para la categoría activa
        categoria_activa = ctk.StringVar(value="Entrada")
        
        # Obtener categorías únicas
        categorias = list(set([p.categoria.value for p in platos]))
        categorias.sort()
        
        # === TABS DE CATEGORÍAS ===
        frame_tabs = ctk.CTkFrame(frame_left, fg_color="transparent")
        frame_tabs.pack(fill="x", pady=(0, 15))
        
        # Botones de categorías
        for cat in categorias:
            btn = ctk.CTkButton(
                frame_tabs,
                text=cat,
                command=lambda c=cat: self._cambiar_categoria(c, categoria_activa, frame_productos, platos, carrito_items),
                fg_color=config.COLORS["primary"],
                hover_color="#D64B1E",
                text_color="white",
                font=("Helvetica", 10),
                height=32
            )
            btn.pack(side="left", padx=3, fill="x", expand=True)
        
        # === GRID DE PRODUCTOS ===
        frame_productos = ctk.CTkFrame(frame_left, fg_color="transparent")
        frame_productos.pack(fill="both", expand=True)
        
        # Carrito (diccionario para almacenar items)
        carrito_items = {}
        
        # Mostrar productos de la categoría inicial
        self._mostrar_productos_categoria("Entrada", frame_productos, platos, carrito_items)
        
        # === PANEL DERECHO (Carrito) ===
        frame_right = ctk.CTkFrame(frame_main, fg_color="#F9FAFB", width=300)
        frame_right.pack(side="right", fill="both", padx=10, pady=10)
        frame_right.pack_propagate(False)
        
        # Header del carrito
        frame_carrito_header = ctk.CTkFrame(frame_right, fg_color="transparent")
        frame_carrito_header.pack(fill="x", pady=(0, 15), side="top")
        
        label_carrito_titulo = ctk.CTkLabel(
            frame_carrito_header,
            text="🛒 Pedido",
            text_color=config.COLORS["text_dark"],
            font=("Helvetica", 14, "bold")
        )
        label_carrito_titulo.pack(anchor="w")
        
        # Frame contenedor para canvas y scrollbar
        frame_canvas_wrapper = ctk.CTkFrame(frame_right, fg_color="transparent")
        frame_canvas_wrapper.pack(fill="both", expand=True, side="top")
        
        # Frame scrollable para items del carrito
        self.canvas_carrito = ctk.CTkCanvas(
            frame_canvas_wrapper,
            bg="#F9FAFB",
            highlightthickness=0
        )
        scrollbar_carrito = ctk.CTkScrollbar(frame_canvas_wrapper, command=self.canvas_carrito.yview)
        self.frame_carrito_items = ctk.CTkFrame(
            self.canvas_carrito,
            fg_color="#F9FAFB"
        )
        
        self.frame_carrito_items.bind(
            "<Configure>",
            lambda e: self.canvas_carrito.configure(scrollregion=self.canvas_carrito.bbox("all"))
        )
        
        self.canvas_carrito.create_window((0, 0), window=self.frame_carrito_items, anchor="nw")
        self.canvas_carrito.configure(yscrollcommand=scrollbar_carrito.set)
        
        self.canvas_carrito.pack(side="left", fill="both", expand=True)
        scrollbar_carrito.pack(side="right", fill="y")
        
        # Footer del carrito
        frame_carrito_footer = ctk.CTkFrame(frame_right, fg_color="transparent")
        frame_carrito_footer.pack(fill="x", padx=0, pady=(15, 0), side="bottom")
        
        # Total
        frame_total = ctk.CTkFrame(frame_carrito_footer, fg_color="transparent")
        frame_total.pack(fill="x", pady=(15, 15), padx=0)
        
        # Línea separadora
        separador = ctk.CTkFrame(frame_carrito_footer, fg_color=config.COLORS["border"], height=1)
        separador.pack(fill="x", pady=(0, 12))
        
        label_total_texto = ctk.CTkLabel(
            frame_total,
            text="Total:",
            text_color=config.COLORS["text_dark"],
            font=("Helvetica", 12, "bold")
        )
        label_total_texto.pack(side="left")
        
        label_total_monto = ctk.CTkLabel(
            frame_total,
            text="$0.00",
            text_color=config.COLORS["primary"],
            font=("Helvetica", 16, "bold")
        )
        label_total_monto.pack(side="right")
        
        # Botones
        frame_acciones = ctk.CTkFrame(frame_carrito_footer, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=0, pady=0)
        
        def crear_pedido_final():
            self._procesar_nuevo_pedido(mesa, combo_mesero, carrito_items, meseros, dialog, label_total_monto)
        
        btn_crear = ctk.CTkButton(
            frame_acciones,
            text="✅ Crear Pedido",
            command=crear_pedido_final,
            fg_color=config.COLORS["success"],
            hover_color="#0E9F6E",
            text_color="white",
            font=("Helvetica", 12, "bold"),
            height=40
        )
        btn_crear.pack(fill="x", pady=(0, 8))
        
        btn_cancelar = ctk.CTkButton(
            frame_acciones,
            text="❌ Cancelar",
            command=dialog.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563",
            text_color="white",
            font=("Helvetica", 12, "bold"),
            height=40
        )
        btn_cancelar.pack(fill="x")
        
        # Almacenar referencias para actualizaciones
        self.carrito_actual = carrito_items
        self.label_total_actual = label_total_monto
        self.frame_carrito_actual = self.frame_carrito_items
        self.canvas_carrito_actual = self.canvas_carrito
        self.frame_productos_actual = frame_productos
    
    def _cambiar_categoria(self, categoria, categoria_var, frame_productos, platos, carrito_items):
        """Cambiar categoría de productos"""
        for widget in frame_productos.winfo_children():
            widget.destroy()
        
        self._mostrar_productos_categoria(categoria, frame_productos, platos, carrito_items)
    
    def _mostrar_productos_categoria(self, categoria, frame_productos, platos, carrito_items):
        """Mostrar grid de productos de una categoría"""
        # Limpiar frame anterior
        for widget in frame_productos.winfo_children():
            widget.destroy()
        
        # Filtrar platos por categoría
        platos_categoria = [p for p in platos if p.categoria.value == categoria]
        
        if not platos_categoria:
            label_vacio = ctk.CTkLabel(
                frame_productos,
                text=f"No hay platos en {categoria}",
                text_color=config.COLORS["text_dark"],
                font=("Helvetica", 12)
            )
            label_vacio.pack(pady=40)
            return
        
        # Canvas para scroll
        canvas = ctk.CTkCanvas(
            frame_productos,
            bg=config.COLORS["light_bg"],
            highlightthickness=0
        )
        scrollbar = ctk.CTkScrollbar(frame_productos, command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(
            canvas,
            fg_color=config.COLORS["light_bg"]
        )
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Agrupar platos de 2 en 2
        for idx in range(0, len(platos_categoria), 2):
            # Row frame para 2 columnas
            row_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=4, pady=4)
            
            # Primera columna
            plato_izq = platos_categoria[idx]
            self._crear_card_plato(row_frame, plato_izq, carrito_items)
            
            # Segunda columna (si existe)
            if idx + 1 < len(platos_categoria):
                plato_der = platos_categoria[idx + 1]
                self._crear_card_plato(row_frame, plato_der, carrito_items)
    
    def _crear_card_plato(self, parent, plato, carrito_items):
        """Crear un card interactivo para un plato"""
        # Card del producto como frame
        card_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            border_width=1,
            border_color=config.COLORS["border"],
            corner_radius=8
        )
        card_frame.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        
        # Función del click
        def on_click(event=None):
            self._agregar_al_carrito(plato, carrito_items)
        
        # Funciones para hover effect
        def on_enter(event=None):
            card_frame.configure(fg_color="#F3F4F6")
            card_frame.configure(border_color=config.COLORS["primary"])
            card_frame.configure(border_width=2)
        
        def on_leave(event=None):
            card_frame.configure(fg_color="white")
            card_frame.configure(border_color=config.COLORS["border"])
            card_frame.configure(border_width=1)
        
        # Bindear eventos de clic en el frame
        card_frame.bind("<Button-1>", on_click)
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Content dentro del frame
        content = ctk.CTkFrame(card_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Bindear también en el content para que funcione el click
        content.bind("<Button-1>", on_click)
        content.bind("<Enter>", on_enter)
        content.bind("<Leave>", on_leave)
        
        # Nombre
        name_label = ctk.CTkLabel(
            content,
            text=plato.nombre,
            text_color=config.COLORS["text_dark"],
            font=("Helvetica", 11, "bold"),
            wraplength=140
        )
        name_label.pack(anchor="w", pady=(0, 8))
        name_label.bind("<Button-1>", on_click)
        name_label.bind("<Enter>", on_enter)
        name_label.bind("<Leave>", on_leave)
        
        # Precio
        price_label = ctk.CTkLabel(
            content,
            text=f"${plato.precio:.2f}",
            text_color=config.COLORS["primary"],
            font=("Helvetica", 13, "bold")
        )
        price_label.pack(anchor="w")
        price_label.bind("<Button-1>", on_click)
        price_label.bind("<Enter>", on_enter)
        price_label.bind("<Leave>", on_leave)
    
    def _agregar_al_carrito(self, plato, carrito_items):
        """Agregar plato al carrito"""
        if plato.id in carrito_items:
            carrito_items[plato.id]['cantidad'] += 1
        else:
            carrito_items[plato.id] = {
                'plato': plato,
                'cantidad': 1
            }
        
        self._actualizar_carrito_visual(carrito_items)
    
    def _actualizar_carrito_visual(self, carrito_items):
        """Actualizar visualización del carrito"""
        # Limpiar carrito anterior
        for widget in self.frame_carrito_actual.winfo_children():
            widget.destroy()
        
        if not carrito_items:
            label_vacio = ctk.CTkLabel(
                self.frame_carrito_actual,
                text="Carrito vacío",
                text_color="#9CA3AF",
                font=("Helvetica", 11)
            )
            label_vacio.pack(pady=40)
            self.label_total_actual.configure(text="$0.00")
            return
        
        # Mostrar items
        total = 0
        for plato_id, item in carrito_items.items():
            plato = item['plato']
            cantidad = item['cantidad']
            subtotal = plato.precio * cantidad
            total += subtotal
            
            # Card del item
            item_card = ctk.CTkFrame(
                self.frame_carrito_actual,
                fg_color="white",
                border_width=1,
                border_color=config.COLORS["border"],
                corner_radius=6
            )
            item_card.pack(fill="x", pady=6, padx=0)
            
            # Content del item
            content = ctk.CTkFrame(item_card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=10, pady=8)
            
            # Nombre y precio unitario
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", pady=(0, 6))
            
            name_label = ctk.CTkLabel(
                header,
                text=plato.nombre,
                text_color=config.COLORS["text_dark"],
                font=("Helvetica", 10, "bold"),
                wraplength=200
            )
            name_label.pack(anchor="w", side="left")
            
            price_label = ctk.CTkLabel(
                header,
                text=f"${plato.precio:.2f}",
                text_color="#6B7280",
                font=("Helvetica", 9)
            )
            price_label.pack(anchor="e", side="right")
            
            # Controles cantidad y delete
            footer = ctk.CTkFrame(content, fg_color="transparent")
            footer.pack(fill="x")
            
            # Botones cantidad
            btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
            btn_frame.pack(side="left")
            
            btn_minus = ctk.CTkButton(
                btn_frame,
                text="−",
                command=lambda pid=plato_id: self._cambiar_cantidad(pid, -1, carrito_items),
                width=25,
                height=25,
                fg_color="#E5E7EB",
                text_color=config.COLORS["text_dark"],
                font=("Helvetica", 12, "bold")
            )
            btn_minus.pack(side="left", padx=2)
            
            qty_label = ctk.CTkLabel(
                btn_frame,
                text=str(cantidad),
                text_color=config.COLORS["text_dark"],
                font=("Helsinki", 10, "bold"),
                width=30
            )
            qty_label.pack(side="left", padx=3)
            
            btn_plus = ctk.CTkButton(
                btn_frame,
                text="+",
                command=lambda pid=plato_id: self._cambiar_cantidad(pid, 1, carrito_items),
                width=25,
                height=25,
                fg_color="#E5E7EB",
                text_color=config.COLORS["text_dark"],
                font=("Helvetica", 12, "bold")
            )
            btn_plus.pack(side="left", padx=2)
            
            # Botón delete
            btn_delete = ctk.CTkButton(
                footer,
                text="🗑️",
                command=lambda pid=plato_id: self._eliminar_del_carrito(pid, carrito_items),
                width=30,
                height=25,
                fg_color="#FEE2E2",
                text_color="#EF4444",
                font=("Helvetica", 10)
            )
            btn_delete.pack(side="right")
            
            # Subtotal
            subtotal_label = ctk.CTkLabel(
                footer,
                text=f"${subtotal:.2f}",
                text_color=config.COLORS["primary"],
                font=("Helvetica", 10, "bold")
            )
            subtotal_label.pack(side="right", padx=10)
        
        # Actualizar total
        self.label_total_actual.configure(text=f"${total:.2f}")
    
    def _cambiar_cantidad(self, plato_id, delta, carrito_items):
        """Cambiar cantidad de un item"""
        if plato_id not in carrito_items:
            return
        
        carrito_items[plato_id]['cantidad'] += delta
        
        if carrito_items[plato_id]['cantidad'] <= 0:
            del carrito_items[plato_id]
        
        self._actualizar_carrito_visual(carrito_items)
    
    def _eliminar_del_carrito(self, plato_id, carrito_items):
        """Eliminar item del carrito"""
        if plato_id in carrito_items:
            del carrito_items[plato_id]
        
        self._actualizar_carrito_visual(carrito_items)
  
    def _procesar_nuevo_pedido(self, mesa, combo_mesero, carrito_items, meseros, dialog, label_total):
        """Procesar y crear el nuevo pedido - Usando cliente genérico global"""
        from controllers.pedidos_controller import PedidosController
        
        # Validaciones
        if not combo_mesero.get() or combo_mesero.get() == "No hay meseros":
            DialogUtils.mostrar_error("Error", "Selecciona un mesero")
            return
        
        if not carrito_items:
            DialogUtils.mostrar_error("Error", "Agrega al menos un plato al pedido")
            return
        
        # Obtener ID del mesero seleccionado
        mesero_name = combo_mesero.get()
        mesero = next((m for m in meseros if m.nombre == mesero_name), None)
        if not mesero:
            DialogUtils.mostrar_error("Error", "Mesero no válido")
            return
        
        # Verificar que existe el cliente genérico
        if not self.cliente_generico:
            DialogUtils.mostrar_error("Error", "No se pudo crear el cliente genérico")
            return
        
        try:
            # Crear pedido con el cliente genérico global
            controller_pedidos = PedidosController()
            success, pedido, msg = controller_pedidos.crear_pedido(
                cliente_id=self.cliente_generico.id,  # Usar el cliente genérico
                mesa_id=mesa.id,
                empleado_id=mesero.id
            )
            
            if not success:
                DialogUtils.mostrar_error("Error", f"Error al crear pedido: {msg}")
                return
            
            # Agregar items al pedido
            for plato_id, item in carrito_items.items():
                success, _, msg = controller_pedidos.agregar_plato_pedido(
                    pedido.id,
                    plato_id,
                    item['cantidad']
                )
                
                if not success:
                    DialogUtils.mostrar_error("Error", f"Error al agregar plato: {msg}")
                    return
            
            # Actualizar estado de mesa a OCUPADA
            success, _, msg = self.controller.cambiar_estado_mesa(mesa.id, "ocupada")
            
            if not success:
                DialogUtils.mostrar_error("Error", f"Error al actualizar mesa: {msg}")
                return
            
            # Guardar referencia del pedido actual en la mesa
            if not hasattr(self, 'mesa_pedido_actual'):
                self.mesa_pedido_actual = {}
            self.mesa_pedido_actual[mesa.id] = pedido.id
            
            DialogUtils.mostrar_exito("Éxito", f"Pedido #{pedido.id} creado correctamente")
            dialog.destroy()
            self.refrescar_tabla()
        
        except Exception as e:
            print(f"ERROR DETALLADO: {str(e)}")
            import traceback
            traceback.print_exc()
            DialogUtils.mostrar_error("Error", f"Error: {str(e)}")

    def _crear_cliente_temporal(self, mesa, timestamp):
        """Crear un cliente temporal único para un pedido específico"""
        from controllers.clientes_controller import ClientesController
        
        controller_clientes = ClientesController()
        
        # Crear identificador único para este pedido
        fecha_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_cliente = f"MESA_{mesa.numero}_PED_{timestamp}"
        
        success, nuevo_cliente, msg = controller_clientes.crear_cliente(
            cedula=f"TEMP_{mesa.numero}_{timestamp}_{fecha_hora}",
            nombre=nombre_cliente,
            apellido=f"Pedido_{timestamp}",
            telefono="0000000000",
            direccion=f"Mesa {mesa.numero} - Pedido temporal",
            correo=f"mesa{mesa.numero}_pedido{timestamp}@temporal.com"
        )
        
        if success:
            return nuevo_cliente
        else:
            print(f"Error al crear cliente temporal: {msg}")
            return None
    
    def _obtener_o_crear_cliente_generico(self, mesa):
        """Obtener o crear un cliente genérico para la mesa"""
        from controllers.clientes_controller import ClientesController
        import datetime
        
        controller_clientes = ClientesController()
        
        # Buscar si ya existe un cliente genérico para esta mesa
        success, clientes, _ = controller_clientes.obtener_todos_clientes()
        
        if success and clientes:
            for cliente in clientes:
                # Buscar cliente con el patrón "MESA_X_TEMP"
                if hasattr(cliente, 'nombre') and cliente.nombre == f"MESA_{mesa.numero}_TEMP":
                    return cliente
        
        # Si no existe, crear cliente temporal
        timestamp = int(datetime.datetime.now().timestamp())
        success, nuevo_cliente, msg = controller_clientes.crear_cliente(
            cedula=f"TEMP_{mesa.numero}_{timestamp}",
            nombre=f"MESA_{mesa.numero}_TEMP",
            apellido="Temporal",
            telefono="0000000000",  # Teléfono por defecto
            direccion="Mesa temporal",
            correo=f"mesa{mesa.numero}@temporal.com"
        )
        
        if success:
            return nuevo_cliente
        else:
            print(f"Error al crear cliente temporal: {msg}")
            return None
        
    def crear_mesa(self):
        """Muestra el diálogo para crear una nueva mesa sin vista previa"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Mesa")
        dialog.geometry("400x500") # Más compacta al no tener preview
        dialog.resizable(False, False)
        dialog.grab_set() 
        dialog.configure(fg_color="#F3F4F6")

        # === HEADER NARANJA ===
        header_frame = ctk.CTkFrame(dialog, fg_color="#EA580C", corner_radius=15, height=140)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)

        ctk.CTkLabel(header_frame, text="🍴", font=("Helvetica", 45)).pack(pady=(15, 0))
        ctk.CTkLabel(
            header_frame, 
            text="Crear Nueva Mesa", 
            text_color="white", 
            font=("Helvetica", 20, "bold")
        ).pack()

        # === CUERPO DEL FORMULARIO ===
        body_frame = ctk.CTkFrame(dialog, fg_color="white", corner_radius=15)
        body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Entrada: Número de Mesa
        label_num = ctk.CTkLabel(body_frame, text="🔢 Número de Mesa", font=("Helvetica", 12, "bold"), text_color="#374151")
        label_num.pack(anchor="w", padx=25, pady=(20, 5))
        
        entry_numero = ctk.CTkEntry(
            body_frame, placeholder_text="Ej: 1, 2, 3...", 
            height=40, border_color="#D1D5DB", fg_color="#F9FAFB"
        )
        entry_numero.pack(fill="x", padx=25)
        
        # Entrada: Capacidad
        label_cap = ctk.CTkLabel(body_frame, text="👥 Capacidad", font=("Helvetica", 12, "bold"), text_color="#374151")
        label_cap.pack(anchor="w", padx=25, pady=(15, 5))
        
        entry_capacidad = ctk.CTkEntry(
            body_frame, placeholder_text="Ej: 2, 4, 6...", 
            height=40, border_color="#D1D5DB", fg_color="#F9FAFB"
        )
        entry_capacidad.pack(fill="x", padx=25)

        # === BOTONES DE ACCIÓN ===
        # Ajustamos el padding para que respire el diseño
        btn_save = ctk.CTkButton(
            dialog, text="✅ Guardar Mesa", fg_color="#EA580C", hover_color="#C2410C",
            height=45, font=("Helvetica", 13, "bold"),
            command=lambda: self._guardar_nueva_mesa(entry_numero.get(), entry_capacidad.get(), dialog)
        )
        btn_save.pack(fill="x", padx=20, pady=(20, 5))

        btn_cancel = ctk.CTkButton(
            dialog, text="Cancelar", fg_color="transparent", text_color="#4B5563",
            hover_color="#E5E7EB", height=40, 
            command=dialog.destroy
        )
        btn_cancel.pack(fill="x", padx=20, pady=(0, 20))

    def _guardar_nueva_mesa(self, numero, capacidad, dialog):
        """Lógica corregida para manejar el retorno del controlador"""
        if not numero or not capacidad:
            DialogUtils.mostrar_error("Error", "Todos los campos son obligatorios")
            return
        
        # CORRECCIÓN DEL ERROR: Añadimos una variable extra (mesa_result) 
        success, mesa_result, msg = self.controller.crear_mesa(numero, capacidad)
        
        if success:
            DialogUtils.mostrar_exito("Éxito", "Mesa creada correctamente")
            dialog.destroy()
            self.refrescar_tabla()
        else:
            DialogUtils.mostrar_error("Error", msg)

    def _agregar_platos_pedido_existente(self, mesa):
        """Agregar platos a un pedido existente"""
        from controllers.pedidos_controller import PedidosController
        from controllers.platos_controller import PlatosController
        
        controller_pedidos = PedidosController()
        
        # Obtener el pedido activo de la mesa
        success, pedido, msg = controller_pedidos.obtener_pedido_activo_mesa(mesa.id)
        
        if not success or not pedido:
            DialogUtils.mostrar_error("Error", "No hay un pedido activo en esta mesa")
            return
        
        # Cargar platos
        controller_platos = PlatosController()
        success_platos, platos, _ = controller_platos.obtener_platos_disponibles()
        
        if not success_platos or not platos:
            DialogUtils.mostrar_error("Error", "No hay platos disponibles")
            return
        
        # Crear dialog
        dialog = ctk.CTkToplevel()
        dialog.title(f"Agregar Platos - Mesa {mesa.numero}")
        dialog.geometry("900x550")
        dialog.resizable(True, True)
        dialog.attributes('-topmost', True)  # Mantener en el frente
        dialog.grab_set()  # Hacerla modal
        
        # === HEADER ===
        frame_header = ctk.CTkFrame(dialog, fg_color=config.COLORS["primary"], height=60)
        frame_header.pack(side="top", fill="x", padx=0, pady=0)
        frame_header.pack_propagate(False)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text=f"Agregar Platos - Mesa {mesa.numero}",
            text_color="white",
            font=("Helvetica", 20, "bold")
        )
        titulo.pack(side="left", padx=20, pady=15)
        
        # === CONTENIDO PRINCIPAL ===
        frame_main = ctk.CTkFrame(dialog, fg_color=config.COLORS["light_bg"])
        frame_main.pack(fill="both", expand=True, padx=0, pady=0)
        
        # === PANEL IZQUIERDO (Productos) ===
        frame_left = ctk.CTkFrame(frame_main, fg_color=config.COLORS["light_bg"])
        frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Obtener categorías
        categoria_activa = ctk.StringVar(value="Entrada")
        categorias = list(set([p.categoria.value for p in platos]))
        categorias.sort()
        
        # === TABS DE CATEGORÍAS ===
        frame_tabs = ctk.CTkFrame(frame_left, fg_color="transparent")
        frame_tabs.pack(fill="x", pady=(0, 15))
        
        # Carrito para esta operación
        carrito_items = {}
        
        # Botones de categorías
        for cat in categorias:
            btn = ctk.CTkButton(
                frame_tabs,
                text=cat,
                command=lambda c=cat: self._cambiar_categoria(c, categoria_activa, frame_productos, platos, carrito_items),
                fg_color=config.COLORS["primary"],
                hover_color="#D64B1E",
                text_color="white",
                font=("Helvetica", 10),
                height=32
            )
            btn.pack(side="left", padx=3, fill="x", expand=True)
        
        # === GRID DE PRODUCTOS ===
        frame_productos = ctk.CTkFrame(frame_left, fg_color="transparent")
        frame_productos.pack(fill="both", expand=True)
        
        # Mostrar productos de la categoría inicial
        self._mostrar_productos_categoria("Entrada", frame_productos, platos, carrito_items)
        
        # === PANEL DERECHO (Carrito) ===
        frame_right = ctk.CTkFrame(frame_main, fg_color="#F9FAFB", width=300)
        frame_right.pack(side="right", fill="both", padx=10, pady=10)
        frame_right.pack_propagate(False)
        
        # Header del carrito
        frame_carrito_header = ctk.CTkFrame(frame_right, fg_color="transparent")
        frame_carrito_header.pack(fill="x", pady=(0, 15), side="top")
        
        label_carrito_titulo = ctk.CTkLabel(
            frame_carrito_header,
            text="🛒 Agregar",
            text_color=config.COLORS["text_dark"],
            font=("Helvetica", 14, "bold")
        )
        label_carrito_titulo.pack(anchor="w")
        
        # Frame contenedor para canvas y scrollbar
        frame_canvas_wrapper = ctk.CTkFrame(frame_right, fg_color="transparent")
        frame_canvas_wrapper.pack(fill="both", expand=True, side="top")
        
        # Frame scrollable para items del carrito
        self.canvas_carrito = ctk.CTkCanvas(
            frame_canvas_wrapper,
            bg="#F9FAFB",
            highlightthickness=0
        )
        scrollbar_carrito = ctk.CTkScrollbar(frame_canvas_wrapper, command=self.canvas_carrito.yview)
        self.frame_carrito_items = ctk.CTkFrame(
            self.canvas_carrito,
            fg_color="#F9FAFB"
        )
        
        self.frame_carrito_items.bind(
            "<Configure>",
            lambda e: self.canvas_carrito.configure(scrollregion=self.canvas_carrito.bbox("all"))
        )
        
        self.canvas_carrito.create_window((0, 0), window=self.frame_carrito_items, anchor="nw")
        self.canvas_carrito.configure(yscrollcommand=scrollbar_carrito.set)
        
        self.canvas_carrito.pack(side="left", fill="both", expand=True)
        scrollbar_carrito.pack(side="right", fill="y")
        
        # Footer del carrito
        frame_carrito_footer = ctk.CTkFrame(frame_right, fg_color="transparent")
        frame_carrito_footer.pack(fill="x", padx=0, pady=(15, 0), side="bottom")
        
        # Total
        frame_total = ctk.CTkFrame(frame_carrito_footer, fg_color="transparent")
        frame_total.pack(fill="x", pady=(15, 15), padx=0)
        
        # Línea separadora
        separador = ctk.CTkFrame(frame_carrito_footer, fg_color=config.COLORS["border"], height=1)
        separador.pack(fill="x", pady=(0, 12))
        
        label_total_texto = ctk.CTkLabel(
            frame_total,
            text="Total:",
            text_color=config.COLORS["text_dark"],
            font=("Helvetica", 12, "bold")
        )
        label_total_texto.pack(side="left")
        
        label_total_monto = ctk.CTkLabel(
            frame_total,
            text="$0.00",
            text_color=config.COLORS["primary"],
            font=("Helvetica", 16, "bold")
        )
        label_total_monto.pack(side="right")
        
        # Botones
        frame_acciones = ctk.CTkFrame(frame_carrito_footer, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=0, pady=0)
        
        def agregar_platos_final():
            self._procesar_agregar_platos(pedido, carrito_items, dialog, label_total_monto)
        
        btn_agregar = ctk.CTkButton(
            frame_acciones,
            text="✅ Agregar Platos",
            command=agregar_platos_final,
            fg_color=config.COLORS["success"],
            hover_color="#0E9F6E",
            text_color="white",
            font=("Helvetica", 12, "bold"),
            height=40
        )
        btn_agregar.pack(fill="x", pady=(0, 8))
        
        btn_cancelar = ctk.CTkButton(
            frame_acciones,
            text="❌ Cancelar",
            command=dialog.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563",
            text_color="white",
            font=("Helvetica", 12, "bold"),
            height=40
        )
        btn_cancelar.pack(fill="x")
        
        # Almacenar referencias
        self.carrito_actual = carrito_items
        self.label_total_actual = label_total_monto
        self.frame_carrito_actual = self.frame_carrito_items
        self.canvas_carrito_actual = self.canvas_carrito
        self.frame_productos_actual = frame_productos
    
    def _procesar_agregar_platos(self, pedido, carrito_items, dialog, label_total):
        """Procesar y agregar platos a pedido existente"""
        from controllers.pedidos_controller import PedidosController
        
        # Validación
        if not carrito_items:
            DialogUtils.mostrar_error("Error", "Agrega al menos un plato")
            return
        
        try:
            controller_pedidos = PedidosController()
            
            # Agregar items al pedido existente
            for plato_id, item in carrito_items.items():
                success, _, msg = controller_pedidos.agregar_plato_pedido(
                    pedido.id,
                    plato_id,
                    item['cantidad']
                )
                
                if not success:
                    DialogUtils.mostrar_error("Error", f"Error al agregar plato: {msg}")
                    return
            
            DialogUtils.mostrar_exito("Éxito", "Platos agregados correctamente")
            dialog.destroy()
            self.refrescar_tabla()
        
        except Exception as e:
            print(f"ERROR DETALLADO: {str(e)}")
            import traceback
            traceback.print_exc()
            DialogUtils.mostrar_error("Error", f"Error: {str(e)}")
