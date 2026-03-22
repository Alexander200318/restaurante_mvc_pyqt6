"""
Página: Gestión de Menú (Platos)
"""
import customtkinter as ctk
from controllers.platos_controller import PlatosController
from controllers.ingredientes_controller import IngredientesController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils, FormDialog
import config

class PlatoFormDialog(ctk.CTkToplevel):
    """Diálogo específico para Platos con gestión de Ingredientes"""
    def __init__(self, parent, titulo, plato_controller, ingredientes_controller, plato_data=None, on_success=None):
        super().__init__(parent)
        self.controller = plato_controller
        self.ing_controller = ingredientes_controller
        self.plato_data = plato_data
        self.on_success = on_success
        
        # Estado local de ingredientes: Lista de dicts {'id', 'nombre', 'cantidad', 'unidad'}
        self.ingredientes_actuales = [] 
        
        # Cargar ingredientes si es edición
        if self.plato_data:
            success, ings, _ = self.controller.obtener_ingredientes_plato_completo(self.plato_data.id)
            if success:
                self.ingredientes_actuales = ings

        # Configuración ventana
        self.title(titulo)
        self.geometry("950x650")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        
        self.attributes('-topmost', True)
        
        # Layout Principal (Grid 2 columnas)
        self.grid_columnconfigure(0, weight=1) # Info Plato
        self.grid_columnconfigure(1, weight=1) # Ingredientes
        self.grid_rowconfigure(1, weight=1)    # Contenido expandible
        
        # Header
        header = ctk.CTkLabel(
            self, text=titulo, font=("Segoe UI", 20, "bold"), text_color="#1F2937"
        )
        header.grid(row=0, column=0, columnspan=2, pady=20, padx=20, sticky="w")
        
        # --- COLUMNA IZQUIERDA: DATOS DEL PLATO ---
        self.frame_datos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_datos.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self._crear_campos_plato()
        
        # --- COLUMNA DERECHA: INGREDIENTES ---
        self.frame_ingredientes = ctk.CTkFrame(self, fg_color="#F9FAFB", corner_radius=10) # Fondo gris muy claro
        self.frame_ingredientes.grid(row=1, column=1, sticky="nsew", padx=20, pady=(0, 20))
        
        self._crear_gestion_ingredientes()
        
        # --- FOOTER: BOTONES ---
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.frame_botones.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        btn_cancelar = ctk.CTkButton(
            self.frame_botones, text="Cancelar", command=self.destroy,
            fg_color="transparent", border_width=1, border_color="#D1D5DB", text_color="#374151"
        )
        btn_cancelar.pack(side="right", padx=10)
        
        btn_guardar = ctk.CTkButton(
            self.frame_botones, text="Guardar Todo", command=self._guardar,
            fg_color=config.COLORS["success"], text_color="white", font=("Segoe UI", 13, "bold")
        )
        btn_guardar.pack(side="right")
        
        # Estado inicial componentes según categoría
        if 'categoria' in self.vars:
            self._on_categoria_change(self.vars['categoria'].get())

        # Centrar
        self.update()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
        except: pass
        self.grab_set()

    def _on_categoria_change(self, choice):
        """Habilita o deshabilita la sección de ingredientes según la categoría"""
        state = "normal"
        if choice == config.PlatoCategoría.PRODUCTO.value:
            state = "disabled"
            # Limpiar ingredientes si se cambia a producto
            self.ingredientes_actuales = []
            if hasattr(self, 'lista_scroll'):
                self._renderizar_lista_ingredientes()
        
        # Habilitar/Deshabilitar widgets de ingredientes
        try:
            self.combo_ing.configure(state=state)
            self.entry_cantidad.configure(state=state)
            self.btn_add.configure(state=state)
            
            # También deshabilitar botones de eliminar en la lista
            for widget in self.lista_scroll.winfo_children():
                # El frame row contiene label y botón
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkButton):
                            child.configure(state=state)
        except AttributeError:
            pass # Los widgets aún no existen

    def _crear_campos_plato(self):
        self.vars = {}
        self.error_labels = {} 
        
        # Valores por defecto
        d = {
            'nombre': self.plato_data.nombre if self.plato_data else "",
            'precio': str(self.plato_data.precio) if self.plato_data else "",
            'descripcion': self.plato_data.descripcion if self.plato_data else "",
            'tiempo': str(self.plato_data.tiempo_preparacion) if self.plato_data else "15",
            'categoria': self.plato_data.categoria.value if self.plato_data else None,
            'disponible': (self.plato_data.estado.value == "disponible") if self.plato_data else True
        }
        
        categorias = self.controller.obtener_categorias_disponibles()
        
        # --- Helper UI ---
        # Definir el grid layout weights
        self.frame_datos.columnconfigure(0, weight=1)
        self.frame_datos.columnconfigure(1, weight=1)

        def create_entry(label, col, row, key, default_val, placeholder="", width=None, colspan=1):
            lbl = ctk.CTkLabel(self.frame_datos, text=label, font=("Segoe UI", 12, "bold"), text_color="#374151", anchor="w")
            lbl.grid(row=row, column=col, sticky="w", padx=10, pady=(10, 0), columnspan=colspan)
            
            entry = ctk.CTkEntry(self.frame_datos, height=35, fg_color="#F3F4F6", text_color="#1F2937", border_color="#D1D5DB", placeholder_text=placeholder)
            if width: entry.configure(width=width)
            if default_val: entry.insert(0, str(default_val))
            entry.grid(row=row+1, column=col, sticky="ew", padx=10, pady=(5, 0), columnspan=colspan)
            
            self.vars[key] = entry
            
            err = ctk.CTkLabel(self.frame_datos, text="", text_color="red", font=("Segoe UI", 10), anchor="w", height=15)
            err.grid(row=row+2, column=col, sticky="ew", padx=10, columnspan=colspan)
            self.error_labels[key] = err

        # 1. Nombre (Full width)
        create_entry("Nombre del Plato", 0, 0, 'nombre', d['nombre'], colspan=2)

        # 2. Precio (Left) y Tiempo (Right)
        create_entry("Precio ($)", 0, 3, 'precio', d['precio'], placeholder="0.00")
        create_entry("Tiempo de Preparación (min)", 1, 3, 'tiempo', d['tiempo'], placeholder="15")

        # 3. Categoría (Left) - Row 6
        lbl_cat = ctk.CTkLabel(self.frame_datos, text="Categoría", font=("Segoe UI", 12, "bold"), text_color="#374151", anchor="w")
        lbl_cat.grid(row=6, column=0, sticky="w", padx=10, pady=(10, 0))
        
        combo_cat = ctk.CTkComboBox(self.frame_datos, values=categorias, height=35, fg_color="#F3F4F6", text_color="#1F2937", border_color="#D1D5DB", button_color="#2563EB", dropdown_hover_color="#3B82F6", command=self._on_categoria_change)
        if d['categoria']: combo_cat.set(d['categoria'])
        elif categorias: combo_cat.set(categorias[0])
        combo_cat.grid(row=7, column=0, sticky="ew", padx=10, pady=(5, 0))
        self.vars['categoria'] = combo_cat
        
        err_cat = ctk.CTkLabel(self.frame_datos, text="", text_color="red", font=("Segoe UI", 10), anchor="w", height=15)
        err_cat.grid(row=8, column=0, sticky="ew", padx=10)
        self.error_labels['categoria'] = err_cat


        # 4. Disponibilidad (Switch - Right) - Row 6
        lbl_disp = ctk.CTkLabel(self.frame_datos, text="Estado del Plato", font=("Segoe UI", 12, "bold"), text_color="#374151")
        lbl_disp.grid(row=6, column=1, sticky="w", padx=10, pady=(10, 0))
        
        switch_fr = ctk.CTkFrame(self.frame_datos, fg_color="transparent", height=35)
        switch_fr.grid(row=7, column=1, sticky="w", padx=10, pady=(5, 0))
        
        s_disp = ctk.CTkSwitch(switch_fr, text="Disponible", onvalue=True, offvalue=False, progress_color="#10B981")
        if d['disponible']: s_disp.select()
        else: s_disp.deselect()
        s_disp.pack(side="left", pady=5)
        self.vars['disponible'] = s_disp

        # 5. Descripción (Full width, Bigger) - Row 9
        lbl_desc = ctk.CTkLabel(self.frame_datos, text="Descripción del Plato", font=("Segoe UI", 12, "bold"), text_color="#374151")
        lbl_desc.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
        
        txt_desc = ctk.CTkTextbox(self.frame_datos, height=150, fg_color="#F3F4F6", text_color="#1F2937", border_color="#D1D5DB", font=("Segoe UI", 12))
        if d['descripcion']: txt_desc.insert("1.0", d['descripcion'])
        txt_desc.grid(row=10, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5, 0))
        self.vars['descripcion'] = txt_desc
        
        err_desc = ctk.CTkLabel(self.frame_datos, text="", text_color="red", font=("Segoe UI", 10), anchor="w", height=15)
        err_desc.grid(row=11, column=0, columnspan=2, sticky="ew", padx=10)
        self.error_labels['descripcion'] = err_desc



    def _crear_gestion_ingredientes(self):
        # Título sección
        ctk.CTkLabel(
            self.frame_ingredientes, text="Ingredientes de la Receta", 
            font=("Segoe UI", 14, "bold"), text_color="#1F2937"
        ).pack(pady=15, padx=15, anchor="w")
        
        # --- SELECTOR ---
        frame_add = ctk.CTkFrame(self.frame_ingredientes, fg_color="transparent")
        frame_add.pack(fill="x", padx=15, pady=(0, 15))

        
        # Obtener lista de ingredientes disponibles (Nombre + Unidad)
        success, all_ings, _ = self.ing_controller.obtener_todos_ingredientes()
        self.map_ingredientes = {} # nombre -> objeto completo
        nombres_ing = []
        if success:
            for ing in all_ings:
                # ing es tupla o objeto? El controller retorna tupla formateada en 'obtener_todos_ingredientes'
                # Necesitamos objetos o datos crudos.
                # 'obtener_todos_ingredientes' en controller retorna formateados para tabla.
                # Mejor usamos 'model.obtener_todos_ingredientes' directamente o 'obtener_selectorlist' si existe?
                pass
        
        # Necesitamos una forma de obtener ID y Unidad dado el Nombre seleccionado
        # Voy a asumir que controller tiene metodo para obtener raw o hare un truco
        # Mejor cambio el controller de Ingredientes para darme lista cruda o uso el modelo
        
        # Por ahora usare el metodo `obtener_todos_ingredientes` que retorna formateado
        # (id, nombre, cantidad, unidad, precio, estado, cant_min, proveedor)
        # ID=0, Nombre=1, Cantidad=2, Unidad=3
        
        self.ings_disponibles = []
        if success: 
            self.ings_disponibles = all_ings

        nombres_combo = [f"{i[1]} ({i[3]})" for i in self.ings_disponibles] # Nombre (Unidad)
        
        self.combo_ing = ctk.CTkComboBox(frame_add, values=nombres_combo, width=200, height=35)
        self.combo_ing.pack(side="left", padx=(0, 10), expand=True, fill="x")
        if not nombres_combo: self.combo_ing.set("No hay ingredientes")

        self.entry_cantidad = ctk.CTkEntry(frame_add, width=80, placeholder_text="Cant.", height=35)
        self.entry_cantidad.pack(side="left", padx=(0, 10))
        
        self.btn_add = ctk.CTkButton(
            frame_add, text="+", width=40, height=35, 
            fg_color=config.COLORS["secondary"], command=self._agregar_ing_lista
        )
        self.btn_add.pack(side="left")
        
        # --- LISTA ---
        self.lista_scroll = ctk.CTkScrollableFrame(self.frame_ingredientes, fg_color="white")
        self.lista_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 5))

        self.lbl_error_ingredientes = ctk.CTkLabel(self.frame_ingredientes, text="", text_color="red", font=("Segoe UI", 10))
        self.lbl_error_ingredientes.pack(pady=(0, 10))
        
        self._renderizar_lista_ingredientes()

    def _renderizar_lista_ingredientes(self):
        for w in self.lista_scroll.winfo_children(): w.destroy()
            
        if not self.ingredientes_actuales:
            ctk.CTkLabel(self.lista_scroll, text="Sin ingredientes asignados", text_color="gray").pack(pady=20)
            return

        for idx, item in enumerate(self.ingredientes_actuales):
            row = ctk.CTkFrame(self.lista_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # Formato item: {'id', 'nombre', 'cantidad', 'unidad'}
            txt = f"{item['cantidad']} {item['unidad']} de {item['nombre']}"
            
            ctk.CTkLabel(row, text=txt, text_color="#374151", anchor="w").pack(side="left", padx=5)
            
            btn_del = ctk.CTkButton(
                row, text="×", width=30, height=25, fg_color="transparent", 
                text_color="red", hover_color="#FEE2E2",
                command=lambda i=idx: self._remover_ing_lista(i)
            )
            btn_del.pack(side="right")
    
    def _agregar_ing_lista(self):
        seleccion_texto = self.combo_ing.get()
        cantidad_str = self.entry_cantidad.get()
        
        if not seleccion_texto or "No hay" in seleccion_texto: return
        if not cantidad_str: return
        
        try:
            cant = float(cantidad_str)
            if cant <= 0: raise ValueError
        except:
            DialogUtils.mostrar_error("Error", "Cantidad inválida", self)
            return

        # Buscar ID y nombre real basado en el texto del combo "Nombre (Unidad)"
        ing_obj = None
        for ing in self.ings_disponibles:
            if f"{ing[1]} ({ing[3]})" == seleccion_texto:
                ing_obj = ing
                break
        
        if not ing_obj: return
        
        # ing_obj structure from controller: (id, nombre, cantidad, unidad, ...)
        nuevo_item = {
            'id': ing_obj[0],
            'nombre': ing_obj[1],
            'cantidad': cant,
            'unidad': ing_obj[3]
        }
        
        # Verificar duplicados y sumar, o rechazar
        existe = False
        for cur in self.ingredientes_actuales:
            if cur['id'] == nuevo_item['id']:
                cur['cantidad'] += cant # Sumar cantidad
                existe = True
                break
        
        if not existe:
            self.ingredientes_actuales.append(nuevo_item)
            
        self.entry_cantidad.delete(0, 'end')
        self._renderizar_lista_ingredientes()

    def _remover_ing_lista(self, index):
        if 0 <= index < len(self.ingredientes_actuales):
            self.ingredientes_actuales.pop(index)
            self._renderizar_lista_ingredientes()

    def _guardar(self):
        # 0. Limpiar errores previos
        for key, lbl in self.error_labels.items():
            lbl.configure(text="")
        self.lbl_error_ingredientes.configure(text="")

        datos = {}
        hay_errores = False

        # --- Helper para validar ---
        def set_error(key, msg):
             if key in self.error_labels:
                 self.error_labels[key].configure(text=msg)
                 
        # 1. Nombre
        nombre = self.vars['nombre'].get().strip()

        if not nombre:
            set_error('nombre', "Campo requerido")
            hay_errores = True
        datos['nombre'] = nombre

        # 2. Precio
        s_precio = self.vars['precio'].get()
        if not s_precio:
            set_error('precio', "Campo requerido")
            hay_errores = True
        else:
            try:
                p = float(s_precio)
                if p < 0:
                     set_error('precio', "No puede ser negativo")
                     hay_errores = True
                datos['precio'] = p
            except ValueError:
                set_error('precio', "Debe ser un número")
                hay_errores = True

        # 3. Categoría
        cat = self.vars['categoria'].get()
        if not cat:
             set_error('categoria', "Campo requerido")
             hay_errores = True
        datos['categoria'] = cat

        # 4. Tiempo
        s_tiempo = self.vars['tiempo'].get()
        if not s_tiempo:
            set_error('tiempo', "Campo requerido")
            hay_errores = True
        else:
            try:
                t = int(s_tiempo)
                if t <= 0:
                     set_error('tiempo', "Debe ser mayor a 0")
                     hay_errores = True
                datos['tiempo_preparacion'] = t
            except ValueError:
                set_error('tiempo', "Debe ser entero")
                hay_errores = True

        # 5. Descripción
        desc = self.vars['descripcion'].get("1.0", "end-1c").strip()
        if not desc:
            set_error('descripcion', "Campo requerido")
            hay_errores = True
        elif len(desc) < 10:
             set_error('descripcion', "Mínimo 10 caracteres")
             hay_errores = True
        datos['descripcion'] = desc

        # 6. Disponible
        datos['disponible'] = bool(self.vars['disponible'].get())
        
        # 7. INGREDIENTES (Validación requerida, excepto Productos)
        es_producto = (datos.get('categoria') == config.PlatoCategoría.PRODUCTO.value)
        if not es_producto and not self.ingredientes_actuales:
             self.lbl_error_ingredientes.configure(text="⚠️ Debes agregar al menos un ingrediente a la receta")
             hay_errores = True

        if hay_errores: 
            return

        # ================= GUARDADO =================

        # Preparar ingredientes para controller
        ingredientes_para_guardar = []
        for item in self.ingredientes_actuales:
            ingredientes_para_guardar.append({
                'id': item['id'],
                'cantidad': item['cantidad']
            })

        # 3. Llamar Controller
        if self.plato_data:
            # EDITAR
            success, _, msg = self.controller.actualizar_plato(
                self.plato_data.id,
                nombre=datos['nombre'],
                precio=datos['precio'],
                categoria=datos['categoria'],
                descripcion=datos['descripcion'],
                tiempo_preparacion=datos['tiempo_preparacion'],
                ingredientes=ingredientes_para_guardar
            )
            # Actualizar estado (disponible/agotado)
            self.controller.cambiar_disponibilidad(self.plato_data.id, datos['disponible'])
            
        else:
            # CREAR
            success, _, msg = self.controller.crear_plato(
                nombre=datos['nombre'],
                precio=datos['precio'],
                categoria=datos['categoria'],
                descripcion=datos['descripcion'],
                tiempo_preparacion=datos['tiempo_preparacion'],
                ingredientes=ingredientes_para_guardar
            )

        if success:
            self.destroy()
            if self.on_success: self.on_success()
            DialogUtils.mostrar_exito("Éxito", "Plato guardado correctamente", self.master)
        else:
            DialogUtils.mostrar_error("Error al guardar", msg, self)


class MenuPage(ctk.CTkFrame):
    """Módulo de Menú/Platos - Diseño Moderno"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color=config.COLORS["light_bg"])
        
        self.controller = PlatosController()
        self.ingredientes_controller = IngredientesController()
        self.tabla = None
        self.plato_seleccionado = None
        
        # Paginación
        self.pagina_actual = 1
        self.items_por_pagina = 20
        self.todos_los_platos = []
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz estilo dashboard moderno"""
        
        # --- HEADER PRINCIPAL (Estilo Ingredientes) ---
        # Barra superior con color primario completo
        frame_header = ctk.CTkFrame(
            self, 
            fg_color=config.COLORS["primary"],
            corner_radius=0,
            height=70
        )
        frame_header.pack(fill="x", padx=0, pady=0)
        
        # Contenedor interno del header para alinear contenido
        header_content = ctk.CTkFrame(frame_header, fg_color="transparent")
        header_content.pack(fill="x", padx=30, pady=15)
        
        titulo = ctk.CTkLabel(
            header_content,
            text="🍽️  GESTIÓN DEL MENÚ",
            text_color="#FFFFFF",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(side="left")

        # Botón Nuevo Plato (EN EL HEADER)
        btn_nuevo = ctk.CTkButton(
            header_content,
            text="＋ Nuevo Plato",
            command=self.crear_plato,
            fg_color=config.COLORS["success"], 
            hover_color="#059669",
            text_color="white",
            font=("Segoe UI", 13, "bold"),
            height=40,
            corner_radius=10,
            width=160
        )
        btn_nuevo.pack(side="right")
        
        # ===== FRAME PRINCIPAL (Scrollable para pantallas pequeñas) =====
        self.frame_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent" # Fondo transparente para heredar el gris claro
        )
        self.frame_scroll.pack(fill="both", expand=True, padx=0, pady=0)
        
        # ===== MÉTRICAS =====
        self._crear_metricas()
        
        # ===== CONTENEDOR PRINCIPAL (Tabla + Panel) =====
        self._crear_contenedor_principal()
    
    def _crear_metricas(self):
        """Tarjetas de métricas modernas"""
        container = ctk.CTkFrame(self.frame_scroll, fg_color="transparent")
        container.pack(fill="x", padx=30, pady=(0, 25))
        
        success, platos, _ = self.controller.obtener_todos_platos_formateados()
        total_platos = len(platos) if success else 0
        
        # Contar platos por estado
        disponibles = sum(1 for p in platos if p[5] == "disponible") if success else 0
        no_disponibles = total_platos - disponibles if success else 0
        
        # Configuración de cards
        cards_data = [
            {"icon": "📋", "title": "Total Platos", "value": str(total_platos), "color": config.COLORS["info"]},
            {"icon": "✅", "title": "Disponibles", "value": str(disponibles), "color": config.COLORS["success"]},
            {"icon": "🛑", "title": "Agotados", "value": str(no_disponibles), "color": config.COLORS["danger"]},
        ]
        
        for i, card in enumerate(cards_data):
            self._crear_metric_card(container, card, i)
    
    def _crear_metric_card(self, parent, data, index):
        """Grid de tarjetas responsive"""
        card = ctk.CTkFrame(
            parent,
            fg_color=config.COLORS["dark_bg"],
            corner_radius=15,
            border_width=0 # Sin borde para look más limpio
        )
        card.grid(row=0, column=index, padx=10 if index == 1 else 0, sticky="nsew")
        parent.grid_columnconfigure(index, weight=1)
        
        # Layout interno con padding generoso
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icono con fondo circular
        icon_bg = ctk.CTkFrame(
            inner, 
            fg_color=data["color"], 
            width=50, 
            height=50, 
            corner_radius=25
        )
        icon_bg.pack(side="left", anchor="center")
        icon_bg.pack_propagate(False) # Forzar tamaño
        
        ctk.CTkLabel(
            icon_bg,
            text=data["icon"],
            font=("Segoe UI", 20),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Textos
        text_frame = ctk.CTkFrame(inner, fg_color="transparent")
        text_frame.pack(side="left", padx=(15, 0), expand=True, fill="x")
        
        ctk.CTkLabel(
            text_frame,
            text=data["title"],
            font=("Segoe UI", 12, "bold"),
            text_color=config.COLORS["secondary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_frame,
            text=data["value"],
            font=("Segoe UI", 22, "bold"),
            text_color=config.COLORS["text_dark"]
        ).pack(anchor="w", pady=(2, 0))

    def _crear_contenedor_principal(self):
        """Layout principal: Tabla + Sidebar"""
        container = ctk.CTkFrame(self.frame_scroll, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # ===== COLUMNA IZQUIERDA: TABLA =====
        # Contenedor de la tabla con fondo blanco y bordes redondeados
        table_container = ctk.CTkFrame(
            container,
            fg_color=config.COLORS["dark_bg"],
            corner_radius=15
        )
        table_container.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Titulo de la sección Tabla
        table_header = ctk.CTkFrame(table_container, fg_color="transparent")
        table_header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            table_header,
            text="Listado del Menú",
            font=("Segoe UI", 16, "bold"),
            text_color=config.COLORS["text_dark"]
        ).pack(side="left")

        # Tabla
        table_inner_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_inner_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tabla = TreeViewWidget(
            table_inner_frame,
            columnas=["Nombre", "Precio", "Categoría", "T. Prep.", "Estado"], # Columna ID eliminada
            altura=12,
            row_height=40, # Filas más altas para toque táctil/moderno
            font_size=12,
            heading_font_size=12
        )
        self.tabla.pack(fill="both", expand=True)
        self.tabla.set_on_select(self._on_plato_select) # Vincular evento click
        
        # --- CONTROL DE PAGINACIÓN ---
        self.frame_paginacion = ctk.CTkFrame(table_container, fg_color="transparent", height=40)
        self.frame_paginacion.pack(fill="x", padx=20, pady=10)
        
        self.btn_anterior = ctk.CTkButton(
            self.frame_paginacion,
            text="< Anterior",
            width=100,
            fg_color="#3B82F6",         # Color primario (Azul)
            text_color="#FFFFFF",       # Texto blanco
            hover_color="#2563EB",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._cambiar_pagina(-1)
        )
        self.btn_anterior.pack(side="left")
        
        self.lbl_paginacion = ctk.CTkLabel(
            self.frame_paginacion,
            text="Página 1 de 1",
            font=("Segoe UI", 14, "bold"),
            text_color="#1F2937" # Texto oscuro para alto contraste
        )
        self.lbl_paginacion.pack(side="left", expand=True, fill="x") # Centrado y expandir
        
        self.btn_siguiente = ctk.CTkButton(
            self.frame_paginacion,
            text="Siguiente >",
            width=100,
            fg_color="#3B82F6",         # Azul brillante para que se vea bien
            text_color="#FFFFFF",       # Texto blanco
            hover_color="#2563EB",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._cambiar_pagina(1)
        )
        self.btn_siguiente.pack(side="right")

        # ===== COLUMNA DERECHA: SIDEBAR DETALLES =====
        self._crear_panel_informacion(container)

    def _crear_panel_informacion(self, parent):
        """Panel lateral moderno"""
        self.panel_info = ctk.CTkFrame(
            parent,
            fg_color=config.COLORS["dark_bg"],
            corner_radius=15,
            width=320 # Ancho fijo
        )
        self.panel_info.pack(side="right", fill="y")
        self.panel_info.pack_propagate(False)
        
        self._actualizar_panel()
    
    def _actualizar_panel(self):
        """Renderizar contenido del panel"""
        for widget in self.panel_info.winfo_children():
            widget.destroy()
            
        # Contenedor interno con padding
        content = ctk.CTkFrame(self.panel_info, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=25)
        
        # Título Panel
        ctk.CTkLabel(
            content,
            text="Detalle del Plato",
            font=("Segoe UI", 16, "bold"),
            text_color=config.COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 20))
        
        if not self.plato_seleccionado:
            # Estado vacío (Placeholder)
            placeholder = ctk.CTkFrame(content, fg_color=config.COLORS["light_bg"], corner_radius=10)
            placeholder.pack(fill="both", expand=True, pady=10)
            
            ctk.CTkLabel(
                placeholder,
                text="👆",
                font=("Segoe UI", 40)
            ).pack(expand=True, pady=(0, 10))
            
            ctk.CTkLabel(
                placeholder,
                text="Selecciona un plato\npara ver sus detalles",
                font=("Segoe UI", 13),
                text_color=config.COLORS["secondary"],
                justify="center"
            ).place(relx=0.5, rely=0.6, anchor="center")
            return
            
        # === MODO DETALLE ===
        plato_id, nombre, precio, categoria, tiempo, estado, _ = self.plato_seleccionado
        
        # 1. Cabecera con Nombre y Precio
        header_card = ctk.CTkFrame(content, fg_color=config.COLORS["light_bg"], corner_radius=12)
        header_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_card,
            text=nombre,
            font=("Segoe UI", 16, "bold"),
            text_color=config.COLORS["text_dark"],
            wraplength=240
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            header_card,
            text=precio, # Ya viene con símbolo de moneda
            font=("Segoe UI", 20, "bold"),
            text_color=config.COLORS["primary"]
        ).pack(anchor="w", padx=15, pady=(0, 15))
        
        # 2. badge de Estado
        status_color = config.COLORS["success"] if "disponible" in str(estado).lower() else config.COLORS["danger"]
        status_text = "DISPONIBLE" if "disponible" in str(estado).lower() else "AGOTADO"
        
        status_badge = ctk.CTkFrame(content, fg_color="transparent", border_width=1, border_color=status_color, corner_radius=20)
        status_badge.pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(
            status_badge,
            text=f"●  {status_text}",
            font=("Segoe UI", 11, "bold"),
            text_color=status_color
        ).pack(padx=12, pady=5)
        
        # 3. Datos Grid
        datos_grid = ctk.CTkFrame(content, fg_color="transparent")
        datos_grid.pack(fill="x", pady=(0, 15)) # Reducir padding inferior
        
        items = [
            ("Categoría", categoria),
            ("Tiempo Prep.", f"{tiempo} min"),
            # ID Sistema ELIMINADO
        ]
        
        for titulo, valor in items:
            row = ctk.CTkFrame(datos_grid, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=titulo, font=("Segoe UI", 12), text_color=config.COLORS["secondary"]).pack(side="left")
            ctk.CTkLabel(row, text=valor, font=("Segoe UI", 12, "bold"), text_color=config.COLORS["text_dark"]).pack(side="right")
        
        # 4. Botones de Acción (SUBIDOS para visibilidad)
        # Separador visual
        ctk.CTkFrame(content, height=1, fg_color="#E5E7EB").pack(fill="x", pady=(0, 15))

        btn_editar = ctk.CTkButton(
            content,
            text="✏️ Editar Plato",
            command=self.editar_plato,
            fg_color=config.COLORS["warning"],
            hover_color="#D97706",
            font=("Segoe UI", 13, "bold"),
            height=40,
            text_color="white",
            corner_radius=10
        )
        btn_editar.pack(fill="x", pady=(0, 10))
        
        btn_eliminar = ctk.CTkButton(
            content,
            text="🗑️ Eliminar",
            command=self.eliminar_plato,
            fg_color="transparent",
            border_width=2,
            border_color=config.COLORS["danger"],
            text_color=config.COLORS["danger"],
            hover_color="#FEF2F2",
            font=("Segoe UI", 13, "bold"),
            height=40,
            corner_radius=10
        )
        btn_eliminar.pack(fill="x", pady=0)
        
        # Espacio final flexible (empuja todo arriba)
        # ctk.CTkLabel(content, text="").pack(expand=True)  <-- ELIMINADO para evitar scroll


    # ==========================
    # LOGICA DE NEGOCIO (INTACTA)
    # ==========================
    
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
    
    def refrescar_tabla(self):
        """Refrescar datos de la tabla con paginación"""
        success, datos, msg = self.controller.obtener_todos_platos_formateados()
        
        if success:
            self.todos_los_platos = datos
            self.pagina_actual = 1
            self._actualizar_vista_tabla()
        else:
            DialogUtils.mostrar_error("Error", msg)

    def _cambiar_pagina(self, direccion):
        """Cambiar página actual"""
        total_items = len(self.todos_los_platos)
        total_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        
        nueva_pagina = self.pagina_actual + direccion
        
        if 1 <= nueva_pagina <= total_paginas:
            self.pagina_actual = nueva_pagina
            self._actualizar_vista_tabla()

    def _actualizar_vista_tabla(self):
        """Mostrar items correspondientes a la página actual"""
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        
        items_pagina = self.todos_los_platos[inicio:fin]
        
        self.tabla.limpiar()
        for dato in items_pagina:
            # dato es (id, nombre, precio, categoria, tiempo, estado, ing)
            # Queremos mostrar: (nombre, precio, categoria, tiempo, estado)
            # Indico 1:6 para saltar el ID (0) y no tomar Ingredientes (6)
            datos_visibles = dato[1:6] 
            
            # Pasamos datos_visibles para la tabla, pero guardamos 'dato' completo en ocultos
            # para poder recuperar el ID al seleccionar
            self.tabla.agregar_fila(datos_visibles, datos_ocultos=dato)
            
        # Actualizar labels y botones
        total_items = len(self.todos_los_platos)
        total_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        
        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} de {total_paginas} | Total: {total_items}")
        
        # Color azul cuando está activo, gris cuando desactivado
        self.btn_anterior.configure(state="normal" if self.pagina_actual > 1 else "disabled", fg_color="#3B82F6" if self.pagina_actual > 1 else "#9CA3AF")
        self.btn_siguiente.configure(state="normal" if self.pagina_actual < total_paginas else "disabled", fg_color="#3B82F6" if self.pagina_actual < total_paginas else "#9CA3AF")
    
    def crear_plato(self):
        """Crear nuevo plato"""
        def on_success():
            # Recargar y mostrar la última página
            success_load, datos, _ = self.controller.obtener_todos_platos_formateados()
            if success_load:
                self.todos_los_platos = datos
                total_items = len(self.todos_los_platos)
                self.pagina_actual = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
                self._actualizar_vista_tabla()
            
            self.plato_seleccionado = None
            self._actualizar_panel()

        PlatoFormDialog(
            self.winfo_toplevel(),
            "Crear Nuevo Plato",
            self.controller,
            self.ingredientes_controller,
            plato_data=None,
            on_success=on_success
        )

    
    def editar_plato(self):
        """Editar plato seleccionado"""
        if not self.plato_seleccionado:
            DialogUtils.mostrar_advertencia("⚠️ Advertencia", "Selecciona un plato para editar")
            return
        
        # Obtener el objeto plato completo incluyendo ID y todo lo demás
        success, plato_obj, msg = self.controller.obtener_plato(self.plato_seleccionado[0])
        
        if not success or not plato_obj:
            DialogUtils.mostrar_error("❌ Error", msg or "No se pudo obtener el plato")
            return

        def on_success():
            # Recargar y mostrar la última página o la actual
            pagina_temp = self.pagina_actual
            success_load, datos, _ = self.controller.obtener_todos_platos_formateados()
            if success_load:
                self.todos_los_platos = datos
                self.pagina_actual = pagina_temp
                self._actualizar_vista_tabla()
            
            self.plato_seleccionado = None
            self._actualizar_panel()

        PlatoFormDialog(
            self.winfo_toplevel(),
            "Editar Plato",
            self.controller,
            self.ingredientes_controller,
            plato_data=plato_obj,
            on_success=on_success
        )

    
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
                
                # Recargar datos desde backend y mantener página si es posible
                pagina_actual_temp = self.pagina_actual
                success_load, datos, msg = self.controller.obtener_todos_platos_formateados()
                
                if success_load:
                    self.todos_los_platos = datos
                    
                    # Verificar si la página actual sigue siendo válida
                    total_items = len(self.todos_los_platos)
                    total_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
                    
                    if pagina_actual_temp > total_paginas:
                        self.pagina_actual = total_paginas
                    else:
                        self.pagina_actual = pagina_actual_temp
                        
                    self._actualizar_vista_tabla()
                
                self._actualizar_panel()
            else:
                DialogUtils.mostrar_error("❌ Error", msg)
