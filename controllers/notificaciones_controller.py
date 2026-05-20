"""
Controlador para gestión de notificaciones
Maneja la lógica de negocio relacionada con notificaciones
"""
from database import get_notifications, clear_notifications

class NotificacionesController:
    """Controlador para gestionar notificaciones del sistema"""
    
    @staticmethod
    def obtener_notificaciones(limit=50):
        """
        Obtiene las notificaciones del sistema
        
        Args:
            limit: Número máximo de notificaciones a obtener (default: 50)
        
        Returns:
            list: Lista de notificaciones ordenadas por fecha (más recientes primero)
        """
        try:
            return get_notifications(limit)
        except Exception as e:
            print(f"Error obteniendo notificaciones: {e}")
            return []
    
    @staticmethod
    def limpiar_notificaciones():
        """
        Borra todas las notificaciones del sistema
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            clear_notifications()
            return {
                "success": True,
                "message": "Notificaciones eliminadas correctamente"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al limpiar notificaciones: {str(e)}"
            }
    
    @staticmethod
    def obtener_notificaciones_por_nivel(nivel, limit=50):
        """
        Obtiene notificaciones filtradas por nivel de severidad
        
        Args:
            nivel: Nivel de notificación ("crítico", "advertencia", "info")
            limit: Número máximo de notificaciones a obtener
        
        Returns:
            list: Lista de notificaciones del nivel especificado
        """
        try:
            todas = get_notifications(limit * 2)  # Obtener más para filtrar
            filtradas = [n for n in todas if n.get("nivel", "").lower() == nivel.lower()]
            return filtradas[:limit]
        except Exception as e:
            print(f"Error obteniendo notificaciones por nivel: {e}")
            return []
