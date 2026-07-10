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

def _normalizar_estado(valor, default="off"):
    if isinstance(valor, bool):
        return "on" if valor else "off"
    if valor is None:
        return default
    val = str(valor).strip().lower()
    if val in ("on", "encendido", "true", "1", "si", "sí"):
        return "on"
    if val in ("off", "apagado", "false", "0", "no"):
        return "off"
    return default

class DataController:
    
    # ILUMINACIÓN
    @staticmethod
    def obtener_luminosidad():
        return _leer_json("light.json").get("luminosity", 0)

    @staticmethod
    def obtener_estado_luz():
        # PRIORIZAR: Estado real del sistema (actualizado por auto Y manual)
        data_estado = _leer_json("light_state.json")
        if isinstance(data_estado, dict):
            estado = data_estado.get("estado") or data_estado.get("estado_luces")
            if estado is not None:
                return _normalizar_estado(estado)
        
        # SEGUNDO: Estado de light.json (actualizado por scheduler)
        data_light = _leer_json("light.json")
        if isinstance(data_light, dict):
            estado = data_light.get("estado")
            if estado is not None:
                return _normalizar_estado(estado)

        # FALLBACK: Estado manual
        data_manual = _leer_json("light_manual_state.json")
        if isinstance(data_manual, dict):
            estado = data_manual.get("state") if "state" in data_manual else data_manual.get("encender")
            if estado is not None:
                return _normalizar_estado(estado)

        return "off"

    @staticmethod
    def guardar_estado_luz_manual(estado):
        estado_normalizado = _normalizar_estado(estado)
        ruta_manual = os.path.join(DATA_DIR, "light_manual_state.json")
        ruta_estado = os.path.join(DATA_DIR, "light_state.json")
        
        # Guardar en manual
        data_manual = {"state": estado_normalizado}
        try:
            with open(ruta_manual, "w") as f:
                json.dump(data_manual, f, indent=4)
        except:
            return False
        
        # También actualizar light_state.json para sincronización
        try:
            data_estado = _leer_json("light_state.json")
            if not isinstance(data_estado, dict):
                data_estado = {}
            data_estado["estado"] = estado_normalizado.upper()  # Mantener formato ON/OFF
            data_estado["modo"] = "MANUAL"
            with open(ruta_estado, "w") as f:
                json.dump(data_estado, f, indent=4)
        except:
            pass  # No crítico si falla
        
        # Actualizar también light.json para mantener consistencia
        try:
            ruta_light = os.path.join(DATA_DIR, "light.json")
            data_light = _leer_json("light.json")
            if isinstance(data_light, dict):
                data_light["estado"] = estado_normalizado
                with open(ruta_light, "w") as f:
                    json.dump(data_light, f, indent=4)
        except:
            pass  # No crítico si falla
        
        return True

    @staticmethod
    def guardar_estado_luz_automatico(estado, modo="AUTOMATICO"):
        """Guarda el estado de las luces cuando se controla automáticamente (umbral, horario, etc.)"""
        estado_normalizado = _normalizar_estado(estado)
        ruta_estado = os.path.join(DATA_DIR, "light_state.json")
        
        try:
            data_estado = _leer_json("light_state.json")
            if not isinstance(data_estado, dict):
                data_estado = {}
            data_estado["estado"] = estado_normalizado.upper()  # Mantener formato ON/OFF
            data_estado["modo"] = modo
            with open(ruta_estado, "w") as f:
                json.dump(data_estado, f, indent=4)
            return True
        except:
            return False

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
    def obtener_estado_barrera(barrera="norte"):
        """Devuelve el estado de una barrera específica (norte o sur) y distancia."""
        data = _leer_json("access_state.json")
        if not data or not isinstance(data, dict):
            return {"barrera_abierta": False, "mensaje": "Iniciando...", "distancia_detectada": 500}
        
        # Si el formato es antiguo (sin norte/sur), devolver compatibilidad
        if "barrera_abierta" in data:
            return data
        
        # Formato nuevo con múltiples barreras
        estado_barrera = data.get(barrera, {})
        if not estado_barrera:
            return {"barrera_abierta": False, "mensaje": "BARRERA CERRADA", "distancia_detectada": 500}
        return estado_barrera

    @staticmethod
    def obtener_estado_barreras():
        """Devuelve el estado de todas las barreras."""
        data = _leer_json("access_state.json")
        if not data or not isinstance(data, dict):
            return {
                "norte": {"barrera_abierta": False, "mensaje": "BARRERA CERRADA", "distancia_detectada": 500},
                "sur": {"barrera_abierta": False, "mensaje": "BARRERA CERRADA", "distancia_detectada": 500}
            }
        
        # Si el formato es antiguo, convertirlo
        if "barrera_abierta" in data:
            return {
                "norte": data,
                "sur": {"barrera_abierta": False, "mensaje": "BARRERA CERRADA", "distancia_detectada": 500}
            }
        
        return data

    @staticmethod
    def obtener_historial_accesos():
        """Devuelve la lista de últimos accesos."""
        return _leer_json("access_log.json")

    @staticmethod
    def obtener_manual_barrera(barrera="norte"):
        """Lee la configuración manual de una barrera específica."""
        ruta = os.path.join(DATA_DIR, "access_manual_state.json")
        if os.path.exists(ruta):
            try:
                with open(ruta, "r") as f: 
                    data = json.load(f)
                    # Si el formato es antiguo (sin norte/sur), devolver compatibilidad
                    if "modo_manual" in data:
                        return data
                    # Formato nuevo con múltiples barreras
                    return data.get(barrera, {"modo_manual": False, "abrir": False})
            except: pass
        return {"modo_manual": False, "abrir": False}

    @staticmethod
    def obtener_manual_barreras():
        """Lee la configuración manual de todas las barreras."""
        ruta = os.path.join(DATA_DIR, "access_manual_state.json")
        if os.path.exists(ruta):
            try:
                with open(ruta, "r") as f: 
                    data = json.load(f)
                    # Si el formato es antiguo, convertirlo
                    if "modo_manual" in data:
                        return {
                            "norte": data,
                            "sur": {"modo_manual": False, "abrir": False}
                        }
                    return data
            except: pass
        return {
            "norte": {"modo_manual": False, "abrir": False},
            "sur": {"modo_manual": False, "abrir": False}
        }

    @staticmethod
    def guardar_manual_barrera(barrera, modo_manual, abrir):
        """Guarda la orden del usuario para una barrera específica."""
        ruta = os.path.join(DATA_DIR, "access_manual_state.json")
        try:
            # Leer datos existentes
            if os.path.exists(ruta):
                with open(ruta, "r") as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Si el formato es antiguo, convertirlo
            if "modo_manual" in data:
                data = {
                    "norte": data,
                    "sur": {"modo_manual": False, "abrir": False}
                }
            
            # Actualizar la barrera específica
            if barrera not in data:
                data[barrera] = {"modo_manual": False, "abrir": False}
            
            data[barrera]["modo_manual"] = modo_manual
            data[barrera]["abrir"] = abrir
            
            # Guardar
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