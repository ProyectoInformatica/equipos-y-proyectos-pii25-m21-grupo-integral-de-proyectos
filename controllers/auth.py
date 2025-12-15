import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH_FILE = os.path.join(BASE_DIR, "data", "auth.json")

class AuthController:
    @staticmethod
    def _load_users():
        if not os.path.exists(AUTH_FILE):
            return []
        try:
            with open(AUTH_FILE, "r") as f:
                data = json.load(f)
                return data.get("users", [])
        except:
            return []

    @staticmethod
    def login(username, password):
        """
        Verifica credenciales.
        Retorna: Un diccionario con datos del usuario (role, name) si es correcto.
        Retorna: None si falla.
        """
        users = AuthController._load_users()
        for user in users:
            if user["username"] == username and user["password"] == password:
                return user # Retornamos todo el objeto usuario
        return None