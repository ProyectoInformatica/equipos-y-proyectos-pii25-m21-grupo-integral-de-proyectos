import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "alert_config.json")

# Función auxiliar definida fuera de la clase
def _leer_json(nombre_archivo):
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r") as f: return json.load(f)
        except: pass
    # Retornar lista vacía si es historial (contiene 'env' o 'resource'), o dict vacío si es estado
    return [] if "env" in nombre_archivo or "resource" in nombre_archivo else {}

class DataController:
    
    # ILUMINACIÓN
    @staticmethod
    def obtener_luminosidad():
        return _leer_json("light.json").get("luminosity", 0)

    @staticmethod
    def obtener_estado_luz():
        return _leer_json("light.json").get("estado", "off")

    # AMBIENTALES
    @staticmethod
    def obtener_datos_ambientales():
        return {
            "temp": _leer_json("envtemperatura.json"),
            "hum": _leer_json("envhumedad.json"),
            "iaq": _leer_json("envcalidadaire.json")
        }

    # EMERGENCIAS
    @staticmethod
    def obtener_datos_emergencia():
        return {
            "viento": _leer_json("envviento.json"),
            "humo": _leer_json("envhumo.json")
        }

    # ACCESOS
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

    @staticmethod
    def obtener_manual_barrera():
        """Lee la configuración manual de la barrera."""
        ruta = os.path.join(DATA_DIR, "access_manual_state.json")
        if os.path.exists(ruta):
            try:
                with open(ruta, "r") as f: return json.load(f)
            except: pass
        return {"modo_manual": False, "abrir": False}

    @staticmethod
    def guardar_manual_barrera(modo_manual, abrir):
        """Guarda la orden del usuario."""
        ruta = os.path.join(DATA_DIR, "access_manual_state.json")
        data = {"modo_manual": modo_manual, "abrir": abrir}
        try:
            with open(ruta, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except: return False

    # RECURSOS 
    @staticmethod
    def obtener_datos_agua():
        """Devuelve historial de consumo de agua."""
        return _leer_json("resource_water.json")

    @staticmethod
    def obtener_datos_electricidad():
        """Devuelve historial de consumo eléctrico."""
        return _leer_json("resource_power.json")

    # CONFIGURACIÓN ALERTAS
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