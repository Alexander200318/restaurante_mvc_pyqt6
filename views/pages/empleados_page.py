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
        
        # Estado de Paginación
        self.pagina_actual = 1
        self.registros_por_pagina = 20
        self.total_paginas = 1
        self.todos_los_datos = []
        
        self._crear_ui()
        self.refrescar_tabla()
    
    def _crear_ui(self):
        """Crear interfaz con diseño ULTRA moderno y refinado"""
        
        # --- HEADER PRINCIPAL (Estilo Flat moderno) ---
        self.header_bg = config.COLORS["primary"]
        
        frame_header = ctk.CTkFrame(
            self, 
            fg_color=self.header_bg,
            corner_radius=0, 
            height=85
        )
        frame_header.pack(fill="x", padx=0, pady=0)
        
        # Contenedor interno del header
        header_content = ctk.CTkFrame(frame_header, fg_color="transparent")
        header_content.pack(fill="x", padx=40, pady=25)
        
        # Título con tipografía elegante
        titulo = ctk.CTkLabel(
            header_content,
            text="GESTIÓN DE TALENTO HUMANO",
            text_color="#FFFFFF",
            font=("Segoe UI Display", 26, "bold")
        )
        titulo.pack(side="left")
        
        # Subtítulo pequeño o breadcrumb
        subtitulo = ctk.CTkLabel(
            header_content,
            text=" / Directorio Activo",
            text_color="#FEF3C7", # Amarillo muy claro
            font=("Segoe UI", 16)
        )
        subtitulo.pack(side="left", pady=(8,0), padx=5)

        # --- CONTENIDO PRINCIPAL ---
        # Fondo general más limpio
        self.contenido = ctk.CTkFrame(self, fg_color="#F8FAFC") # Slate-50 background
        self.contenido.pack(fill="both", expand=True)
        
        # Layout de dos columnas con espaciado generoso
        frame_layout = ctk.CTkFrame(self.contenido, fg_color="transparent")
        frame_layout.pack(fill="both", expand=True, padx=40, pady=30)
        
        # 1. COLUMNA IZQUIERDA: DIRECTORIO (Flexible)
        col_izquierda = ctk.CTkFrame(frame_layout, fg_color="transparent")
        col_izquierda.pack(side="left", fill="both", expand=True, padx=(0, 25))
        
        # Barra de Acciones (Floating style)
        acciones_frame = ctk.CTkFrame(col_izquierda, fg_color="transparent", height=50)
        acciones_frame.pack(fill="x", pady=(0, 20))
        
        # Stats rápidas (Simuladas visualmente por ahora)
        filtros_frame = ctk.CTkFrame(acciones_frame, fg_color="white", corner_radius=20, border_width=1, border_color="#E2E8F0")
        filtros_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(filtros_frame, text="🔍", font=("Segoe UI", 14), text_color="#64748B").pack(side="left", padx=(15, 5))
        ctk.CTkEntry(
            filtros_frame, 
            placeholder_text="Buscar empleado...", 
            border_width=0, 
            fg_color="transparent",
            width=200,
            text_color="#334155",
            font=("Segoe UI", 13)
        ).pack(side="left", padx=(0, 15), pady=5)

        # Botón Nuevo (Gradiante visual o color sólido fuerte)
        btn_nuevo = ctk.CTkButton(
            acciones_frame,
            text="＋ NUEVO CONTRATO",
            command=self.crear_empleado,
            fg_color="#10B981", # Emerald-500
            hover_color="#059669", # Emerald-600
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            height=42,
            corner_radius=21, # Pill shape
            width=180
        )
        btn_nuevo.pack(side="right")
        
        # Tabla Containers (Elevated Card)
        card_tabla = ctk.CTkFrame(
            col_izquierda, 
            fg_color="white", 
            corner_radius=16,
            border_width=0, # Sin borde, solo sombra (no soportada nativamente, simulamos con contraste)
        )
        card_tabla.pack(fill="both", expand=True)
        
        # Linea decorativa top tabla
        ctk.CTkFrame(card_tabla, height=4, fg_color=config.COLORS["primary"], corner_radius=2).pack(fill="x")

        # --- Controles de Paginación (Al pie) ---
        self.frame_paginacion = ctk.CTkFrame(card_tabla, fg_color="transparent", height=40)
        self.frame_paginacion.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.btn_anterior = ctk.CTkButton(
            self.frame_paginacion,
            text="◀ Anterior",
            width=90,
            height=28,
            font=("Segoe UI", 11),
            fg_color="#F1F5F9",
            text_color="#64748B",
            hover_color="#E2E8F0",
            state="disabled",
            command=self._pagina_anterior
        )
        self.btn_anterior.pack(side="left")
        
        self.lbl_paginacion = ctk.CTkLabel(
            self.frame_paginacion,
            text="Página 1 de 1",
            font=("Segoe UI", 12, "bold"),
            text_color="#64748B"
        )
        self.lbl_paginacion.pack(side="left", expand=True)

        self.btn_siguiente = ctk.CTkButton(
            self.frame_paginacion,
            text="Siguiente ▶",
            width=90,
            height=28,
            font=("Segoe UI", 11),
            fg_color="#F1F5F9",
            text_color="#64748B",
            hover_color="#E2E8F0",
            state="disabled",
            command=self._pagina_siguiente
        )
        self.btn_siguiente.pack(side="right")
        
        # Tabla
        self.tabla = TreeViewWidget(
            card_tabla,
            columnas=["Nombre Completo", "Cargo", "Teléfono", "Email Corporativo", "Salario Base", "Estado"],
            altura=15, # Ajustado para asegurar visibilidad en pantalla
            font_size=13, # Texto más grande
            heading_font_size=12,
            row_height=40 # Filas aireadas pero manejables
        )
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.tabla.set_on_select(self._on_empleado_select)
        # -------------------------------
        
        # 2. COLUMNA DERECHA: PERFIL (Fijo)
        self.panel_perfil = ctk.CTkFrame(
            frame_layout, 
            fg_color="white", 
            width=380, # Panel más ancho
            corner_radius=20
        )
        self.panel_perfil.pack(side="right", fill="y", padx=0, pady=0)
        self.panel_perfil.pack_propagate(False)
        
        self._construir_perfil_ui()

    def _construir_perfil_ui(self):
        """Construye el panel derecho de perfil COMPACTO"""
        
        # Header Perfil (Más compacto)
        header_perfil = ctk.CTkFrame(self.panel_perfil, fg_color="#F1F5F9", height=90, corner_radius=15)
        header_perfil.pack(fill="x", padx=10, pady=10)
        header_perfil.pack_propagate(False) # Mantener altura fija
        
        # Avatar Flotante (Más pequeño)
        self.avatar_frame = ctk.CTkFrame(header_perfil, width=60, height=60, corner_radius=30, fg_color="white")
        self.avatar_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.lbl_avatar_emoji = ctk.CTkLabel(self.avatar_frame, text="👤", font=("Segoe UI", 30))
        self.lbl_avatar_emoji.place(relx=0.5, rely=0.5, anchor="center")
        
        # Nombre y Cargo (Menos espacio vertical)
        frame_info_header = ctk.CTkFrame(self.panel_perfil, fg_color="transparent")
        frame_info_header.pack(fill="x", pady=(5, 5))
        
        self.lbl_nombre_perfil = ctk.CTkLabel(
            frame_info_header,
            text="Seleccione Empleado",
            font=("Segoe UI", 16, "bold"),
            text_color="#1E293B"
        )
        self.lbl_nombre_perfil.pack(pady=(0, 0))
        
        self.lbl_cargo_perfil = ctk.CTkLabel(
            frame_info_header,
            text="---",
            font=("Segoe UI", 13),
            text_color="#64748B"
        )
        self.lbl_cargo_perfil.pack(pady=(0, 5))
        
        # Badge Estado (Compacto)
        self.badge_estado = ctk.CTkFrame(frame_info_header, fg_color="#E2E8F0", corner_radius=8, height=20)
        self.badge_estado.pack()
        self.lbl_estado_texto = ctk.CTkLabel(self.badge_estado, text="INACTIVO", font=("Segoe UI", 9, "bold"), text_color="#64748B")
        self.lbl_estado_texto.pack(padx=8, pady=1)

        # Detalles (Grid 2 columnas para ahorrar espacio)
        self.info_container = ctk.CTkFrame(self.panel_perfil, fg_color="transparent")
        self.info_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Fila 1: Teléfono y Email
        self._crear_fila_doble("📱 Teléfono", "lbl_tel_val", "📧 Email", "lbl_email_val")
        
        # Separador sutil
        ctk.CTkFrame(self.info_container, height=1, fg_color="#E2E8F0").pack(fill="x", pady=10)

        # Fila 2: Salario y ID
        self._crear_fila_doble("💰 Salario", "lbl_salario_val", "🆔 ID", "lbl_id_val")

        # Espaciador flexible para empujar botones al fondo si sobra espacio
        ctk.CTkLabel(self.panel_perfil, text="").pack(expand=True)

        # Botones Pie (Compactos)
        frame_btns = ctk.CTkFrame(self.panel_perfil, fg_color="transparent")
        frame_btns.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.btn_editar = ctk.CTkButton(
            frame_btns,
            text="Editar Perfil",
            command=self.editar_empleado,
            fg_color="#3B82F6", 
            hover_color="#2563EB",
            height=35, # Botón más delgado
            corner_radius=8,
            font=("Segoe UI", 12, "bold"),
            state="disabled"
        )
        self.btn_editar.pack(fill="x", pady=(0, 8))
        
        self.btn_eliminar = ctk.CTkButton(
            frame_btns,
            text="Dar de Baja",
            command=self.eliminar_empleado,
            fg_color="#FEE2E2", # Rojo muy claro (Soft UI)
            hover_color="#FCA5A5", # Rojo suave al pasar mouse
            text_color="#B91C1C", # Rojo oscuro texto (Contrast 700)
            height=35, 
            corner_radius=8,
            font=("Segoe UI", 12, "bold"),
            state="disabled"
        )
        self.btn_eliminar.pack(fill="x")
        
    def _crear_fila_doble(self, titulo1, attr1, titulo2, attr2):
        """Crea una fila con dos columnas de datos"""
        row = ctk.CTkFrame(self.info_container, fg_color="transparent")
        row.pack(fill="x", pady=5)
        
        # Columna 1
        col1 = ctk.CTkFrame(row, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(col1, text=titulo1, font=("Segoe UI", 10, "bold"), text_color="#94A3B8", anchor="w").pack(fill="x")
        lbl1 = ctk.CTkLabel(col1, text="---", font=("Segoe UI", 12), text_color="#334155", anchor="w")
        lbl1.pack(fill="x")
        setattr(self, attr1, lbl1)
        
        # Columna 2
        col2 = ctk.CTkFrame(row, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(10, 0)) # Margen entre columnas
        
        ctk.CTkLabel(col2, text=titulo2, font=("Segoe UI", 10, "bold"), text_color="#94A3B8", anchor="w").pack(fill="x")
        lbl2 = ctk.CTkLabel(col2, text="---", font=("Segoe UI", 12), text_color="#334155", anchor="w")
        lbl2.pack(fill="x")
        setattr(self, attr2, lbl2)

    def _crear_fila_info(self, seccion, icono, label, attr_name):
        # Deprecated
        pass

    def _crear_panel_informacion(self, parent):
        # Deprecated
        pass

    def _crear_item_detalle(self, titulo):
        # Deprecated logic kept safe
        pass
    
    def _crear_card_info(self, parent, etiqueta, valor):
        # Deprecated
        pass
    
    def _actualizar_panel(self):
        """Actualizar datos del perfil seleccionado"""
        if not self.empleado_seleccionado:
            self._reset_panel()
            return
        
        # Activar controles
        self.btn_editar.configure(state="normal", fg_color="#3B82F6")
        self.btn_eliminar.configure(state="normal", text_color="#EF4444", border_color="#EF4444")
        
        datos = self.empleado_seleccionado
        # [ID, Nombre, Puesto, Teléfono, Email, Salario, Estado]
        
        # Header Info
        self.lbl_nombre_perfil.configure(text=str(datos[1]))
        self.lbl_cargo_perfil.configure(text=str(datos[2]))
        
        # Estado Badge
        estado_str = str(datos[6]).upper()
        if estado_str == "ACTIVO":
            self.badge_estado.configure(fg_color="#DCFCE7") # Green-100
            self.lbl_estado_texto.configure(text="ACTIVO", text_color="#166534") # Green-800
        else:
            self.badge_estado.configure(fg_color="#FEE2E2") # Red-100
            self.lbl_estado_texto.configure(text="INACTIVO", text_color="#991B1B") # Red-800
            
        # Detalles
        self.lbl_tel_val.configure(text=str(datos[3]))
        self.lbl_email_val.configure(text=str(datos[4]))
        self.lbl_salario_val.configure(text=str(datos[5]))
        self.lbl_id_val.configure(text=f"EMP-{str(datos[0]).zfill(4)}")

    def _reset_panel(self):
        self.lbl_nombre_perfil.configure(text="Seleccione Empleado")
        self.lbl_cargo_perfil.configure(text="---")
        self.badge_estado.configure(fg_color="#E2E8F0")
        self.lbl_estado_texto.configure(text="---", text_color="#64748B")
        
        self.lbl_tel_val.configure(text="---")
        self.lbl_email_val.configure(text="---")
        self.lbl_salario_val.configure(text="---")
        self.lbl_id_val.configure(text="---")
        
        self.btn_editar.configure(state="disabled", fg_color="#94A3B8")
        self.btn_eliminar.configure(state="disabled", text_color="#94A3B8", border_color="#E2E8F0")

    def _on_empleado_select(self, datos):
        self.empleado_seleccionado = datos
        self._actualizar_panel()

    def refrescar_tabla(self):
        """Refrescar tabla de empleados con paginación"""
        success, datos, msg = self.controller.obtener_todos_empleados_formateados()
        if success:
            self.todos_los_datos = datos
            # Calcular total páginas
            import math
            self.total_paginas = math.ceil(len(datos) / self.registros_por_pagina)
            if self.total_paginas == 0: self.total_paginas = 1
            
            self.pagina_actual = 1
            self._mostrar_pagina_actual()
            
            self.empleado_seleccionado = None
            self._actualizar_panel()
        else:
            DialogUtils.mostrar_error("Error", msg)

    def _mostrar_pagina_actual(self):
        """Renderiza los datos de la página actual en la tabla"""
        self.tabla.limpiar()
        
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        datos_slice = self.todos_los_datos[inicio:fin]
        
        for dato in datos_slice:
            # Omitimos el primer elemento (ID) para la vista
            self.tabla.agregar_fila(dato[1:], datos_ocultos=dato)
            
        self._actualizar_estado_paginacion()

    def _actualizar_estado_paginacion(self):
        """Actualiza label y botones de paginación"""
        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} de {self.total_paginas}")
        
        # Estado botón Anterior
        if self.pagina_actual > 1:
            self.btn_anterior.configure(state="normal", fg_color="#3B82F6", text_color="white")
        else:
            self.btn_anterior.configure(state="disabled", fg_color="#F1F5F9", text_color="#94A3B8")
            
        # Estado botón Siguiente
        if self.pagina_actual < self.total_paginas:
            self.btn_siguiente.configure(state="normal", fg_color="#3B82F6", text_color="white")
        else:
            self.btn_siguiente.configure(state="disabled", fg_color="#F1F5F9", text_color="#94A3B8")

    def _pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self._mostrar_pagina_actual()

    def _pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._mostrar_pagina_actual()
    
    def crear_empleado(self):
        puestos = self.controller.obtener_puestos_disponibles()
        
        campos = {
            'nombre': {'label': '👤 Nombre', 'type': 'text', 'required': True},
            'puesto': {'label': '💼 Puesto', 'type': 'dropdown', 'options': puestos, 'required': True},
            'telefono': {'label': '📱 Teléfono', 'type': 'phone', 'required': True},
            'email': {'label': '📧 Email', 'type': 'email', 'required': True},
            'salario': {'label': '💰 Salario', 'type': 'number', 'required': True, 'min': 0}
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
                return True # Cerrar diálogo
            else:
                # Si el error es de tipo específico (puesto, email, etc), lo devolvemos
                # como un dict de errores para mostrar inline.
                msg_lower = msg.lower() if msg else ""
                
                if "email" in msg_lower:
                    return {'email': msg}
                elif "telefono" in msg_lower:
                    return {'telefono': msg}
                elif "salario" in msg_lower:
                    return {'salario': msg}
                    
                DialogUtils.mostrar_error("Error", msg)
                return False # Mantener abierto
        
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
            salario_str = str(salario_str).replace("$", "").replace(",", "").strip()
            salario_num = float(salario_str) if salario_str and salario_str != "—" else ""
        except ValueError:
            salario_num = ""
        
        puestos = self.controller.obtener_puestos_disponibles()
        estados = ["ACTIVO", "INACTIVO"]
        
        campos = {
            'nombre': {'label': '👤 Nombre', 'type': 'text', 'value': nombre, 'required': True},
            'puesto': {'label': '💼 Puesto', 'type': 'dropdown', 'options': puestos, 'value': puesto, 'required': True},
            'telefono': {'label': '📱 Teléfono', 'type': 'phone', 'value': telefono, 'required': True},
            'email': {'label': '📧 Email', 'type': 'email', 'value': email, 'required': True},
            'salario': {'label': '💰 Salario', 'type': 'number', 'value': salario_num, 'required': True, 'min': 0},
            'estado': {'label': '🔖 Estado', 'type': 'dropdown', 'options': estados, 'value': estado, 'required': True}
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
                msg_lower = msg.lower() if msg else ""
                if "email" in msg_lower: return {'email': msg}
                if "telefono" in msg_lower: return {'telefono': msg}
                
                DialogUtils.mostrar_error("Error", msg)
                return False
            
            # Actualizar estado si cambió
            if valores.get('estado') and valores.get('estado') != estado:
                success_estado, _, msg_estado = self.controller.cambiar_estado_empleado(
                    id_emp,
                    valores.get('estado')
                )
                if not success_estado:
                    DialogUtils.mostrar_error("Error al actualizar estado", msg_estado)
                    return False
            
            DialogUtils.mostrar_exito("Éxito", "Empleado actualizado")
            self.refrescar_tabla()
            return True
        
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
