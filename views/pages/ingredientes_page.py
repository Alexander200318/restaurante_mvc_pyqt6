"""
Página: Gestión de Ingredientes
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
        self.tabla = None
        self.tabla_bajo_stock = None
        self.ingrediente_seleccionado = None
        self.datos_completos = [] # Copia local para buscador
        
        self._crear_ui()
        self.refrescar_tablas()
    
    def _crear_ui(self):
        """Crear interfaz moderna"""
        # --- HEADER PRINCIPAL ---
        # Barra superior con color primario completo
        frame_header = ctk.CTkFrame(
            self, 
            fg_color=config.COLORS["primary"],
            corner_radius=0, # Borde recto para estilo de barra superior
            height=70
        )
        frame_header.pack(fill="x", padx=0, pady=0)
        
        # Contenedor interno del header para alinear contenido
        header_content = ctk.CTkFrame(frame_header, fg_color="transparent")
        header_content.pack(fill="x", padx=30, pady=15)
        
        titulo = ctk.CTkLabel(
            header_content,
            text="📦  INVENTARIO DE COCINA",
            text_color="#FFFFFF",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(side="left")

        # --- BARRA DE HERRAMIENTAS (TOOLBAR) ---
        # Botones de acción separados del header para limpieza visual
        frame_toolbar = ctk.CTkFrame(self, fg_color="transparent", height=60)
        frame_toolbar.pack(fill="x", padx=30, pady=(25, 15))

        # Botón Nuevo (Verde Brillante)
        btn_nuevo = ctk.CTkButton(
            frame_toolbar,
            text="＋ Nuevo Producto",
            command=self.crear_ingrediente,
            fg_color=config.COLORS["success"],
            hover_color="#059669",
            text_color="white",
            font=("Segoe UI", 13, "bold"),
            height=45, # Botones más altos
            corner_radius=10,
            width=160
        )
        btn_nuevo.pack(side="left", padx=(0, 15))

        # Botón Abastecer (Azul Intenso)
        btn_abastecer = ctk.CTkButton(
            frame_toolbar,
            text="📥 Entrada Stock",
            command=self.abastecer_ingrediente,
            fg_color=config.COLORS["info"],
            hover_color="#2563EB", 
            text_color="white",
            font=("Segoe UI", 13, "bold"),
            height=45,
            corner_radius=10,
            width=160
        )
        btn_abastecer.pack(side="left", padx=0)
        
        # ELIMINAR BUSCADOR ANTERIOR
        # Espaciador para empujar el botón editar a la derecha
        ctk.CTkLabel(frame_toolbar, text="").pack(side="left", expand=True)

        # Botón Editar (Naranja/Warning - Estilo Outline/Fantasma para diferenciar)
        btn_editar = ctk.CTkButton(
            frame_toolbar,
            text="✏️ Editar Selección",
            command=self.editar_ingrediente,
            fg_color="transparent", 
            border_width=2,
            border_color=config.COLORS["warning"],
            text_color=config.COLORS["warning"],
            hover_color=config.COLORS["secondary"],
            font=("Segoe UI", 13, "bold"),
            height=45,
            corner_radius=10,
            width=150
        )
        btn_editar.pack(side="right", padx=0)
        
        # --- CONTROL Y NAVEGACIÓN (Buscador + Pestañas en la misma línea) ---
        frame_controls = ctk.CTkFrame(self, fg_color="transparent")
        frame_controls.pack(fill="x", padx=30, pady=(15, 5)) 

        # 1. BUSCADOR (Izquierda)
        self.entry_busqueda = ctk.CTkEntry(
            frame_controls,
            placeholder_text="🔍 Buscar por producto o proveedor",
            placeholder_text_color="#6B7280",
            width=300, 
            height=35,
            font=("Segoe UI", 12),
            text_color="#1F2937",
            corner_radius=10, 
            border_width=1,
            border_color="#9CA3AF",
            fg_color="#FFFFFF"
        )
        self.entry_busqueda.pack(side="left")
        
        # Vincular evento de teclado para búsqueda en tiempo real
        self.entry_busqueda.bind("<KeyRelease>", self._filtrar_resultados)

        # 2. PESTAÑAS (Derecha) - Usamos SegmentedButton para simular tabs pero controlando posición
        self.vista_actual = ctk.StringVar(value="Inventario Completo")
        self.selector_vista = ctk.CTkSegmentedButton(
            frame_controls,
            values=["Inventario Completo", "Alertas de Stock"],
            command=self._cambiar_vista,
            variable=self.vista_actual,
            font=("Segoe UI", 13, "bold"),
            selected_color=config.COLORS["primary"],
            selected_hover_color=config.COLORS["accent"],
            unselected_color=config.COLORS["secondary"],
            unselected_hover_color="#4B5563",
            text_color="#FFFFFF",
            height=35
        )
        self.selector_vista.pack(side="right")
        
        # Estado de Paginación
        self.pagina_actual = 1
        self.elementos_por_pagina = 10 # Probemos con 10 para ver si aparece
        self.datos_filtrados_paginacion = [] 

        # --- ÁREA DE CONTENIDO (Tablas) ---
        self.frame_contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_contenido.pack(fill="both", expand=True, padx=30, pady=(5, 30))
        
        # Frame Tabla 1: Todos
        self.frame_tabla_todos = ctk.CTkFrame(self.frame_contenido, fg_color=config.COLORS["secondary"], corner_radius=15)
        
        self.tabla = TreeViewWidget(
            self.frame_tabla_todos,
            columnas=["Producto", "Total en Inventario", "Costo", "Mínimo", "Proveedor", "Estado"],
            altura=18, # Reducimos un poco para dar espacio a paginación
            row_height=35,       
            font_size=12,        
            heading_font_size=11
        )
        # Controles de Paginación (Solo para tabla 1)
        # Usamos pack(side="bottom") ANTES de la tabla pero con fill x
        # En realidad, empaquetamos la tabla PRIMERO y luego la paginación ABAJO
        
        self.frame_paginacion = ctk.CTkFrame(self.frame_tabla_todos, fg_color="transparent", height=40)
        self.frame_paginacion.pack(side="bottom", fill="x", padx=15, pady=15)
        
        # Tabla va arriba y expande
        self.tabla.pack(side="top", fill="both", expand=True, padx=15, pady=(15, 5))
        self.tabla.set_on_select(self._on_ingrediente_select)
        
        self.btn_anterior = ctk.CTkButton(
            self.frame_paginacion,
            text="< Anterior",
            width=100,
            fg_color="#374151",
            hover_color="#4B5563",
            command=lambda: self._cambiar_pagina(-1)
        )
        self.btn_anterior.pack(side="left")
        
        self.lbl_paginacion = ctk.CTkLabel(
            self.frame_paginacion,
            text="Página 1 de 1",
            font=("Segoe UI", 12, "bold"),
            text_color="#D1D5DB"
        )
        self.lbl_paginacion.pack(side="left", expand=True, fill="x") # Centrado y expandir
        
        self.btn_siguiente = ctk.CTkButton(
            self.frame_paginacion,
            text="Siguiente >",
            width=100,
            fg_color="#374151",
            hover_color="#4B5563",
            command=lambda: self._cambiar_pagina(1)
        )
        self.btn_siguiente.pack(side="right")

        # Frame Tabla 2: Bajo Stock
        self.frame_tabla_bajo = ctk.CTkFrame(self.frame_contenido, fg_color=config.COLORS["secondary"], corner_radius=15)
        
        self.tabla_bajo_stock = TreeViewWidget(
            self.frame_tabla_bajo,
            columnas=["Producto", "Stock Actual", "Mínimo", "Estado"],
            altura=20, # Tabla de alertas puede ser completa (menos items usualmente)
            row_height=35,
            font_size=12,
            heading_font_size=11
        )
        self.tabla_bajo_stock.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Inicializar vista
        self._cambiar_vista("Inventario Completo")

    def _cambiar_pagina(self, direccion):
        """Moverse entre páginas"""
        nueva_pagina = self.pagina_actual + direccion
        
        total_items = len(self.datos_filtrados_paginacion)
        # Calcular total páginas
        total_paginas = max(1, (total_items + self.elementos_por_pagina - 1) // self.elementos_por_pagina)
        
        if 1 <= nueva_pagina <= total_paginas:
            self.pagina_actual = nueva_pagina
            self._actualizar_vista_tabla()

    def _actualizar_vista_tabla(self):
        """Renderizar items de la página actual"""
        inicio = (self.pagina_actual - 1) * self.elementos_por_pagina
        fin = inicio + self.elementos_por_pagina
        
        items_pagina = self.datos_filtrados_paginacion[inicio:fin]
        
        # Actualizar tabla (ocultando ID)
        datos_visibles = [d[1:] for d in items_pagina]
        self.tabla.limpiar()
        # Pasamos items_pagina como segundo argumento para mantener la referencia al ID oculto
        self.tabla.agregar_filas(datos_visibles, items_pagina)
        
        # Actualizar UI paginación
        total_items = len(self.datos_filtrados_paginacion)
        total_paginas = max(1, (total_items + self.elementos_por_pagina - 1) // self.elementos_por_pagina)
        
        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} de {total_paginas} | Total: {total_items}")
        
        # Estados botones
        self.btn_anterior.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_siguiente.configure(state="normal" if self.pagina_actual < total_paginas else "disabled")

    def _cambiar_vista(self, vista):
        """Cambiar entre frames de tabla"""
        if vista == "Inventario Completo":
            self.frame_tabla_bajo.pack_forget()
            self.frame_tabla_todos.pack(fill="both", expand=True)
        else:
            self.frame_tabla_todos.pack_forget()
            self.frame_tabla_bajo.pack(fill="both", expand=True)
    
    def _on_ingrediente_select(self, datos):
        # Al quitar el ID de la vista, necesitamos recuperarlo de otra forma
        # TreeViewWidget debería estar configurado para manejar una columna oculta para el ID
        # O ajustamos para usar el ID invisible que Treeview suele tener
        self.ingrediente_seleccionado = datos
    
    def refrescar_tablas(self):
        success, datos, msg = self.controller.obtener_todos_ingredientes()
        
        if success:
            self.datos_completos = datos # Guardamos copia para filtrar
            self._filtrar_resultados()   # Esto activará la paginación interna
        
        success, datos_bajo, _ = self.controller.obtener_bajo_stock_formateados()
        if success:
            # datos_bajo también trae el ID en posición 0
            datos_bajo_visibles = [d[1:] for d in datos_bajo]
            
            self.tabla_bajo_stock.limpiar()
            self.tabla_bajo_stock.agregar_filas(datos_bajo_visibles, datos_bajo)
            
    def _filtrar_resultados(self, *args):
        """Filtrar tabla principal según texto de búsqueda y paginar"""
        if self.vista_actual.get() != "Inventario Completo":
            return # Solo filtramos la tabla principal por ahora
            
        busqueda = self.entry_busqueda.get().strip().lower()
        
        datos_filtrados = []
        
        # Si no hay búsqueda, mostrar todo
        if not busqueda:
            datos_filtrados = self.datos_completos
        else:
            # Filtrar
            for item in self.datos_completos:
                # item: (id, nombre, stock_fmt, precio_fmt, min, prov, estado)
                nombre = str(item[1]).lower()
                proveedor = str(item[5]).lower() if item[5] else ""
                
                # Búsqueda parcial en nombre o proveedor
                if busqueda in nombre or busqueda in proveedor:
                    datos_filtrados.append(item)
        
        # Guardar resultado del filtro para paginación
        self.datos_filtrados_paginacion = datos_filtrados
        self.pagina_actual = 1 # Resetear a página 1 al filtrar
        
        # Renderizar vista actual
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
        """Aumentar stock de un ingrediente existente"""
        if not self.ingrediente_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Por favor selecciona el producto al que quieres agregar stock")
            return
        
        ingrediente_id = self.ingrediente_seleccionado[0]
        
        # Obtener datos reales
        success, ing, msg = self.controller.obtener_ingrediente(ingrediente_id)
        if not success or not ing:
            DialogUtils.mostrar_error("Error", "No se pudo cargar el producto.")
            return
        
        # Mostrar diálogo simple para sumar
        mensaje = f"Actualmente tienes: {ing.cantidad} {ing.unidad}\n\n¿Cuánto TE LLEGÓ hoy?"
        
        # Creamos un dialogo especial para sumar cantidad
        # Usamos FormDialog con un solo campo
        campos = {
            'cantidad_recibida': {
                'label': f'Cantidad Recibida ({ing.unidad})', 
                'type': 'number', 
                'required': True, 
                'min': 0.001
            }
        }
        
        def procesar(valores):
            try:
                recibida = float(valores.get('cantidad_recibida', 0))
                # La validación <= 0 ya la hace FormDialog (min=0.001)
                
                nueva_cantidad_total = ing.cantidad + recibida
                
                # Actualizar en BD
                success, _, msg = self.controller.ajustar_cantidad(ingrediente_id, nueva_cantidad_total)
                
                if success:
                    DialogUtils.mostrar_exito(
                        "Stock Actualizado", 
                        f"¡Listo! Sumamos {recibida}.\nNuevo Total: {nueva_cantidad_total} {ing.unidad}"
                    )
                    self.refrescar_tablas()
                else:
                    DialogUtils.mostrar_error("Error al guardar", msg)
            except ValueError:
                # Este caso es muy raro porque FormDialog ya valida números
                pass

        FormDialog(self.winfo_toplevel(), f"Entrada de {ing.nombre}", campos, procesar)

    def editar_ingrediente(self):
        print("Seleccionado:", self.ingrediente_seleccionado)

        if not self.ingrediente_seleccionado:
            DialogUtils.mostrar_advertencia(
                "Advertencia",
                "Selecciona un ingrediente de la tabla primero"
            )
            return

        ingrediente_id = self.ingrediente_seleccionado[0]
        
        # Obtener datos reales desde base de datos usando el ID
        success, ing, msg = self.controller.obtener_ingrediente(ingrediente_id)
        if not success or not ing:
             DialogUtils.mostrar_error("Error", f"No se pudo cargar el ingrediente: {msg}")
             return

        unidades = self.controller.obtener_unidades_disponibles()

        campos = {
            'nombre': {'label': 'Nombre del Producto', 'type': 'text', 'value': ing.nombre, 'required': True},
            'unidad': {'label': 'Unidad (Kilos, Litros...)', 'type': 'dropdown', 'options': unidades, 'editable': True, 'value': ing.unidad, 'required': True},
            'precio_unitario': {'label': 'Costo Unitario ($)', 'type': 'number', 'value': ing.precio_unitario, 'min': 0, 'required': True},
            'cantidad': {'label': '¿Cuánto tienes HOY en la cocina?', 'type': 'number', 'value': ing.cantidad, 'min': 0, 'required': True}, 
            'cantidad_minima': {'label': 'AVISARME cuando quede menos de:', 'type': 'number', 'value': ing.cantidad_minima, 'min': 0, 'required': True},
            'proveedor': {'label': 'Proveedor', 'type': 'text', 'value': ing.proveedor, 'required': True}
        }

        def procesar(valores):
            # 1. Actualizar datos básicos (nombre, precio, etc)
            success, _, msg = self.controller.actualizar_ingrediente(
                ingrediente_id=ingrediente_id,
                nombre=valores.get('nombre'),
                unidad=valores.get('unidad'),
                precio_unitario=valores.get('precio_unitario'),
                cantidad_minima=valores.get('cantidad_minima'),
                proveedor=valores.get('proveedor')
            )
            
            # 2. Actualizar CANTIDAD (Stock) si se modificó
            if success and valores.get('cantidad') is not None:
                nueva_cantidad = float(valores.get('cantidad'))
                if nueva_cantidad != ing.cantidad:
                     self.controller.ajustar_cantidad(ingrediente_id, nueva_cantidad)

            if success:
                DialogUtils.mostrar_exito("Éxito", "Ingrediente actualizado")
                self.refrescar_tablas()
            else:
                DialogUtils.mostrar_error("Error", msg)

        FormDialog(self.winfo_toplevel(), "Editar Ingrediente", campos, procesar)