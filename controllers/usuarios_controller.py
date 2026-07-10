"""
Controlador para gestión de usuarios
Maneja la lógica de negocio relacionada con usuarios
"""
from database import create_user, get_all_users

class UsuariosController:
    """Controlador para gestionar usuarios del sistema"""
    
    @staticmethod
    def registrar_usuario(username, password, role, name):
        """
        Valida y registra un nuevo usuario
        
        Args:
            username: Nombre de usuario (único)
            password: Contraseña
            role: Rol del usuario ("admin", "tecnico", "cliente")
            name: Nombre completo del usuario
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        # Validaciones
        if not username or not username.strip():
            return {"success": False, "message": "El nombre de usuario es requerido"}
        
        if not password or not password.strip():
            return {"success": False, "message": "La contraseña es requerida"}
        
        if len(password.strip()) < 4:
            return {"success": False, "message": "La contraseña debe tener al menos 4 caracteres"}
        
        if len(username.strip()) < 3:
            return {"success": False, "message": "El nombre de usuario debe tener al menos 3 caracteres"}
        
        if role not in ["admin", "tecnico", "cliente"]:
            return {
                "success": False,
                "message": f"Rol inválido: {role}. Debe ser 'admin', 'tecnico' o 'cliente'"
            }
        
        if not name or not name.strip():
            name = username.strip()  # Usar username como nombre si no se proporciona
        
        # Crear usuario
        success, message = create_user(
            username=username.strip(),
            password=password.strip(),
            role=role,
            name=name.strip()
        )
        
        return {"success": success, "message": message}
    
    @staticmethod
    def obtener_todos_usuarios():
        """
        Obtiene todos los usuarios del sistema
        
        Returns:
            list: Lista de todos los usuarios
        """
        try:
            return get_all_users()
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
            return []
    
    @staticmethod
    def validar_username(username):
        """
        Valida si un nombre de usuario es válido
        
        Args:
            username: Nombre de usuario a validar
        
        Returns:
            dict: {"valid": bool, "message": str}
        """
        if not username or not username.strip():
            return {"valid": False, "message": "El nombre de usuario no puede estar vacío"}
        
        if len(username.strip()) < 3:
            return {"valid": False, "message": "El nombre de usuario debe tener al menos 3 caracteres"}
        
        if len(username.strip()) > 50:
            return {"valid": False, "message": "El nombre de usuario no puede exceder 50 caracteres"}
        
        # Verificar caracteres válidos (solo letras, números y guiones bajos)
        if not username.replace("_", "").replace("-", "").isalnum():
            return {"valid": False, "message": "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos"}
        
        return {"valid": True, "message": "Nombre de usuario válido"}
