"""
Página: Gestión de Empleados
"""
import customtkinter as ctk
from datetime import datetime
try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

from controllers.empleados_controller import EmpleadosController
from controllers.turnos_controller import TurnosController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils, FormDialog
import config

class EmpleadosPage(ctk.CTkFrame):
    """Módulo de Empleados"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controller = EmpleadosController()
        self.turnos_controller = TurnosController()
        self.tabla = None
        self.empleado_seleccionado = None
        self.label_info_nombre = None
        self.label_info_puesto = None
        self.label_info_telefono = None
        self.label_info_email = None
        self.label_info_salario = None
        self.label_info_estado = None
        
        # Turnos activos para cronómetro
        self._turnos_activos_ui = {} # {item_id: timestamp_inicio}
        self._cronometro_id = None
        
        # Estado de Paginación
        self.pagina_actual = 1
        self.registros_por_pagina = 20
        self.total_paginas = 1
        self.todos_los_datos = []
        self.datos_filtrados = [] # Datos filtrados para la tabla principal
        
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
        
        # Entrada de Búsqueda Frontend - Mejorada
        self.var_busqueda_principal = ctk.StringVar()
        self.entry_busqueda_principal = ctk.CTkEntry(
            filtros_frame, 
            placeholder_text="Buscar empleado...", 
            border_width=0, 
            fg_color="transparent",
            width=200,
            text_color="#334155",
            font=("Segoe UI", 13),
            textvariable=self.var_busqueda_principal
        )
        self.entry_busqueda_principal.pack(side="left", padx=(0, 15), pady=5)
        
        # Trace para filtrar en tiempo real
        self.var_busqueda_principal.trace_add("write", lambda *args: self._filtrar_empleados_principal())

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
        btn_nuevo.pack(side="right") # Pack es relativo, va a la derecha del todo
        
        # Botón Historial Turnos (A la izquierda de Nuevo Contrato)
        btn_historial = ctk.CTkButton(
            acciones_frame,
            text="📅 HISTORIAL TURNOS",
            command=self.mostrar_historial_turnos,
            fg_color="#6366F1", # Indigo-500
            hover_color="#4F46E5", # Indigo-600
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            height=42,
            corner_radius=21, # Pill shape
            width=180
        )
        btn_historial.pack(side="right", padx=(0, 10))
        
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
            columnas=["Nombre Completo", "Cargo", "Teléfono", "Email Corporativo", "Salario Base", "Estado", "Tiempo Turno"],
            altura=15, # Ajustado para asegurar visibilidad en pantalla
            font_size=13, # Texto más grande
            heading_font_size=12,
            row_height=40 # Filas aireadas pero manejables
        )
        self.tabla.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.tabla.set_on_select(self._on_empleado_select)

        # Iniciar cronómetro
        self._iniciar_cronometro()
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
        self._crear_fila_doble("� Salario", "lbl_salario_val", "🆔 ID", "lbl_id_val")

        # Espaciador flexible para empujar botones al fondo si sobra espacio
        ctk.CTkLabel(self.panel_perfil, text="").pack(expand=True)
        
        # --- SECCIÓN CONTROL TURNOS EN PANEL ---
        self.frame_control_turnos = ctk.CTkFrame(self.panel_perfil, fg_color="#F8FAFC", corner_radius=10)
        self.frame_control_turnos.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(self.frame_control_turnos, text="Control Check-In/Out", font=("Segoe UI", 11, "bold"), text_color="#64748B").pack(pady=(10,5))
        
        self.btn_marcar_entrada = ctk.CTkButton(
            self.frame_control_turnos,
            text="⏰ Marcar Entrada",
            command=self._on_marcar_entrada,
            fg_color="#10B981", 
            hover_color="#059669",
            height=32,
            font=("Segoe UI", 12),
            state="disabled"
        )
        self.btn_marcar_entrada.pack(fill="x", padx=10, pady=(0, 5))
        
        self.btn_marcar_salida = ctk.CTkButton(
            self.frame_control_turnos,
            text="🏠 Marcar Salida",
            command=self._on_marcar_salida,
            fg_color="#EF4444", 
            hover_color="#DC2626",
            height=32,
            font=("Segoe UI", 12),
            state="disabled"
        )
        self.btn_marcar_salida.pack(fill="x", padx=10, pady=(0, 10))
        
        # ---------------------------------------

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
            self._reset_botones_turno()
            return
        
        # Activar controles básicos
        self.btn_editar.configure(state="normal", fg_color="#3B82F6")
        self.btn_eliminar.configure(state="normal", text_color="#EF4444", border_color="#EF4444")
        
        datos = self.empleado_seleccionado
        # [ID, Nombre, Puesto, Teléfono, Email, Salario, Estado]
        emp_id = datos[0]
        emp_estado = str(datos[6]).upper()
        
        # Actualizar Info Perfil
        self.lbl_nombre_perfil.configure(text=str(datos[1]))
        self.lbl_cargo_perfil.configure(text=str(datos[2]))
        
        if emp_estado == "ACTIVO":
            self.badge_estado.configure(fg_color="#DCFCE7") # Green-100
            self.lbl_estado_texto.configure(text="ACTIVO", text_color="#166534") # Green-800
        else:
            self.badge_estado.configure(fg_color="#FEE2E2") # Red-100
            self.lbl_estado_texto.configure(text="INACTIVO", text_color="#991B1B") # Red-800
            
        self.lbl_tel_val.configure(text=str(datos[3]))
        self.lbl_email_val.configure(text=str(datos[4]))
        self.lbl_salario_val.configure(text=str(datos[5]))
        self.lbl_id_val.configure(text=f"EMP-{str(datos[0]).zfill(4)}")

        # Actualizar Botones de Turno
        self._actualizar_estado_botones_turno(emp_id)

    def _reset_botones_turno(self):
        self.btn_marcar_entrada.configure(state="disabled", fg_color="#94A3B8")
        self.btn_marcar_salida.configure(state="disabled", fg_color="#94A3B8")

    def _actualizar_estado_botones_turno(self, emp_id):
        """Verifica si el empleado tiene turno abierto y configura botones"""
        success, turno_actual, _ = self.turnos_controller.obtener_turno_actual(emp_id)
        
        if turno_actual:
            # Tiene turno abierto -> Puede marcar salida
            self.btn_marcar_entrada.configure(state="disabled", fg_color="#94A3B8")
            self.btn_marcar_salida.configure(state="normal", fg_color="#EF4444")
        else:
            # No tiene turno abierto -> Puede marcar entrada
            self.btn_marcar_entrada.configure(state="normal", fg_color="#10B981")
            self.btn_marcar_salida.configure(state="disabled", fg_color="#94A3B8")
    
    def _on_marcar_entrada(self):
        if not self.empleado_seleccionado: return
        
        emp_id = self.empleado_seleccionado[0]
        nombre = self.empleado_seleccionado[1]
        
        success, _, msg = self.turnos_controller.iniciar_turno(emp_id)
        if success:
            DialogUtils.mostrar_exito("Turno Iniciado", f"Entrada registrada para {nombre}")
            self._actualizar_estado_botones_turno(emp_id)
        else:
            DialogUtils.mostrar_error("Error", msg)

    def _on_marcar_salida(self):
        if not self.empleado_seleccionado: return
        
        emp_id = self.empleado_seleccionado[0]
        nombre = self.empleado_seleccionado[1]
        
        success, _, msg = self.turnos_controller.finalizar_turno(emp_id)
        if success:
            DialogUtils.mostrar_exito("Turno Finalizado", f"Salida registrada para {nombre}")
            self._actualizar_estado_botones_turno(emp_id)
        else:
            DialogUtils.mostrar_error("Error", msg)
            
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
        
        # Reset Botones Turno
        self.btn_marcar_entrada.configure(state="disabled", fg_color="#94A3B8")
        self.btn_marcar_salida.configure(state="disabled", fg_color="#94A3B8")

    def _on_empleado_select(self, datos):
        self.empleado_seleccionado = datos
        self._actualizar_panel()
        
    def _on_marcar_entrada(self):
        if not self.empleado_seleccionado: return
        
        emp_id = self.empleado_seleccionado[0]
        emp_nombre = self.empleado_seleccionado[1]
        
        success, _, msg = self.turnos_controller.iniciar_turno(emp_id)
        if success:
            DialogUtils.mostrar_exito("Asistencia Registrada", f"✅ Turno iniciado para {emp_nombre}")
            self._actualizar_estado_botones_turno(emp_id)
            # Refrescar tabla para activar el contador
            self.refrescar_tabla()
        else:
            DialogUtils.mostrar_error("Error", msg)

    def _on_marcar_salida(self):
        if not self.empleado_seleccionado: return
        
        emp_id = self.empleado_seleccionado[0]
        emp_nombre = self.empleado_seleccionado[1]
        
        success, _, msg = self.turnos_controller.finalizar_turno(emp_id)
        if success:
            # Podríamos buscar el último turno para mostrar cuánto duró, pero por simplicidad solo confirmamos
            DialogUtils.mostrar_exito("Asistencia Registrada", f"🏁 Turno finalizado para {emp_nombre}")
            self._actualizar_estado_botones_turno(emp_id)
            # Refrescar tabla para detener el contador
            self.refrescar_tabla()
        else:
            DialogUtils.mostrar_error("Error", msg)

    def _actualizar_estado_botones_turno(self, emp_id):
        # Verificar si tiene turno abierto
        success, turno_abierto, _ = self.turnos_controller.obtener_turno_actual(emp_id)
        
        if turno_abierto:
            # Tiene turno abierto -> Habilitar SALIDA, Deshabilitar ENTRADA
            self.btn_marcar_entrada.configure(state="disabled", fg_color="#94A3B8")
            self.btn_marcar_salida.configure(state="normal", fg_color="#EF4444", hover_color="#DC2626")
        else:
            # No tiene turno abierto -> Habilitar ENTRADA, Deshabilitar SALIDA
            self.btn_marcar_entrada.configure(state="normal", fg_color="#10B981", hover_color="#059669")
            self.btn_marcar_salida.configure(state="disabled", fg_color="#94A3B8")
            
    def mostrar_historial_turnos(self):
        """Muestra ventana modal con el historial general y FILTROS AVANZADOS (Diseño Light Moderno)"""
        # Crear Toplevel
        toplevel = ctk.CTkToplevel(self)
        toplevel.title("Historial de Asistencia")
        toplevel.geometry("1100x750")
        toplevel.transient(self)
        toplevel.grab_set()
        
        # --- COLORES DEL TEMA LIGHT REFINADO ---
        theme = {
            "bg_main": "#F8FAFC",      # Slate-50
            "bg_panel": "#FFFFFF",     # White
            "text_primary": "#0F172A", # Slate-900 (Más oscuro, mayor contraste)
            "text_secondary": "#64748B", # Slate-500
            "accent": "#4F46E5",       # Indigo-600 (Más moderno que el azul estándar)
            "border": "#E2E8F0",       # Slate-200
            "input_bg": "#F1F5F9",     # Slate-100
            "input_fg": "#334155",     # Slate-700
            "success": "#10B981",      # Emerald-500
            "danger": "#EF4444"        # Red-500
        }
        
        toplevel.configure(fg_color=theme["bg_main"])
        
        # --- UI LAYOUT SUPERIOR ---
        # Header con gradiente simulado
        header = ctk.CTkFrame(toplevel, height=90, fg_color=theme["bg_panel"], corner_radius=0)
        header.pack(fill="x", pady=(0, 1)) # Línea separadora sutil
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="x", padx=40, pady=25)
        
        # Contenedor título con icono
        title_box = ctk.CTkFrame(header_content, fg_color="transparent")
        title_box.pack(side="left")
        
        # Icono decorativo
        icon_bg = ctk.CTkFrame(title_box, width=42, height=42, corner_radius=10, fg_color="#EEF2FF") # Indigo-50
        icon_bg.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(icon_bg, text="📅", font=("Segoe UI Emoji", 20)).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            title_box, 
            text="Registro de Asistencia", 
            font=("Segoe UI Display", 22, "bold"), 
            text_color=theme["text_primary"]
        ).pack(side="left")
        
        # Badge de "Control Mensual"
        badge = ctk.CTkFrame(title_box, fg_color="#F1F5F9", corner_radius=6)
        badge.pack(side="left", padx=10, pady=2)
        ctk.CTkLabel(badge, text="HISTORIAL UNIFICADO", font=("Segoe UI", 10, "bold"), text_color=theme["text_secondary"]).pack(padx=8, pady=2)

        # --- CONTENEDOR PRINCIPAL FLUIDO ---
        main_content = ctk.CTkFrame(toplevel, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=40, pady=25)

        # PANEL DE FILTROS FLOTANTE
        filtros_card = ctk.CTkFrame(
            main_content, 
            fg_color=theme["bg_panel"], 
            corner_radius=12,
            border_width=0 # Sin borde, solo sombra (si se pudiera) o limpio
            # border_color=theme["border"] # Borde eliminado para look más limpio
        )
        filtros_card.pack(fill="x", pady=(0, 20), ipady=5)
        
        # Decoración lateral filtro (Color accent)
        indicator = ctk.CTkFrame(filtros_card, width=4, fg_color=theme["accent"], corner_radius=0)
        indicator.pack(side="left", fill="y", padx=0, pady=0)
        
        # Título Filtros
        filtros_header = ctk.CTkFrame(filtros_card, fg_color="transparent", height=40)
        filtros_header.pack(fill="x", padx=20, pady=(15, 0))
        
        ctk.CTkLabel(
            filtros_header, 
            text="EJECUTAR BÚSQUEDA AVANZADA", 
            font=("Segoe UI", 11, "bold"), 
            text_color=theme["text_secondary"]
        ).pack(side="left")

        # Grid de Inputs
        grid_filtros = ctk.CTkFrame(filtros_card, fg_color="transparent")
        grid_filtros.pack(fill="x", padx=20, pady=15)
        grid_filtros.grid_columnconfigure(0, weight=3) # Fechas
        grid_filtros.grid_columnconfigure(1, weight=4) # Nombre (un poco más ancho)
        grid_filtros.grid_columnconfigure(2, weight=3) # Duración
        grid_filtros.grid_columnconfigure(3, weight=2) # Botones
        
        # Helper para crear campos (modificado para grid si fuera necesario, pero usaremos frames manuales)
        pass 

        # Col 1: Fechas
        col_fechas = ctk.CTkFrame(grid_filtros, fg_color="transparent")
        col_fechas.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        ctk.CTkLabel(col_fechas, text="Rango de Fechas", font=("Segoe UI", 12, "bold"), text_color=theme["text_primary"]).pack(anchor="w", pady=(0, 5))
        
        row_dates = ctk.CTkFrame(col_fechas, fg_color="transparent")
        row_dates.pack(fill="x")
        
        if DateEntry:
            # Estilo personalizado para DateEntry (FLAT DESIGN MEJORADO)
            from tkinter import ttk
            style = ttk.Style()
            if 'clam' in style.theme_names():
                style.theme_use('clam')
            
            # Configurar colores para que coincidan con CTkEntry
            style.configure('my.DateEntry', 
                fieldbackground='#F1F5F9', # Mismo que input_bg
                background=theme["accent"],      # Color del botón del calendario
                foreground='#334155',      # Color del texto (input_fg)
                arrowcolor='white',
                borderwidth=1,
                relief="flat"
            )
            
            # Hack para el borde del entry dentro de DateEntry
            style.map('my.DateEntry',
                fieldbackground=[('readonly', '#F1F5F9')],
                foreground=[('readonly', '#334155')],
                bordercolor=[('focus', theme["accent"]), ('!focus', '#E2E8F0')]
            )

            entry_fecha_ini = DateEntry(
                row_dates, 
                width=12, 
                background=theme["accent"],
                foreground='white',
                borderwidth=0, 
                date_pattern='yyyy-mm-dd',
                font=("Segoe UI", 11),
                style='my.DateEntry',
                selectbackground=theme["accent"],
                selectforeground='white'
            )
            # Agregar padding visual simulando altura de CTkEntry (35px)
            entry_fecha_ini.pack(side="left", padx=(0, 5), fill="y", ipady=4)
            entry_fecha_ini.delete(0, "end")
            
            ctk.CTkLabel(row_dates, text="➝", text_color=theme["text_secondary"], font=("Segoe UI", 14)).pack(side="left", padx=5)
            
            entry_fecha_fin = DateEntry(
                row_dates, 
                width=12, 
                background=theme["accent"],
                foreground='white', 
                borderwidth=0, 
                date_pattern='yyyy-mm-dd',
                font=("Segoe UI", 11),
                style='my.DateEntry',
                selectbackground=theme["accent"],
                selectforeground='white'
            )
            entry_fecha_fin.pack(side="left", padx=(5, 0), fill="y", ipady=4)
            entry_fecha_fin.delete(0, "end")
        else:
             # Fallback
            entry_fecha_ini = ctk.CTkEntry(row_dates, width=100, placeholder_text="YYYY-MM-DD", 
                                         fg_color=theme["input_bg"], text_color=theme["input_fg"], border_color=theme["border"], height=35)
            entry_fecha_ini.pack(side="left", fill="x", expand=True, padx=(0,5))
            
            ctk.CTkLabel(row_dates, text="➝", text_color=theme["text_secondary"]).pack(side="left")
            
            entry_fecha_fin = ctk.CTkEntry(row_dates, width=100, placeholder_text="YYYY-MM-DD", 
                                         fg_color=theme["input_bg"], text_color=theme["input_fg"], border_color=theme["border"], height=35)
            entry_fecha_fin.pack(side="left", fill="x", expand=True, padx=(5,0))

        # Col 2: Empleado con StringVar
        var_nombre = ctk.StringVar()
        f_emp = ctk.CTkFrame(grid_filtros, fg_color="transparent")
        f_emp.grid(row=0, column=1, padx=(0, 15), sticky="nsew")
        
        ctk.CTkLabel(f_emp, text="Nombre Empleado", font=("Segoe UI", 12, "bold"), text_color=theme["text_primary"]).pack(anchor="w", pady=(0, 5))
        
        entry_nombre = ctk.CTkEntry(
            f_emp, 
            width=200, 
            placeholder_text="Ej. Juan Pérez",
            fg_color=theme["input_bg"],
            text_color=theme["input_fg"],
            border_color=theme["border"],
            corner_radius=8,
            height=35,
            textvariable=var_nombre
        )
        entry_nombre.pack(fill="x")
        
        if DateEntry:
            # Bindings will be set after realizar_busqueda is defined
            pass

        # Col 3: Duración
        col_duracion = ctk.CTkFrame(grid_filtros, fg_color="transparent")
        col_duracion.grid(row=0, column=2, padx=(0, 15), sticky="nsew")
        
        ctk.CTkLabel(col_duracion, text="Duración (Horas:Min)", font=("Segoe UI", 12, "bold"), text_color=theme["text_primary"]).pack(anchor="w", pady=(0, 5))
        
        row_hours = ctk.CTkFrame(col_duracion, fg_color="transparent")
        row_hours.pack(fill="x")
        
        entry_min_horas = ctk.CTkEntry(row_hours, width=90, placeholder_text="Mín (e.g. 1h)", 
                                     fg_color=theme["input_bg"], text_color=theme["input_fg"], border_color=theme["border"], height=35)
        entry_min_horas.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(row_hours, text="-", text_color=theme["text_secondary"], font=("Segoe UI", 16)).pack(side="left", padx=5)
        
        entry_max_horas = ctk.CTkEntry(row_hours, width=90, placeholder_text="Máx (e.g. 8h)", 
                                     fg_color=theme["input_bg"], text_color=theme["input_fg"], border_color=theme["border"], height=35)
        entry_max_horas.pack(side="left", fill="x", expand=True)

        # Col 4: Botones Acción
        col_btns = ctk.CTkFrame(grid_filtros, fg_color="transparent")
        col_btns.grid(row=0, column=3, padx=(0, 0), sticky="nsew")
        
        # Contenedor botones alineado abajo
        btns_container = ctk.CTkFrame(col_btns, fg_color="transparent")
        btns_container.pack(side="bottom", fill="x", pady=0)
        
        btn_buscar = ctk.CTkButton(
            btns_container, 
            text="Buscar", 
            fg_color=theme["accent"],
            hover_color="#4338CA", # Indigo-700
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            height=35,
            corner_radius=8,
            width=90
        )
        btn_buscar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_limpiar = ctk.CTkButton(
            btns_container, 
            text="Limpiar", 
            fg_color="white", # Fondo blanco para contraste secundario
            border_width=1,
            border_color="#CBD5E1", # Slate-300
            text_color=theme["text_secondary"],
            hover_color="#F8FAFC",
            font=("Segoe UI", 12),
            height=35, 
            width=80,
            command=lambda: limpiar_filtros()
        )
        btn_limpiar.pack(side="left", fill="x", expand=True)

        # --- TABLA DE RESULTADOS ---
        # Contenedor tabla con aspecto limpio (Card)
        tabla_container = ctk.CTkFrame(
            main_content, 
            fg_color=theme["bg_panel"], 
            corner_radius=12,
            border_width=0
        )
        tabla_container.pack(fill="both", expand=True)

        # Header Tabla Fake
        t_header = ctk.CTkFrame(tabla_container, height=50, fg_color="transparent")
        t_header.pack(fill="x", padx=15, pady=10)
        
        # Totales
        self.lbl_resultados = ctk.CTkLabel(
            t_header, 
            text="Resultados de la búsqueda", 
            font=("Segoe UI", 14, "bold"), 
            text_color=theme["text_primary"]
        )
        self.lbl_resultados.pack(side="left", padx=5, pady=5)
        
        # Tabla real
        tabla = TreeViewWidget(
            tabla_container,
            columnas=["Empleado", "Inicio Turno", "Fin Turno", "Duración", "Estado"],
            altura=16, # Un poco más alta
            row_height=45 # Aún más filas respirables para modernidad
        )
        tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # --- PERSONALIZACIÓN DE TABLA (MODERN LOOK) ---
        style_tree = ttk.Style()
        # Header de tabla con más contraste y fuente limpia
        style_tree.configure("Treeview.Heading", 
            font=("Segoe UI Semibold", 11), 
            foreground="#64748B", 
            background="#F8FAFC",
            relief="flat"
        )
        
        # Ajustar anchos y alineaciones
        tabla.arbol.column("Empleado", width=250, anchor="w")     
        tabla.arbol.column("Inicio Turno", width=140, anchor="center")
        tabla.arbol.column("Fin Turno", width=140, anchor="center")
        tabla.arbol.column("Duración", width=100, anchor="center")
        tabla.arbol.column("Estado", width=120, anchor="center")
        
        # Tags de colores para estado (Badge Style text)
        tabla.arbol.tag_configure("activo", foreground="#059669", font=("Segoe UI", 10, "bold"))  # Emerald-600
        tabla.arbol.tag_configure("finalizado", foreground="#64748B") # Slate-500
        
        # --- LÓGICA DE FILTRADO (100% FRONTEND) ---
        self._datos_historial_base = []
        fecha_ini_activa = False
        fecha_fin_activa = False

        def _parse_horas(valor_texto):
            texto = valor_texto.strip().lower().replace(",", ".")
            if not texto:
                return None

            try:
                if ":" in texto:
                    partes = texto.split(":")
                    if len(partes) != 2:
                        return "INVALID"
                    horas = int(partes[0])
                    minutos = int(partes[1])
                    if horas < 0 or minutos < 0 or minutos >= 60:
                        return "INVALID"
                    return horas + (minutos / 60.0)

                texto_compacto = texto.replace(" ", "")
                if "h" in texto_compacto or "m" in texto_compacto:
                    horas = 0.0
                    minutos = 0.0

                    if "h" in texto_compacto:
                        parte_horas, resto = texto_compacto.split("h", 1)
                        horas = float(parte_horas) if parte_horas else 0.0
                    else:
                        resto = texto_compacto

                    if "m" in resto:
                        parte_min = resto.replace("m", "")
                        minutos = float(parte_min) if parte_min else 0.0
                    elif resto:
                        return "INVALID"

                    total = horas + (minutos / 60.0)
                    return total if total >= 0 else "INVALID"

                valor = float(texto)
                return valor if valor >= 0 else "INVALID"
            except ValueError:
                return "INVALID"

        def _parse_fecha_widget(widget, activa=False):
            texto = widget.get().strip()
            if DateEntry and hasattr(widget, "get_date") and not activa:
                return None
            if not texto:
                return None
            try:
                if DateEntry and hasattr(widget, "get_date"):
                    return widget.get_date()
                return datetime.strptime(texto, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return "INVALID"

        def _duracion_a_horas(duracion_texto):
            texto = duracion_texto.replace("(Actual)", "").strip()
            horas = 0
            minutos = 0
            for token in texto.split():
                if token.endswith("h"):
                    try:
                        horas = int(token[:-1])
                    except ValueError:
                        pass
                elif token.endswith("m"):
                    try:
                        minutos = int(token[:-1])
                    except ValueError:
                        pass
            return horas + (minutos / 60.0)

        def aplicar_filtros_locales(silent=True):
            fecha_ini = _parse_fecha_widget(entry_fecha_ini, fecha_ini_activa)
            fecha_fin = _parse_fecha_widget(entry_fecha_fin, fecha_fin_activa)

            if fecha_ini == "INVALID" or fecha_fin == "INVALID":
                if not silent:
                    DialogUtils.mostrar_error("Error de Formato", "Las fechas deben ser YYYY-MM-DD")
                    return
                # En modo silencioso no bloquear el resto de filtros
                fecha_ini = None if fecha_ini == "INVALID" else fecha_ini
                fecha_fin = None if fecha_fin == "INVALID" else fecha_fin

            if fecha_ini and fecha_fin and fecha_ini > fecha_fin:
                if not silent:
                    DialogUtils.mostrar_error("Fechas Inválidas", "La fecha inicial no puede ser mayor a la final.")
                return

            horas_min = _parse_horas(entry_min_horas.get())
            horas_max = _parse_horas(entry_max_horas.get())

            if horas_min == "INVALID" or horas_max == "INVALID":
                if not silent:
                    DialogUtils.mostrar_error("Error de Formato", "Usa duración válida: 1.5, 1:30, 1h 30m o 90m")
                    return
                # En modo silencioso, ignorar duración inválida para no congelar el filtro por nombre
                horas_min = None if horas_min == "INVALID" else horas_min
                horas_max = None if horas_max == "INVALID" else horas_max

            if horas_min is not None and horas_max is not None and horas_min > horas_max:
                if not silent:
                    DialogUtils.mostrar_error("Rango inválido", "La duración mínima no puede ser mayor a la máxima")
                return

            nombre_filtro = var_nombre.get().strip().lower()

            datos_filtrados = []
            for registro in self._datos_historial_base:
                nombre_emp = str(registro[1]).lower()
                inicio_turno = str(registro[2])
                fin_turno = str(registro[3])
                duracion_str = str(registro[4])

                if nombre_filtro and nombre_filtro not in nombre_emp:
                    continue

                try:
                    fecha_turno = datetime.strptime(inicio_turno, "%d/%m/%Y %H:%M").date()
                except ValueError:
                    continue

                if fecha_ini and fecha_turno < fecha_ini:
                    continue
                if fecha_fin and fecha_turno > fecha_fin:
                    continue

                duracion_horas = _duracion_a_horas(duracion_str)
                if horas_min is not None and duracion_horas < horas_min:
                    continue
                if horas_max is not None and duracion_horas > horas_max:
                    continue

                estado_texto = "EN CURSO" if fin_turno == "En curso" else "FINALIZADO"
                
                # Excluir ID (índice 0) para la vista
                valores_view = list(registro)[1:] 
                valores_view.append(estado_texto)
                
                # Guardamos ID original como dato oculto (por si acaso)
                datos_filtrados.append((tuple(valores_view), registro[0]))

            tabla.limpiar()
            for fila in datos_filtrados:
                # fila: (datos_fila, id_turno)
                datos_fila = fila[0]
                id_turno = fila[1]
                
                estado = datos_fila[-1]
                tag_extra = "activo" if estado == "EN CURSO" else "finalizado"
                
                # Agregar fila pasandole el ID oculto
                item_id = tabla.agregar_fila(datos_fila, id_datos=id_turno)
                
                # Preservar tags de alternancia de color (par/impar) y agregar el de estado
                tags_actuales = tabla.arbol.item(item_id, "tags")
                tabla.arbol.item(item_id, tags=tags_actuales + (tag_extra,))

            if datos_filtrados:
                self.lbl_resultados.configure(text=f"Resultados encontrados: {len(datos_filtrados)}")
            else:
                self.lbl_resultados.configure(text="No se encontraron registros")

        def cargar_datos_base():
            success, datos, msg = self.turnos_controller.obtener_historial_formateado()

            # El backend actual devuelve success=False cuando no hay turnos, lo tratamos como lista vacía.
            if success:
                self._datos_historial_base = datos if datos else []
            elif not datos:
                self._datos_historial_base = []
            else:
                DialogUtils.mostrar_error("Error al cargar", msg)
                self._datos_historial_base = []

            aplicar_filtros_locales(silent=True)

        def limpiar_filtros():
            nonlocal fecha_ini_activa, fecha_fin_activa
            if DateEntry:
                try:
                    entry_fecha_ini.delete(0, "end")
                    entry_fecha_fin.delete(0, "end")
                except Exception:
                    pass
            else:
                entry_fecha_ini.delete(0, "end")
                entry_fecha_fin.delete(0, "end")

            var_nombre.set("")
            entry_min_horas.delete(0, "end")
            entry_max_horas.delete(0, "end")
            fecha_ini_activa = False
            fecha_fin_activa = False
            self.lbl_resultados.configure(text="Mostrando todos los registros")
            aplicar_filtros_locales(silent=True)

        btn_buscar.configure(command=lambda: aplicar_filtros_locales(silent=False))

        var_nombre.trace_add("write", lambda *args: aplicar_filtros_locales(silent=True))
        entry_min_horas.bind("<KeyRelease>", lambda event: aplicar_filtros_locales(silent=True))
        entry_max_horas.bind("<KeyRelease>", lambda event: aplicar_filtros_locales(silent=True))

        if DateEntry:
            def _on_fecha_ini_selected(event):
                nonlocal fecha_ini_activa
                fecha_ini_activa = True
                aplicar_filtros_locales(silent=True)

            def _on_fecha_fin_selected(event):
                nonlocal fecha_fin_activa
                fecha_fin_activa = True
                aplicar_filtros_locales(silent=True)

            entry_fecha_ini.bind("<<DateEntrySelected>>", _on_fecha_ini_selected)
            entry_fecha_fin.bind("<<DateEntrySelected>>", _on_fecha_fin_selected)
        else:
            entry_fecha_ini.bind("<KeyRelease>", lambda event: aplicar_filtros_locales(silent=True))
            entry_fecha_fin.bind("<KeyRelease>", lambda event: aplicar_filtros_locales(silent=True))

        cargar_datos_base()


    def refrescar_tabla(self):
        """Refrescar tabla de empleados con paginación"""
        success, datos, msg = self.controller.obtener_todos_empleados_formateados()
        if success:
            self.todos_los_datos = datos
            self.datos_filtrados = datos[:] # Inicialmente es una copia completa
            
            # Limpiar búsqueda si existe (disparará el filtro, pero no importa)
            if hasattr(self, 'var_busqueda_principal'):
                 self.var_busqueda_principal.set("")

            # Calcular total páginas
            import math
            self.total_paginas = math.ceil(len(self.datos_filtrados) / self.registros_por_pagina)
            if self.total_paginas == 0: self.total_paginas = 1
            
            self.pagina_actual = 1
            self._mostrar_pagina_actual()
            
            self.empleado_seleccionado = None
            self._actualizar_panel()
        else:
            DialogUtils.mostrar_error("Error", msg)

    def _filtrar_empleados_principal(self):
        """Filtra la tabla principal en tiempo real (Frontend)"""
        if not hasattr(self, 'var_busqueda_principal'): return
        
        texto = self.var_busqueda_principal.get().lower().strip()
        
        if not texto:
            self.datos_filtrados = self.todos_los_datos[:]
        else:
            self.datos_filtrados = []
            for emp in self.todos_los_datos:
                # emp: (id, nombre, puesto, tel, email, salario, estado, ...)
                # Buscamos en Nombre, ID, Puesto
                nombre = str(emp[1]).lower()
                puesto = str(emp[2]).lower()
                emp_id = str(emp[0]).lower()
                
                if texto in nombre or texto in puesto or texto in emp_id:
                    self.datos_filtrados.append(emp)
        
        # Recalcular paginación
        import math
        self.total_paginas = math.ceil(len(self.datos_filtrados) / self.registros_por_pagina)
        if self.total_paginas == 0: self.total_paginas = 1
        
        self.pagina_actual = 1
        self._mostrar_pagina_actual()

    def _mostrar_pagina_actual(self):
        """Renderiza los datos de la página actual en la tabla"""
        # Limpiar
        self.tabla.limpiar()
        self._turnos_activos_ui.clear()
        
        if not self.datos_filtrados:
            self._actualizar_estado_paginacion()
            # Opcional: Mostrar mensaje de "no encontrados" en tabla vacía
            return
            
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        datos_slice = self.datos_filtrados[inicio:fin]
        
        for dato in datos_slice:
            # dato: (id, nombre, puesto, telefono, email, salario, estado, timestamp_turno)
            # La tupla puede tener 7 u 8 elementos
            
            timestamp_turno = None
            if len(dato) > 7:
                 timestamp_turno = dato[7]
            
            # Columnas visibles (Nombre...Estado)
            # Asegurarse que haya suficientes datos
            if len(dato) >= 7:
                datos_visibles = list(dato[1:7]) # Indices 1 a 6
                # Añadir columna Tiempo Turno
                datos_visibles.append("---")
                
                # Importante: Pasar dato completo como oculto
                # Nota: TreeViewWidget.agregar_fila devuelve el ID
                item_id = self.tabla.agregar_fila(tuple(datos_visibles), datos_ocultos=dato)
                
                if timestamp_turno:
                    self._turnos_activos_ui[item_id] = timestamp_turno
            
        self._actualizar_estado_paginacion()
        # Forzar un ciclo de actualización del cronómetro inmediato
        self._callback_cronometro()

    def _iniciar_cronometro(self):
        if self._cronometro_id is not None:
             self.after_cancel(self._cronometro_id)
        self._loop_cronometro()

    def _loop_cronometro(self):
        self._callback_cronometro()
        self._cronometro_id = self.after(1000, self._loop_cronometro)

    def _callback_cronometro(self):
        if not self._turnos_activos_ui:
            return
            
        now = datetime.now().timestamp()
        
        for item_id, start_ts in self._turnos_activos_ui.items():
            if not start_ts: continue
            
            diff = int(now - start_ts)
            if diff < 0: diff = 0
            
            h, r = divmod(diff, 3600)
            m, s = divmod(r, 60)
            
            tiempo_fmt = f"⏱ {h:02d}:{m:02d}:{s:02d} ({diff//60}m)"
            
            # Usar indice 6 o nombre "Tiempo Turno" segun definicion en TreeViewWidget
            # Treeview usa nombre de columna definido en 'columns'
            self.tabla.actualizar_celda(item_id, "Tiempo Turno", tiempo_fmt)

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
