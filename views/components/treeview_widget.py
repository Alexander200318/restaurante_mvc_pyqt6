"""
Widget TreeView (Tabla) reutilizable para customtkinter
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Callable, Optional
import config

class TreeViewWidget(ctk.CTkFrame):
    """Widget tabla/árbol personalizado con estilo moderno"""
    
    def __init__(
        self,
        parent,
        columnas: List[str],
        altura: int = 15,
        font_size: int = 12,
        heading_font_size: int = 12,
        row_height: int = 30,
        **kwargs
    ):
        """
        columnas: lista de nombres de columnas ['ID', 'Nombre', 'Precio', ...]
        altura: filas que se ven
        """
        super().__init__(parent, **kwargs)
        
        self.columnas = columnas
        self.altura = altura
        self.font_size = font_size
        self.heading_font_size = heading_font_size
        self.row_height = row_height
        self.arbol = None
        self.items_datos = {}  # Mapeo de ID de fila a datos
        self.on_seleccionar = None
        self.on_doble_click = None
        self.style_name = f"Custom{id(self)}.Treeview"
        
        self._crear_treeview()
    
    def _crear_treeview(self):
        """Crear el widget treeview con estilo"""
        style = ttk.Style(self)
        try:
            if "clam" in style.theme_names():
                style.theme_use("clam")
        except:
            pass
        
        # Colores personalizados (TEMA CLARO / BLANCO)
        primary_color = config.COLORS["primary"]
        bg_color = "#FFFFFF" # Fondo BLANCO puro
        text_color = "#1F2937" # Texto oscuro para contraste
        row_alt_color = "#F3F4F6" # Gris muy muy claro para alternar
        
        # Configurar Estilo de Tabla
        style.configure(
            self.style_name,
            background=bg_color,
            foreground=text_color,
            fieldbackground=bg_color,
            rowheight=self.row_height,
            font=("Segoe UI", self.font_size),
            borderwidth=0
        )
        
        # Configurar Estilo de Cabecera (Gris claro elegante)
        style.configure(
            f"{self.style_name}.Heading",
            background="#E5E7EB", # Gris suave encabezado
            foreground="#111827", # Texto oscuro encabezado
            relief="flat",
            font=("Segoe UI", self.heading_font_size, "bold")
        )
        
        # Mapa de colores para selección
        style.map(
            self.style_name,
            background=[('selected', primary_color)], # Naranja al seleccionar
            foreground=[('selected', 'white')] # Texto blanco al seleccionar
        )

        # Frame con scrollbar
        frame_tabla = ctk.CTkFrame(self, fg_color="transparent")
        frame_tabla.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollbars minimalistas (si es posible, sino default)
        vsb = ttk.Scrollbar(frame_tabla, orient="vertical")
        hsb = ttk.Scrollbar(frame_tabla, orient="horizontal")
        
        # TreeView
        self.arbol = ttk.Treeview(
            frame_tabla,
            columns=self.columnas,
            height=self.altura,
            style=self.style_name,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            show='headings'
        )
        
        # Configurar tags para filas alternas
        self.arbol.tag_configure('impar', background=bg_color)
        self.arbol.tag_configure('par', background=row_alt_color)
        
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
    

    def agregar_fila(self, datos: Tuple, datos_ocultos=None):
        """
        Agrega una fila
        datos: Tupla con los datos VISIBLES para las columnas
        datos_ocultos: (Opcional) El objeto completo o ID que se recupera al seleccionar
                       Si es None, se usa 'datos' como el objeto de retorno.
        """
        # Asegurar longitud correcta para display
        datos_formateados = list(datos)[:len(self.columnas)]
        while len(datos_formateados) < len(self.columnas):
            datos_formateados.append("")
        
        # Alternar colores
        tag = 'par' if len(self.arbol.get_children()) % 2 == 0 else 'impar'
        
        # Insertar en treeview
        item_id = self.arbol.insert('', 'end', values=datos_formateados, tags=(tag,))
        
        # Guardar la referencia al objeto original (o el oculto si se provee)
        if datos_ocultos is not None:
            self.items_datos[item_id] = datos_ocultos
        else:
            self.items_datos[item_id] = datos
            
        return item_id



    def agregar_filas(self, datos_lista: List[Tuple], datos_ocultos_lista: Optional[List[object]] = None):
        """
        Agregar múltiples filas
        datos_lista: Lista de tuplas con datos para las columnas visibles
        datos_ocultos_lista: (Opcional) Lista de objetos a retornar al seleccionar cada fila (IDs, objetos, etc)
                             Debe tener la misma longitud que datos_lista si se provee.
        """
        if datos_ocultos_lista and len(datos_ocultos_lista) == len(datos_lista):
             for i, datos in enumerate(datos_lista):
                self.agregar_fila(datos, datos_ocultos_lista[i])
        else:
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
    
    def set_on_doble_click(self, callback: Callable):
        """Establecer callback para doble click"""
        self.on_doble_click = callback
    
    def set_on_double_click(self, callback: Callable):
        """Establecer callback para doble click"""
        self.on_doble_click = callback
