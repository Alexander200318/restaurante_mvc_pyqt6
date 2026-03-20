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
        self.label_info_nombre = None
        self.label_info_puesto = None
        self.label_info_telefono = None
        self.label_info_email = None
        self.label_info_salario = None
        self.label_info_estado = None
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz con diseño mejorado - Colores naranjas"""
        # Header
        frame_header = ctk.CTkFrame(self, fg_color="#EA580C", height=80)
        frame_header.pack(fill="x", padx=0, pady=0)
        frame_header.pack_propagate(False)
        
        # Título
        titulo = ctk.CTkLabel(
            frame_header,
            text="👥 Gestión de Empleados",
            text_color="#ffffff",
            font=("Helvetica", 20, "bold")
        )
        titulo.pack(side="left", padx=15, pady=15)
        
        # Botón nuevo
        btn_nuevo = ctk.CTkButton(
            frame_header,
            text="➕ Nuevo Empleado",
            command=self.crear_empleado,
            fg_color="#ff8c42",
            hover_color="#ff7724",
            text_color="white",
            font=("Helvetica", 12, "bold")
        )
        btn_nuevo.pack(side="right", padx=15, pady=15)
        
        # Separador
        sep = ctk.CTkFrame(self, fg_color="#ffc9a1", height=1)
        sep.pack(fill="x", padx=0, pady=0)
        
        # Contenedor principal (tabla + panel)
        contenido = ctk.CTkFrame(self, fg_color="#fffaf5")
        contenido.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame tabla (izquierda)
        frame_tabla = ctk.CTkFrame(contenido, fg_color="transparent")
        frame_tabla.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Label tabla
        lbl_tabla = ctk.CTkLabel(
            frame_tabla,
            text="📋 Empleados",
            text_color="#EA580C",
            font=("Helvetica", 13, "bold")
        )
        lbl_tabla.pack(anchor="w", padx=5, pady=(0, 5))
        
        # Tabla
        self.tabla = TreeViewWidget(
            frame_tabla,
            columnas=["ID", "Nombre", "Puesto", "Teléfono", "Email", "Salario", "Estado"],
            altura=20,
            font_size=11,
            heading_font_size=11,
            row_height=30
        )
        self.tabla.pack(fill="both", expand=True)
        self.tabla.set_on_select(self._on_empleado_select)
        
        # Panel información (derecha)
        self._crear_panel_informacion(contenido)
    
    def _crear_panel_informacion(self, parent):
        """Crear panel lateral con información del empleado - Colores naranjas"""
        panel = ctk.CTkFrame(parent, fg_color="#ffffff", width=320, corner_radius=10)
        panel.pack(side="right", fill="y", padx=10, pady=10)
        panel.pack_propagate(False)
        
        # Header del panel con color naranja claro
        header_panel = ctk.CTkFrame(panel, fg_color="#ffebdb", corner_radius=10, height=50)
        header_panel.pack(fill="x", padx=0, pady=0)
        header_panel.pack_propagate(False)
        
        lbl_header = ctk.CTkLabel(
            header_panel,
            text="👤 Detalles del Empleado",
            text_color="#EA580C",
            font=("Helvetica", 12, "bold")
        )
        lbl_header.pack(pady=12)
        
        # Contenedor scrollable para información
        frame_scroll = ctk.CTkScrollableFrame(panel, fg_color="#ffffff")
        frame_scroll.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Frame para datos del empleado con tarjetas
        self.frame_datos = ctk.CTkFrame(frame_scroll, fg_color="transparent")
        self.frame_datos.pack(fill="x", padx=0, pady=0)
        
        # Labels para información (se actualizarán dinámicamente)
        self.label_info_nombre = self._crear_card_info(self.frame_datos, "👤 Nombre", "-")
        self.label_info_puesto = self._crear_card_info(self.frame_datos, "💼 Puesto", "-")
        self.label_info_telefono = self._crear_card_info(self.frame_datos, "📱 Teléfono", "-")
        self.label_info_email = self._crear_card_info(self.frame_datos, "📧 Email", "-")
        self.label_info_salario = self._crear_card_info(self.frame_datos, "💰 Salario", "-")
        self.label_info_estado = self._crear_card_info(self.frame_datos, "🔖 Estado", "-")
        
        # Separador visual
        sep = ctk.CTkFrame(frame_scroll, fg_color="#EA580C", height=1)
        sep.pack(fill="x", padx=0, pady=15)
        
        # Botones de acción con mejor diseño
        frame_botones = ctk.CTkFrame(frame_scroll, fg_color="transparent")
        frame_botones.pack(fill="x", padx=0, pady=10)
        
        btn_editar = ctk.CTkButton(
            frame_botones,
            text="✏️ Editar",
            command=self.editar_empleado,
            fg_color="#ff8c42",
            hover_color="#ff7724",
            text_color="white",
            font=("Helvetica", 11, "bold"),
            corner_radius=8
        )
        btn_editar.pack(fill="x", pady=5)
        
        btn_eliminar = ctk.CTkButton(
            frame_botones,
            text="🗑️ Eliminar Empleado",
            command=self.eliminar_empleado,
            fg_color="#ff6b6b",
            hover_color="#ff5252",
            text_color="white",
            font=("Helvetica", 11, "bold"),
            corner_radius=8
        )
        btn_eliminar.pack(fill="x", pady=5)
    
    def _crear_card_info(self, parent, etiqueta, valor):
        """Crear una tarjeta de información mejorada"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="x", pady=15)
        
        # Marco interno con padding
        frame_contenido = ctk.CTkFrame(card, fg_color="white", corner_radius=8)
        frame_contenido.pack(fill="x", padx=12, pady=10)
        
        # Etiqueta
        lbl_etiqueta = ctk.CTkLabel(
            frame_contenido,
            text=etiqueta,
            text_color="#EA580C",
            font=("Helvetica", 9, "bold")
        )
        lbl_etiqueta.pack(anchor="w", pady=(0, 4))
        
        # Valor
        lbl_valor = ctk.CTkLabel(
            frame_contenido,
            text=valor,
            text_color="#ff9d5c",
            font=("Helvetica", 11, "bold")
        )
        lbl_valor.pack(anchor="w")
        
        return lbl_valor
    
    def _on_empleado_select(self, datos):
        """Callback cuando se selecciona un empleado"""
        self.empleado_seleccionado = datos
        self._actualizar_panel()
    
    def _actualizar_panel(self):
        """Actualizar panel con información del empleado seleccionado"""
        if not self.empleado_seleccionado:
            # Limpiar panel
            self.label_info_nombre.configure(text="-", text_color="#ff9d5c")
            self.label_info_puesto.configure(text="-", text_color="#ff9d5c")
            self.label_info_telefono.configure(text="-", text_color="#ff9d5c")
            self.label_info_email.configure(text="-", text_color="#ff9d5c")
            self.label_info_salario.configure(text="-", text_color="#ff9d5c")
            self.label_info_estado.configure(text="-", text_color="#ff9d5c")
            return
        
        datos = self.empleado_seleccionado
        # Extraer datos (orden según columnas: ID, Nombre, Puesto, Teléfono, Email, Salario, Estado)
        id_emp = datos[0]
        nombre = datos[1] if len(datos) > 1 else "-"
        puesto = datos[2] if len(datos) > 2 else "-"
        telefono = datos[3] if len(datos) > 3 else "-"
        email = datos[4] if len(datos) > 4 else "-"
        salario = datos[5] if len(datos) > 5 else "-"
        estado = datos[6] if len(datos) > 6 else "-"
        
        # Actualizar labels
        self.label_info_nombre.configure(text=str(nombre), text_color="#ff9d5c")
        self.label_info_puesto.configure(text=str(puesto), text_color="#ff9d5c")
        self.label_info_telefono.configure(text=str(telefono), text_color="#ff9d5c")
        self.label_info_email.configure(text=str(email), text_color="#ff9d5c")
        self.label_info_salario.configure(text=str(salario), text_color="#ff9d5c")
        
        # Actualizar color de estado
        color_estado = config.COLORS["success"] if estado.lower() == "activo" else config.COLORS["danger"]
        self.label_info_estado.configure(text=str(estado), text_color=color_estado)
    
    def refrescar_tabla(self):
        """Refrescar tabla de empleados"""
        success, datos, msg = self.controller.obtener_todos_empleados_formateados()
        if success:
            self.tabla.limpiar()
            for dato in datos:
                self.tabla.agregar_fila(dato, id_datos=dato)
            self.empleado_seleccionado = None
            self._actualizar_panel()
        else:
            DialogUtils.mostrar_error("Error", msg)
    
    def crear_empleado(self):
        puestos = self.controller.obtener_puestos_disponibles()
        
        campos = {
            'nombre': {'label': '👤 Nombre', 'type': 'text'},
            'puesto': {'label': '💼 Puesto', 'type': 'dropdown', 'options': puestos},
            'telefono': {'label': '📱 Teléfono', 'type': 'text'},
            'email': {'label': '📧 Email', 'type': 'text'},
            'salario': {'label': '💰 Salario', 'type': 'number'}
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
        
        FormDialog(self.winfo_toplevel(), "➕ Nuevo Empleado", campos, procesar)
    
    def editar_empleado(self):
        """Editar empleado seleccionado"""
        if not self.empleado_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un empleado para editar")
            return
        
        id_emp = self.empleado_seleccionado[0]
        nombre = self.empleado_seleccionado[1]
        puesto = self.empleado_seleccionado[2]
        telefono = self.empleado_seleccionado[3]
        email = self.empleado_seleccionado[4]
        salario_str = self.empleado_seleccionado[5]  # Viene como "$xxxx.xx"
        estado = self.empleado_seleccionado[6]
        
        # Extraer número del formato "$xxxx.xx"
        try:
            salario_num = float(salario_str.replace("$", "").replace(",", "").strip()) if salario_str and salario_str != "—" else ""
        except ValueError:
            salario_num = ""
        
        puestos = self.controller.obtener_puestos_disponibles()
        estados = ["ACTIVO", "INACTIVO"]
        
        campos = {
            'nombre': {'label': '👤 Nombre', 'type': 'text', 'value': nombre},
            'puesto': {'label': '💼 Puesto', 'type': 'dropdown', 'options': puestos, 'value': puesto},
            'telefono': {'label': '📱 Teléfono', 'type': 'text', 'value': telefono},
            'email': {'label': '📧 Email', 'type': 'text', 'value': email},
            'salario': {'label': '💰 Salario', 'type': 'number', 'value': salario_num},
            'estado': {'label': '🔖 Estado', 'type': 'dropdown', 'options': estados, 'value': estado}
        }
        
        def procesar(valores):
            # Actualizar datos básicos del empleado
            success, _, msg = self.controller.actualizar_empleado(
                id_emp,
                valores.get('nombre'),
                valores.get('puesto'),
                valores.get('telefono'),
                valores.get('email'),
                valores.get('salario')
            )
            
            if not success:
                DialogUtils.mostrar_error("Error", msg)
                return
            
            # Actualizar estado si cambió
            if valores.get('estado') and valores.get('estado') != estado:
                success_estado, _, msg_estado = self.controller.cambiar_estado_empleado(
                    id_emp,
                    valores.get('estado')
                )
                if not success_estado:
                    DialogUtils.mostrar_error("Error al actualizar estado", msg_estado)
                    return
            
            DialogUtils.mostrar_exito("Éxito", "Empleado actualizado")
            self.refrescar_tabla()
        
        FormDialog(self.winfo_toplevel(), "✏️ Editar Empleado", campos, procesar)
    
    def eliminar_empleado(self):
        if not self.empleado_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un empleado para eliminar")
            return
        
        nombre_empleado = self.empleado_seleccionado[1]
        
        if DialogUtils.pedir_confirmacion("Confirmar Eliminación", f"¿Eliminar permanentemente a {nombre_empleado}?"):
            success, _, msg = self.controller.eliminar_empleado(self.empleado_seleccionado[0])
            
            if success:
                DialogUtils.mostrar_exito("Éxito", f"Empleado {nombre_empleado} eliminado")
                self.refrescar_tabla()
            else:
                DialogUtils.mostrar_error("Error", msg)
