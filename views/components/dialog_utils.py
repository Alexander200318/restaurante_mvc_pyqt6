"""
Componentes de diálogo reutilizables
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from typing import Callable, Optional

class DialogUtils:
    """Utilidades para mostrar diálogos"""
    
    @staticmethod
    def mostrar_exito(titulo: str, mensaje: str, parent=None):
        """Mostrar diálogo de éxito"""
        messagebox.showinfo(titulo, mensaje, parent=parent)
    
    @staticmethod
    def mostrar_error(titulo: str, mensaje: str, parent=None):
        """Mostrar diálogo de error"""
        messagebox.showerror(titulo, mensaje, parent=parent)
    
    @staticmethod
    def mostrar_advertencia(titulo: str, mensaje: str, parent=None):
        """Mostrar diálogo de advertencia"""
        messagebox.showwarning(titulo, mensaje, parent=parent)
    
    @staticmethod
    def pedir_confirmacion(titulo: str, mensaje: str, parent=None) -> bool:
        """Pedir confirmación (Sí/No)"""
        return messagebox.askyesno(titulo, mensaje, parent=parent)
    
    @staticmethod
    def pedir_okcancel(titulo: str, mensaje: str, parent=None) -> bool:
        """Pedir OK/Cancelar"""
        return messagebox.askokcancel(titulo, mensaje, parent=parent)

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
            
            if tipo == 'text':
                widget = ctk.CTkEntry(frame)
                widget.pack(fill="x", pady=(0, 5))
            
            elif tipo == 'number':
                widget = ctk.CTkEntry(frame)
                widget.pack(fill="x", pady=(0, 5))
            
            elif tipo == 'dropdown':
                opciones = config.get('options', [])
                widget = ctk.CTkComboBox(frame, values=opciones, state="readonly")
                widget.pack(fill="x", pady=(0, 5))
            
            elif tipo == 'textarea':
                widget = ctk.CTkTextbox(frame, height=60)
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
