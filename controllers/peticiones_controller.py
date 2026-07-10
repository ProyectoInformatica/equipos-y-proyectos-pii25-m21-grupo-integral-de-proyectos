"""
Controlador para gestión de peticiones de clientes
Maneja la lógica de negocio relacionada con peticiones
"""
from database import (
    create_client_request, get_client_requests,
    get_all_client_requests, update_request_status
)

class PeticionesController:
    """Controlador para gestionar peticiones de clientes"""
    
    @staticmethod
    def crear_peticion(usuario_id, titulo, descripcion):
        """
        Valida y crea una nueva petición de cliente
        
        Args:
            usuario_id: ID del usuario que crea la petición
            titulo: Título de la petición
            descripcion: Descripción de la petición
        
        Returns:
            dict: {"success": bool, "message": str, "request_id": int (opcional)}
        """
        # Validaciones
        if not titulo or not titulo.strip():
            return {"success": False, "message": "El título es requerido"}
        
        if not descripcion or not descripcion.strip():
            return {"success": False, "message": "La descripción es requerida"}
        
        if len(descripcion.strip()) < 10:
            return {"success": False, "message": "La descripción debe tener al menos 10 caracteres"}
        
        if len(titulo.strip()) > 100:
            return {"success": False, "message": "El título no puede exceder 100 caracteres"}
        
        if len(descripcion.strip()) > 1000:
            return {"success": False, "message": "La descripción no puede exceder 1000 caracteres"}
        
        # Crear petición
        try:
            request_id = create_client_request(
                usuario_id=usuario_id,
                titulo=titulo.strip(),
                descripcion=descripcion.strip()
            )
            return {
                "success": True,
                "message": "Petición creada correctamente",
                "request_id": request_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear petición: {str(e)}"
            }
    
    @staticmethod
    def obtener_peticiones_cliente(usuario_id):
        """
        Obtiene las peticiones de un cliente específico
        
        Args:
            usuario_id: ID del cliente
        
        Returns:
            list: Lista de peticiones del cliente
        """
        try:
            return get_client_requests(usuario_id)
        except Exception as e:
            print(f"Error obteniendo peticiones del cliente {usuario_id}: {e}")
            return []
    
    @staticmethod
    def obtener_todas_peticiones():
        """
        Obtiene todas las peticiones (para admin/tecnico)
        
        Returns:
            list: Lista de todas las peticiones
        """
        try:
            return get_all_client_requests()
        except Exception as e:
            print(f"Error obteniendo todas las peticiones: {e}")
            return []
    
    @staticmethod
    def actualizar_estado(request_id, nuevo_estado):
        """
        Actualiza el estado de una petición
        
        Args:
            request_id: ID de la petición
            nuevo_estado: Nuevo estado ("Pendiente", "En proceso", "Resuelta")
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        estados_validos = ["Pendiente", "En proceso", "Resuelta"]
        
        if nuevo_estado not in estados_validos:
            return {
                "success": False,
                "message": f"Estado inválido: {nuevo_estado}. Debe ser uno de: {', '.join(estados_validos)}"
            }
        
        try:
            success = update_request_status(request_id, nuevo_estado)
            if success:
                return {
                    "success": True,
                    "message": "Estado actualizado correctamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se pudo actualizar el estado. La petición puede no existir."
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al actualizar estado: {str(e)}"
            }
