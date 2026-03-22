"""
Página: Gestión de Ingredientes - Diseño Master-Detail Moderno
"""
import customtkinter as ctk
from controllers.ingredientes_controller import IngredientesController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils, FormDialog
import config

class IngredientesPage(ctk.CTkFrame):
    """Módulo de Ingredientes"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controller = IngredientesController()
        # Referencias de tabla
        self.tabla = None
        self.tabla_bajo_stock = None
        
        # Estado
        self.ingrediente_seleccionado = None
        self.datos_completos = [] 
        
        # Paginación
        self.pagina_actual = 1
        self.elementos_por_pagina = 15
        self.datos_filtrados_paginacion = [] 
        
        # Referencias UI Panel Derecho
        self.lbl_nombre_perfil = None
        self.lbl_cantidad_perfil = None
        self.badge_estado = None
        self.lbl_estado_texto = None
        self.lbl_unidad_val = None
        self.lbl_costo_val = None
        self.lbl_minimo_val = None
        self.lbl_proveedor_val = None
        self.lbl_valor_total = None
        
        # Botones Panel Derecho
        self.btn_abastecer = None
        self.btn_editar = None
        self.btn_eliminar = None
        
        self._crear_ui()
        self.refrescar_tablas()
    
    def _crear_ui(self):
        """Crear interfaz moderna Master-Detail"""
        
        # --- HEADER PRINCIPAL ---
        self.header_bg = config.COLORS["primary"] # Tomate
        
        frame_header = ctk.CTkFrame(
            self, 
            fg_color=self.header_bg,
            corner_radius=0, 
            height=85
        )
        frame_header.pack(fill="x", padx=0, pady=0)
        
        # Contenedor interno del header
        header_content = ctk.CTkFrame(frame_header, fg_color="transparent")
        header_content.pack(fill="x", padx=40, pady=25)
        
        # Título
        titulo = ctk.CTkLabel(
            header_content,
            text="INVENTARIO DE COCINA",
            text_color="#FFFFFF",
            font=("Segoe UI Display", 26, "bold")
        )
        titulo.pack(side="left")
        
        subtitulo = ctk.CTkLabel(
            header_content,
            text=" / Control de Stock e Insumos",
            text_color="#FEF3C7",
            font=("Segoe UI", 16)
        )
        subtitulo.pack(side="left", pady=(8,0), padx=5)

        # --- CONTENIDO PRINCIPAL ---
        self.contenido = ctk.CTkFrame(self, fg_color="#F8FAFC") # Slate-50 background
        self.contenido.pack(fill="both", expand=True)
        
        # Layout de dos columnas
        frame_layout = ctk.CTkFrame(self.contenido, fg_color="transparent")
        frame_layout.pack(fill="both", expand=True, padx=40, pady=30)
        
        # 1. COLUMNA IZQUIERDA: LISTADO (Flexible)
        col_izquierda = ctk.CTkFrame(frame_layout, fg_color="transparent")
        col_izquierda.pack(side="left", fill="both", expand=True, padx=(0, 25))
        
        # Barra de Acciones (Floating style)
        acciones_frame = ctk.CTkFrame(col_izquierda, fg_color="transparent", height=50)
        acciones_frame.pack(fill="x", pady=(0, 20))
        
        # Buscador y Filtros
        filtros_frame = ctk.CTkFrame(acciones_frame, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        filtros_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(filtros_frame, text="🔍", font=("Segoe UI", 14), text_color="#64748B").pack(side="left", padx=(15, 5))
        self.entry_busqueda = ctk.CTkEntry(
            filtros_frame, 
            placeholder_text="Buscar ingrediente...", 
            border_width=0, 
            fg_color="transparent",
            width=200,
            text_color="#334155",
            font=("Segoe UI", 13)
        )
        self.entry_busqueda.pack(side="left", padx=(0, 15), pady=5)
        self.entry_busqueda.bind("<KeyRelease>", self._filtrar_resultados)

        # Segmented Control para Vistas
        self.vista_actual = ctk.StringVar(value="Todos")
        self.selector_vista = ctk.CTkSegmentedButton(
            acciones_frame,
            values=["Todos", "Bajo Stock"],
            command=self._cambiar_vista,
            variable=self.vista_actual,
            selected_color=config.COLORS["primary"],
            selected_hover_color=config.COLORS["accent"],
            unselected_color="white", 
            unselected_hover_color="#E2E8F0",
            text_color="#334155",
            font=("Segoe UI", 12, "bold"),
            height=35
        )
        self.selector_vista.set("Todos")
        self.selector_vista.pack(side="left", padx=20)

        # Botón Nuevo
        btn_nuevo = ctk.CTkButton(
            acciones_frame,
            text="＋ NUEVO PRODUCTO",
            command=self.crear_ingrediente,
            fg_color="#10B981", 
            hover_color="#059669",
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            height=42,
            corner_radius=21,
            width=160
        )
        btn_nuevo.pack(side="right")
        
        # Tabla Containers
        self.card_tabla = ctk.CTkFrame(
            col_izquierda, 
            fg_color="white", 
            corner_radius=16,
            border_width=0
        )
        self.card_tabla.pack(fill="both", expand=True)
        
        # Linea decorativa top tabla
        ctk.CTkFrame(self.card_tabla, height=4, fg_color=config.COLORS["primary"], corner_radius=2).pack(fill="x")

        # Frame Tabla Todos (se muestra por defecto)
        self.frame_tabla_todos = ctk.CTkFrame(self.card_tabla, fg_color="transparent")
        self.frame_tabla_todos.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.tabla = TreeViewWidget(
            self.frame_tabla_todos,
            columnas=["Producto", "Stock", "Costo", "Mínimo", "Proveedor", "Estado"],
            altura=15,
            font_size=13,
            heading_font_size=12,
            row_height=40
        )
        self.tabla.pack(fill="both", expand=True)
        self.tabla.set_on_select(self._on_ingrediente_select)

        # Frame Tabla Bajo Stock (oculto por defecto)
        self.frame_tabla_bajo = ctk.CTkFrame(self.card_tabla, fg_color="transparent")
        
        self.tabla_bajo_stock = TreeViewWidget(
            self.frame_tabla_bajo,
            columnas=["Producto", "Stock Actual", "Mínimo", "Estado"],
            altura=15,
            font_size=13,
            heading_font_size=12,
            row_height=40
        )
        self.tabla_bajo_stock.pack(fill="both", expand=True)
        self.tabla_bajo_stock.set_on_select(self._on_ingrediente_select)

        # Controles de Paginación (Al pie de la card)
        self.frame_paginacion = ctk.CTkFrame(self.card_tabla, fg_color="transparent", height=40)
        self.frame_paginacion.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.btn_anterior = ctk.CTkButton(
            self.frame_paginacion,
            text="◀ Anterior",
            width=90,
            height=28,
            font=("Segoe UI", 11),
            fg_color="#F1F5F9",
            text_color="#64748B",
            hover_color="#E2E8F0",
            state="disabled",
            command=lambda: self._cambiar_pagina(-1)
        )
        self.btn_anterior.pack(side="left")
        
        self.lbl_paginacion = ctk.CTkLabel(
            self.frame_paginacion,
            text="Página 1 de 1",
            font=("Segoe UI", 12, "bold"),
            text_color="#64748B"
        )
        self.lbl_paginacion.pack(side="left", expand=True)

        self.btn_siguiente = ctk.CTkButton(
            self.frame_paginacion,
            text="Siguiente ▶",
            width=90,
            height=28,
            font=("Segoe UI", 11),
            fg_color="#F1F5F9",
            text_color="#64748B",
            hover_color="#E2E8F0",
            state="disabled",
            command=lambda: self._cambiar_pagina(1)
        )
        self.btn_siguiente.pack(side="right")
        
        # 2. COLUMNA DERECHA: DETALLE (Fijo)
        self.panel_derecho = ctk.CTkFrame(
            frame_layout, 
            fg_color="white", 
            width=380,
            corner_radius=20
        )
        self.panel_derecho.pack(side="right", fill="y", padx=0, pady=0)
        self.panel_derecho.pack_propagate(False)
        
        self._construir_detalle_ui() # Construir panel derecho

    def _construir_detalle_ui(self):
        """Construye el panel derecho de detalle del ingrediente"""
        
        # Header Perfil
        header_perfil = ctk.CTkFrame(self.panel_derecho, fg_color="#F1F5F9", height=90, corner_radius=15)
        header_perfil.pack(fill="x", padx=10, pady=10)
        header_perfil.pack_propagate(False) 
        
        # Icono Ingrediente
        icon_frame = ctk.CTkFrame(header_perfil, width=60, height=60, corner_radius=30, fg_color="white")
        icon_frame.place(relx=0.15, rely=0.5, anchor="center")
        ctk.CTkLabel(icon_frame, text="🍎", font=("Segoe UI", 30)).place(relx=0.5, rely=0.5, anchor="center")
        
        # Info Principal Header
        self.lbl_nombre_perfil = ctk.CTkLabel(
            header_perfil,
            text="Seleccione Producto",
            font=("Segoe UI", 16, "bold"),
            text_color="#1E293B",
            anchor="w"
        )
        self.lbl_nombre_perfil.place(relx=0.32, rely=0.35, anchor="w")
        
        self.lbl_cantidad_perfil = ctk.CTkLabel(
            header_perfil,
            text="---",
            font=("Segoe UI", 13),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_cantidad_perfil.place(relx=0.32, rely=0.65, anchor="w")
        
        # Badge Estado (Posicionado absoluto en header corner)
        self.badge_estado = ctk.CTkFrame(header_perfil, fg_color="#E2E8F0", corner_radius=6, height=20, width=80)
        self.badge_estado.place(relx=0.95, rely=0.2, anchor="ne")
        self.lbl_estado_texto = ctk.CTkLabel(self.badge_estado, text="---", font=("Segoe UI", 9, "bold"), text_color="#64748B")
        self.lbl_estado_texto.place(relx=0.5, rely=0.5, anchor="center")

        # Detalles (Grid)
        self.info_container = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        self.info_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Filas de datos
        self._crear_fila_info("⚖️ Unidad Medida", "lbl_unidad_val")
        self._crear_fila_info("💲 Costo Unitario", "lbl_costo_val")
        self._crear_fila_info("📉 Stock Mínimo", "lbl_minimo_val")
        self._crear_fila_info("🏭 Proveedor", "lbl_proveedor_val")
        
        ctk.CTkFrame(self.info_container, height=1, fg_color="#E2E8F0").pack(fill="x", pady=15)
        
        self._crear_fila_info("💵 Valor en Stock", "lbl_valor_total", font_val=("Segoe UI", 14, "bold"), color_val=config.COLORS["primary"])

        # Botones Pie (Acciones)
        frame_btns = ctk.CTkFrame(self.panel_derecho, fg_color="transparent")
        frame_btns.pack(fill="x", padx=20, pady=20, side="bottom")
        
        # Botón Abastecer (Principal acción)
        self.btn_abastecer = ctk.CTkButton(
            frame_btns,
            text="📥  ENTRADA DE STOCK",
            command=self.abastecer_ingrediente,
            fg_color=config.COLORS["info"],
            hover_color="#2563EB",
            text_color="white",
            height=45,
            corner_radius=10,
            font=("Segoe UI", 12, "bold"),
            state="disabled"
        )
        self.btn_abastecer.pack(fill="x", pady=(0, 10))
        
        # Botones secundarios (row)
        btns_sec_frame = ctk.CTkFrame(frame_btns, fg_color="transparent")
        btns_sec_frame.pack(fill="x")
        
        self.btn_editar = ctk.CTkButton(
            btns_sec_frame,
            text="Editar",
            command=self.editar_ingrediente,
            fg_color="#F1F5F9", 
            text_color="#475569",
            hover_color="#E2E8F0",
            height=35,
            corner_radius=8,
            font=("Segoe UI", 12, "bold"),
            width=150,
            state="disabled"
        )
        self.btn_editar.pack(side="left", padx=(0, 5), expand=True, fill="x")
        
        self.btn_eliminar = ctk.CTkButton(
            btns_sec_frame,
            text="Eliminar",
            command=self.eliminar_ingrediente_seleccionado,
            fg_color="#FEE2E2",
            text_color="#B91C1C",
            hover_color="#FCA5A5", 
            height=35, 
            corner_radius=8,
            font=("Segoe UI", 12, "bold"),
            width=150,
            state="disabled"
        )
        self.btn_eliminar.pack(side="right", padx=(5, 0), expand=True, fill="x")

    def _crear_fila_info(self, label, attr_name, font_val=("Segoe UI", 13), color_val="#334155"):
        frame = ctk.CTkFrame(self.info_container, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(frame, text=label, font=("Segoe UI", 12), text_color="#94A3B8").pack(side="left")
        val = ctk.CTkLabel(frame, text="---", font=font_val, text_color=color_val)
        val.pack(side="right")
        setattr(self, attr_name, val)

    def _actualizar_panel_derecho(self):
        """Actualizar datos del panel derecho"""
        if not self.ingrediente_seleccionado:
            self._reset_panel()
            return

        # Activar controles
        self.btn_abastecer.configure(state="normal")
        self.btn_editar.configure(state="normal")
        self.btn_eliminar.configure(state="normal")
        
        # Datos vienen de tabla: (ID, Producto, Stock, Costo, Mínimo, Proveedor, Estado)
        # Ojo: dependiendo de la vista, el formato cambia ligeramente.
        # Mejor recuperar objeto completo del controller por ID para estar seguros
        ing_id = self.ingrediente_seleccionado[0]
        success, ing, _ = self.controller.obtener_ingrediente(ing_id)
        
        if success and ing:
            self.lbl_nombre_perfil.configure(text=ing.nombre)
            self.lbl_cantidad_perfil.configure(text=f"{ing.cantidad} {ing.unidad}")
            
            self.lbl_unidad_val.configure(text=ing.unidad)
            self.lbl_costo_val.configure(text=f"${ing.precio_unitario:.2f}")
            self.lbl_minimo_val.configure(text=f"{ing.cantidad_minima} {ing.unidad}")
            self.lbl_proveedor_val.configure(text=ing.proveedor or "---")
            
            valor_total = ing.cantidad * ing.precio_unitario
            self.lbl_valor_total.configure(text=f"${valor_total:.2f}")
            
            # Estado Badge
            estado = "DISPONIBLE"
            bg_color = "#DCFCE7" # Verde claro
            text_color = "#15803D"
            
            if ing.cantidad <= 0:
                estado = "AGOTADO"
                bg_color = "#FEE2E2" # Rojo claro
                text_color = "#991B1B"
            elif ing.esta_bajo_stock():
                estado = "BAJO STOCK"
                bg_color = "#FEF3C7" # Amarillo claro
                text_color = "#92400E"
                
            self.badge_estado.configure(fg_color=bg_color)
            self.lbl_estado_texto.configure(text=estado, text_color=text_color)
            
    def _reset_panel(self):
        self.lbl_nombre_perfil.configure(text="Seleccione Producto")
        self.lbl_cantidad_perfil.configure(text="---")
        self.badge_estado.configure(fg_color="#E2E8F0")
        self.lbl_estado_texto.configure(text="---", text_color="#64748B")
        
        self.lbl_unidad_val.configure(text="---")
        self.lbl_costo_val.configure(text="---")
        self.lbl_minimo_val.configure(text="---")
        self.lbl_proveedor_val.configure(text="---")
        self.lbl_valor_total.configure(text="---")
        
        self.btn_abastecer.configure(state="disabled")
        self.btn_editar.configure(state="disabled")
        self.btn_eliminar.configure(state="disabled")

    def _cambiar_pagina(self, direccion):
        """Moverse entre páginas"""
        nueva_pagina = self.pagina_actual + direccion
        
        total_items = len(self.datos_filtrados_paginacion)
        total_paginas = max(1, (total_items + self.elementos_por_pagina - 1) // self.elementos_por_pagina)
        
        if 1 <= nueva_pagina <= total_paginas:
            self.pagina_actual = nueva_pagina
            self._actualizar_vista_tabla()

    def _actualizar_vista_tabla(self):
        """Renderizar items de la página actual"""
        inicio = (self.pagina_actual - 1) * self.elementos_por_pagina
        fin = inicio + self.elementos_por_pagina
        
        items_pagina = self.datos_filtrados_paginacion[inicio:fin]
        
        datos_visibles = [d[1:] for d in items_pagina]
        
        if self.vista_actual.get() == "Todos":
            self.tabla.limpiar()
            self.tabla.agregar_filas(datos_visibles, items_pagina)
        else:
            self.tabla_bajo_stock.limpiar()
            self.tabla_bajo_stock.agregar_filas(datos_visibles, items_pagina)
        
        # Paginación UI
        total_items = len(self.datos_filtrados_paginacion)
        total_paginas = max(1, (total_items + self.elementos_por_pagina - 1) // self.elementos_por_pagina)
        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} de {total_paginas} | Total: {total_items}")
        
        self.btn_anterior.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_siguiente.configure(state="normal" if self.pagina_actual < total_paginas else "disabled")

    def _cambiar_vista(self, vista):
        """Cambiar entre frames de tabla"""
        if vista == "Todos":
            self.frame_tabla_bajo.pack_forget()
            self.frame_tabla_todos.pack(fill="both", expand=True, padx=10, pady=(10, 0))
            self.datos_filtrados_paginacion = self.datos_completos # Restaurar filtro base
        else:
            self.frame_tabla_todos.pack_forget()
            self.frame_tabla_bajo.pack(fill="both", expand=True, padx=10, pady=(10, 0))
            # Aquí deberíamos filtrar por bajos, pero ya lo hacemos en refrescar o filtrar
            # Simular filtro
            self.refrescar_tablas() # Re-fetch más fácil
            
        self.pagina_actual = 1
        self._filtrar_resultados()

    def _on_ingrediente_select(self, datos):
        self.ingrediente_seleccionado = datos
        self._actualizar_panel_derecho()
    
    def refrescar_tablas(self):
        # 1. Obtener todos
        success, datos, msg = self.controller.obtener_todos_ingredientes()
        if success:
            self.datos_completos = datos 

        # 2. Si estamos en modo bajo stock, filtrar o pedir solo esos
        if self.vista_actual.get() == "Bajo Stock":
            success_bajo, datos_bajo, _ = self.controller.obtener_bajo_stock_formateados()
            if success_bajo:
                 self.datos_filtrados_paginacion = datos_bajo
            else:
                 self.datos_filtrados_paginacion = []
        else:
             self.datos_filtrados_paginacion = self.datos_completos
             
        self._filtrar_resultados() # Aplica busqueda sobre lo actual y pagina

    def _filtrar_resultados(self, *args):
        # Filtro de texto sobre la colección actual (ya sea Todos o Bajo Stock)
        busqueda = self.entry_busqueda.get().strip().lower()
        
        # Si venimos de cambiar vista, datos_filtrados_paginacion tiene la base
        # Pero si escribimos, tenemos que filtrar sobre esa base... o sobre datos_completos?
        # Simplificación: Si hay búsqueda, busca en datos_completos. Si no, respeta la vista.
        
        base = self.datos_completos
        if self.vista_actual.get() == "Bajo Stock":
             success_bajo, datos_bajo, _ = self.controller.obtener_bajo_stock_formateados()
             if success_bajo: base = datos_bajo
        
        resultado = []
        if not busqueda:
            resultado = base
        else:
            for item in base:
                # Buscar en todas las columnas texto
                texto_fila = " ".join([str(x).lower() for x in item])
                if busqueda in texto_fila:
                    resultado.append(item)
                    
        self.datos_filtrados_paginacion = resultado
        self.pagina_actual = 1
        self._actualizar_vista_tabla()

    
    def crear_ingrediente(self):
        unidades = self.controller.obtener_unidades_disponibles()
        
        campos = {
            'nombre': {'label': 'Nombre del Producto', 'type': 'text', 'required': True},
            'unidad': {'label': 'Unidad (Kilos, Litros...)', 'type': 'dropdown', 'options': unidades, 'editable': True, 'required': True},
            'precio_unitario': {'label': 'Costo Unitario ($)', 'type': 'number', 'min': 0, 'required': True},
            'cantidad': {'label': '¿Cuánto tienes HOY en la cocina?', 'type': 'number', 'min': 0, 'required': True},
            'cantidad_minima': {'label': 'AVISARME cuando quede menos de:', 'type': 'number', 'min': 0, 'required': True},
            'proveedor': {'label': 'Proveedor', 'type': 'text', 'required': True}
        }
        
        def procesar(valores):
            success, ing, msg = self.controller.crear_ingrediente(
                valores.get('nombre'),
                valores.get('unidad'),
                valores.get('precio_unitario', 0),
                valores.get('cantidad', 0),
                valores.get('cantidad_minima', 5),
                valores.get('proveedor')
            )
            
            if success:
                DialogUtils.mostrar_exito("Éxito", "Ingrediente creado")
                self.refrescar_tablas()
            else:
                DialogUtils.mostrar_error("Error", msg)
        FormDialog(self.winfo_toplevel(), "Nuevo Ingrediente", campos, procesar)
    
    def abastecer_ingrediente(self):
        if not self.ingrediente_seleccionado: return
        ingrediente_id = self.ingrediente_seleccionado[0]
        
        success, ing, msg = self.controller.obtener_ingrediente(ingrediente_id)
        if not success or not ing: return
        
        campos = {
            'cantidad_recibida': {
                'label': f'Cantidad Recibida ({ing.unidad})', 
                'type': 'number', 'required': True, 'min': 0.001
            }
        }
        
        def procesar(valores):
            try:
                recibida = float(valores.get('cantidad_recibida', 0))
                nueva_cantidad_total = ing.cantidad + recibida
                
                success, _, msg = self.controller.ajustar_cantidad(ingrediente_id, nueva_cantidad_total)
                if success:
                    DialogUtils.mostrar_exito("Stock Actualizado", f"Nuevo Total: {nueva_cantidad_total} {ing.unidad}")
                    self.refrescar_tablas()
                    self._actualizar_panel_derecho() # Actualizar card
                else:
                    DialogUtils.mostrar_error("Error", msg)
            except ValueError: pass

        FormDialog(self.winfo_toplevel(), f"Entrada de {ing.nombre}", campos, procesar)

    def eliminar_ingrediente_seleccionado(self):
        if not self.ingrediente_seleccionado: return
        
        ingrediente_id = self.ingrediente_seleccionado[0]
        success_stock, ing_obj, _ = self.controller.obtener_ingrediente(ingrediente_id)
        
        if success_stock and ing_obj and ing_obj.cantidad > 0:
            DialogUtils.mostrar_error("Stock Activo", "No se puede eliminar productos con existencia > 0.")
            return

        confirmacion = DialogUtils.pedir_confirmacion("Eliminar", "¿Estás seguro? Esta acción es irreversible.")
        if confirmacion:
            success, _, msg = self.controller.eliminar_ingrediente(ingrediente_id)
            if success:
                self.ingrediente_seleccionado = None
                self._reset_panel()
                self.refrescar_tablas()
                DialogUtils.mostrar_exito("Eliminado", "Producto eliminado correctamente.")

    def editar_ingrediente(self):
        if not self.ingrediente_seleccionado: return
        ingrediente_id = self.ingrediente_seleccionado[0]
        
        success, ing, msg = self.controller.obtener_ingrediente(ingrediente_id)
        if not success: return

        unidades = self.controller.obtener_unidades_disponibles()
        campos = {
            'nombre': {'label': 'Producto', 'type': 'text', 'value': ing.nombre, 'required': True},
            'unidad': {'label': 'Unidad', 'type': 'dropdown', 'options': unidades, 'editable': True, 'value': ing.unidad, 'required': True},
            'precio_unitario': {'label': 'Costo Unitario ($)', 'type': 'number', 'value': ing.precio_unitario, 'min': 0, 'required': True},
            'cantidad': {'label': 'Stock Actual', 'type': 'number', 'value': ing.cantidad, 'min': 0, 'required': True}, 
            'cantidad_minima': {'label': 'Stock Mínimo Alerta', 'type': 'number', 'value': ing.cantidad_minima, 'min': 0, 'required': True},
            'proveedor': {'label': 'Proveedor', 'type': 'text', 'value': ing.proveedor, 'required': True}
        }

        def procesar(valores):
            success, _, msg = self.controller.actualizar_ingrediente(
                ingrediente_id=ingrediente_id,
                nombre=valores.get('nombre'),
                unidad=valores.get('unidad'),
                precio_unitario=valores.get('precio_unitario'),
                cantidad_minima=valores.get('cantidad_minima'),
                proveedor=valores.get('proveedor')
            )
            
            if success and valores.get('cantidad') is not None:
                nueva = float(valores.get('cantidad'))
                if nueva != ing.cantidad: self.controller.ajustar_cantidad(ingrediente_id, nueva)

            if success:
                self.refrescar_tablas()
                self._actualizar_panel_derecho() # Actualizar card inmediata
            else:
                DialogUtils.mostrar_error("Error", msg)

        FormDialog(self.winfo_toplevel(), "Editar Ingrediente", campos, procesar)