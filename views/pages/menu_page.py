"""
Página: Gestión de Menú (Platos)
"""
import customtkinter as ctk
from controllers.platos_controller import PlatosController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils, FormDialog
import config

class MenuPage(ctk.CTkFrame):
    """Módulo de Menú/Platos"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controller = PlatosController()
        self.tabla = None
        self.plato_seleccionado = None
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz"""
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"])
        frame_header.pack(fill="x", padx=10, pady=10)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text="🍖 Menú de Platos",
            text_color=config.COLORS["text_light"],
            font=("Arial", 18, "bold")
        )
        titulo.pack(side="left", padx=10, pady=10)
        
        btn_nuevo = ctk.CTkButton(
            frame_header,
            text="➕ Nuevo Plato",
            command=self.crear_plato,
            fg_color=config.COLORS["success"],
            hover_color="#45a049"
        )
        btn_nuevo.pack(side="right", padx=5, pady=10)
        
        btn_editar = ctk.CTkButton(
            frame_header,
            text="✏️ Editar",
            command=self.editar_plato,
            fg_color=config.COLORS["warning"],
            hover_color="#e68900"
        )
        btn_editar.pack(side="right", padx=5, pady=10)
        
        btn_eliminar = ctk.CTkButton(
            frame_header,
            text="🗑️ Eliminar",
            command=self.eliminar_plato,
            fg_color=config.COLORS["danger"],
            hover_color="#da190b"
        )
        btn_eliminar.pack(side="right", padx=5, pady=10)
        
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabla = TreeViewWidget(
            frame_tabla,
            columnas=["ID", "Nombre", "Precio", "Categoría", "Tiempo Prep.", "Estado", "Ingredientes"],
            altura=20
        )
        self.tabla.pack(fill="both", expand=True)
        self.tabla.set_on_select(self._on_plato_select)
        
        frame_info = ctk.CTkFrame(self, fg_color=config.COLORS["light_bg"])
        frame_info.pack(fill="x", padx=10, pady=10)
        
        self.label_info = ctk.CTkLabel(
            frame_info,
            text="Selecciona un plato",
            text_color=config.COLORS["text_dark"]
        )
        self.label_info.pack(padx=10, pady=10)
    
    def _on_plato_select(self, datos):
        self.plato_seleccionado = datos
        if datos:
            self.label_info.configure(text=f"{datos[1]} - ${datos[2]}")
    
    def refrescar_tabla(self):
        success, datos, msg = self.controller.obtener_todos_platos_formateados()
        if success:
            self.tabla.limpiar()
            self.tabla.agregar_filas(datos)
        else:
            DialogUtils.mostrar_error("Error", msg)
    
    def crear_plato(self):
        categorias = self.controller.obtener_categorias_disponibles()
        
        campos = {
            'nombre': {'label': 'Nombre', 'type': 'text'},
            'precio': {'label': 'Precio', 'type': 'number'},
            'categoria': {'label': 'Categoría', 'type': 'dropdown', 'options': categorias},
            'descripcion': {'label': 'Descripción', 'type': 'textarea'},
            'tiempo_preparacion': {'label': 'Tiempo Preparación (min)', 'type': 'number'}
        }
        
        def procesar(valores):
            success, plato, msg = self.controller.crear_plato(
                valores.get('nombre'),
                valores.get('precio', 0),
                valores.get('categoria'),
                valores.get('descripcion'),
                int(valores.get('tiempo_preparacion', 15))
            )
            
            if success:
                DialogUtils.mostrar_exito("Éxito", "Plato creado")
                self.refrescar_tabla()
            else:
                DialogUtils.mostrar_error("Error", msg)
        
        FormDialog(self.winfo_toplevel(), "Nuevo Plato", campos, procesar)
    
    def editar_plato(self):
        if not self.plato_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un plato")
            return
        
        DialogUtils.mostrar_exito("Funcionalidad", "Edición en progreso")
    
    def eliminar_plato(self):
        if not self.plato_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un plato")
            return
        
        if DialogUtils.pedir_confirmacion("Confirmar", "¿Eliminar plato?"):
            success, _, msg = self.controller.eliminar_plato(self.plato_seleccionado[0])
            
            if success:
                DialogUtils.mostrar_exito("Éxito", "Plato eliminado")
                self.refrescar_tabla()
            else:
                DialogUtils.mostrar_error("Error", msg)
