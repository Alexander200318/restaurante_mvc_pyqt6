"""
Página: Gestión de Empleados
"""
import customtkinter as ctk
from controllers.empleados_controller import EmpleadosController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils, FormDialog
import config

class EmpleadosPage(ctk.CTkFrame):
    """Módulo de Empleados"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controller = EmpleadosController()
        self.tabla = None
        self.empleado_seleccionado = None
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz"""
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"])
        frame_header.pack(fill="x", padx=10, pady=10)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text="👥 Gestión de Empleados",
            text_color=config.COLORS["text_light"],
            font=("Arial", 18, "bold")
        )
        titulo.pack(side="left", padx=10, pady=10)
        
        btn_nuevo = ctk.CTkButton(
            frame_header,
            text="➕ Nuevo",
            command=self.crear_empleado,
            fg_color=config.COLORS["success"],
            hover_color="#45a049"
        )
        btn_nuevo.pack(side="right", padx=5, pady=10)
        
        btn_editar = ctk.CTkButton(
            frame_header,
            text="✏️ Editar",
            command=self.editar_empleado,
            fg_color=config.COLORS["warning"],
            hover_color="#e68900"
        )
        btn_editar.pack(side="right", padx=5, pady=10)
        
        btn_eliminar = ctk.CTkButton(
            frame_header,
            text="🗑️ Desactivar",
            command=self.eliminar_empleado,
            fg_color=config.COLORS["danger"],
            hover_color="#da190b"
        )
        btn_eliminar.pack(side="right", padx=5, pady=10)
        
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabla = TreeViewWidget(
            frame_tabla,
            columnas=["ID", "Nombre", "Puesto", "Teléfono", "Email", "Salario", "Estado"],
            altura=20
        )
        self.tabla.pack(fill="both", expand=True)
        self.tabla.set_on_select(self._on_empleado_select)
        
        frame_info = ctk.CTkFrame(self, fg_color=config.COLORS["light_bg"])
        frame_info.pack(fill="x", padx=10, pady=10)
        
        self.label_info = ctk.CTkLabel(
            frame_info,
            text="Selecciona un empleado",
            text_color=config.COLORS["text_dark"]
        )
        self.label_info.pack(padx=10, pady=10)
    
    def _on_empleado_select(self, datos):
        self.empleado_seleccionado = datos
        if datos:
            self.label_info.configure(text=f"{datos[1]} - {datos[2]}")
    
    def refrescar_tabla(self):
        success, datos, msg = self.controller.obtener_todos_empleados_formateados()
        if success:
            self.tabla.limpiar()
            self.tabla.agregar_filas(datos)
        else:
            DialogUtils.mostrar_error("Error", msg)
    
    def crear_empleado(self):
        puestos = self.controller.obtener_puestos_disponibles()
        
        campos = {
            'nombre': {'label': 'Nombre', 'type': 'text'},
            'puesto': {'label': 'Puesto', 'type': 'dropdown', 'options': puestos},
            'telefono': {'label': 'Teléfono', 'type': 'text'},
            'email': {'label': 'Email', 'type': 'text'},
            'salario': {'label': 'Salario', 'type': 'number'}
        }
        
        def procesar(valores):
            success, emp, msg = self.controller.crear_empleado(
                valores.get('nombre'),
                valores.get('puesto'),
                valores.get('telefono'),
                valores.get('email'),
                valores.get('salario')
            )
            
            if success:
                DialogUtils.mostrar_exito("Éxito", "Empleado creado")
                self.refrescar_tabla()
            else:
                DialogUtils.mostrar_error("Error", msg)
        
        FormDialog(self.winfo_toplevel(), "Nuevo Empleado", campos, procesar)
    
    def editar_empleado(self):
        if not self.empleado_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un empleado")
            return
        
        DialogUtils.mostrar_exito("Funcionalidad", "Edición en progreso")
    
    def eliminar_empleado(self):
        if not self.empleado_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un empleado")
            return
        
        if DialogUtils.pedir_confirmacion("Confirmar", "¿Desactivar empleado?"):
            success, _, msg = self.controller.eliminar_empleado(self.empleado_seleccionado[0])
            
            if success:
                DialogUtils.mostrar_exito("Éxito", "Empleado desactivado")
                self.refrescar_tabla()
            else:
                DialogUtils.mostrar_error("Error", msg)
