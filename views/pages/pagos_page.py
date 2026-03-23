"""
Página: Gestión de Pagos - Diseño Moderno
"""
import customtkinter as ctk
import json
import config
from controllers.pagos_controller import PagosController
from controllers.clientes_controller import ClientesController
from views.components.dialog_utils import DialogUtils
from views.components.pago_card import PagoCard

class PagosPage(ctk.CTkFrame):
    """Módulo de Pagos"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#F1F5F9", **kwargs)
        
        self.controller = PagosController()
        self.clientes_controller = ClientesController()
        self.pagos = []
        self.filtro_actual = None # None = Todos
        self.filtro_buttons = {}
        
        # Estado actual
        self.pago_seleccionado = None
        self.cliente_seleccionado_historial = None # Para la vista de detalle en Historial
        
        self._crear_ui()
        self.refrescar_datos()

    # === VALIDACIONES ===
    def _validar_cedula(self, cedula):
        if not cedula: return False, "La cédula es requerida"
        if not cedula.isdigit() or len(cedula) != 10: return False, "La cédula debe tener 10 dígitos"
        provincia = int(cedula[:2])
        if provincia < 1 or provincia > 24: return False, "Provincia inválida (01-24)"
        if int(cedula[2]) >= 6: return False, "Tercer dígito inválido (< 6)"
        suma = 0
        for i in range(9):
            num = int(cedula[i])
            if i % 2 == 0:
                num *= 2
                if num > 9: num -= 9
            suma += num
        digito_verificador = (10 - (suma % 10)) % 10
        if digito_verificador != int(cedula[9]): return False, "Dígito verificador inválido"
        return True, ""

    def _validar_nombre(self, nombre):
        if not nombre: return False, "El nombre es requerido"
        if not all(c.isalpha() or c.isspace() for c in nombre): return False, "Solo letras y espacios permitidos"
        return True, ""

    def _validar_apellido(self, apellido):
        if not apellido: return False, "El apellido es requerido"
        if not all(c.isalpha() or c.isspace() for c in apellido): return False, "Solo letras y espacios permitidos"
        return True, ""

    def _validar_telefono(self, telefono):
        if not telefono: return False, "El teléfono es necesario"
        if len(telefono) != 10 or not telefono.isdigit(): return False, "Debe tener 10 dígitos numéricos"
        return True, ""

    def _validar_correo(self, correo):
        import re
        if not correo: return False, "El correo es necesario"
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, correo): return False, "Formato inválido (ej: usuario@mail.com)"
        return True, ""

    def _validar_direccion(self, direccion):
        if not direccion: return False, "La dirección es necesaria"
        return True, ""
    
    def _crear_ui(self):
        """Layout principal moderno"""
        
        # --- HEADER PRINCIPAL ---
        header_bg = ctk.CTkFrame(self, fg_color=config.COLORS["primary"], corner_radius=0, height=80)
        header_bg.pack(fill="x")
        
        header_content = ctk.CTkFrame(header_bg, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=40)
        
        # Título
        titles = ctk.CTkFrame(header_content, fg_color="transparent")
        titles.pack(side="left", pady=20)
        
        ctk.CTkLabel(
            titles,
            text="Control de Caja",
            font=("Segoe UI Display", 24, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            titles,
            text="Gestión de cobros y facturación",
            font=("Segoe UI", 14),
            text_color="#FEF3C7"
        ).pack(anchor="w")

        # Botón Refrescar
        btn_refresh = ctk.CTkButton(
            header_content,
            text="🔄  Refrescar",
            command=self.refrescar_datos,
            fg_color="#F8FAFC",
            text_color="#475569",
            hover_color="#E2E8F0",
            height=36,
            font=("Segoe UI", 13, "bold")
        )
        btn_refresh.pack(side="right", pady=20)

        # --- BARRA DE FILTROS ---
        filter_bar = ctk.CTkFrame(self, fg_color="#F1F5F9", height=60, corner_radius=0)
        filter_bar.pack(fill="x", padx=40, pady=(20, 10))
        
        self.filter_container = ctk.CTkFrame(filter_bar, fg_color="#E2E8F0", corner_radius=100, height=45) 
        self.filter_container.pack(side="left", fill="y")
        
        # --- BUSCADOR (Derecha - Solo visible en HISTORIAL) ---
        self.search_frame_historial = ctk.CTkFrame(filter_bar, fg_color="white", corner_radius=20, height=36)
        
        ctk.CTkLabel(self.search_frame_historial, text="🔍 Cliente:", text_color="#94A3B8").pack(side="left", padx=(12, 5))
        
        self.entry_busqueda = ctk.CTkEntry(
            self.search_frame_historial, 
            placeholder_text="Buscar Cédula/Nombre...", 
            border_width=0, 
            fg_color="transparent",
            width=220,
            font=("Segoe UI", 13),
            text_color="#334155"
        )
        self.entry_busqueda.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.entry_busqueda.bind("<KeyRelease>", self._filtrar_por_texto)
        
        filtros = [
            ("Todos", None),
            ("Pendientes", config.PagoEstado.PENDIENTE),
            ("Parciales", config.PagoEstado.PARCIAL),
            ("Completados", config.PagoEstado.PAGADO),
            ("Historial", "HISTORIAL")
        ]
        
        for text, estado in filtros:
            key = str(estado) if estado else "None"
            btn = ctk.CTkButton(
                self.filter_container,
                text=text,
                fg_color="transparent",
                text_color="#64748B",
                hover_color="white",
                corner_radius=100,
                height=35,
                width=110,
                font=("Segoe UI", 12, "bold"),
                command=lambda e=estado: self.cambiar_filtro(e)
            )
            btn.pack(side="left", padx=4, pady=4)
            self.filtro_buttons[key] = btn

        # --- AREA DE TARJETAS (GRID) ---
        self.scroll_area = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            label_text=""
        )
        self.scroll_area.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Grid layout (4 columnas)
        self.scroll_area.grid_columnconfigure(0, weight=1)
        self.scroll_area.grid_columnconfigure(1, weight=1)
        self.scroll_area.grid_columnconfigure(2, weight=1)
        self.scroll_area.grid_columnconfigure(3, weight=1)

    def cambiar_filtro(self, nuevo_estado):
        # 1. Resetear selección de Historial al cambiar TAB
        self.cliente_seleccionado_historial = None
        
        self.filtro_actual = nuevo_estado
        self._actualizar_estilos_filtros()
        
        # 2. Control Visibilidad Buscador
        if self.filtro_actual == "HISTORIAL":
            self.search_frame_historial.pack(side="right", padx=5, pady=5, fill="y")
            self.entry_busqueda.delete(0, 'end')
            self.entry_busqueda.focus()
        else:
            self.search_frame_historial.pack_forget()

        self.renderizar_tarjetas()

    def _filtrar_por_texto(self, event=None):
        # Solo relevante en Historial
        if self.filtro_actual == "HISTORIAL":
            self.renderizar_tarjetas()
        
    def _actualizar_estilos_filtros(self):
        key_actual = str(self.filtro_actual) if self.filtro_actual else "None"
        for key, btn in self.filtro_buttons.items():
            if key == key_actual:
                btn.configure(
                    fg_color="white",
                    text_color=config.COLORS["primary"],
                    border_width=2,
                    border_color=config.COLORS["primary"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#64748B",
                    border_width=0
                )

    def refrescar_datos(self):
        # Obtener objetos Pago directamente
        success, pagos, msg = self.controller.model.obtener_todos_pagos()
        
        if success:
            self.pagos = pagos
            self._actualizar_contadores()
            self.cambiar_filtro(self.filtro_actual)
        else:
            DialogUtils.mostrar_error("Error", f"Error de carga: {msg}")

    def _actualizar_contadores(self):
        labels = {
            "None": "Todos",
            str(config.PagoEstado.PENDIENTE): "Pendientes",
            str(config.PagoEstado.PARCIAL): "Parciales",
            str(config.PagoEstado.PAGADO): "Completados",
            "HISTORIAL": "Historial"
        }
        
        # Actualizamos solo el texto base, sin contadores visuales
        for key, btn in self.filtro_buttons.items():
            texto_base = labels.get(key, "Filtro")
            # Forzamos texto limpio sin (N)
            btn.configure(text=texto_base)

    def renderizar_tarjetas(self):
        for widget in self.scroll_area.winfo_children(): widget.destroy()
        
        # === CASO: HISTORIAL POR CLIENTE ===
        if self.filtro_actual == "HISTORIAL":
            self._render_vista_historial()
            return

        # === CASO: FILTROS NORMALES (Pendiente, Pagado, etc) ===
        display_pagos = []
        if self.filtro_actual is None:
            # Ordenar: Pendientes primero
            activos = [p for p in self.pagos if p.estado != config.PagoEstado.PAGADO]
            inactivos = [p for p in self.pagos if p.estado == config.PagoEstado.PAGADO]
            display_pagos = activos + inactivos
        else:
            display_pagos = [p for p in self.pagos if p.estado == self.filtro_actual]
            
        if not display_pagos:
            self._mostrar_empty_state()
            return
            
        columnas = 4
        for i, pago in enumerate(display_pagos):
            card = PagoCard(self.scroll_area, pago=pago, on_action=self._on_card_action)
            row = i // columnas
            col = i % columnas
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def _render_vista_historial(self):
        """Renderiza la vista de navegación de Historial de Clientes"""
        
        # 1. Si hay cliente seleccionado = Ver sus facturas
        if self.cliente_seleccionado_historial:
            # Header Cliente + Botón Regresar
            header = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
            header.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))
            
            # --- Aquí es donde se define el botón de volver ---
            btn_volver = ctk.CTkButton(
                header, text="⬅ Volver a Lista", 
                fg_color="transparent", border_width=1, border_color="#CBD5E1",
                text_color="#475569", width=120, height=32,
                command=lambda: self._seleccionar_cliente_historial(None)  # Esta función debe existir
            )
            btn_volver.pack(side="left")
            
            # El resto del header...
            nm = f"{self.cliente_seleccionado_historial.nombre} {self.cliente_seleccionado_historial.apellido}"
            ctk.CTkLabel(header, text=f"Historial de: {nm}", font=("Segoe UI", 16, "bold"), text_color="#1E293B").pack(side="left", padx=20)

            # Filtrar pagos de este cliente específico
            cid = self.cliente_seleccionado_historial.id
            pagos_cliente = [p for p in self.pagos if p.pedido.cliente and p.pedido.cliente.id == cid]
            
            # Ordenar por fecha (recientes primero)
            pagos_cliente.sort(key=lambda p: p.id, reverse=True)
            
            if not pagos_cliente:
                ctk.CTkLabel(self.scroll_area, text="No hay facturas registradas.", text_color="gray").grid(row=1, column=0, columnspan=4, pady=20)
                return

            columnas = 4
            for i, pago in enumerate(pagos_cliente):
                card = PagoCard(self.scroll_area, pago=pago, on_action=self._on_card_action)
                row = (i // columnas) + 1 # +1 por el header (que ocupa row 0)
                col = i % columnas
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            # Forzamos la actualización del layout del scroll
            self.scroll_area.update_idletasks()
            return

        # 2. Si NO hay seleccionado = Lista de Clientes (Agrupados)
        # Buscar texto
        texto_busqueda = ""
        if hasattr(self, 'entry_busqueda') and self.entry_busqueda:
             texto_busqueda = self.entry_busqueda.get().strip().lower()
        
        # Agrupar pagos por cliente (solo procesar si hay texto de búsqueda o mostrar todos)
        # Vamos a mostrar solo si hay búsqueda, o todos si no hay muchos.
        
        clientes_map = {} # cliente_id -> {id, obj, count, total}
        
        for p in self.pagos:
            if not p.pedido.cliente: continue # Ignorar anónimos
            
            cli = p.pedido.cliente
            # Filtrado previo simple
            full_name = f"{cli.nombre} {cli.apellido}".lower()
            cedula = str(cli.cedula)
            
            if texto_busqueda and (texto_busqueda not in full_name and texto_busqueda not in cedula):
                # Si hay busqueda y no coincide, saltar
                continue

            if cli.id not in clientes_map:
                clientes_map[cli.id] = {
                    "id": cli.id,
                    "obj": cli,
                    "nombre": f"{cli.nombre} {cli.apellido}",
                    "cedula": cli.cedula,
                    "count": 0
                }
            
            clientes_map[cli.id]["count"] += 1
        
        # Convertir a lista
        lista_clientes = list(clientes_map.values())
        
        if not lista_clientes:
            msg = "Escribe para buscar un cliente..." if not texto_busqueda else "No se encontraron clientes."
            ctk.CTkLabel(self.scroll_area, text=msg, font=("Segoe UI", 16), text_color="#94A3B8").grid(row=0, column=0, columnspan=4, pady=50)
            return

        # Renderizar Tarjetas de Clientes (Estilo Contacto Moderno)
        col_c = 3
        
        # Configurar columnas del grid para que se expandan
        for c in range(col_c):
             self.scroll_area.grid_columnconfigure(c, weight=1)
        
        for i, data in enumerate(lista_clientes):
            cli = data["obj"]
            
            # --- CARD CONTAINER ---
            # Usamos un color de borde suave inicialmente
            card = ctk.CTkFrame(
                self.scroll_area, 
                fg_color="white", 
                corner_radius=12, 
                border_width=2, 
                border_color="#E2E8F0"
            )
            card.grid(row=i//col_c, column=i%col_c, padx=10, pady=10, sticky="nsew")
            
            # --- CONTENIDO ---
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=15, pady=15, fill="both", expand=True)
            
            # 1. Avatar / Icono Circular
            avatar_bg = ctk.CTkFrame(inner, fg_color="#F1F5F9", width=50, height=50, corner_radius=25)
            avatar_bg.pack(side="left", padx=(0, 15))
            # Forzamos tamaño del avatar
            avatar_bg.pack_propagate(False)
            
            ctk.CTkLabel(avatar_bg, text="👤", font=("Segoe UI", 20)).place(relx=0.5, rely=0.5, anchor="center")
            
            # 2. Info Texto
            info_box = ctk.CTkFrame(inner, fg_color="transparent")
            info_box.pack(side="left", fill="x", expand=True)
            
            # Nombre truncado si es muy largo
            nm_str = data["nombre"]
            if len(nm_str) > 25: nm_str = nm_str[:22] + "..."
                
            ctk.CTkLabel(info_box, text=nm_str, font=("Segoe UI", 14, "bold"), text_color="#1E293B").pack(anchor="w")
            ctk.CTkLabel(info_box, text=f"CI: {data['cedula']}", font=("Segoe UI", 12), text_color="#64748B").pack(anchor="w")
            
            # 3. Chevron / Flecha
            ctk.CTkLabel(inner, text="❯", font=("Arial", 16, "bold"), text_color="#CBD5E1").pack(side="right")

            # 4. Footer Stats
            stats = ctk.CTkFrame(card, fg_color="#F8FAFC", height=32, corner_radius=0)
            stats.pack(fill="x", side="bottom")
            
            # Linea superior del footer simulada con un frame pixel (opcional) o confiamos en el contraste
            
            ctk.CTkLabel(stats, text=f"📄 {data['count']} Facturas registradas", font=("Segoe UI", 11, "bold"), text_color="#475569").pack(side="left", padx=15)
            
            # --- HOVER EFFECT & EVENTS ---
            
            def on_enter(e, c=card, a=avatar_bg):
                # Brillo en los costados (Borde Primario) + Fondo sutilmente diferente
                c.configure(border_color=config.COLORS["primary"]) 
                a.configure(fg_color="#E0F2FE") # Azulito claro en el avatar
                
            def on_leave(e, c=card, a=avatar_bg):
                c.configure(border_color="#E2E8F0")
                a.configure(fg_color="#F1F5F9")
            
            def on_click(e, c=cli):
                self._seleccionar_cliente_historial(c)

            # Bindings recursivos para asegurar que funcione al pasar por encima de cualquier elemento
            widgets_to_bind = [card, inner, avatar_bg, info_box, stats] + inner.winfo_children() + info_box.winfo_children() + stats.winfo_children() + avatar_bg.winfo_children()
            
            for w in widgets_to_bind:
                try:
                    w.bind("<Enter>", lambda e, c=card, a=avatar_bg: on_enter(e, c, a), add="+")
                    w.bind("<Leave>", lambda e, c=card, a=avatar_bg: on_leave(e, c, a), add="+")
                    w.bind("<Button-1>", on_click, add="+")
                except: pass

    def _seleccionar_cliente_historial(self, cliente):
        self.cliente_seleccionado_historial = cliente
        self.renderizar_tarjetas() 
        
    def _mostrar_empty_state(self):
        frame = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
        frame.grid(row=0, column=0, columnspan=4, pady=80)
        
        ctk.CTkLabel(frame, text="✅", font=("Segoe UI", 64)).pack(pady=(0, 10))
        ctk.CTkLabel(frame, text="No hay pagos aquí", font=("Segoe UI", 18, "bold"), text_color="#94A3B8").pack()

    def _on_card_action(self, pago_incompleto):
        # Recargar el pago completo desde la base de datos para tener todas las relaciones (detalles, etc)
        success, pago, msg = self.controller.model.obtener_pago(pago_incompleto.id)
        
        if not success or not pago:
            DialogUtils.mostrar_error("Error", "No se pudo cargar la información del pago.")
            return

        self.pago_seleccionado = pago
        
        if pago.estado == config.PagoEstado.PAGADO:
            self._mostrar_ticket(pago.id)
        else:
            self._abrir_dialogo_pago(pago)

    def _abrir_dialogo_pago(self, pago, personas_iniciales=2):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Registrar Pago")
        
        # Dimensiones - Formato Ancho y Alto (Landscape Plus)
        w, h = 1000, 750
        
        # Centrar ventana (Ajustado más arriba a petición del usuario)
        try:
            main_window = self.winfo_toplevel()
            # Ajustar X/Y para evitar que se salga de la pantalla
            x = max(0, int(main_window.winfo_x() + (main_window.winfo_width() // 2) - (w // 2)))
            # Posicionamos Y 50px abajo del top de la ventana principal para que salga más arriba
            y = max(0, int(main_window.winfo_y() + 50))
            
            dialogo.geometry(f"{w}x{h}+{x}+{y}")
        except:
            dialogo.geometry(f"{w}x{h}")

        dialogo.configure(fg_color="white")
        dialogo.transient(self.winfo_toplevel())
        dialogo.grab_set()
        dialogo.lift()
        dialogo.focus_force()

        COLOR_ACCENT = config.COLORS["primary"]
        COLOR_ACCENT_HOVER = config.COLORS["accent"] # O usa un color custom si prefieres

        # Main Layout (Grid 2 Columnas)
        main_container = ctk.CTkFrame(dialogo, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        main_container.columnconfigure(0, weight=1) # Panel Izquierdo (Pago)
        main_container.columnconfigure(1, weight=1) # Panel Derecho (Facturación)
        main_container.rowconfigure(0, weight=1)

        # === PANEL IZQUIERDO: Detalles del Cobro ===
        left_panel = ctk.CTkScrollableFrame(main_container, fg_color="transparent") # Scrollable para evitar clipping
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(left_panel, text="Detalles del Cobro", font=("Segoe UI", 16, "bold"), text_color="#1E293B").pack(anchor="w", pady=(0, 15))

        # Info Pedido Base
        info_frame = ctk.CTkFrame(left_panel, fg_color="#F1F5F9")
        info_frame.pack(fill="x", pady=(0, 15))
        
        cliente_nm = pago.pedido.cliente.nombre if pago.pedido.cliente else "N/A"
        mesa_nm = f"Mesa {pago.pedido.mesa.numero}" if pago.pedido.mesa else "Sin mesa"
        ctk.CTkLabel(info_frame, text=f"{mesa_nm}  •  {cliente_nm}", text_color="#475569", font=("Segoe UI", 13)).pack(pady=10)

        # Totales
        total_pedido = pago.pedido.calcular_total()
        monto_previo = pago.monto if pago.estado == config.PagoEstado.PARCIAL else 0.0
        restante = max(0, total_pedido - monto_previo)

        frame_totales = ctk.CTkFrame(left_panel, fg_color="#F8FAFC", corner_radius=6)
        frame_totales.pack(fill="x", pady=(0, 15))
        
        def _row(p, l, v, color="#1E293B"):
            fr = ctk.CTkFrame(p, fg_color="transparent", height=24)
            fr.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(fr, text=l, font=("Segoe UI", 12), text_color="#64748B").pack(side="left")
            ctk.CTkLabel(fr, text=v, font=("Segoe UI", 12, "bold"), text_color=color).pack(side="right")

        _row(frame_totales, "Total Pedido:", f"${total_pedido:.2f}")
        if monto_previo > 0:
            _row(frame_totales, "Pagado:", f"${monto_previo:.2f}", color="#F59E0B")
            _row(frame_totales, "Pendiente:", f"${restante:.2f}", color="#EF4444")

        # Control Dividir Cuenta
        es_pago_parcial = monto_previo > 0
        
        # Recuperar estado de items parciales desde observaciones (JSON)
        items_pagados_qty = {}
        tiene_items_previos = False
        if pago.observaciones and pago.observaciones.strip().startswith("{"):
            try:
                dat = json.loads(pago.observaciones)
                if "items_paid" in dat:
                    items_pagados_qty = {int(k): v for k, v in dat["items_paid"].items()}
                    tiene_items_previos = True
            except Exception as e:
                print(f"Error parseando items pagados: {e}")
        
        # Determinar modo inicial inteligente
        modo_inicial = "Completo"
        if es_pago_parcial:
            if tiene_items_previos:
                modo_inicial = "Items"
            else:
                modo_inicial = "Completo" # Si no hay datos de items, asumir que fue pago manual parcial (raro sin modo dividir)
        
        tipo_pago_var = ctk.StringVar(value=modo_inicial)
        personas_var = ctk.IntVar(value=personas_iniciales)
        
        # Helper styles
        BTN_ACTIVE = {"fg_color": COLOR_ACCENT, "text_color": "white"}
        BTN_INACTIVE = {"fg_color": "transparent", "text_color": "#64748B"}

        # State de controles de división
        toggle_frame = ctk.CTkFrame(left_panel, fg_color="#E2E8F0", corner_radius=20, height=36)
        toggle_frame.pack(fill="x", pady=(0, 10))
        
        # Desactivar botones de cambio de modo si ya estamos en secuencia
        btn_full = ctk.CTkButton(toggle_frame, text="Pagar Todo", corner_radius=20, width=100, height=32, font=("Segoe UI", 12, "bold"), state="normal" if not tiene_items_previos else "disabled")
        btn_full.pack(side="left", padx=2, pady=2, expand=True, fill="both")
        
        # btn_split (Dividir) ELIMINADO

        item_state = "normal" 
        if es_pago_parcial and not tiene_items_previos: item_state = "disabled" # Si pago manual, no puede ir a items
        
        btn_items = ctk.CTkButton(toggle_frame, text="Por Plato", corner_radius=20, width=100, height=32, font=("Segoe UI", 12, "bold"), state=item_state)
        btn_items.pack(side="left", padx=2, pady=2, expand=True, fill="both")

        # --- CONTROLES DE DIVISIÓN ---
        split_controls = ctk.CTkFrame(left_panel, fg_color="transparent")
        
        if es_pago_parcial:
            ctk.CTkLabel(split_controls, text="Pago Secuencial Activo", font=("Segoe UI", 12, "bold"), text_color="#EF4444").pack(anchor="w")
        
        lbl_personas_t = ctk.CTkLabel(split_controls, text="Personas Pagando:", font=("Segoe UI", 12), text_color="black")
        lbl_personas_t.pack(anchor="w")

        counter_box = ctk.CTkFrame(split_controls, fg_color="#F1F5F9", corner_radius=8)
        counter_box.pack(fill="x", pady=5)

        lbl_count = ctk.CTkLabel(counter_box, text=str(personas_iniciales), font=("Segoe UI", 16, "bold"), width=40, text_color="black")
        
        def update_split(delta=0, val=None):
            curr = personas_var.get()
            if val: new_val = val
            else: 
                # Si hay pago parcial (estamos contando hacia abajo), permitimos llegar a 1
                min_val = 1 if es_pago_parcial else 2
                new_val = min(20, max(min_val, curr + delta)) # Max 20 personas
            
            personas_var.set(new_val)
            lbl_count.configure(text=str(new_val))
            
            # Solo actualizar monto si estamos en modo Dividir (no items)
            if tipo_pago_var.get() == "Dividido":
                monto_ind = restante / new_val
                lbl_math.configure(text=f"${restante:.2f} / {new_val} = ${monto_ind:.2f} c/u")
                entry_monto.configure(state="normal")
                entry_monto.delete(0, "end")
                entry_monto.insert(0, f"{monto_ind:.2f}")
                calcular_propina()

        btn_minus = ctk.CTkButton(counter_box, text="-", width=40, fg_color="transparent", text_color="#EF4444", font=("Arial", 18, "bold"), hover_color="#FECACA", command=lambda: update_split(-1))
        if not es_pago_parcial: btn_minus.pack(side="left")
        
        lbl_count.pack(side="left", expand=True)
        
        btn_plus = ctk.CTkButton(counter_box, text="+", width=40, fg_color="transparent", text_color="#10B981", font=("Arial", 18, "bold"), hover_color="#D1FAE5", command=lambda: update_split(1))
        if not es_pago_parcial: btn_plus.pack(side="right")
        
        lbl_math = ctk.CTkLabel(split_controls, text="", font=("Segoe UI", 11, "bold"), text_color=COLOR_ACCENT)
        lbl_math.pack(pady=(0, 10))

        # --- PANEL POR ÍTEMS ---
        items_controls = ctk.CTkFrame(left_panel, fg_color="transparent")
        
        # Header items con monto dinámico
        header_items = ctk.CTkFrame(items_controls, fg_color="transparent")
        header_items.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(header_items, text="Selecciona qué paga este cliente:", font=("Segoe UI", 12), text_color="#64748B").pack(side="left")
        
        # Etiqueta para el monto dinámico (arribita)
        lbl_monto_items = ctk.CTkLabel(header_items, text="$0.00", font=("Segoe UI", 16, "bold"), text_color=COLOR_ACCENT)
        lbl_monto_items.pack(side="right")

        # Propina (Movido arriba junto al monto)
        propina_box = ctk.CTkFrame(items_controls, fg_color="#F8FAFC", height=30) # Compacto
        propina_box.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(propina_box, text="Propina Sugerida (10%):", text_color="black", font=("Segoe UI", 11)).pack(side="left", padx=10)
        entry_propina = ctk.CTkEntry(propina_box, width=80, height=24, border_width=0, fg_color="transparent", text_color="black", font=("Segoe UI", 12, "bold"))
        entry_propina.pack(side="right", padx=10)
        
        items_scroll = ctk.CTkScrollableFrame(items_controls, height=200, fg_color="#FFFFFF", border_width=1, border_color="#E2E8F0") # Scroll interno también
        items_scroll.pack(fill="both", expand=True)
        
        items_vars = {} # id -> IntVar (ahora almacena cantidad a pagar)

        def update_items_total(d=None):
            total_sel = 0.0
            cnt = 0
            for det in pago.pedido.detalles:
                if det.id in items_vars:
                    qty = items_vars[det.id].get()
                    if qty > 0:
                        total_sel += qty * det.precio_unitario
                        cnt += 1
            
            # Actualizar etiqueta superior
            lbl_monto_items.configure(text=f"${total_sel:.2f}")

            entry_monto.configure(state="normal")
            entry_monto.delete(0, "end")
            entry_monto.insert(0, f"{total_sel:.2f}")
            entry_monto.configure(state="disabled") # Bloquear manual edit si es por items
            calcular_propina()

        def render_items_list():
            for w in items_scroll.winfo_children(): w.destroy()
            items_vars.clear()
            
            # Si solo queda 1 persona, autoseleccionar todo el resto
            is_last_person = personas_var.get() == 1
            
            hay_pendientes = False
            for det in pago.pedido.detalles:
                qty_total = det.cantidad
                # Use safe get becauseitems_pagados_qty might not be initialized as dict yet if user hasn't restarted dialog fully
                # But we changed initialization above already.
                qty_already_paid = items_pagados_qty.get(det.id, 0) if isinstance(items_pagados_qty, dict) else 0 
                qty_avail = qty_total - qty_already_paid
                
                if qty_avail <= 0:
                    continue
                
                hay_pendientes = True
                
                # Container Row
                row = ctk.CTkFrame(items_scroll, fg_color="transparent")
                row.pack(fill="x", pady=2, padx=5)
                
                # Left: Name
                txt_info = f"{det.plato.nombre} (${det.precio_unitario:.2f})"
                ctk.CTkLabel(row, text=txt_info, font=("Segoe UI", 12), text_color="#0F172A", anchor="w").pack(side="left", padx=5)

                # Right: Controls
                ctrl_frame = ctk.CTkFrame(row, fg_color="transparent")
                ctrl_frame.pack(side="right", padx=5)
                
                initial_val = 0
                var = ctk.IntVar(value=initial_val)
                items_vars[det.id] = var
                
                lbl_val = ctk.CTkLabel(ctrl_frame, text=f"{initial_val} / {qty_avail}", font=("Segoe UI", 12, "bold"), width=40)
                lbl_val.pack(side="left", padx=2)

                # Definir lógica de actualización segura capturando variables
                def update_qty(delta, v=var, l=lbl_val, max_q=qty_avail):
                    c = v.get()
                    n = max(0, min(max_q, c + delta))
                    v.set(n)
                    l.configure(text=f"{n} / {max_q}")
                    l.configure(text_color=COLOR_ACCENT if n > 0 else "black")
                    update_items_total()

                # Botones habilitados siempre
                state_btns = "normal"

                btn_m = ctk.CTkButton(ctrl_frame, text="-", width=25, height=25, fg_color="#E2E8F0", text_color="black", hover_color="#CBD5E1", 
                                    state=state_btns, command=lambda u=update_qty: u(-1))
                btn_m.pack(side="left", padx=2, before=lbl_val)
                
                btn_p = ctk.CTkButton(ctrl_frame, text="+", width=25, height=25, fg_color="#E2E8F0", text_color="black", hover_color="#CBD5E1", 
                                    state=state_btns, command=lambda u=update_qty: u(1))
                btn_p.pack(side="left", padx=2)
            
            if not hay_pendientes:
                ctk.CTkLabel(items_scroll, text="Todo asignado.", font=("Segoe UI", 12, "italic"), text_color="#94A3B8").pack(pady=20)

        # Inputs Totales
        inputs_box = ctk.CTkFrame(left_panel, fg_color="transparent")
        inputs_box.pack(fill="x", pady=15) # Mayor separación
        
        metodos = self.controller.obtener_metodos_disponibles()
        metodo_var = ctk.StringVar(value="") # Sin valor por defecto
        
        ctk.CTkLabel(inputs_box, text="Método de Pago", text_color="#64748B", font=("Segoe UI", 11)).pack(anchor="w", padx=2)
        ctk.CTkComboBox(inputs_box, values=metodos, variable=metodo_var, state="readonly", border_color=COLOR_ACCENT, button_color=COLOR_ACCENT, height=32).pack(fill="x", padx=2, pady=2)
        
        # Campo oculto para mantener lógica sin cambios
        entry_monto = ctk.CTkEntry(inputs_box)
        # entry_monto.pack() # No mostrar

        # Propina (Movida arriba)

        # === PANEL DERECHO: Facturación ===
        right_panel = ctk.CTkFrame(main_container, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E2E8F0")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        inner_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        inner_right.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(inner_right, text="Datos de Facturación", font=("Segoe UI", 14, "bold"), text_color="#1E293B").pack(anchor="w", pady=(0, 10))

        tipo_factura_var = ctk.StringVar(value="CF")
        cliente_id_var = ctk.StringVar(value="")

        frame_cf = ctk.CTkFrame(inner_right, fg_color="transparent")
        ctk.CTkLabel(frame_cf, text="Consumidor Final", font=("Segoe UI", 14, "bold"), text_color=COLOR_ACCENT).pack(pady=20)
        ctk.CTkLabel(frame_cf, text="9999999999", font=("Segoe UI", 12), text_color="#64748B").pack()

        frame_datos = ctk.CTkFrame(inner_right, fg_color="transparent")
        
        # Search
        search_row = ctk.CTkFrame(frame_datos, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 0)) # Reduced padding
        
        search_input_frame = ctk.CTkFrame(search_row, fg_color="transparent")
        search_input_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        entry_cedula = ctk.CTkEntry(search_input_frame, placeholder_text="Buscar Cédula/RUC", height=32)
        entry_cedula.pack(fill="x")
        
        lbl_error_cedula = ctk.CTkLabel(search_input_frame, text="", text_color="#EF4444", font=("Segoe UI", 10), height=14)
        lbl_error_cedula.pack(anchor="w")
        
        # Form
        form_grid = ctk.CTkFrame(frame_datos, fg_color="transparent")
        
        field_errors = {}

        # Helper creator
        def _mk_field(parent, key, label, placeholder, row, col, colspan=1):
            fr = ctk.CTkFrame(parent, fg_color="transparent")
            fr.grid(row=row, column=col, columnspan=colspan, padx=2, pady=4, sticky="ew")
            
            ctk.CTkLabel(fr, text=label, font=("Segoe UI", 11, "bold"), text_color="#475569").pack(anchor="w", pady=(0, 1))
            ent = ctk.CTkEntry(fr, placeholder_text=placeholder, height=32, font=("Segoe UI", 12))
            ent.pack(fill="x")
            
            err = ctk.CTkLabel(fr, text="", text_color="#EF4444", font=("Segoe UI", 10), height=14)
            err.pack(anchor="w")
            
            field_errors[key] = err
            return ent

        entry_nombre = _mk_field(form_grid, "nombre", "Nombre (*)", "Ej. Carlos", 0, 0)
        entry_apellido = _mk_field(form_grid, "apellido", "Apellido (*)", "Ej. Espinoza", 0, 1)
        entry_telefono = _mk_field(form_grid, "telefono", "Teléfono", "Ej. 0991234567", 1, 0)
        entry_direccion = _mk_field(form_grid, "direccion", "Dirección", "Ej. Av. Principal 123", 1, 1)
        entry_correo = _mk_field(form_grid, "correo", "Correo Electrónico", "Ej. carlos@email.com", 2, 0, colspan=2)
        
        form_grid.columnconfigure(0, weight=1)
        form_grid.columnconfigure(1, weight=1)

        lbl_status = ctk.CTkLabel(frame_datos, text="", font=("Segoe UI", 11))

        def reset_form():
            entry_nombre.delete(0, "end")
            entry_apellido.delete(0, "end")
            entry_telefono.delete(0, "end")
            entry_direccion.delete(0, "end")
            entry_correo.delete(0, "end")
            
            lbl_error_cedula.configure(text="")
            for err in field_errors.values():
                err.configure(text="")

        def buscar_cliente(event=None):
            ced = entry_cedula.get().strip()
            if not ced: return
            
            form_grid.pack_forget()
            lbl_status.pack_forget()
            cliente_id_var.set("")
            reset_form() # Clears errors

            # 1. Validar formato de cédula antes de buscar
            is_valid, msg_val = self._validar_cedula(ced)
            if not is_valid:
                lbl_error_cedula.configure(text=msg_val)
                # No mostramos el formulario si la cédula es inválida
                return
            
            success, obj, msg = self.clientes_controller.buscar_por_cedula(ced)
            
            if success and obj:
                cliente_id_var.set(str(obj.id))
                lbl_status.configure(text=f"✓ Cliente Encontrado: {obj.nombre}", text_color="#10B981")
                lbl_status.pack(pady=5)
            else:
                lbl_status.configure(text="Cliente Nuevo - Llenar Datos", text_color="#64748B")
                lbl_status.pack(pady=5)
                form_grid.pack(fill="x", pady=5)
                
                # Forzar refresco visual de los placeholders
                entry_nombre.configure(placeholder_text="Ej. Carlos")
                entry_apellido.configure(placeholder_text="Ej. Espinoza")
                entry_telefono.configure(placeholder_text="Ej. 0991234567")
                entry_direccion.configure(placeholder_text="Ej. Av. Principal 123")
                entry_correo.configure(placeholder_text="Ej. carlos@email.com")

                # No forzar foco para mantener placeholders visibles

        ctk.CTkButton(search_row, text="🔍", width=40, height=32, fg_color="#334155", command=buscar_cliente).pack(side="right", anchor="n", pady=2)
        entry_cedula.bind("<Return>", buscar_cliente)

        def toggle_factura(value=None):
            if tipo_factura_var.get() == "Consumidor Final":
                frame_datos.pack_forget()
                frame_cf.pack(fill="both", expand=True)
            elif tipo_factura_var.get() == "Con Datos":
                frame_cf.pack_forget()
                frame_datos.pack(fill="both", expand=True)
            else:
                frame_cf.pack_forget()
                frame_datos.pack_forget()

        tipo_factura_var.set("") # Default: Ninguno seleccionado
        
        seg_factura = ctk.CTkSegmentedButton(
            inner_right,
            values=["Consumidor Final", "Con Datos"],
            variable=tipo_factura_var,
            command=toggle_factura,
            selected_color=COLOR_ACCENT,
            selected_hover_color=COLOR_ACCENT_HOVER
        )
        seg_factura.pack(fill="x", pady=(0, 15))
        
        toggle_factura()

        # Update Logic
        def calcular_propina(event=None):
            try:
                m = float(entry_monto.get() or 0)
                entry_propina.delete(0, "end")
                entry_propina.insert(0, str(round(m * 0.10, 2)))
            except: pass
        entry_monto.bind("<KeyRelease>", calcular_propina)

        # Helper styles
        BTN_ACTIVE = {"fg_color": COLOR_ACCENT, "text_color": "white"}
        BTN_INACTIVE = {"fg_color": "transparent", "text_color": "#64748B"}

        def set_mode(m):
            tipo_pago_var.set(m)
            entry_monto.configure(state="normal")
            
            # Reset UI
            split_controls.pack_forget()
            items_controls.pack_forget()
            
            btn_full.configure(**BTN_INACTIVE)
            # btn_split.configure(**BTN_INACTIVE)
            btn_items.configure(**BTN_INACTIVE)
            
            if m == "Completo":
                btn_full.configure(**BTN_ACTIVE)
                entry_monto.delete(0, "end")
                entry_monto.insert(0, f"{restante:.2f}")
                entry_monto.configure(state="disabled") # Bloquear editing en completo
                
            elif m == "Dividido":
                # Removed
                pass
                
            elif m == "Items":
                btn_items.configure(**BTN_ACTIVE)
                # Mostrar contador de persona y lista de items
                split_controls.pack(after=toggle_frame, fill="x", pady=10)
                items_controls.pack(after=split_controls, fill="x", pady=10)
                render_items_list()
                update_items_total()
                
            calcular_propina()

        btn_full.configure(command=lambda: set_mode("Completo"))
        # btn_split.configure(command=lambda: set_mode("Dividido"))
        btn_items.configure(command=lambda: set_mode("Items"))
        set_mode(modo_inicial)

        # --- Confirm Logic ---
        def confirmar():
            nonlocal restante, monto_previo 
            pago_id = pago.id
            tipo = tipo_pago_var.get()
            monto_str = entry_monto.get()
            propina_str = entry_propina.get()
            
            # VALIDACIÓN: MÉTODO DE PAGO
            if not metodo_var.get() or metodo_var.get() not in metodos:
                DialogUtils.mostrar_error("Falta Información", "⚠️ Por favor, seleccione un Método de Pago para continuar.")
                return

            # 1. VALIDACIONES ESPECÍFICAS
            paid_items_delta = {} # items paying NOW {id: quantity}
            
            # Forzar actualización de vista si estamos en Items (para asegurar conteo actualizado)
            # No necesario si personas_var ya lo tiene
            current_personas = personas_var.get()
            
            if tipo == "Items":
                has_any = False
                for did, v in items_vars.items():
                    qty = v.get()
                    if qty > 0:
                        paid_items_delta[did] = qty
                        has_any = True
                
                if not has_any:
                     DialogUtils.mostrar_error("Error", "Selecciona al menos una cantidad")
                     return

            # 2. CLIENTE
            tipo_fac = tipo_factura_var.get()
            if not tipo_fac:
                DialogUtils.mostrar_error("Falta Información", "Por favor seleccione el tipo de facturación (Consumidor Final o Con Datos).")
                return

            final_cli_id = None
            if tipo_fac == "Consumidor Final":
                s, cf, m = self.clientes_controller.buscar_por_cedula("9999999999")
                if not s: 
                     self.clientes_controller.crear_cliente("9999999999", "Consumidor", "Final", "0999999999", "N/A", "cf@mail")
                     s, cf, m = self.clientes_controller.buscar_por_cedula("9999999999")
                if cf: final_cli_id = cf.id
            else:
                if cliente_id_var.get():
                    final_cli_id = int(cliente_id_var.get())
                else: 
                    # Crear nuevo con validaciones in-line
                    ced = entry_cedula.get().strip()
                    nom = entry_nombre.get().strip()
                    ape = entry_apellido.get().strip()
                    tel = entry_telefono.get().strip()
                    direc = entry_direccion.get().strip()
                    correo = entry_correo.get().strip()

                    # Limpiar errores previos
                    lbl_error_cedula.configure(text="")
                    for err in field_errors.values():
                        err.configure(text="")
                    
                    has_error = False

                    # Validaciones individuales
                    ok, msg = self._validar_cedula(ced)
                    if not ok: 
                        lbl_error_cedula.configure(text=msg)
                        has_error = True

                    ok, msg = self._validar_nombre(nom)
                    if not ok: 
                        field_errors["nombre"].configure(text=msg)
                        has_error = True
                    
                    ok, msg = self._validar_apellido(ape)
                    if not ok: 
                        field_errors["apellido"].configure(text=msg)
                        has_error = True

                    ok, msg = self._validar_telefono(tel)
                    if not ok: 
                        field_errors["telefono"].configure(text=msg)
                        has_error = True

                    ok, msg = self._validar_direccion(direc)
                    if not ok: 
                        field_errors["direccion"].configure(text=msg)
                        has_error = True

                    ok, msg = self._validar_correo(correo)
                    if not ok: 
                        field_errors["correo"].configure(text=msg)
                        has_error = True

                    if has_error:
                        return

                    # Si todo ok
                    s, new_c, m = self.clientes_controller.crear_cliente(ced, nom, ape, tel, direc, correo)
                    if new_c: final_cli_id = new_c.id
                    else:
                        DialogUtils.mostrar_error("Error al crear cliente", m)
                        return

            # Asignar cliente al pedido de forma PERSISTENTE (para que salga en el ticket)
            if final_cli_id:
                # 1. Actualizar DB
                # Usamos el controller para llamar al modelo
                ok_cli, _, msg_cli = self.controller.actualizar_cliente_pago(pago_id, final_cli_id)
                if not ok_cli:
                    DialogUtils.mostrar_error("Error", f"No se pudo asignar el cliente: {msg_cli}")
                    return
                # 2. Actualizar objeto local
                pago.pedido.cliente_id = final_cli_id

            try:
                val_m = float(monto_str)
                val_p = float(propina_str or 0)
            except: 
                return

            if val_m <= 0: return

            # 3. COMPROBAR ESTADO ACTUAL (Concurrency check simple)
            s_bd, p_bd, _ = self.controller.model.obtener_pago(pago_id)
            if not s_bd: return
            real_paid = p_bd.monto or 0.0
            
            # Calcular nuevo monto acumulado
            nuevo_total = real_paid + val_m
            total_pedido = pago.pedido.calcular_total()
            
            if nuevo_total > total_pedido + 0.10: # Tolerancia
                DialogUtils.mostrar_error("Error", f"El monto excede el total (${total_pedido:.2f})")
                return

            # VALIDAR ÚLTIMA PERSONA: Debe cubrir el total
            # Si personas_var es 1, esta es la última transacción de la secuencia
            if tipo == "Items" and current_personas == 1:
                # El nuevo total debe ser (casi) igual al total del pedido
                if nuevo_total < total_pedido - 0.01:
                    DialogUtils.mostrar_error("Error", "Última persona: Debe seleccionar TODOS los platos/productos restantes para completar el pago.")
                    return

            # 4. PREPARAR DATOS (Observaciones JSON para items)
            obs_json = None
            # Si estamos en modo Items, actualizamos el mapa de cantidades
            if tipo == "Items" and paid_items_delta:
                # Merge con lo que ya estaba
                for did, q in paid_items_delta.items():
                    items_pagados_qty[did] = items_pagados_qty.get(did, 0) + q
                
                # Serializar
                obs_data = {"items_paid": items_pagados_qty}
                obs_json = json.dumps(obs_data)

            # 5. ACTUALIZAR BASE DE DATOS
            # Si es pago completo en una, el estado cambiará a PAGADO automáticamente si monto >= total
            # Si es parcial, cambiará a PARCIAL
            
            success, p_updated, msg = self.controller.actualizar_pago(
                pago_id=pago_id, 
                monto=nuevo_total, 
                metodo=metodo_var.get(), 
                observaciones=obs_json
            )
            
            if success:
                # Verificar si se completó
                if nuevo_total >= total_pedido - 0.01:
                     self.controller.completar_pago(pago_id, val_p)
                     dialogo.destroy()
                     self._mostrar_ticket(pago_id)
                     self.refrescar_datos()
                else:
                     # PAGO PARCIAL EXITOSO: Refrescar UI sin cerrar si es posible, o cerrar y reabrir
                     DialogUtils.mostrar_exito("Cobro Parcial", f"Pago de ${val_m:.2f} registrado.")
                     
                     # Actualizar variables locales para el siguiente pago en la misma ventana?
                     # Es complejo mantener estado. Mejor cerrar y reabrir con datos frescos.
                     dialogo.destroy()
                     
                     # Reabrir el dialogo con el pago actualizado
                     # Necesitamos obtener el pago actualizado FULL first
                     s, p_full, _ = self.controller.model.obtener_pago(pago_id)
                     
                     # Calcular siguientes personas si aplica
                     next_personas = 2
                     curr = current_personas
                     next_personas = max(1, curr - 1)
                     
                     if s:
                         self._abrir_dialogo_pago(p_full, next_personas)
                     
                     self.refrescar_datos()
            else:
                 DialogUtils.mostrar_error("Error", msg)


        # Footer Button
        ctk.CTkButton(dialogo, text="COBRAR PAGO", command=confirmar,  fg_color=config.COLORS["success"], height=50, font=("Segoe UI", 15, "bold")).pack(fill="x", side="bottom", padx=20, pady=20)

    def _mostrar_ticket(self, pago_id):
        # Recargar desde BD para asegurar datos frescos del cliente asignado
        success, pago, msg = self.controller.model.obtener_pago(pago_id)
        
        if not success or not pago: return

        fecha = pago.fecha_pago.strftime("%d/%m/%Y %H:%M") if pago.fecha_pago else datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Obtener datos del cliente fresco
        cli_obj = pago.pedido.cliente
        cliente_str = "Consumidor Final"
        cedula_str = "9999999999"
        
        if cli_obj:
            cliente_str = f"{cli_obj.nombre} {cli_obj.apellido}"
            cedula_str = cli_obj.cedula
        
        mesa_str = f"Mesa {pago.pedido.mesa.numero}" if pago.pedido.mesa else "Sin Mesa"
        
        # --- LÓGICA DE PROMOCIÓN (25% en el más vendido, SOLO ENTRADA o PLATO FUERTE) ---
        descuento_promo = 0.0
        platos_promos = set()
        ranking = []
        try:
            if not hasattr(self, 'pedidos_controller'):
                from controllers.pedidos_controller import PedidosController
                self.pedidos_controller = PedidosController()
            succ_r, ranking, _ = self.pedidos_controller.obtener_platos_mas_vendidos(10)
            if succ_r and ranking:
                for p in ranking:
                    cat_str = str(p[3]).lower() if len(p) > 3 else ""
                    if "plato_fuerte" in cat_str or "entrada" in cat_str:
                        platos_promos.add(p[0])
                        break  # Solo el más vendido de esas categorías
        except Exception as e:
            print(f"Error calculando promo ticket: {e}")

        # Cálculo de detalle de platos y descuentos
        detalles = []
        subtotal_real = 0.0
        for detalle in pago.pedido.detalles:
            nombre = detalle.plato.nombre
            categoria = str(getattr(detalle.plato, 'categoria', '')).lower()
            cantidad = detalle.cantidad
            precio_unit = detalle.precio_unitario
            subtotal = detalle.subtotal
            desc = 0.0
            aplica_promo = nombre in platos_promos and ("plato_fuerte" in categoria or "entrada" in categoria)
            if aplica_promo:
                desc = subtotal * 0.25
                descuento_promo += desc
            detalles.append({
                'nombre': nombre,
                'categoria': categoria,
                'cantidad': cantidad,
                'precio_unit': precio_unit,
                'subtotal': subtotal,
                'descuento': desc
            })
            subtotal_real += subtotal

        propina = pago.cambio or 0.0
        total_final = subtotal_real - descuento_promo + propina
        metodo = pago.metodo.value if pago.metodo else "Efectivo"

        # Construcción del texto del Ticket
        texto = (
            "********************************\n"
            "      RESTAURANTE SABORES       \n"
            "      RUC: 0990001112001        \n"
            "      Matriz: Av. Principal     \n"
            "********************************\n\n"
            f"FECHA: {fecha}\n"
            f"COMPROBANTE #: {pago.id:06d}\n"
            f"MESA: {mesa_str}\n\n"
            "--------------------------------\n"
            "DATOS DEL CLIENTE:\n"
            f"Nombre: {cliente_str}\n"
            f"C.I./RUC: {cedula_str}\n"
            "--------------------------------\n\n"
            "DETALLE DE PAGO:\n"
        )
        texto += "Plato                Cant.  P.Unit   Subtotal   Desc.\n"
        texto += "-----------------------------------------------------\n"
        for d in detalles:
            texto += f"{d['nombre'][:18]:18} {d['cantidad']:>3}   ${d['precio_unit']:>6.2f}  ${d['subtotal']:>7.2f}"
            if d['descuento'] > 0:
                texto += f"  -${d['descuento']:.2f}"
            texto += "\n"
        texto += "-----------------------------------------------------\n"
        texto += f"Subtotal:           ${subtotal_real:.2f}\n"
        texto += f"Propina/Servicio:   ${propina:.2f}\n"
        if descuento_promo > 0:
            texto += f"DESC. PROMO 25%:    -${descuento_promo:.2f}\n"
        texto += (
            "--------------------------------\n"
            f"TOTAL A PAGAR:      ${total_final:.2f}\n"
            f"FORMA DE PAGO:      {metodo}\n\n"
            "********************************\n"
            "      ¡GRACIAS POR SU VISITA!   \n"
            "********************************"
        )
        self._popup_ticket(texto)

    def _popup_ticket(self, texto):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Comprobante de Pago")
        
        # Dimensiones equilibradas (ni muy ancho ni muy delgado)
        w, h = 480, 700
        
        # Centrar
        try:
            main_window = self.winfo_toplevel()
            # Asegurar coordenadas válidas
            mw_x = main_window.winfo_x() if main_window.winfo_x() > 0 else 0
            mw_y = main_window.winfo_y() if main_window.winfo_y() > 0 else 0
            
            x = mw_x + (main_window.winfo_width() // 2) - (w // 2)
            # Alineado arriba, casi a la altura de la ventana principal
            y = mw_y + 20 
            if y < 0: y = 0
            ventana.geometry(f"{w}x{h}+{x}+{y}")
        except:
            ventana.geometry(f"{w}x{h}")

        ventana.configure(fg_color="#F1F5F9") # Fondo dashboard (Slate-50)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()
        ventana.lift()
        ventana.focus_force()

        # Contenedor principal con padding
        container = ctk.CTkFrame(ventana, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        # === TICKET VISUAL (Efecto Papel) ===
        # Usamos un frame blanco puro con borde sutil para simular papel térmico
        paper_shadow = ctk.CTkFrame(container, fg_color="#E2E8F0", corner_radius=2)
        paper_shadow.pack(fill="both", expand=True, pady=(0, 20)) # Sombra simple
        
        ticket_paper = ctk.CTkFrame(paper_shadow, fg_color="white", corner_radius=0)
        ticket_paper.pack(fill="both", expand=True, padx=1, pady=1) # Borde de 1px simulado

        # Scroll para el contenido del ticket
        scroll_content = ctk.CTkScrollableFrame(ticket_paper, fg_color="white", corner_radius=0, width=300)
        scroll_content.pack(fill="both", expand=True, padx=5, pady=5)

        # Título dentro del papel
        ctk.CTkLabel(scroll_content, text="🧾 COMPROBANTE", font=("Courier New", 22, "bold"), text_color="#1E293B").pack(pady=(20, 10))

        # Texto del ticket (Monospaced para alineación)
        ctk.CTkLabel(scroll_content, text=texto, justify="left", font=("Courier New", 12), text_color="#334155").pack(anchor="center", padx=10, pady=(0, 20))

        # === FOOTER DE ACCIONES ===
        # Botones modernos
        actions_grid = ctk.CTkFrame(container, fg_color="transparent")
        actions_grid.pack(fill="x")
        actions_grid.columnconfigure(0, weight=2) # Imprimir (más grande)
        actions_grid.columnconfigure(1, weight=1) # Guardar
        actions_grid.columnconfigure(2, weight=1) # Cerrar

        # 1. IMPRIMIR (Principal)
        btn_print = ctk.CTkButton(
            actions_grid, 
            text="🖨️ Imprimir", 
            fg_color=config.COLORS["success"], # Verde éxito
            hover_color="#15803d",
            text_color="white",
            height=45,
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._imprimir_ticket(texto)
        )
        btn_print.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # 2. GUARDAR PDF (Secundario)
        btn_pdf = ctk.CTkButton(
            actions_grid, 
            text="💾 PDF", 
            fg_color="#334155", # Grid Slate
            hover_color="#1E293B",
            text_color="white",
            height=45,
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._guardar_ticket_pdf(texto)
        )
        btn_pdf.grid(row=0, column=1, padx=5, sticky="ew")
        
        # 3. CERRAR
        btn_cerrar = ctk.CTkButton(
            actions_grid, 
            text="Cerrar", 
            fg_color="#E2E8F0", 
            text_color="#475569", 
            hover_color="#CBD5E1",
            height=45,
            font=("Segoe UI", 13, "bold"),
            command=ventana.destroy
        )
        btn_cerrar.grid(row=0, column=2, padx=(5, 0), sticky="ew")

    def _generar_pdf_file(self, texto, ruta_archivo):
        """Método auxiliar para generar el PDF físico en una ruta"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError:
            DialogUtils.mostrar_error("Error de Dependencia", "Falta instalar 'reportlab' para generar PDFs.\nEjecute: pip install reportlab")
            return False

        try:
            c = canvas.Canvas(ruta_archivo, pagesize=letter)
            c.setFont("Courier", 11)
            y = 750
            for linea in texto.split("\n"):
                if y < 50: # Nueva página si se acaba el espacio
                    c.showPage()
                    c.setFont("Courier", 11)
                    y = 750
                c.drawString(50, y, linea)
                y -= 15
            c.save()
            return True
        except Exception as e:
            DialogUtils.mostrar_error("Error PDF", f"No se pudo generar el PDF: {str(e)}")
            return False

    def _imprimir_ticket(self, texto):
        """Genera PDF temporal y manda a imprimir"""
        import tempfile
        import os
        import sys
        
        # Crear archivo temporal
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd) # Cerrar el descriptor de archivo bajo nivel
        
        if self._generar_pdf_file(texto, path):
            try:
                if sys.platform == "win32":
                    try:
                        # Intentar mandar comando de impresión directo al SO
                        os.startfile(path, "print")
                    except OSError:
                        # Si falla (ej error 1155: Windows no sabe qué programa imprime PDFs),
                        # abrimos el archivo para que el usuario le de Ctrl+P
                        os.startfile(path)
                else:
                    # Intento genérico para Linux/Unix (lp o lpr)
                    import subprocess
                    subprocess.run(["lp", path], check=False)
            except Exception as e:
                DialogUtils.mostrar_error("Error de Impresión", f"No se pudo enviar a la impresora: {str(e)}")

    def _guardar_ticket_pdf(self, texto):
        from tkinter import filedialog
        ruta = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivo PDF", "*.pdf")])
        if not ruta: return

        if self._generar_pdf_file(texto, ruta):
            DialogUtils.mostrar_exito("PDF Generado", "El comprobante se guardó correctamente.")