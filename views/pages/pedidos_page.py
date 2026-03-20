"""
Página: Gestión de Pedidos
"""
import customtkinter as ctk
from controllers.pedidos_controller import PedidosController
from controllers.clientes_controller import ClientesController
from controllers.platos_controller import PlatosController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils
import config

class PedidosPage(ctk.CTkFrame):
    """Módulo de Pedidos"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controller_pedidos = PedidosController()
        self.controller_clientes = ClientesController()
        self.controller_platos = PlatosController()
        self.tabla = None
        self.pedido_seleccionado = None
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz"""
        # Header
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"])
        frame_header.pack(fill="x", padx=10, pady=10)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text="📋 Gestión de Pedidos",
            text_color=config.COLORS["text_light"],
            font=("Arial", 18, "bold")
        )
        titulo.pack(side="left", padx=10, pady=10)
        
        btn_nuevo = ctk.CTkButton(
            frame_header,
            text="➕ Nuevo Pedido",
            command=self.crear_pedido,
            fg_color=config.COLORS["success"],
            hover_color="#45a049"
        )
        btn_nuevo.pack(side="right", padx=5, pady=10)
        
        btn_detalles = ctk.CTkButton(
            frame_header,
            text="👁️ Detalles",
            command=self.ver_detalles,
            fg_color=config.COLORS["primary"],
            hover_color="#0d47a1"
        )
        btn_detalles.pack(side="right", padx=5, pady=10)
        
        # Tabla
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabla = TreeViewWidget(
            frame_tabla,
            columnas=["ID", "Cliente", "Mesa", "Total", "Estado", "Fecha"],
            altura=20
        )
        self.tabla.pack(fill="both", expand=True)
        self.tabla.set_on_select(self._on_pedido_select)
        
        # Info
        frame_info = ctk.CTkFrame(self, fg_color=config.COLORS["light_bg"])
        frame_info.pack(fill="x", padx=10, pady=10)
        
        self.label_info = ctk.CTkLabel(
            frame_info,
            text="Selecciona un pedido para ver detalles",
            text_color=config.COLORS["text_dark"]
        )
        self.label_info.pack(padx=10, pady=10)
    
    def _on_pedido_select(self, datos):
        """Cuando se selecciona un pedido"""
        self.pedido_seleccionado = datos
        if datos:
            self.label_info.configure(text=f"Pedido #{datos[0]} - {datos[1]} (Total: {datos[3]})")
    
    def refrescar_tabla(self):
        """Refrescar tabla"""
        success, datos, msg = self.controller_pedidos.obtener_todos_pedidos_formateados()
        if success:
            self.tabla.limpiar()
            self.tabla.agregar_filas(datos)
        else:
            DialogUtils.mostrar_error("Error", msg)
    
    def crear_pedido(self):
        """Crear nuevo pedido"""
        clientes_ids, clientes_labels = self.controller_clientes.obtener_selectorlist()
        
        if not clientes_ids:
            DialogUtils.mostrar_advertencia("Advertencia", "No hay clientes disponibles")
            return
        
        # Crear ventana dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Pedido")
        dialog.geometry("400x300")
        dialog.attributes('-topmost', True)  # Mantener ventana en el frente
        dialog.grab_set()  # Hacerla modal
        
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        label = ctk.CTkLabel(frame, text="Seleccionar Cliente:")
        label.pack(pady=(0, 10))
        
        combo = ctk.CTkComboBox(frame, values=clientes_labels, state="readonly")
        combo.pack(fill="x", pady=(0, 20))
        
        def procesar():
            idx = combo.current()
            if idx >= 0:
                cliente_id = clientes_ids[idx]
                # Aquí iría lógica para crear pedido y agregar platos
                DialogUtils.mostrar_exito("Éxito", "Esta funcionalidad se completará pronto")
                dialog.destroy()
                # self.refrescar_tabla()
        
        btn = ctk.CTkButton(frame, text="Crear", command=procesar, fg_color=config.COLORS["success"])
        btn.pack(pady=10)
    
    def ver_detalles(self):
        """Ver detalles del pedido"""
        if not self.pedido_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un pedido")
            return
        
        DialogUtils.mostrar_exito("Detalles", f"Pedido #{self.pedido_seleccionado[0]}")
    
    def editar_estado(self):
        """Editar estado del pedido"""
        if not self.pedido_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un pedido")
            return
        
        # Implementar cambio de estado
        DialogUtils.mostrar_exito("Éxito", "Estado actualizado")
