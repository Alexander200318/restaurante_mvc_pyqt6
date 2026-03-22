"""
Página: Gestión de Pedidos - Diseño Moderno
"""
import customtkinter as ctk
from controllers.pedidos_controller import PedidosController
from views.components.dialog_utils import DialogUtils
from views.components.pedido_card import PedidoCard
import config

class PedidosPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#F1F5F9", **kwargs) # Fondo Slate-100 general
        
        self.controller_pedidos = PedidosController()
        # self.controller_clientes = ClientesController() # No usado en esta vista simplificada
        self.filtro_actual = None # None = Todos
        self.pedidos = []
        
        self._crear_ui()
        self.refrescar_datos()
    
    def _crear_ui(self):
        """Layout principal moderno"""
        
        # --- HEADER PRINCIPAL ---
        # Fondo blanco limpio con sombra inferior simulada
        header_bg = ctk.CTkFrame(self, fg_color=config.COLORS["primary"], corner_radius=0, height=80)
        header_bg.pack(fill="x", padx=0, pady=0)
        
        # Contenido Header
        header_content = ctk.CTkFrame(header_bg, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=40)
        
        # Título y Subtítulo
        titles = ctk.CTkFrame(header_content, fg_color="transparent")
        titles.pack(side="left", pady=20)
        
        ctk.CTkLabel(
            titles,
            text="Tablero de Comandas",
            font=("Segoe UI Display", 24, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            titles,
            text="Control de flujo de cocina y servicio",
            font=("Segoe UI", 14),
            text_color="#FEF3C7"
        ).pack(anchor="w")

        # Botón Refrescar (Derecha Header)
        btn_refresh = ctk.CTkButton(
            header_content,
            text="🔄  Refrescar",
            command=self.refrescar_datos,
            fg_color="#F8FAFC",
            text_color="#475569",
            hover_color="#E2E8F0",
            border_width=1,
            border_color="#E2E8F0",
            corner_radius=8,
            height=36,
            font=("Segoe UI", 13, "bold")
        )
        btn_refresh.pack(side="right", pady=20)

        # --- BARRA DE FILTROS (PILLS STYLE) ---
        filter_bar = ctk.CTkFrame(self, fg_color="#F1F5F9", height=60, corner_radius=0)
        filter_bar.pack(fill="x", padx=40, pady=(20, 10))
        
        self.filter_container = ctk.CTkFrame(filter_bar, fg_color="#E2E8F0", corner_radius=100, height=45) 
        self.filter_container.pack(side="left", fill="y")
        
        filtros = [
            ("Todos", None),
            ("Pendientes", config.PedidoEstado.PENDIENTE),
            ("En Proceso", config.PedidoEstado.PREPARANDO), # Renombrado para UX
            ("Listos", config.PedidoEstado.LISTO),
            ("Entregados", config.PedidoEstado.ENTREGADO)   # Renombrado para UX
        ]
        
        self.filtro_buttons = {}
        
        for i, (text, estado) in enumerate(filtros):
            key = str(estado) if estado else "None"
            
            # Botón estilo Segmented Control
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
        # Scrollable area transparente
        self.scroll_area = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            label_text=""
        )
        self.scroll_area.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Grid layout config
        self.scroll_area.grid_columnconfigure(0, weight=1)
        self.scroll_area.grid_columnconfigure(1, weight=1)
        self.scroll_area.grid_columnconfigure(2, weight=1)
        self.scroll_area.grid_columnconfigure(3, weight=1) # 4 Columnas
        
    def cambiar_filtro(self, nuevo_estado):
        self.filtro_actual = nuevo_estado
        self._actualizar_estilos_filtros()
        self.renderizar_tarjetas()
        
    def _actualizar_estilos_filtros(self):
        key_actual = str(self.filtro_actual) if self.filtro_actual else "None"
        
        for key, btn in self.filtro_buttons.items():
            if key == key_actual:
                btn.configure(
                    fg_color="white", 
                    text_color=config.COLORS["primary"], # Highlight con color de marca
                    border_width=0,
                    # Simular elevación (no posible, solo contraste)
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#64748B",
                )

    def refrescar_datos(self):
        # Lógica persistente
        success, pedidos, msg = self.controller_pedidos.model.obtener_todos_pedidos() 
        
        if success:
            self.pedidos = pedidos
            self._actualizar_contadores()
            self.cambiar_filtro(self.filtro_actual) 
        else:
            DialogUtils.mostrar_error("Error", f"Error de carga: {msg}")

    def _actualizar_contadores(self):
        conteo = {
            "None": 0, 
            str(config.PedidoEstado.PENDIENTE): 0,
            str(config.PedidoEstado.PREPARANDO): 0,
            str(config.PedidoEstado.LISTO): 0,
            str(config.PedidoEstado.ENTREGADO): 0
        }
        
        conteo["None"] = len(self.pedidos)
        for p in self.pedidos:
            try:
                clave = str(p.estado)
                if clave in conteo: conteo[clave] += 1
            except: pass 
        
        labels = {
            "None": "Todos",
            str(config.PedidoEstado.PENDIENTE): "Pendientes",
            str(config.PedidoEstado.PREPARANDO): "En Proceso", 
            str(config.PedidoEstado.LISTO): "Listos",
            str(config.PedidoEstado.ENTREGADO): "Entregados"
        }
        
        for key, btn in self.filtro_buttons.items():
            base = labels.get(key, "Filtro")
            count = conteo.get(key, 0)
            btn.configure(text=f"{base} ({count})")

    def renderizar_tarjetas(self):
        for widget in self.scroll_area.winfo_children(): widget.destroy()
            
        display_pedidos = []
        if self.filtro_actual is None:
            # Ordenar: Todos menos entregados primero
            activos = [p for p in self.pedidos if p.estado != config.PedidoEstado.ENTREGADO]
            inactivos = [p for p in self.pedidos if p.estado == config.PedidoEstado.ENTREGADO]
            display_pedidos = activos + inactivos
        else:
            display_pedidos = [p for p in self.pedidos if p.estado == self.filtro_actual]
            
        if not display_pedidos:
            self._mostrar_empty_state()
            return

        columnas = 4
        for i, pedido in enumerate(display_pedidos):
            card = PedidoCard(
                self.scroll_area,
                pedido=pedido,
                on_status_change=self._cambiar_estado_pedido
            )
            row = i // columnas
            col = i % columnas
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def _mostrar_empty_state(self):
        frame = ctk.CTkFrame(self.scroll_area, fg_color="transparent")
        frame.grid(row=0, column=0, columnspan=4, pady=80)
        
        ctk.CTkLabel(frame, text="✅", font=("Segoe UI", 64)).pack(pady=(0, 10))
        ctk.CTkLabel(
            frame, 
            text="Todo limpio por aquí", 
            font=("Segoe UI", 18, "bold"), 
            text_color="#94A3B8"
        ).pack()
        ctk.CTkLabel(
            frame, 
            text="No hay pedidos en esta categoría", 
            font=("Segoe UI", 14), 
            text_color="#CBD5E1"
        ).pack()

    def _cambiar_estado_pedido(self, pedido_id, nuevo_estado):
        estado_str = nuevo_estado.value if hasattr(nuevo_estado, 'value') else str(nuevo_estado)
        success, pedido, msg = self.controller_pedidos.cambiar_estado_pedido(pedido_id, estado_str)
        if success:
            self.refrescar_datos()
        else:
            DialogUtils.mostrar_error("Error", msg)
