import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import get_user

class AuthController:
    @staticmethod
    def login(username, password):
        """
        Verifica credenciales.
        Retorna: Un diccionario con datos del usuario (role, name) si es correcto.
        Retorna: None si falla.
        """
        return get_user(username, password)