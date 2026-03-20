"""
Ventana Principal - Gestión de Navegación
"""
import customtkinter as ctk
from views.sidebar import Sidebar
from views.pages.dashboard import DashboardPage
from views.pages.clientes_page import ClientesPage
from views.pages.mesas_page import MesasPage
from views.pages.pedidos_page import PedidosPage
from views.pages.empleados_page import EmpleadosPage
from views.pages.ingredientes_page import IngredientesPage
from views.pages.menu_page import MenuPage
from views.pages.pagos_page import PagosPage
from views.pages.reportes_page import ReportesPage
import config

class MainWindow:
    """Ventana principal de la aplicación"""
    
    # Mapeo de módulos a páginas
    MODULOS = {
        'dashboard': DashboardPage,
        'clientes': ClientesPage,
        'mesas': MesasPage,
        'pedidos': PedidosPage,
        'empleados': EmpleadosPage,
        'ingredientes': IngredientesPage,
        'menu': MenuPage,
        'pagos': PagosPage,
        'reportes': ReportesPage
    }
    
    def __init__(self, app: ctk.CTk):
        self.app = app
        self.app.title("Restaurante - Sistema de Gestión")
        self.app.geometry("1400x900")
        
        # Config tema
        ctk.set_appearance_mode(config.APPEARANCE)
        ctk.set_default_color_theme("dark-blue")
        
        # Página actual (ANTES de crear Sidebar)
        self.pagina_actual = None
        self.modulo_actual = None
        
        # Frame principal
        self.frame_principal = ctk.CTkFrame(self.app)
        self.frame_principal.pack(fill="both", expand=True)
        
        # Frame de contenido (ANTES de Sidebar para que exista cuando llame el callback)
        self.frame_contenido = ctk.CTkFrame(self.frame_principal, fg_color=config.COLORS["light_bg"])
        self.frame_contenido.pack(side="right", fill="both", expand=True)
        
        # Sidebar (DESPUÉS de frame_contenido)
        self.sidebar = Sidebar(self.frame_principal, on_module_change=self._cambiar_modulo, width=250)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # Ir a primer módulo (dashboard)
        self._cambiar_modulo('dashboard')
    
    def _cambiar_modulo(self, modulo_id: str):
        """
        Cambiar página actual
        
        Args:
            modulo_id: ID del módulo (mesas, pedidos, etc)
        """
        # Limpiar contenido anterior
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()
        
        # Crear nueva página
        if modulo_id in self.MODULOS:
            clase_pagina = self.MODULOS[modulo_id]
            
            # Crear instancia con db_manager si es dashboard
            if modulo_id == 'dashboard':
                from database.db_manager import DatabaseManager
                db_manager = DatabaseManager()
                self.pagina_actual = clase_pagina(self.frame_contenido, db_manager)
                self.pagina_actual.crear()
            else:
                self.pagina_actual = clase_pagina(self.frame_contenido)
                self.pagina_actual.pack(fill="both", expand=True)
            
            self.modulo_actual = modulo_id
            
            # Refrescar datos si la página tiene método
            if hasattr(self.pagina_actual, 'refrescar_tabla'):
                self.pagina_actual.refrescar_tabla()
            elif hasattr(self.pagina_actual, 'refrescar_tablas'):
                self.pagina_actual.refrescar_tablas()
            elif hasattr(self.pagina_actual, 'generar_reportes'):
                self.pagina_actual.generar_reportes()
    
    def run(self):
        """Iniciar aplicación"""
        self.app.mainloop()
