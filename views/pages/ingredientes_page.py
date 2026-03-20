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
        
        self._crear_ui()
        self.refrescar_tablas()
    
    def _crear_ui(self):
        """Crear interfaz"""
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"])
        frame_header.pack(fill="x", padx=10, pady=10)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text="📦 Gestión de Ingredientes",
            text_color=config.COLORS["text_light"],
            font=("Arial", 18, "bold")
        )
        titulo.pack(side="left", padx=10, pady=10)
        
        btn_nuevo = ctk.CTkButton(
            frame_header,
            text="➕ Nuevo",
            command=self.crear_ingrediente,
            fg_color=config.COLORS["success"],
            hover_color="#45a049"
        )
        btn_nuevo.pack(side="right", padx=5, pady=10)
        
        btn_editar = ctk.CTkButton(
            frame_header,
            text="✏️ Editar",
            command=self.editar_ingrediente,
            fg_color=config.COLORS["warning"],
            hover_color="#e68900"
        )
        btn_editar.pack(side="right", padx=5, pady=10)
        
        # Pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab: Todos
        tab_todos = self.tabview.add("Todos")
        frame_tabla = ctk.CTkFrame(tab_todos)
        frame_tabla.pack(fill="both", expand=True)
        
        self.tabla = TreeViewWidget(
            frame_tabla,
            columnas=["ID", "Nombre", "Cantidad", "Precio", "Proveedor", "Estado", "Stock"],
            altura=20
        )
        self.tabla.pack(fill="both", expand=True)
        self.tabla.set_on_select(self._on_ingrediente_select)
        
        # Tab: Bajo Stock
        tab_bajo = self.tabview.add("⚠️ Bajo Stock")
        frame_bajo = ctk.CTkFrame(tab_bajo)
        frame_bajo.pack(fill="both", expand=True)
        
        self.tabla_bajo_stock = TreeViewWidget(
            frame_bajo,
            columnas=["ID", "Nombre", "Stock Actual", "Precio", "Estado"],
            altura=20
        )
        self.tabla_bajo_stock.pack(fill="both", expand=True)
    
    def _on_ingrediente_select(self, datos):
        self.ingrediente_seleccionado = datos
    
    def refrescar_tablas(self):
        success, datos, msg = self.controller.obtener_todos_ingredientes_formateados()
        if success:
            self.tabla.limpiar()
            self.tabla.agregar_filas(datos)
        
        success, datos_bajo, _ = self.controller.obtener_bajo_stock_formateados()
        if success:
            self.tabla_bajo_stock.limpiar()
            self.tabla_bajo_stock.agregar_filas(datos_bajo)
    
    def crear_ingrediente(self):
        unidades = self.controller.obtener_unidades_disponibles()
        
        campos = {
            'nombre': {'label': 'Nombre', 'type': 'text'},
            'unidad': {'label': 'Unidad', 'type': 'dropdown', 'options': unidades},
            'precio_unitario': {'label': 'Precio Unitario', 'type': 'number'},
            'cantidad': {'label': 'Cantidad Inicial', 'type': 'number'},
            'cantidad_minima': {'label': 'Cantidad Mínima', 'type': 'number'},
            'proveedor': {'label': 'Proveedor', 'type': 'text'}
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
    
    def editar_ingrediente(self):
        if not self.ingrediente_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un ingrediente")
            return
        
        DialogUtils.mostrar_exito("Funcionalidad", "Edición en progreso")
