"""
Página: Gestión de Menú (Platos)
"""
import customtkinter as ctk
from controllers.platos_controller import PlatosController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils, FormDialog
import config

class MenuPage(ctk.CTkFrame):
    """Módulo de Menú/Platos - Diseño Profesional"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color=config.COLORS["light_bg"])
        
        self.controller = PlatosController()
        self.tabla = None
        self.plato_seleccionado = None
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz estilo dashboard"""
        
        # ===== FRAME SCROLLABLE =====
        self.frame_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color=config.COLORS["light_bg"]
        )
        self.frame_scroll.pack(fill="both", expand=True)
        
        # ===== HEADER PROFESIONAL =====
        self._crear_header()
        
        # ===== MÉTRICAS PÚBLICAS =====
        self._crear_metricas()
        
        # ===== CONTENEDOR PRINCIPAL (Tabla + Panel) =====
        self._crear_contenedor_principal()
    
    def _crear_header(self):
        """Crear header estilo dashboard"""
        header = ctk.CTkFrame(
            self.frame_scroll, 
            fg_color=config.COLORS["primary"], 
            height=92
        )
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24, pady=14)
        
        # Título principal
        ctk.CTkLabel(
            header_content,
            text="🍖 MENÚ DE PLATOS",
            font=("Helvetica", 22, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(anchor="w", pady=(0, 4))
        
        # Subtítulo
        ctk.CTkLabel(
            header_content,
            text="Administra los platos y especialidades del restaurante",
            font=("Helvetica", 10),
            text_color=config.COLORS["text_light"]
        ).pack(anchor="w")
    
    def _crear_metricas(self):
        """Crear tarjetas de métricas"""
        container = ctk.CTkFrame(self.frame_scroll, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=10)
        
        success, platos, _ = self.controller.obtener_todos_platos_formateados()
        total_platos = len(platos) if success else 0
        
        # Contar platos por estado
        disponibles = sum(1 for p in platos if p[5] == "disponible") if success else 0
        no_disponibles = total_platos - disponibles if success else 0
        
        # Tres metric cards
        cards_data = [
            ("📋", "TOTAL PLATOS", str(total_platos), "en el sistema", config.COLORS["info"]),
            ("✓", "DISPONIBLES", str(disponibles), "listos para servir", config.COLORS["success"]),
            ("✕", "NO DISPONIBLES", str(no_disponibles), "sin stock", config.COLORS["danger"]),
        ]
        
        for i, (icon, titulo, valor, subtitulo, color) in enumerate(cards_data):
            self._crear_metric_card(container, icon, titulo, valor, subtitulo, color, i)
    
    def _crear_metric_card(self, parent, icon, title, value, subtitle, color, column):
        """Crear una tarjeta de métrica estilo dashboard"""
        card = ctk.CTkFrame(
            parent, 
            fg_color=config.COLORS["dark_bg"], 
            corner_radius=12,
            border_width=1,
            border_color=config.COLORS["border"]
        )
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)
        
        # Borde lateral izquierdo
        border = ctk.CTkFrame(card, fg_color=color, width=6, corner_radius=12)
        border.pack(side="left", fill="y")
        border.pack_propagate(False)
        
        # Contenido
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=14, pady=10)
        
        # Icono y título
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 6))
        
        ctk.CTkLabel(
            header_frame, 
            text=icon, 
            font=("Helvetica", 18), 
            text_color=color
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            header_frame, 
            text=title, 
            font=("Helvetica", 9, "bold"), 
            text_color=config.COLORS["secondary"]
        ).pack(side="left")
        
        # Valor principal
        ctk.CTkLabel(
            content, 
            text=value, 
            font=("Helvetica", 18, "bold"), 
            text_color=config.COLORS["text_dark"]
        ).pack(anchor="w", pady=(2, 1))
        
        # Subtítulo
        ctk.CTkLabel(
            content, 
            text=subtitle, 
            font=("Helvetica", 8), 
            text_color=config.COLORS["secondary"]
        ).pack(anchor="w")
    
    def _crear_contenedor_principal(self):
        """Crear contenedor con tabla y controles"""
        # Encabezado de sección
        section_header = ctk.CTkFrame(
            self.frame_scroll,
            fg_color="transparent"
        )
        section_header.pack(fill="x", padx=20, pady=(8, 8))

        ctk.CTkLabel(
            section_header,
            text="📌 Listado de Platos",
            font=("Helvetica", 13, "bold"),
            text_color=config.COLORS["text_dark"]
        ).pack(side="left")

        ctk.CTkLabel(
            section_header,
            text="Selecciona un plato y usa los botones de acción",
            font=("Helvetica", 9),
            text_color=config.COLORS["secondary"]
        ).pack(side="right")
        
        # Container principal
        main_container = ctk.CTkFrame(
            self.frame_scroll,
            fg_color=config.COLORS["dark_bg"],
            corner_radius=12,
            border_width=1,
            border_color=config.COLORS["border"]
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # ===== BARRA DE ACCIONES =====
        acciones_frame = ctk.CTkFrame(
            main_container,
            fg_color=config.COLORS["light_bg"],
            corner_radius=12,
            border_width=1,
            border_color=config.COLORS["border"]
        )
        acciones_frame.pack(fill="x", padx=14, pady=(14, 0))
        
        acciones_content = ctk.CTkFrame(acciones_frame, fg_color="transparent")
        acciones_content.pack(fill="x", padx=12, pady=8)
        
        btn_nuevo = ctk.CTkButton(
            acciones_content,
            text="➕ Nuevo Plato",
            command=self.crear_plato,
            fg_color=config.COLORS["success"],
            hover_color="#0e9f6e",
            font=("Helvetica", 11, "bold"),
            height=30,
            corner_radius=8,
            text_color=config.COLORS["text_light"]
        )
        btn_nuevo.pack(side="left", padx=5)
        
        btn_editar = ctk.CTkButton(
            acciones_content,
            text="✏️ Editar",
            command=self.editar_plato,
            fg_color=config.COLORS["warning"],
            hover_color="#e68900",
            font=("Helvetica", 11, "bold"),
            height=30,
            corner_radius=8,
            text_color=config.COLORS["text_light"]
        )
        btn_editar.pack(side="left", padx=5)
        
        btn_eliminar = ctk.CTkButton(
            acciones_content,
            text="🗑️ Eliminar",
            command=self.eliminar_plato,
            fg_color=config.COLORS["danger"],
            hover_color="#da190b",
            font=("Helvetica", 11, "bold"),
            height=30,
            corner_radius=8,
            text_color=config.COLORS["text_light"]
        )
        btn_eliminar.pack(side="left", padx=5)

        ctk.CTkLabel(
            acciones_content,
            text="Selecciona un plato en la tabla para habilitar acciones",
            font=("Helvetica", 9),
            text_color=config.COLORS["secondary"]
        ).pack(side="right", padx=6)

        # ===== CONTENIDO PRINCIPAL (TABLA + PANEL LATERAL) =====
        contenido = ctk.CTkFrame(main_container, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=14, pady=14)

        # ===== TABLA =====
        tabla_frame = ctk.CTkFrame(
            contenido,
            fg_color=config.COLORS["dark_bg"],
            corner_radius=10,
            border_width=1,
            border_color=config.COLORS["border"]
        )
        tabla_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=0)

        tabla_inner = ctk.CTkFrame(tabla_frame, fg_color="transparent")
        tabla_inner.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.tabla = TreeViewWidget(
            tabla_inner,
            columnas=["ID", "Nombre", "Precio", "Categoría", "T. Prep.", "Estado", "Ing."],
            altura=14,
            font_size=11,
            heading_font_size=11,
            row_height=30
        )
        self.tabla.pack(fill="both", expand=True)
        self.tabla.set_on_select(self._on_plato_select)

        # ===== PANEL DE INFORMACIÓN LATERAL =====
        self._crear_panel_informacion(contenido)
    
    def _crear_panel_informacion(self, parent):
        """Crear panel de información del plato"""
        # Panel lateral
        self.panel_info = ctk.CTkFrame(
            parent,
            fg_color=config.COLORS["dark_bg"],
            corner_radius=12,
            border_width=1,
            border_color=config.COLORS["border"]
        )
        self.panel_info.pack(side="right", fill="y", padx=0, pady=0)
        self.panel_info.configure(width=320)
        self.panel_info.pack_propagate(False)
        
        # Actualizar panel
        self._actualizar_panel()
    
    def _actualizar_panel(self):
        """Actualizar contenido del panel de información"""
        # Limpiar
        for widget in self.panel_info.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.panel_info, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(
            header,
            text="🧾 Plato",
            font=("Helvetica", 12, "bold"),
            text_color=config.COLORS["text_dark"]
        ).pack(side="left")
        
        if not self.plato_seleccionado:
            # Estado vacío
            empty_frame = ctk.CTkFrame(self.panel_info, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, padx=12, pady=10)
            
            ctk.CTkLabel(
                empty_frame,
                text="🍽️",
                font=("Helvetica", 22),
                text_color=config.COLORS["border"]
            ).pack(pady=(4, 4))

            ctk.CTkLabel(
                empty_frame,
                text="Selecciona un plato",
                font=("Helvetica", 11, "bold"),
                text_color=config.COLORS["secondary"]
            ).pack()

            ctk.CTkLabel(
                empty_frame,
                text="Selecciona una fila para editar o eliminar",
                font=("Helvetica", 9),
                text_color=config.COLORS["secondary"]
            ).pack(pady=(4, 0))
        else:
            # Datos del plato
            content = ctk.CTkFrame(self.panel_info, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=10, pady=6)
            
            # Lista compacta de información
            datos = [
                ("🔑", "ID", str(self.plato_seleccionado[0])),
                ("📝", "Nombre", self.plato_seleccionado[1]),
                ("💵", "Precio", self.plato_seleccionado[2]),
                ("🏷️", "Categoría", self.plato_seleccionado[3]),
                ("⏱️", "Tiempo Prep.", f"{self.plato_seleccionado[4]} min"),
                ("📊", "Estado", self.plato_seleccionado[5])
            ]
            
            for icono, etiqueta, valor in datos:
                item_frame = ctk.CTkFrame(
                    content,
                    fg_color=config.COLORS["light_bg"],
                    corner_radius=6,
                    border_width=1,
                    border_color=config.COLORS["border"]
                )
                item_frame.pack(fill="x", pady=3)

                label_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                label_frame.pack(anchor="w", padx=8, pady=(5, 0))
                
                ctk.CTkLabel(
                    label_frame,
                    text=icono,
                    font=("Helvetica", 11),
                    text_color=config.COLORS["primary"]
                ).pack(side="left", padx=(0, 5))
                
                ctk.CTkLabel(
                    label_frame,
                    text=etiqueta + ":",
                    font=("Helvetica", 9, "bold"),
                    text_color=config.COLORS["text_dark"]
                ).pack(side="left")
                
                ctk.CTkLabel(
                    item_frame,
                    text=valor,
                    font=("Helvetica", 9, "bold"),
                    text_color=config.COLORS["text_dark"]
                ).pack(anchor="w", pady=(2, 6), padx=(29, 0))
            
            # Botones
            btn_detalles = ctk.CTkButton(
                content,
                text="👁️ Detalles",
                command=self._ver_detalles_completos,
                fg_color=config.COLORS["secondary"],
                hover_color="#4B5563",
                text_color=config.COLORS["text_light"],
                font=("Helvetica", 9, "bold"),
                height=30,
                corner_radius=7
            )
            btn_detalles.pack(fill="x", pady=(8, 4))

            btn_acciones = ctk.CTkButton(
                content,
                text="✏️ Editar Seleccionado",
                command=self._abrir_acciones_plato,
                fg_color=config.COLORS["primary"],
                hover_color=config.COLORS["accent"],
                text_color=config.COLORS["text_light"],
                font=("Helvetica", 9, "bold"),
                height=30,
                corner_radius=7
            )
            btn_acciones.pack(fill="x", pady=(0, 2))
    
    def _on_plato_select(self, datos):
        """Cuando selecciona un plato"""
        self.plato_seleccionado = datos
        self._actualizar_panel()
    
    def _abrir_acciones_plato(self):
        """Abrir acciones desde el panel de información sin ventana emergente"""
        if not self.plato_seleccionado:
            DialogUtils.mostrar_advertencia("⚠️ Advertencia", "Selecciona un plato para continuar")
            return
        self.editar_plato()
    
    def _abrir_editar_desde_dialogo(self, datos):
        """Abre el formulario de edición desde el diálogo de acciones"""
        if not datos:
            DialogUtils.mostrar_advertencia("⚠️ Advertencia", "No se pudo obtener el plato seleccionado")
            return
        self.plato_seleccionado = datos
        self.editar_plato()
    
    def _abrir_eliminar_desde_dialogo(self, datos):
        """Abre el diálogo de confirmación de eliminación desde el diálogo de acciones"""
        if not datos:
            DialogUtils.mostrar_advertencia("⚠️ Advertencia", "No se pudo obtener el plato seleccionado")
            return
        self.plato_seleccionado = datos
        self.eliminar_plato()
    
    def _ver_detalles_completos(self):
        """Ver detalles completos del plato"""
        if not self.plato_seleccionado:
            return
        
        success, plato, msg = self.controller.obtener_plato(self.plato_seleccionado[0])
        
        if success and plato:
            detalles = f"""
PLATO: {plato.nombre}

ID: {plato.id}
Precio: ${plato.precio:.2f}
Categoría: {plato.categoria.value}
Descripción: {plato.descripcion or 'N/A'}
Tiempo de Preparación: {plato.tiempo_preparacion} minutos
Estado: {plato.estado.value}
URL Imagen: {plato.imagen_url or 'N/A'}
Ingredientes: {len(plato.ingredientes)}
            """
            DialogUtils.mostrar_exito("Detalles del Plato", detalles)
        else:
            DialogUtils.mostrar_error("Error", msg or "No se pudo obtener el plato")
    
    def refrescar_tabla(self):
        """Refrescar datos de la tabla"""
        success, datos, msg = self.controller.obtener_todos_platos_formateados()
        if success:
            self.tabla.limpiar()
            # Agregar filas guardando los datos completos para poder accederlos cuando se selecciona
            for dato in datos:
                self.tabla.agregar_fila(dato, id_datos=dato)
        else:
            DialogUtils.mostrar_error("Error", msg)
    
    def crear_plato(self):
        """Crear nuevo plato"""
        categorias = self.controller.obtener_categorias_disponibles()
        
        campos = {
            'nombre': {'label': 'Nombre del Plato', 'type': 'text'},
            'precio': {'label': 'Precio ($)', 'type': 'number'},
            'categoria': {'label': 'Categoría', 'type': 'dropdown', 'options': categorias},
            'descripcion': {'label': 'Descripción', 'type': 'textarea'},
            'tiempo_preparacion': {'label': 'Tiempo de Preparación (min)', 'type': 'number'}
        }
        
        def procesar(valores):
            if not valores.get('nombre'):
                DialogUtils.mostrar_advertencia("Advertencia", "El nombre es obligatorio")
                return
            if not valores.get('precio'):
                DialogUtils.mostrar_advertencia("Advertencia", "El precio es obligatorio")
                return
            
            # Manejo seguro de conversiones
            try:
                precio = float(valores.get('precio') or 0)
                tiempo = int(valores.get('tiempo_preparacion') or 15)
            except (ValueError, TypeError):
                DialogUtils.mostrar_advertencia("Advertencia", "Verifica que precio y tiempo sean números válidos")
                return
            
            success, plato, msg = self.controller.crear_plato(
                valores.get('nombre'),
                precio,
                valores.get('categoria'),
                valores.get('descripcion'),
                tiempo
            )
            
            if success:
                DialogUtils.mostrar_exito("✅ Éxito", "Plato creado correctamente")
                self.refrescar_tabla()
                self.plato_seleccionado = None
                self._actualizar_panel()
            else:
                DialogUtils.mostrar_error("❌ Error", msg)
        
        FormDialog(self.winfo_toplevel(), "Crear Nuevo Plato", campos, procesar)
    
    def editar_plato(self):
        """Editar plato seleccionado"""
        if not self.plato_seleccionado:
            DialogUtils.mostrar_advertencia("⚠️ Advertencia", "Selecciona un plato para editar")
            return
        
        success, plato, msg = self.controller.obtener_plato(self.plato_seleccionado[0])
        
        if not success or not plato:
            DialogUtils.mostrar_error("❌ Error", msg or "No se pudo obtener el plato")
            return
        
        categorias = self.controller.obtener_categorias_disponibles()
        
        campos = {
            'nombre': {'label': 'Nombre del Plato', 'type': 'text', 'value': plato.nombre},
            'precio': {'label': 'Precio ($)', 'type': 'number', 'value': str(plato.precio)},
            'categoria': {'label': 'Categoría', 'type': 'dropdown', 'options': categorias, 'value': plato.categoria.value},
            'descripcion': {'label': 'Descripción', 'type': 'textarea', 'value': plato.descripcion or ''},
            'tiempo_preparacion': {'label': 'Tiempo de Preparación (min)', 'type': 'number', 'value': str(plato.tiempo_preparacion)}
        }
        
        def procesar(valores):
            if not valores.get('nombre'):
                DialogUtils.mostrar_advertencia("Advertencia", "El nombre es obligatorio")
                return
            if not valores.get('precio'):
                DialogUtils.mostrar_advertencia("Advertencia", "El precio es obligatorio")
                return
            
            # Manejo seguro de conversiones
            try:
                precio = float(valores.get('precio') or 0)
                tiempo = int(valores.get('tiempo_preparacion') or 15)
            except (ValueError, TypeError):
                DialogUtils.mostrar_advertencia("Advertencia", "Verifica que precio y tiempo sean números válidos")
                return
            
            success, plato_actualizado, msg = self.controller.actualizar_plato(
                self.plato_seleccionado[0],
                valores.get('nombre'),
                precio,
                valores.get('categoria'),
                valores.get('descripcion'),
                tiempo
            )
            
            if success:
                DialogUtils.mostrar_exito("✅ Éxito", "Plato actualizado correctamente")
                self.refrescar_tabla()
                self.plato_seleccionado = None
                self._actualizar_panel()
            else:
                DialogUtils.mostrar_error("❌ Error", msg)
        
        FormDialog(self.winfo_toplevel(), "Editar Plato", campos, procesar)
    
    def eliminar_plato(self):
        """Eliminar plato seleccionado"""
        if not self.plato_seleccionado:
            DialogUtils.mostrar_advertencia("⚠️ Advertencia", "Selecciona un plato para eliminar")
            return
        
        nombre_plato = self.plato_seleccionado[1]
        
        if DialogUtils.pedir_confirmacion(
            "🗑️ Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar el plato '{nombre_plato}'?\n\nEsta acción no se puede deshacer."
        ):
            success, _, msg = self.controller.eliminar_plato(self.plato_seleccionado[0])
            
            if success:
                DialogUtils.mostrar_exito("✅ Éxito", "Plato eliminado correctamente")
                self.plato_seleccionado = None
                self.refrescar_tabla()
                self._actualizar_panel()
            else:
                DialogUtils.mostrar_error("❌ Error", msg)
