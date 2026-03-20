"""
Componentes de diálogo reutilizables
"""
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from typing import Callable, Optional

class DialogUtils:
    """Utilidades para mostrar diálogos"""

    @staticmethod
    def _resolver_parent(parent=None):
        """Resolver parent activo para que los messagebox salgan al frente."""
        if parent is not None:
            try:
                if parent.winfo_exists():
                    return parent
            except Exception:
                pass

        root = tk._default_root
        if root is not None:
            try:
                focus_widget = root.focus_get()
                if focus_widget is not None:
                    return focus_widget.winfo_toplevel()
            except Exception:
                pass
        return root

    @staticmethod
    def _preparar_parent(parent=None):
        """Llevar parent al frente antes de abrir un diálogo."""
        resolved_parent = DialogUtils._resolver_parent(parent)
        if resolved_parent is not None:
            try:
                resolved_parent.lift()
                resolved_parent.focus_force()
            except Exception:
                pass
        return resolved_parent
    
    @staticmethod
    def mostrar_exito(titulo: str, mensaje: str, parent=None):
        """Mostrar diálogo de éxito"""
        resolved_parent = DialogUtils._preparar_parent(parent)
        messagebox.showinfo(titulo, mensaje, parent=resolved_parent)
    
    @staticmethod
    def mostrar_error(titulo: str, mensaje: str, parent=None):
        """Mostrar diálogo de error"""
        resolved_parent = DialogUtils._preparar_parent(parent)
        messagebox.showerror(titulo, mensaje, parent=resolved_parent)
    
    @staticmethod
    def mostrar_advertencia(titulo: str, mensaje: str, parent=None):
        """Mostrar diálogo de advertencia"""
        resolved_parent = DialogUtils._preparar_parent(parent)
        messagebox.showwarning(titulo, mensaje, parent=resolved_parent)
    
    @staticmethod
    def pedir_confirmacion(titulo: str, mensaje: str, parent=None) -> bool:
        """Pedir confirmación (Sí/No)"""
        resolved_parent = DialogUtils._preparar_parent(parent)
        return messagebox.askyesno(titulo, mensaje, parent=resolved_parent)
    
    @staticmethod
    def pedir_okcancel(titulo: str, mensaje: str, parent=None) -> bool:
        """Pedir OK/Cancelar"""
        resolved_parent = DialogUtils._preparar_parent(parent)
        return messagebox.askokcancel(titulo, mensaje, parent=resolved_parent)

class FormDialog(ctk.CTkToplevel):
    """Diálogo de formulario genérico"""
    
    def __init__(self, parent, titulo: str, campos: dict, on_submit: Callable):
        """
        campos: {
            'nombre_campo': {'label': 'Etiqueta', 'type': 'text'|'number'|'dropdown', 
                            'options': [opciones si es dropdown]},
            ...
        }
        on_submit: función que recibe dict de valores
        """
        super().__init__(parent)
        self.title(titulo)
        self.geometry("400x300")
        self.resizable(False, False)
        
        self.campos = campos
        self.on_submit = on_submit
        self.valores = {}
        self.widgets = {}
        
        self._crear_formulario()
        
        # Centrar en pantalla
        self.update()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Modal
        self.attributes('-topmost', True)  # Mantener en el frente
        self.grab_set()
    
    def _crear_formulario(self):
        """Crear widgets del formulario"""
        frame = ctk.CTkScrollableFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for nombre_campo, config in self.campos.items():
            # Label
            label = ctk.CTkLabel(frame, text=config.get('label', nombre_campo) + ":")
            label.pack(anchor="w", pady=(10, 0))
            
            # Widget input según tipo
            tipo = config.get('type', 'text')
            valor_inicial = config.get('value', '')
            
            if tipo == 'text':
                widget = ctk.CTkEntry(frame)
                if valor_inicial:
                    widget.insert(0, str(valor_inicial))
                widget.pack(fill="x", pady=(0, 5))
            
            elif tipo == 'number':
                widget = ctk.CTkEntry(frame)
                if valor_inicial:
                    widget.insert(0, str(valor_inicial))
                widget.pack(fill="x", pady=(0, 5))
            
            elif tipo == 'dropdown':
                opciones = config.get('options', [])
                widget = ctk.CTkComboBox(frame, values=opciones, state="readonly")
                if valor_inicial:
                    widget.set(str(valor_inicial))
                widget.pack(fill="x", pady=(0, 5))
            
            elif tipo == 'textarea':
                widget = ctk.CTkTextbox(frame, height=60)
                if valor_inicial:
                    widget.insert("1.0", str(valor_inicial))
                widget.pack(fill="x", pady=(0, 5))
            
            else:
                continue
            
            self.widgets[nombre_campo] = widget
        
        # Botones
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(fill="x", padx=10, pady=10)
        
        btn_ok = ctk.CTkButton(
            frame_botones,
            text="Enviar",
            command=self._on_ok,
            fg_color="#4caf50",
            hover_color="#45a049"
        )
        btn_ok.pack(side="left", padx=5)
        
        btn_cancel = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=self.destroy,
            fg_color="#f44336",
            hover_color="#da190b"
        )
        btn_cancel.pack(side="left", padx=5)
    
    def _on_ok(self):
        """Procesar envío"""
        # Recopilar valores
        for nombre, widget in self.widgets.items():
            tipo = self.campos[nombre].get('type', 'text')
            try:
                if tipo == 'textarea':
                    valor = widget.get("1.0", "end-1c").strip()
                else:
                    valor = widget.get().strip()
                
                if tipo == 'number' and valor:
                    valor = float(valor)
                
                self.valores[nombre] = valor if valor else None
            except ValueError:
                DialogUtils.mostrar_error("Error", f"Valor inválido en {nombre}", parent=self)
                return
        
        # Llamar callback
        self.on_submit(self.valores)
        self.destroy()


class PlatoActionDialog(ctk.CTkToplevel):
    """Diálogo de acciones rápidas para un plato (Editar/Eliminar)"""
    
    def __init__(self, parent, plato_datos: tuple, on_editar: callable, on_eliminar: callable):
        """
        plato_datos: (id, nombre, precio, categoria, tiempo, estado, ingredientes)
        on_editar: callback cuando presione Editar
        on_eliminar: callback cuando presione Eliminar
        """
        super().__init__(parent)
        self.parent = parent
        self.title("Acciones del Plato")
        self.geometry("450x320")
        self.resizable(False, False)
        
        # Importar colores antes de crear UI
        import config
        self.configure(fg_color=config.COLORS["light_bg"])
        
        self.plato_datos = plato_datos
        self.on_editar = on_editar
        self.on_eliminar = on_eliminar
        
        self._crear_ui()
        
        # Centrar en pantalla
        self.update()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Modal
        self.attributes('-topmost', True)
        self.grab_set()
    
    def _crear_ui(self):
        """Crear interfaz del diálogo"""
        import config
        
        # Header con color
        header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"], height=70)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        ctk.CTkLabel(
            header_content,
            text="🍽️ Acciones del Plato",
            font=("Helvetica", 16, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            header_content,
            text=self.plato_datos[1],
            font=("Helvetica", 12),
            text_color=config.COLORS["text_light"]
        ).pack(anchor="w")
        
        # Contenido
        content = ctk.CTkFrame(self, fg_color=config.COLORS["light_bg"])
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Información del plato
        info_frame = ctk.CTkFrame(content, fg_color=config.COLORS["dark_bg"], corner_radius=10, border_width=1, border_color=config.COLORS["border"])
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Grid de información
        info_items = [
            ("💵", "Precio:", self.plato_datos[2]),
            ("🏷️", "Categoría:", self.plato_datos[3]),
            ("⏱️", "Tiempo:", f"{self.plato_datos[4]} min"),
            ("📊", "Estado:", self.plato_datos[5]),
        ]
        
        for row, (icon, label, valor) in enumerate(info_items):
            frame_row = ctk.CTkFrame(info_content, fg_color="transparent")
            frame_row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                frame_row,
                text=f"{icon} {label}",
                font=("Helvetica", 10, "bold"),
                text_color=config.COLORS["text_dark"]
            ).pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(
                frame_row,
                text=valor,
                font=("Helvetica", 10),
                text_color=config.COLORS["primary"]
            ).pack(side="left")
        
        # Botones de acción
        botones_frame = ctk.CTkFrame(content, fg_color="transparent")
        botones_frame.pack(fill="x", pady=(10, 0))
        
        btn_editar = ctk.CTkButton(
            botones_frame,
            text="✏️ Editar Plato",
            command=self._on_editar,
            fg_color=config.COLORS["warning"],
            hover_color="#e68900",
            font=("Helvetica", 11, "bold"),
            height=40,
            text_color="#FFFFFF"
        )
        btn_editar.pack(fill="x", pady=(0, 8))
        
        btn_eliminar = ctk.CTkButton(
            botones_frame,
            text="🗑️ Eliminar Plato",
            command=self._on_eliminar,
            fg_color=config.COLORS["danger"],
            hover_color="#da190b",
            font=("Helvetica", 11, "bold"),
            height=40,
            text_color="#FFFFFF"
        )
        btn_eliminar.pack(fill="x", pady=(0, 8))
        
        # Botón cancelar
        btn_cancelar = ctk.CTkButton(
            botones_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            font=("Helvetica", 10),
            height=32,
            text_color=config.COLORS["text_dark"]
        )
        btn_cancelar.pack(fill="x")
    
    def _on_editar(self):
        """Cuando presiona Editar"""
        callback = self.on_editar
        datos = self.plato_datos
        self.destroy()
        if callback:
            if self.parent is not None and self.parent.winfo_exists():
                self.parent.after(10, lambda: callback(datos))
            else:
                callback(datos)
    
    def _on_eliminar(self):
        """Cuando presiona Eliminar"""
        callback = self.on_eliminar
        datos = self.plato_datos
        self.destroy()
        if callback:
            if self.parent is not None and self.parent.winfo_exists():
                self.parent.after(10, lambda: callback(datos))
            else:
                callback(datos)
