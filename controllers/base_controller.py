"""
Base para todos los controladores
Proporciona métodos comunes para preparar respuestas para la GUI
"""

class BaseController:
    """Clase base para controladores"""
    
    def __init__(self, model):
        self.model = model
    
    def _preparar_respuesta(self, resultado_modelo):
        """
        Convertir respuesta de modelo en formato (success, data, mensaje)
        Entrada: (success, data, mensaje) del modelo
        """
        if isinstance(resultado_modelo, tuple) and len(resultado_modelo) == 3:
            return resultado_modelo
        
        # Si no es tupla, probablemente error
        return False, None, "Error en operación"
    
    def _formatear_lista(self, objetos, formato_str=None):
        """Formatear lista de objetos para mostrar en UI"""
        if not objetos:
            return []
        
        if formato_str:
            return [formato_str(obj) for obj in objetos]
        return [str(obj) for obj in objetos]
