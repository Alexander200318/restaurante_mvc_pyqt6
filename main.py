"""
Sistema de Gestión de Restaurante
Entry Point
"""
import customtkinter as ctk
from database.db_manager import db_manager
from views.main_window import MainWindow

def main():
    """Punto de entrada principal"""
    
    try:
        # Inicializar base de datos
        print("✓ Inicializando base de datos...")
        db_manager.create_tables()
        print("✓ Base de datos lista")
        
        # Cargar datos de prueba
        print("✓ Cargando datos de prueba...")
        try:
            from seed_data import cargar_datos_prueba
            cargar_datos_prueba()
        except Exception as e:
            print(f"ℹ️  Datos de prueba ya existen o error: {e}")
        
        # Crear aplicación
        print("✓ Iniciando interfaz...")
        app = ctk.CTk()
        
        # Crear ventana principal
        main_window = MainWindow(app)
        
        # Ejecutar
        print("✓ Aplicación en ejecución...")
        main_window.run()
    
    except KeyboardInterrupt:
        print("\n✓ Aplicación cerrada por el usuario")

if __name__ == "__main__":
    main()
