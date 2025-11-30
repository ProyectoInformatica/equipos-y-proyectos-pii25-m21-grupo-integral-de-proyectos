import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "alert_config.json")

def _leer_json(nombre_archivo):
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r") as f: return json.load(f)
        except: pass
    # Retornar lista vacía si es historial, o dict vacío si es estado
    return [] if "env" in nombre_archivo or "resource" in nombre_archivo else {}

class DataController:
    
    # --- ILUMINACIÓN ---
    @staticmethod
    def obtener_luminosidad():
        return _leer_json("light.json").get("luminosity", 0)

    @staticmethod
    def obtener_estado_luz():
        return _leer_json("light.json").get("estado", "off")

    # --- AMBIENTAL ---
    @staticmethod
    def obtener_datos_ambientales():
        return {
            "temp": _leer_json("envtemperatura.json"),
            "hum": _leer_json("envhumedad.json"),
            "iaq": _leer_json("envcalidadaire.json")
        }

    # --- EMERGENCIAS ---
    @staticmethod
    def obtener_datos_emergencia():
        return {
            "viento": _leer_json("envviento.json"),
            "humo": _leer_json("envhumo.json")
        }

    # --- ACCESOS (SPRINT 3) ---
    @staticmethod
    def obtener_estado_barrera():
        """Devuelve el estado de la barrera y distancia."""
        data = _leer_json("access_state.json")
        # Valores por defecto si el archivo aun no existe
        if not data:
            return {"barrera_abierta": False, "mensaje": "Iniciando...", "distancia_detectada": 500}
        return data
    
    # ... (código anterior) ...

    # --- ACCESOS (SPRINT 3) ---
    @staticmethod
    def obtener_estado_barrera():
        """Devuelve el estado de la barrera y distancia."""
        data = _leer_json("access_state.json")
        if not data:
            return {"barrera_abierta": False, "mensaje": "Iniciando...", "distancia_detectada": 500}
        return data

    @staticmethod
    def obtener_historial_accesos():
        """Devuelve la lista de últimos accesos."""
        return _leer_json("access_log.json")

    # --- RECURSOS (SPRINT 3) ---
    @staticmethod
    def obtener_datos_agua():
        """Devuelve historial de consumo de agua."""
        return _leer_json("resource_water.json")

    # --- CONFIGURACIÓN ---
    @staticmethod
    def obtener_config_alertas():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return json.load(f)
            except: pass
        return {"temp_max": 35, "hum_min": 30, "hum_max": 70, "iaq_max": 100}

    @staticmethod
    def guardar_config_alertas(config):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            return True
        except: return False