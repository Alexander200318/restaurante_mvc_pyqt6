"""
Página: Gestión de Clientes - Diseño Grid Visual
"""
import customtkinter as ctk
import math
from controllers.clientes_controller import ClientesController
from controllers.mesas_controller import MesasController
from views.components.dialog_utils import DialogUtils
import config

class ClientesPage(ctk.CTkFrame):
    """Módulo de Clientes con Grid Visual"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#FFFFFF", **kwargs)
        
        self.controller = ClientesController()
        self.mesas_controller = MesasController()
        self.cliente_seleccionado = None
        self.grid_frame = None
        self.cliente_cards = {}
        self.grid_fila = 0
        self.grid_columna = 0
        # Nuevo: Variable para búsqueda y paginación
        self.busqueda_var = ctk.StringVar()
        self.busqueda_var.trace("w", self._filtrar_clientes)
        self.todos_los_clientes = [] # Cache local
        self.pagina_actual = 1
        self.items_por_pagina = 20
        self.total_paginas = 1
        
        self._crear_ui()
        self.refrescar_tabla()
    
    # === VALIDACIONES ===
    def _validar_cedula(self, cedula):
        """Validar cédula ecuatoriana según reglas oficiales"""
        # Si está vacía
        if not cedula:
            return False, "La cédula es requerida"
        
        # Verificar que tenga 10 dígitos
        if not cedula.isdigit() or len(cedula) != 10:
            return False, "La cédula debe tener 10 dígitos"
        
        # Validar provincia (01-24)
        provincia = int(cedula[:2])
        if provincia < 1 or provincia > 24:
            return False, "Provincia inválida (primeros 2 dígitos deben estar entre 01-24)"
        
        # Validar tercer dígito (debe ser menor a 6 para personas naturales)
        tercer_digito = int(cedula[2])
        if tercer_digito >= 6:
            return False, "Cédula inválida: tercer dígito debe ser menor a 6"
        
        # Algoritmo de validación de cédula ecuatoriana
        suma = 0
        for i in range(9):
            num = int(cedula[i])
            
            if i % 2 == 0:  # posiciones impares (0-based: 0, 2, 4, 6, 8)
                num *= 2
                if num > 9:
                    num -= 9
            
            suma += num
        
        # Calcular dígito verificador
        digito_verificador = (10 - (suma % 10)) % 10
        
        # Validar que coincida con el último dígito
        if digito_verificador != int(cedula[9]):
            return False, "Cédula inválida: dígito verificador no coincide"
        
        return True, ""
    
    def _validar_nombre(self, nombre):
        """Validar que nombre contenga solo letras y espacios"""
        if not nombre:
            return False, "El nombre es requerido"
        if not all(c.isalpha() or c.isspace() for c in nombre):
            return False, "El nombre solo puede contener letras y espacios"
        return True, ""
    
    def _validar_apellido(self, apellido):
        """Validar que apellido contenga solo letras y espacios"""
        if not apellido:
            return False, "El apellido es requerido"
        if not all(c.isalpha() or c.isspace() for c in apellido):
            return False, "El apellido solo puede contener letras y espacios"
        return True, ""
    
    def _validar_telefono(self, telefono):
        """Validar que teléfono tenga exactamente 10 dígitos"""
        if not telefono:
            return False, "El teléfono es requerido"
        if len(telefono) != 10:
            return False, "El teléfono debe tener exactamente 10 dígitos"
        if not telefono.isdigit():
            return False, "El teléfono debe contener solo números"
        return True, ""
    
    def _validar_correo(self, correo):
        """Validar formato de correo electrónico"""
        import re
        if not correo:
            return False, "El correo es requerido"
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, correo):
            return False, "El correo debe tener un formato válido (ej: usuario@ejemplo.com)"
        return True, ""
    
    def _validar_direccion(self, direccion):
        """Validar que dirección contenga caracteres permitidos"""
        if not direccion:
            return False, "La dirección es requerida"
        permitidos = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-,_:; ")
        if not all(c in permitidos for c in direccion):
            return False, "La dirección contiene caracteres no permitidos"
        return True, ""
    
    def _crear_ui(self):
        """Crear interfaz"""
        # === HEADER ===
        # Diseño mejorado manteniendo el color primario
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"], height=120)
        frame_header.pack(side="top", fill="x", padx=0, pady=0)
        frame_header.pack_propagate(False)
        
        # Contenedor con más padding para aire
        frame_header_content = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_header_content.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Info (Izquierda)
        frame_titulo = ctk.CTkFrame(frame_header_content, fg_color="transparent")
        frame_titulo.pack(side="left", fill="y", pady=5)
        
        # Título más moderno
        titulo = ctk.CTkLabel(
            frame_titulo,
            text="Gestión de Clientes",
            text_color="white",
            font=("Segoe UI", 30, "bold"),
            anchor="w"
        )
        titulo.pack(anchor="w")
        
        # Subtítulo más suave
        subtitulo = ctk.CTkLabel(
            frame_titulo,
            text="Administra tu base de datos y fidelización de clientes",
            text_color="#E0E7FF", # Azul/Blanco muy claro
            font=("Segoe UI", 13),
            anchor="w"
        )
        subtitulo.pack(anchor="w", pady=(4, 0))
        
        # Botón Nuevo Cliente (Derecha - Estilo Botón Flotante/Pill)
        frame_acciones = ctk.CTkFrame(frame_header_content, fg_color="transparent")
        frame_acciones.pack(side="right", fill="y", anchor="center")
        
        btn_nuevo = ctk.CTkButton(
            frame_acciones,
            text="＋ Nuevo Cliente",
            command=self._crear_dialogo_nuevo_cliente,
            fg_color="#10B981", # Emerald
            hover_color="#059669",
            text_color="white",
            font=("Segoe UI", 14, "bold"),
            height=46,
            width=180,
            corner_radius=23, # Totalmente redondeado
            border_spacing=2
        )
        btn_nuevo.pack(side="right")
        
        # Eliminamos el separador duro para un look más limpio, o usamos uno muy sutil si prefieres
        # separator = ctk.CTkFrame(self, fg_color="#E5E7EB", height=1)
        # separator.pack(fill="x", pady=0, padx=0)
        
        # === FILTROS / BÚSQUEDA (Diseño Card) ===
        frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtros.pack(fill="x", padx=24, pady=(20, 10))
        
        # Card contenedora para la barra de búsqueda
        search_card = ctk.CTkFrame(
            frame_filtros, 
            fg_color="white", 
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB",
            height=70
        )
        search_card.pack(fill="x")
        search_card.pack_propagate(False)
        
        inner_search = ctk.CTkFrame(search_card, fg_color="transparent")
        inner_search.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 1. Grupo de Input (Icono + Entry) estilo "pill"
        input_container = ctk.CTkFrame(inner_search, fg_color="#F3F4F6", corner_radius=10, width=420)
        input_container.pack(side="left", fill="y", pady=3)
        input_container.pack_propagate(False)
        
        ctk.CTkLabel(input_container, text="🔍", font=("Segoe UI Emoji", 14), text_color="#9CA3AF").pack(side="left", padx=(15, 8))
        
        self.entry_busqueda = ctk.CTkEntry(
            input_container,
            placeholder_text="Buscar por nombre, cédula, teléfono...",
            placeholder_text_color="#9CA3AF",
            font=("Helvetica", 13),
            height=34,
            border_width=0,
            fg_color="transparent",
            text_color="#1F2937",
            width=350
        )
        self.entry_busqueda.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.entry_busqueda.bind("<KeyRelease>", self._on_search_change)


        # === PAGINACIÓN (Anclado al fondo) ===
        self.frame_paginacion = ctk.CTkFrame(self, fg_color="#F9FAFB", height=50)
        self.frame_paginacion.pack(side="bottom", fill="x", padx=0, pady=0)
        self.frame_paginacion.pack_propagate(False)

        container_pag = ctk.CTkFrame(self.frame_paginacion, fg_color="transparent")
        container_pag.pack(expand=True, pady=10)

        # Botón Anterior
        self.btn_anterior = ctk.CTkButton(
            container_pag, 
            text="◀ Anterior", 
            command=lambda: self._cambiar_pagina(-1),
            width=100,
            height=30,
            fg_color="#E5E7EB",
            text_color="#374151",
            hover_color="#D1D5DB"
        )
        self.btn_anterior.pack(side="left", padx=10)

        # Label estado
        self.lbl_paginacion = ctk.CTkLabel(
            container_pag,
            text="Página 1 de 1",
            font=("Helvetica", 12, "bold"),
            text_color="#4B5563"
        )
        self.lbl_paginacion.pack(side="left", padx=10)

        # Botón Siguiente
        self.btn_siguiente = ctk.CTkButton(
            container_pag, 
            text="Siguiente ▶", 
            command=lambda: self._cambiar_pagina(1),
            width=100,
            height=30,
            fg_color="#E5E7EB",
            text_color="#374151",
            hover_color="#D1D5DB"
        )
        self.btn_siguiente.pack(side="left", padx=10)
        
        # === CONTENIDO PRINCIPAL ===
        frame_main = ctk.CTkFrame(self, fg_color="#FFFFFF")
        frame_main.pack(fill="both", expand=True, padx=24, pady=24)
        
        # Frame scrollable para el grid
        self.canvas = ctk.CTkCanvas(
            frame_main,
            bg="#FFFFFF",
            highlightthickness=0,
            height=400
        )
        scrollbar = ctk.CTkScrollbar(frame_main, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(
            self.canvas,
            fg_color="#FFFFFF"
        )
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def _configure_window(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            
        self.canvas.bind("<Configure>", _configure_window)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Habilitar scroll con mouse
        self._bind_mouse_wheel(self.canvas)
        self._bind_mouse_wheel(self.scrollable_frame)

        # Grid frame para los clientes (4 columnas)
        self.grid_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=8)
        self._bind_mouse_wheel(self.grid_frame)
        
        # Configurar 4 columnas con peso igual
        for i in range(4):
            self.grid_frame.grid_columnconfigure(i, weight=1)
    
    def _bind_mouse_wheel(self, widget):
        # Scroll para Windows con velocidad ajustada
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        widget.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
        widget.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def refrescar_tabla(self):
        """Refrescar grid de clientes"""
        # 1. Obtener todos los clientes de la BD
        success, clientes, msg = self.controller.obtener_todos_clientes()
        
        if success and clientes:
            self.todos_los_clientes = clientes
        else:
            self.todos_los_clientes = []
            
        # 2. Resetear a página 1 y aplicar filtro
        self.pagina_actual = 1
        self._filtrar_clientes()

    def _on_search_change(self, event=None):
        """Al escribir, resetear a página 1"""
        self.pagina_actual = 1
        self._filtrar_clientes()

    def _cambiar_pagina(self, direccion):
        """Cambiar página actual"""
        nueva_pagina = self.pagina_actual + direccion
        if 1 <= nueva_pagina <= self.total_paginas:
            self.pagina_actual = nueva_pagina
            self._filtrar_clientes()

    def _filtrar_clientes(self, *args):
        """Filtrar lista de clientes según búsqueda y renderizar con paginación"""
        # Obtenemos el texto directamente del entry, usando .get()
        # Esto evita problemas con variables reactivas (StringVar) y placeholders
        try:
            busqueda = self.entry_busqueda.get().lower().strip()
        except AttributeError:
             # Si se llama antes de crear el entry
             busqueda = ""
        except Exception:
             busqueda = ""
        
        # Limpiar grid anterior
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.cliente_cards = {}
        self.grid_fila = 0
        self.grid_columna = 0
        
        # Si no hay clientes en BD
        if not self.todos_los_clientes:
            self._mostrar_empty_state_bd()
            self._actualizar_controles_paginacion(0)
            return

        # Filtrar lista
        clientes_filtrados = []
        if not busqueda:
            clientes_filtrados = self.todos_los_clientes
        else:
            busqueda = busqueda.lower()
            for c in self.todos_los_clientes:
                # Buscar en nombre, apellido, cédula y teléfono
                telefono = str(c.telefono) if c.telefono else ""
                texto_busqueda = f"{c.nombre} {c.apellido} {c.cedula} {telefono}".lower()
                if busqueda in texto_busqueda:
                    clientes_filtrados.append(c)
        
        # Si no hay resultados de búsqueda
        if not clientes_filtrados:
            self._mostrar_empty_state_busqueda()
            self._actualizar_controles_paginacion(0)
            return
            
        # --- PAGINACIÓN ---
        total_items = len(clientes_filtrados)
        self.total_paginas = math.ceil(total_items / self.items_por_pagina) or 1
        
        # Asegurar página válida
        if self.pagina_actual > self.total_paginas:
             self.pagina_actual = self.total_paginas
        if self.pagina_actual < 1:
             self.pagina_actual = 1
             
        # Calcular slice
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        clientes_pagina = clientes_filtrados[inicio:fin]

        # Renderizar tarjetas
        for idx, cliente in enumerate(clientes_pagina):
            self._crear_fila_cliente(cliente, idx)
            
        # Actualizar controles
        self._actualizar_controles_paginacion(total_items)

    def _actualizar_controles_paginacion(self, total_items):
        """Actualizar estado de botones y label de paginación"""
        try:
            if not getattr(self, 'lbl_paginacion', None): return
            
            # Texto informativo
            if total_items == 0:
                 self.lbl_paginacion.configure(text="Sin resultados")
                 self.btn_anterior.configure(state="disabled", fg_color="#E5E7EB")
                 self.btn_siguiente.configure(state="disabled", fg_color="#E5E7EB")
                 return
                 
            inicio = (self.pagina_actual - 1) * self.items_por_pagina + 1
            fin = min(self.pagina_actual * self.items_por_pagina, total_items)
            
            self.lbl_paginacion.configure(text=f"Mostrando {inicio}-{fin} de {total_items} (Página {self.pagina_actual}/{self.total_paginas})")
            
            # Estado botón anterior
            if self.pagina_actual > 1:
                self.btn_anterior.configure(state="normal", fg_color="#3B82F6", text_color="white")
            else:
                self.btn_anterior.configure(state="disabled", fg_color="#E5E7EB", text_color="#9CA3AF")
                
            # Estado botón siguiente
            if self.pagina_actual < self.total_paginas:
                self.btn_siguiente.configure(state="normal", fg_color="#3B82F6", text_color="white")
            else:
                self.btn_siguiente.configure(state="disabled", fg_color="#E5E7EB", text_color="#9CA3AF")
                
        except Exception as e:
            print(f"Error actualizando paginación: {e}")

    def _mostrar_empty_state_bd(self):
            # Estado vacío por falta de datos
            empty_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=50)
            
            center = ctk.CTkFrame(empty_frame, fg_color="transparent")
            center.pack(expand=True)
            
            ctk.CTkLabel(center, text="👥", font=("Helvetica", 64), text_color="#D1D5DB").pack(pady=(0, 16))
            ctk.CTkLabel(center, text="No hay clientes registrados", font=("Helvetica", 16, "bold"), text_color="#6B7280").pack(pady=(0, 8))
            ctk.CTkLabel(center, text="Haz clic en '➕ Nuevo Cliente' para crear uno", font=("Helvetica", 12), text_color="#9CA3AF").pack()

    def _mostrar_empty_state_busqueda(self):
            # Estado vacío por búsqueda sin resultados
            empty_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=50)
            
            center = ctk.CTkFrame(empty_frame, fg_color="transparent")
            center.pack(expand=True)
            
            ctk.CTkLabel(center, text="🔍", font=("Helvetica", 64), text_color="#D1D5DB").pack(pady=(0, 16))
            ctk.CTkLabel(center, text="No se encontraron resultados", font=("Helvetica", 16, "bold"), text_color="#6B7280").pack(pady=(0, 8))
            
            # Texto amigable
            busqueda = ""
            try: busqueda = self.entry_busqueda.get()
            except: pass
            
            ctk.CTkLabel(center, text=f"No hay coincidencias con '{busqueda}'", font=("Helvetica", 12), text_color="#9CA3AF").pack()
    
    def _crear_fila_cliente(self, cliente, idx):
        """Crear tarjeta de cliente con diseño moderno y avatar"""
        # --- CONFIGURACIÓN DE TARJETA ---
        card_height = 185
        card_frame = ctk.CTkFrame(
            self.grid_frame, 
            fg_color="white", 
            border_width=1, 
            border_color="#E5E7EB", 
            corner_radius=12,
            height=card_height
        )
        card_frame.grid(row=self.grid_fila, column=self.grid_columna, sticky="nsew", padx=6, pady=6)
        card_frame.pack_propagate(False)
        card_frame.grid_propagate(False)

        # Configurar peso para que se expanda en grid padre
        self.grid_frame.grid_rowconfigure(self.grid_fila, weight=1)

        # --- HEADER (Avatar + Info) ---
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent", height=55)
        header_frame.pack(fill="x", padx=12, pady=(12, 5))
        
        # Avatar con iniciales
        initials = (cliente.nombre[0] if cliente.nombre else "") + (cliente.apellido[0] if cliente.apellido else "")
        initials = initials[:2].upper()
        
        # Colores pastel aleatorios para avatar
        colors = [("#DBEAFE", "#1E40AF"), ("#D1FAE5", "#065F46"), ("#FEF3C7", "#92400E"), ("#E0E7FF", "#3730A3"), ("#FCE7F3", "#9D174D")]
        bg_color, txt_color = colors[idx % len(colors)]
        
        # Frame circular para avatar
        avatar_frame = ctk.CTkFrame(header_frame, width=42, height=42, corner_radius=21, fg_color=bg_color)
        avatar_frame.pack(side="left")
        
        # Label para iniciales
        ctk.CTkLabel(avatar_frame, text=initials, font=("Helvetica", 14, "bold"), text_color=txt_color).place(relx=0.5, rely=0.5, anchor="center")

        # Info Principal
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        nombre_completo = f"{cliente.nombre} {cliente.apellido}"
        if len(nombre_completo) > 18: nombre_completo = nombre_completo[:16] + "..."
            
        ctk.CTkLabel(
            info_frame, text=nombre_completo, font=("Helvetica", 13, "bold"), text_color="#111827", anchor="w"
        ).pack(fill="x", pady=(2, 0))
        
        ctk.CTkLabel(
            info_frame, text=cliente.cedula, font=("Helvetica", 11), text_color="#6B7280", anchor="w"
        ).pack(fill="x")

        # --- BODY (Datos contacto) ---
        body_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=14, pady=(5, 0))
        
        # Item Teléfono
        if cliente.telefono:
            row_tel = ctk.CTkFrame(body_frame, fg_color="transparent", height=20)
            row_tel.pack(fill="x", pady=2)
            ctk.CTkLabel(row_tel, text="�", font=("Segoe UI Emoji", 11), text_color="#9CA3AF", width=20, anchor="w").pack(side="left")
            ctk.CTkLabel(row_tel, text=cliente.telefono, font=("Helvetica", 11), text_color="#4B5563").pack(side="left")

        # Item Secundario (Correo o Dirección)
        item_sec = cliente.correo if cliente.correo else cliente.direccion
        icon_sec = "✉️" if cliente.correo else "📍"
        if item_sec:
            if len(item_sec) > 22: item_sec = item_sec[:20] + "..."
            row_sec = ctk.CTkFrame(body_frame, fg_color="transparent", height=20)
            row_sec.pack(fill="x", pady=2)
            ctk.CTkLabel(row_sec, text=icon_sec, font=("Segoe UI Emoji", 11), text_color="#9CA3AF", width=20, anchor="w").pack(side="left")
            ctk.CTkLabel(row_sec, text=item_sec, font=("Helvetica", 11), text_color="#4B5563").pack(side="left")

        # --- FOOTER (Botones acción) ---
        footer_frame = ctk.CTkFrame(card_frame, fg_color="transparent", height=45)
        footer_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        footer_frame.pack_propagate(False)
        
        btn_style = {"font": ("Helvetica", 11, "bold"), "height": 34, "corner_radius": 8, "width": 30}
        
        # Botones estilo 'Soft UI'
        btn_ver = ctk.CTkButton(
            footer_frame, text="Ver", command=lambda: self._mostrar_detalles_cliente(cliente),
            fg_color="#EFF6FF", text_color="#2563EB", hover_color="#DBEAFE", **btn_style
        )
        btn_ver.pack(side="left", fill="both", expand=True, padx=(0, 4))
        
        btn_editar = ctk.CTkButton(
            footer_frame, text="Editar", command=lambda: self._editar_cliente(cliente.id),
            fg_color="#FFFBEB", text_color="#D97706", hover_color="#FEF3C7", **btn_style
        )
        btn_editar.pack(side="left", fill="both", expand=True, padx=4)
        
        btn_eliminar = ctk.CTkButton(
            footer_frame, text="Borrar", command=lambda: self._eliminar_cliente(cliente.id),
            fg_color="#FEF2F2", text_color="#DC2626", hover_color="#FEE2E2", **btn_style
        )
        btn_eliminar.pack(side="left", fill="both", expand=True, padx=(4, 0))

        # --- HOVER EFFECTS ---
        self.cliente_cards[cliente.id] = {'frame': card_frame, 'cliente': cliente}
        
        def on_enter(e):
            try: card_frame.configure(border_color="#3B82F6", border_width=2) 
            except: pass
            
        def on_leave(e):
            try: card_frame.configure(border_color="#E5E7EB", border_width=1)
            except: pass

        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Bind recursivo
        for child in card_frame.winfo_children():
            if not isinstance(child, ctk.CTkButton):
                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)
                for grand in child.winfo_children():
                    if not isinstance(grand, ctk.CTkButton):
                        grand.bind("<Enter>", on_enter)
                        grand.bind("<Leave>", on_leave)

        # Actualizar posición de grid
        self.grid_columna += 1
        if self.grid_columna >= 4:
            self.grid_columna = 0
            self.grid_fila += 1
    
    def _on_row_hover_enter(self, cliente_id):
        """Efecto hover en fila"""
        if cliente_id not in self.cliente_cards:
            return
        row_frame = self.cliente_cards[cliente_id]['frame']
        row_frame.configure(fg_color="#F9FAFB", border_color=config.COLORS["primary"])
    
    def _on_row_hover_leave(self, cliente_id):
        """Restaurar color de fila"""
        if cliente_id not in self.cliente_cards:
            return
        row_frame = self.cliente_cards[cliente_id]['frame']
        row_frame.configure(fg_color="white", border_color="#E5E7EB")
    
    def _crear_card_cliente(self, cliente, row, col):
        """Crear tarjeta visual para un cliente - DEPRECATED"""
        pass
    
    def _on_hover_enter(self, cliente_id):
        """Efecto hover al pasar ratón - DEPRECATED"""
        pass
    
    def _on_hover_leave(self, cliente_id):
        """Restaurar color original - DEPRECATED"""
        pass
    
    def _on_cliente_click(self, cliente):
        """Click en un cliente"""
        self.cliente_seleccionado = cliente
        # Ya no se usa, los botones llaman directamente
    
    def _mostrar_detalles_cliente(self, cliente):
        """Mostrar diálogo con detalles del cliente (Diseño Moderno)"""
        dialog = ctk.CTkToplevel()
        dialog.configure(fg_color="#FFFFFF")
        dialog.title("Detalles del Cliente")
        dialog.geometry("450x580")
        dialog.resizable(False, False)
        
        # Centrar ventana
        x = (dialog.winfo_screenwidth() // 2) - 225
        y = (dialog.winfo_screenheight() // 2) - 290
        dialog.geometry(f"450x580+{x}+{y}")
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        # === HEADER CON AVATAR ===
        header_frame = ctk.CTkFrame(dialog, fg_color="#F3F4F6", height=140, corner_radius=0)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Avatar Gigante
        initials = (cliente.nombre[0] + cliente.apellido[0]).upper() if cliente.nombre and cliente.apellido else "??"
        
        avatar_container = ctk.CTkFrame(header_frame, width=80, height=80, corner_radius=40, fg_color="#3B82F6")
        avatar_container.place(relx=0.5, rely=0.4, anchor="center")
        
        ctk.CTkLabel(
            avatar_container, 
            text=initials, 
            font=("Segoe UI", 32, "bold"), 
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Nombre y Rol
        ctk.CTkLabel(
            header_frame, 
            text=f"{cliente.nombre} {cliente.apellido}", 
            font=("Segoe UI", 18, "bold"), 
            text_color="#1F2937"
        ).place(relx=0.5, rely=0.75, anchor="center")
        
        ctk.CTkLabel(
            header_frame, 
            text="Cliente Registrado", 
            font=("Segoe UI", 12), 
            text_color="#6B7280"
        ).place(relx=0.5, rely=0.88, anchor="center")
        
        # === INFO BODY ===
        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        def _add_info_row(icon, label, value):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=8)
            
            # Icono
            icon_frame = ctk.CTkFrame(row, width=36, height=36, corner_radius=8, fg_color="#EFF6FF")
            icon_frame.pack(side="left")
            ctk.CTkLabel(icon_frame, text=icon, font=("Segoe UI Emoji", 14)).place(relx=0.5, rely=0.5, anchor="center")
            
            # Textos
            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", padx=12)
            
            ctk.CTkLabel(text_frame, text=label, font=("Segoe UI", 10, "bold"), text_color="#9CA3AF", anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_frame, text=value if value else "No registrado", font=("Segoe UI", 13), text_color="#374151", anchor="w").pack(anchor="w")

        _add_info_row("🆔", "Cédula / RUC", cliente.cedula)
        _add_info_row("📞", "Teléfono Móvil", cliente.telefono)
        _add_info_row("✉️", "Correo Electrónico", cliente.correo)
        _add_info_row("📍", "Dirección Domiciliaria", cliente.direccion)
        
        # === FOOTER ACTIONS ===
        footer = ctk.CTkFrame(dialog, fg_color="white", height=80)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        ctk.CTkFrame(footer, height=1, fg_color="#F3F4F6").pack(fill="x") # Separador
        
        btn_box = ctk.CTkFrame(footer, fg_color="transparent")
        btn_box.pack(expand=True, pady=15)
        
        ctk.CTkButton(
            btn_box, 
            text="Editar", 
            command=lambda: self._editar_cliente(cliente.id, dialog),
            fg_color="#F59E0B", 
            hover_color="#D97706", 
            text_color="white",
            width=140, 
            height=40, 
            corner_radius=20,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_box, 
            text="Cerrar", 
            command=dialog.destroy,
            fg_color="#F3F4F6", 
            hover_color="#E5E7EB", 
            text_color="#374151",
            width=100, 
            height=40, 
            corner_radius=20,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=10)
    
    def _mostrar_empty_state(self):
        """Mostrar estado vacío"""
        empty_frame = ctk.CTkFrame(self.frame_tabla, fg_color=config.COLORS["info"], corner_radius=10)
        empty_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Contenedor centrado
        center = ctk.CTkFrame(empty_frame, fg_color="transparent")
        center.pack(expand=True)
        
        ctk.CTkLabel(
            center,
            text="👥",
            font=("Helvetica", 64),
            text_color=config.COLORS["text_light"]
        ).pack(pady=(0, 15))
        
        ctk.CTkLabel(
            center,
            text="No hay clientes registrados",
            font=("Helvetica", 18, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            center,
            text="Haz clic en '➕ Nuevo Cliente' para crear uno",
            font=("Helvetica", 13),
            text_color=config.COLORS["text_light"]
        ).pack()
    
    def _crear_tabla_visual(self, clientes_data):
        """Crear tabla visual de clientes"""
        # Container de la tabla
        tabla_container = ctk.CTkFrame(self.frame_tabla, fg_color=config.COLORS["dark_bg"], corner_radius=10)
        tabla_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # === ENCABEZADO DE TABLA ===
        header_frame = ctk.CTkFrame(tabla_container, fg_color=config.COLORS["info"], corner_radius=10)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        columns = ["ID", "Nombre", "Mesa", "Personas", "Teléfono", "Estado", "Acciones"]
        column_widths = [50, 150, 80, 100, 120, 100, 120]
        
        for col, (header_text, width) in enumerate(zip(columns, column_widths)):
            ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=("Helvetica", 11, "bold"),
                text_color=config.COLORS["text_light"]
            ).grid(row=0, column=col, padx=12, pady=12, sticky="w", width=width)
        
        # === FILAS DE DATOS ===
        for row_idx, cliente_data in enumerate(clientes_data, 1):
            cliente_id, nombre, mesa, personas, telefono, estado = cliente_data
            
            # Alternancia de colores
            bg_color = config.COLORS["light_bg"] if row_idx % 2 == 0 else config.COLORS["dark_bg"]
            row_frame = ctk.CTkFrame(tabla_container, fg_color=bg_color)
            row_frame.pack(fill="x", padx=10, pady=3, ipady=8)
            
            # ID
            ctk.CTkLabel(
                row_frame,
                text=str(cliente_id),
                font=("Helvetica", 10),
                text_color=config.COLORS["secondary"]
            ).grid(row=0, column=0, padx=12, sticky="w", width=50)
            
            # Nombre
            ctk.CTkLabel(
                row_frame,
                text=nombre,
                font=("Helvetica", 11, "bold"),
                text_color=config.COLORS["text_dark"]
            ).grid(row=0, column=1, padx=12, sticky="w", width=150)
            
            # Mesa
            mesa_text = f"Mesa {mesa}" if isinstance(mesa, int) else str(mesa)
            ctk.CTkLabel(
                row_frame,
                text=mesa_text,
                font=("Helvetica", 10),
                text_color=config.COLORS["secondary"]
            ).grid(row=0, column=2, padx=12, sticky="w", width=80)
            
            # Personas
            personas_text = f"{personas} pax"
            ctk.CTkLabel(
                row_frame,
                text=personas_text,
                font=("Helvetica", 10),
                text_color=config.COLORS["secondary"]
            ).grid(row=0, column=3, padx=12, sticky="w", width=100)
            
            # Teléfono
            ctk.CTkLabel(
                row_frame,
                text=telefono if telefono != "—" else "—",
                font=("Helvetica", 10),
                text_color=config.COLORS["secondary"]
            ).grid(row=0, column=4, padx=12, sticky="w", width=120)
            
            # Estado (badge)
            estado_color = self._get_color_estado(estado)
            estado_frame = ctk.CTkFrame(row_frame, fg_color=estado_color, corner_radius=6)
            estado_frame.grid(row=0, column=5, padx=12, sticky="w", width=100)
            
            ctk.CTkLabel(
                estado_frame,
                text=estado.capitalize(),
                font=("Helvetica", 9, "bold"),
                text_color=config.COLORS["text_light"]
            ).pack(padx=8, pady=3)
            
            # Botones de acción
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=6, padx=12, sticky="w", width=120)
            
            # Botón Editar
            btn_edit = ctk.CTkButton(
                actions_frame,
                text="✏️ Editar",
                font=("Helvetica", 9),
                fg_color=config.COLORS["warning"],
                hover_color=config.COLORS["accent"],
                text_color=config.COLORS["text_light"],
                height=28,
                width=60,
                command=lambda cid=cliente_id: self._editar_cliente(cid)
            )
            btn_edit.pack(side="left", padx=2)
            
            # Botón Eliminar
            btn_delete = ctk.CTkButton(
                actions_frame,
                text="🗑️ Borrar",
                font=("Helvetica", 9),
                fg_color=config.COLORS["danger"],
                hover_color=config.COLORS["primary"],
                text_color=config.COLORS["text_light"],
                height=28,
                width=60,
                command=lambda cid=cliente_id: self._eliminar_cliente(cid)
            )
            btn_delete.pack(side="left", padx=2)
    
    def _get_color_estado(self, estado):
        """Obtener color según estado"""
        if estado.lower() == "comiendo":
            return config.COLORS["success"]
        elif estado.lower() == "pagado":
            return config.COLORS["info"]
        else:  # cancelado
            return config.COLORS["secondary"]
    
    def _crear_dialogo_form(self, title, is_edit=False, cliente=None):
        """Builder de formulario unificado"""
        dialog = ctk.CTkToplevel()
        dialog.configure(fg_color="#FFFFFF")
        dialog.title(title)
        dialog.geometry("420x680")
        dialog.resizable(False, False)
        
        # Centrar
        x = (dialog.winfo_screenwidth() // 2) - 210
        y = (dialog.winfo_screenheight() // 2) - 340
        dialog.geometry(f"420x680+{x}+{y}")
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="white", height=70)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=title, font=("Segoe UI", 22, "bold"), text_color="#111827").pack(side="left", padx=24, pady=20)
        
        # Scroll area
        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=0)
        
        content = ctk.CTkFrame(scroll, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=10)
        
        entries = {}
        error_labels = {}
        
        def add_field(key, label_text, placeholder, value=""):
            ctk.CTkLabel(content, text=label_text, font=("Segoe UI", 12, "bold"), text_color="#374151").pack(anchor="w", pady=(8, 4))
            entry = ctk.CTkEntry(
                content, 
                placeholder_text=placeholder, 
                height=40, 
                border_color="#D1D5DB", 
                fg_color="white", 
                text_color="#111827",
                corner_radius=8,
                font=("Segoe UI", 13)
            )
            entry.pack(fill="x")
            if value: entry.insert(0, str(value))
            if is_edit and key == 'cedula': entry.configure(state="disabled", fg_color="#F3F4F6")
            
            lbl_err = ctk.CTkLabel(content, text="", text_color="#EF4444", font=("Segoe UI", 10), height=14)
            lbl_err.pack(anchor="w", pady=(2, 0))
            
            entries[key] = entry
            error_labels[key] = lbl_err

        # Campos
        add_field("cedula", "Cédula / RUC", "Ej: 1720...", cliente.cedula if cliente else "")
        add_field("nombre", "Nombres", "Ej: Juan Alberto", cliente.nombre if cliente else "")
        add_field("apellido", "Apellidos", "Ej: Pérez", cliente.apellido if cliente else "")
        add_field("telefono", "Teléfono Móvil", "099...", cliente.telefono if cliente else "")
        add_field("correo", "Correo Electrónico", "juan@gmail.com", cliente.correo if cliente else "")
        add_field("direccion", "Dirección Domiciliaria", "Av. Principal...", cliente.direccion if cliente else "")
        
        # Footer
        footer = ctk.CTkFrame(dialog, fg_color="white", height=80)
        footer.pack(fill="x", side="bottom")
        ctk.CTkFrame(footer, height=1, fg_color="#F3F4F6").pack(fill="x")
        
        def save():
            # Limpiar errores
            for l in error_labels.values(): l.configure(text="")
            
            # Recoger datos
            data = {k: v.get().strip() for k, v in entries.items()}
            valid = True
            
            # Validaciones rápidas
            check_map = {
                'cedula': self._validar_cedula, 'nombre': self._validar_nombre,
                'apellido': self._validar_nombre, 'telefono': self._validar_telefono,
                'correo': self._validar_correo, 'direccion': self._validar_direccion
            }
            
            for k, func in check_map.items():
                ok, msg = func(data[k])
                if not ok:
                    error_labels[k].configure(text=msg)
                    valid = False
            
            if not valid: return
            
            # Ejecutar acción
            if is_edit:
                success, _, msg = self.controller.actualizar_cliente(cliente.id, data['nombre'], data['apellido'], data['telefono'], data['direccion'], data['correo'])
            else:
                success, _, msg = self.controller.crear_cliente(data['cedula'], data['nombre'], data['apellido'], data['telefono'], data['direccion'], data['correo'])
                
            if success:
                dialog.destroy()
                self.refrescar_tabla()
                DialogUtils.mostrar_exito("Éxito", "Operación realizada correctamente", parent=self)
            else:
                DialogUtils.mostrar_error("Error", msg, parent=dialog)

        btn_box = ctk.CTkFrame(footer, fg_color="transparent")
        btn_box.pack(expand=True, pady=15)
        
        ctk.CTkButton(
            btn_box, text="Guardar", command=save, width=140, height=40,
            fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 13, "bold"), corner_radius=20
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_box, text="Cancelar", command=dialog.destroy, width=100, height=40,
            fg_color="#F3F4F6", text_color="#374151", hover_color="#E5E7EB", font=("Segoe UI", 13, "bold"), corner_radius=20
        ).pack(side="left", padx=5)

    def _crear_dialogo_nuevo_cliente(self):
        self._crear_dialogo_form("Nuevo Cliente")
    
    def _editar_cliente(self, cliente_id, dialog_parent=None):
        if dialog_parent: dialog_parent.destroy()
        success, cliente, msg = self.controller.obtener_cliente(cliente_id)
        if success:
            self._crear_dialogo_form("Editar Cliente", is_edit=True, cliente=cliente)
        else:
            DialogUtils.mostrar_error("Error", "No se encontró el cliente")

    # MÉTODOS OBSOLETOS REEMPLAZADOS POR EL BUILDER _crear_dialogo_form
    # Se mantienen abajo solo para evitar errores de referencia si algún código viejo los llama,
    # aunque idealmente deberían desaparecer. En este caso los sobreescribo totalmente arriba.
    
    def _old_crear_dialogo(self):
        pass

    
    def _eliminar_cliente(self, cliente_id):
        """Eliminar cliente con confirmación"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Eliminar Cliente")
        ventana.geometry("480x280")
        ventana.resizable(False, False)
        ventana.update_idletasks()
        # Centrar ventana en la pantalla
        x = (ventana.winfo_screenwidth() // 2) - (240)
        y = (ventana.winfo_screenheight() // 2) - (140)
        ventana.geometry(f"480x280+{x}+{y}")
        ventana.attributes('-topmost', True)
        ventana.configure(fg_color="#FFFFFF")
        ventana.grab_set()
        
        # Header del diálogo con icono
        header_frame = ctk.CTkFrame(ventana, fg_color="#FEE2E2", height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24, pady=20)
        
        ctk.CTkLabel(
            header_content,
            text="⚠️ Eliminar Cliente",
            text_color="#DC2626",
            font=("Helvetica", 18, "bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_content,
            text="Esta acción no se puede deshacer",
            text_color="#991B1B",
            font=("Helvetica", 11)
        ).pack(anchor="w", pady=(2, 0))
        
        # Separador
        separator = ctk.CTkFrame(ventana, fg_color="#F3F4F6", height=1)
        separator.pack(fill="x", pady=0, padx=0)
        
        # Contenido principal
        content_frame = ctk.CTkFrame(ventana, fg_color="#FFFFFF")
        content_frame.pack(fill="both", expand=True, padx=24, pady=20)
        
        ctk.CTkLabel(
            content_frame,
            text="¿Estás seguro de que deseas eliminar este cliente?",
            text_color="#1F2937",
            font=("Helvetica", 13, "bold")
        ).pack(anchor="w", pady=(0, 12))
        
        ctk.CTkLabel(
            content_frame,
            text="Se eliminarán todos los datos y registros asociados.",
            text_color="#6B7280",
            font=("Helvetica", 11)
        ).pack(anchor="w")
        
        # Separador antes de botones
        separator2 = ctk.CTkFrame(ventana, fg_color="#F3F4F6", height=1)
        separator2.pack(fill="x", pady=0, padx=0)
        
        # Botones
        btn_frame = ctk.CTkFrame(ventana, fg_color="#FFFFFF")
        btn_frame.pack(fill="x", padx=20, pady=16)
        
        def confirmar():
            success, _, msg = self.controller.eliminar_cliente(cliente_id)
            if success:
                DialogUtils.mostrar_exito("Éxito", "Cliente eliminado exitosamente", parent=ventana)
                ventana.destroy()
                self.refrescar_tabla()
            else:
                DialogUtils.mostrar_error("Error", msg, parent=ventana)
        
        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="✕ Cancelar",
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color="#374151",
            command=ventana.destroy,
            height=40,
            font=("Helvetica", 11, "bold"),
            corner_radius=7
        )
        btn_cancelar.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        btn_eliminar = ctk.CTkButton(
            btn_frame,
            text="✓ Eliminar",
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="white",
            command=confirmar,
            height=40,
            font=("Helvetica", 11, "bold"),
            corner_radius=7
        )
        btn_eliminar.pack(side="left", padx=(10, 0), expand=True, fill="x")
    
    def _mostrar_exito(self, mensaje):
        """Mostrar mensaje de éxito"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Éxito")
        ventana.geometry("350x120")
        ventana.resizable(False, False)
        ventana.update_idletasks()
        # Centrar ventana en la pantalla
        x = (ventana.winfo_screenwidth() // 2) - (175)
        y = (ventana.winfo_screenheight() // 2) - (60)
        ventana.geometry(f"350x120+{x}+{y}")
        ventana.attributes('-topmost', True)
        
        frame = ctk.CTkFrame(ventana, fg_color=config.COLORS["success"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"✓ {mensaje}",
            font=("Helvetica", 13, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=20)
        
        ventana.after(2000, ventana.destroy)
    
    def _mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Error")
        ventana.geometry("350x120")
        ventana.resizable(False, False)
        ventana.update_idletasks()
        # Centrar ventana en la pantalla
        x = (ventana.winfo_screenwidth() // 2) - (175)
        y = (ventana.winfo_screenheight() // 2) - (60)
        ventana.geometry(f"350x120+{x}+{y}")
        ventana.attributes('-topmost', True)
        
        frame = ctk.CTkFrame(ventana, fg_color=config.COLORS["danger"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"✗ {mensaje}",
            font=("Helvetica", 13, "bold"),
            text_color=config.COLORS["text_light"]
        ).pack(pady=20)
        
        ventana.after(3000, ventana.destroy)
