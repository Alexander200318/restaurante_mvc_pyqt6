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
    """Diálogo de formulario genérico con diseño moderno"""
    
    def __init__(self, parent, titulo: str, campos: dict, on_submit: Callable):
        super().__init__(parent)
        
        # Colores modernos (Light theme)
        self.bg_color = "#FFFFFF" 
        self.text_color = "#1F2937"  # Gris muy oscuro
        self.label_color = "#374151" # Gris oscuro
        self.accent_color = "#2563EB" # Azul royal moderno
        self.input_bg = "#F3F4F6"    # Gris muy claro para inputs
        
        self.configure(fg_color=self.bg_color)
        
        self.title(titulo)
        self.geometry("500x550") # Un poco más grande para que respire
        self.resizable(False, False)
        
        self.campos = campos
        self.on_submit = on_submit
        self.valores = {}
        self.widgets = {}
        self.error_labels = {} # Almacenar referencias a labels de error
        
        # Header simple
        header = ctk.CTkLabel(
            self, 
            text=titulo, 
            font=("Segoe UI", 18, "bold"),
            text_color=self.text_color
        )
        header.pack(pady=(20, 10), padx=20, anchor="w")
        
        self._crear_formulario()
        
        # Centrar en pantalla
        self.update()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
        except:
            pass
        
        # Modal
        self.attributes('-topmost', True)
        self.grab_set()
        
        # Foco al primer campo
        if self.widgets:
            first_widget = list(self.widgets.values())[0]
            try:
                first_widget.focus_set()
            except:
                pass
    
    def _crear_formulario(self):
        """Crear widgets del formulario"""
        # Frame scrolleable para campos
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=25, pady=10)
        
        self.widgets = {} # Reset
        self.error_labels = {} 

        for nombre_campo, config in self.campos.items():
            # Label moderno
            label_text = config.get('label', nombre_campo)
            label = ctk.CTkLabel(
                frame, 
                text=label_text,
                text_color=self.label_color,
                font=("Segoe UI", 13, "bold"),
                anchor="w"
            )
            label.pack(fill="x", pady=(10, 5))
            
            # Estilo común para inputs
            input_kwargs = {
                "font": ("Segoe UI", 13),
                "height": 38,
                "corner_radius": 8,
                "border_width": 1,
                "border_color": "#D1D5DB",
                "fg_color": self.input_bg,
                "text_color": self.text_color
            }
            
            tipo = config.get('type', 'text')
            valor_inicial = config.get('value', '')
            
            if tipo == 'text' or tipo == 'number':
                widget = ctk.CTkEntry(
                    frame, 
                    placeholder_text=f"Ingrese {label_text.lower()}",
                    placeholder_text_color="#9CA3AF",
                    **input_kwargs
                )
                if valor_inicial is not None:
                    widget.insert(0, str(valor_inicial))
                widget.pack(fill="x", pady=(0, 5))
            
            elif tipo == 'dropdown':
                opciones = config.get('options', [])
                es_editable = config.get('editable', False)
                estado = "normal" if es_editable else "readonly"
                
                widget = ctk.CTkComboBox(
                    frame, 
                    values=opciones, 
                    state=estado,
                    button_color=self.accent_color,
                    dropdown_hover_color=self.accent_color,
                    **input_kwargs
                )
                if valor_inicial:
                    widget.set(str(valor_inicial))
                elif opciones:
                    widget.set(opciones[0])
                    
                widget.pack(fill="x", pady=(0, 5))
            
            elif tipo == 'textarea':
                widget = ctk.CTkTextbox(
                    frame, 
                    height=100,
                    corner_radius=8,
                    border_width=1,
                    border_color="#D1D5DB",
                    fg_color=self.input_bg,
                    text_color=self.text_color,
                    font=("Segoe UI", 13)
                )
                if valor_inicial:
                    widget.insert("1.0", str(valor_inicial))
                widget.pack(fill="x", pady=(0, 5))
            
            else:
                continue
            
            # Label de error (se muestra solo si hay fallo)
            error_label = ctk.CTkLabel(
                frame, 
                text="", 
                text_color="#DC2626", # Rojo fuerte para alertas
                font=("Segoe UI", 11, "bold"),
                anchor="w",
                height=15 
            )
            error_label.pack(fill="x", pady=(0, 5))
            
            self.error_labels[nombre_campo] = error_label
            self.widgets[nombre_campo] = widget 
        
        # Botones (Footer)
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(fill="x", padx=25, pady=25)
        
        # Botón Guardar (Verde moderno / Azul)
        btn_ok = ctk.CTkButton(
            frame_botones,
            text="Guardar Cambios",
            command=self._on_ok,
            fg_color="#10B981", # Emerald 500
            hover_color="#059669", # Emerald 600
            font=("Segoe UI", 13, "bold"),
            text_color="white",
            height=40,
            corner_radius=8
        )
        btn_ok.pack(side="right", padx=(10, 0), fill="x", expand=True)
        
        # Botón Cancelar (Gris/Outlined)
        btn_cancel = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=self.destroy,
            fg_color="transparent",
            border_width=1,
            border_color="#D1D5DB",
            text_color="#6B7280",
            hover_color="#F3F4F6",
            font=("Segoe UI", 13),
            height=40,
            corner_radius=8
        )
        btn_cancel.pack(side="right", padx=(0, 10), fill="x", expand=True)

    def _on_ok(self):
        """Procesar envío con validación INLINE"""
        self.valores = {}
        error_general = False # Si hay error en algun campo
        
        # 1. Limpiar todos los errores previos
        for nombre in self.error_labels:
            self.error_labels[nombre].configure(text="")
            # Opcional: Podríamos regresar los bordes a gris si tuvieramos referencia
            if nombre in self.widgets:
                 try:
                     self.widgets[nombre].configure(border_color="#D1D5DB")
                 except: pass

        for nombre, widget in self.widgets.items():
            config = self.campos[nombre]
            tipo = config.get('type', 'text')
            label = config.get('label', nombre)
            es_requerido = config.get('required', False)
            min_val = config.get('min', None)
            
            error_msg = "" # Mensaje específico para este campo

            try:
                # Obtener valor crudo
                if tipo == 'textarea':
                    valor_raw = widget.get("1.0", "end-1c")
                else:
                    valor_raw = widget.get()
                
                valor_str = valor_raw.strip() if valor_raw else ""
                
                # A. Validación: REQUERIDO (Aplica a texto, numero, dropdown...)
                if es_requerido and not valor_str:
                    error_msg = "⚠ Campo obligatorio"

                # B. Validación: CARACTERES PROHIBIDOS (Solo para texto)
                elif tipo == 'text' and any(c in valor_str for c in ["<", ">", "{", "}", "[", "]", "*", ";"]):
                    error_msg = "⚠ No se permiten: < > { } [ ] * ;"
                
                # C. Validación: TIPO NÚMERO
                elif tipo == 'number':
                    if valor_str:
                        try:
                            valor = float(valor_str)
                            # C.1 Validación: Mínimo
                            if min_val is not None and valor < min_val:
                                error_msg = f"⚠ Debe ser mayor o igual a {min_val}"
                            # C.2 Validación: Máximo razonable (opcional)
                            elif valor > 999999:
                                error_msg = "⚠ Número demasiado grande"
                        except ValueError:
                             error_msg = "⚠ Debe ser un número válido"
                    # Si es vacío y NO es requerido, pasa. Si es vacío y ES requerido, ya cayó en A.
                
                # Si hubo error en este campo
                if error_msg:
                    self.error_labels[nombre].configure(text=error_msg)
                    try:
                        widget.configure(border_color="#DC2626") # Borde rojo fuerte
                    except: pass
                    error_general = True
                    # No continue, validamos todo
                
                # Si pasa validación, guardamos el valor limpio
                if tipo == 'number':
                    self.valores[nombre] = float(valor_str) if valor_str else 0.0
                else:
                    self.valores[nombre] = valor_str
                
            except Exception as e:
                # Error inesperado
                self.error_labels[nombre].configure(text=f"⚠ Error interno: {str(e)}")
                error_general = True

        if not error_general:
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
