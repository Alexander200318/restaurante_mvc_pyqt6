"""
Widget TreeView (Tabla) reutilizable para customtkinter
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Callable, Optional

class TreeViewWidget(ctk.CTkFrame):
    """Widget tabla/árbol personalizado"""
    
    def __init__(self, parent, columnas: List[str], altura: int = 15, **kwargs):
        """
        columnas: lista de nombres de columnas ['ID', 'Nombre', 'Precio', ...]
        altura: filas que se ven
        """
        super().__init__(parent, **kwargs)
        
        self.columnas = columnas
        self.altura = altura
        self.arbol = None
        self.items_datos = {}  # Mapeo de ID de fila a datos
        self.on_seleccionar = None
        self.on_doble_click = None
        
        self._crear_treeview()
    
    def _crear_treeview(self):
        """Crear el widget treeview"""
        # Frame con scrollbar
        frame_tabla = ctk.CTkFrame(self, fg_color="transparent")
        frame_tabla.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tabla, orient="vertical")
        hsb = ttk.Scrollbar(frame_tabla, orient="horizontal")
        
        # TreeView
        self.arbol = ttk.Treeview(
            frame_tabla,
            columns=self.columnas,
            height=self.altura,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            show='headings'
        )
        
        vsb.config(command=self.arbol.yview)
        hsb.config(command=self.arbol.xview)
        
        # Configurar columnas
        ancho_col = int(60 / len(self.columnas)) if self.columnas else 60
        for col in self.columnas:
            self.arbol.heading(col, text=col)
            self.arbol.column(col, width=ancho_col * 10, anchor="w")
        
        # Grid
        self.arbol.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        
        # Bindings
        self.arbol.bind('<<TreeviewSelect>>', self._on_select)
        self.arbol.bind('<Double-Button-1>', self._on_double_click)
    
    def _on_select(self, event):
        """Cuando selecciona fila"""
        if self.on_seleccionar:
            selection = self.arbol.selection()
            if selection:
                item_id = selection[0]
                datos = self.items_datos.get(item_id)
                self.on_seleccionar(datos)
    
    def _on_double_click(self, event):
        """Cuando hace doble click"""
        if self.on_doble_click:
            selection = self.arbol.selection()
            if selection:
                item_id = selection[0]
                datos = self.items_datos.get(item_id)
                self.on_doble_click(datos)
    
    def agregar_fila(self, datos: Tuple, id_datos=None):
        """Agregar fila a la tabla"""
        # Asegurar que datos tiene cantidad correcta de columnas
        datos_formateados = list(datos)[:len(self.columnas)]
        while len(datos_formateados) < len(self.columnas):
            datos_formateados.append("")
        
        item_id = self.arbol.insert('', 'end', values=datos_formateados)
        
        if id_datos is not None:
            self.items_datos[item_id] = id_datos
        
        return item_id
    
    def agregar_filas(self, datos_lista: List[Tuple]):
        """Agregar múltiples filas"""
        for datos in datos_lista:
            self.agregar_fila(datos)
    
    def limpiar(self):
        """Limpiar todas las filas"""
        for item in self.arbol.get_children():
            self.arbol.delete(item)
        self.items_datos.clear()
    
    def obtener_seleccionada(self):
        """Obtener datos de fila seleccionada"""
        selection = self.arbol.selection()
        if selection:
            item_id = selection[0]
            return self.items_datos.get(item_id)
        return None
    
    def obtener_todas_las_filas(self):
        """Obtener todos los datos"""
        return list(self.items_datos.values())
    
    def eliminar_fila(self, id_datos=None):
        """Eliminar fila seleccionada o por ID"""
        if id_datos is None:
            selection = self.arbol.selection()
            if not selection:
                return False
            item_id = selection[0]
        else:
            # Buscar por id_datos
            item_id = None
            for iid, datos in self.items_datos.items():
                if datos == id_datos:
                    item_id = iid
                    break
            if not item_id:
                return False
        
        self.arbol.delete(item_id)
        self.items_datos.pop(item_id, None)
        return True
    
    def set_on_select(self, callback: Callable):
        """Establecer callback para selección"""
        self.on_seleccionar = callback
    
    def set_on_double_click(self, callback: Callable):
        """Establecer callback para doble click"""
        self.on_doble_click = callback
