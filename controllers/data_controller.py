import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import (
    get_sensor_data, get_resource_data, get_light_sensor, get_light_state,
    get_light_manual_state, set_light_state, set_light_manual_state,
    get_access_state, get_access_manual_state, set_access_manual_state,
    get_access_log, get_alert_config, set_alert_config,
    get_light_config, set_light_config, get_schedule,
    add_pulsometro_data, get_pulsometro_data, update_pulsometro_data
)

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
        light_data = get_light_sensor()
        return light_data.get("luminosity", 0)

    @staticmethod
    def obtener_estado_luz():
        # PRIORIZAR: Estado real del sistema (actualizado por auto Y manual)
        data_estado = get_light_state()
        if data_estado and data_estado.get("estado"):
            return _normalizar_estado(data_estado["estado"])
        
        # FALLBACK: Estado manual
        estado_manual = get_light_manual_state()
        if estado_manual:
            return _normalizar_estado(estado_manual)

        return "off"

    @staticmethod
    def guardar_estado_luz_manual(estado):
        estado_normalizado = _normalizar_estado(estado)
        try:
            # Guardar en manual
            set_light_manual_state(estado_normalizado)
            # También actualizar light_state para sincronización
            set_light_state(estado_normalizado.upper(), 100 if estado_normalizado == "on" else 0, "MANUAL")
            return True
        except:
            return False

    @staticmethod
    def guardar_estado_luz_automatico(estado, modo="AUTOMATICO"):
        """Guarda el estado de las luces cuando se controla automáticamente (umbral, horario, etc.)"""
        estado_normalizado = _normalizar_estado(estado)
        try:
            intensidad = 100 if estado_normalizado == "on" else 0
            set_light_state(estado_normalizado.upper(), intensidad, modo)
            return True
        except:
            return False

    # AMBIENTALES
    @staticmethod
    def obtener_datos_ambientales():
        return {
            "temp": get_sensor_data("temp", 24),
            "hum": get_sensor_data("hum", 24),
            "iaq": get_sensor_data("iaq", 24)
        }

    # EMERGENCIAS
    @staticmethod
    def obtener_datos_emergencia():
        return {
            "viento": get_sensor_data("viento", 24),
            "humo": get_sensor_data("humo", 24)
        }

    # ACCESOS
    @staticmethod
    def obtener_estado_barrera(barrera="norte"):
        """Devuelve el estado de una barrera específica (norte o sur) y distancia."""
        return get_access_state(barrera)

    @staticmethod
    def obtener_estado_barreras():
        """Devuelve el estado de todas las barreras."""
        return get_access_state()

    @staticmethod
    def obtener_historial_accesos():
        """Devuelve la lista de últimos accesos."""
        return get_access_log(20)

    @staticmethod
    def obtener_manual_barrera(barrera="norte"):
        """Lee la configuración manual de una barrera específica."""
        return get_access_manual_state(barrera)

    @staticmethod
    def obtener_manual_barreras():
        """Lee la configuración manual de todas las barreras."""
        return get_access_manual_state()

    @staticmethod
    def guardar_manual_barrera(barrera, modo_manual, abrir):
        """Guarda la orden del usuario para una barrera específica."""
        try:
            set_access_manual_state(barrera, modo_manual, abrir)
            return True
        except:
            return False

    # RECURSOS 
    @staticmethod
    def obtener_datos_agua():
        """Devuelve historial de consumo de agua."""
        return get_resource_data("water", 24)

    @staticmethod
    def obtener_datos_electricidad():
        """Devuelve historial de consumo eléctrico."""
        return get_resource_data("power", 24)

    # CONFIGURACIÓN ALERTAS
    @staticmethod
    def obtener_config_alertas():
        return get_alert_config()

    @staticmethod
    def guardar_config_alertas(config):
        try:
            for key, value in config.items():
                set_alert_config(key, value)
            return True
        except:
            return False
    
    # CONFIGURACIÓN DE ILUMINACIÓN
    @staticmethod
    def obtener_config_iluminacion():
        """Obtiene la configuración de iluminación (umbral, horario)"""
        try:
            umbral_config = get_light_config("umbral_luminosidad")
            umbral = 50  # Valor por defecto
            if umbral_config and "umbral_luminosidad" in umbral_config:
                try:
                    umbral = int(umbral_config["umbral_luminosidad"])
                except:
                    pass
            
            horario = get_schedule()
            
            return {
                "umbral": umbral,
                "horario": horario
            }
        except Exception as e:
            print(f"Error obteniendo configuración de iluminación: {e}")
            return {
                "umbral": 50,
                "horario": {"hora_inicio": 0, "minuto_inicio": 0, "hora_fin": 0, "minuto_fin": 0}
            }
    
    @staticmethod
    def obtener_umbral_luminosidad():
        """Obtiene el umbral de luminosidad configurado"""
        try:
            config = get_light_config("umbral_luminosidad")
            if config and "umbral_luminosidad" in config:
                return int(config["umbral_luminosidad"])
            return 50  # Valor por defecto
        except:
            return 50
    
    @staticmethod
    def guardar_umbral_luminosidad(umbral):
        """Guarda el umbral de luminosidad"""
        try:
            if not (0 <= umbral <= 100):
                return {"success": False, "message": "El umbral debe estar entre 0 y 100"}
            set_light_config("umbral_luminosidad", str(int(umbral)))
            return {"success": True, "message": "Umbral guardado correctamente"}
        except Exception as e:
            return {"success": False, "message": f"Error al guardar umbral: {str(e)}"}
    
    @staticmethod
    def obtener_horario():
        """Obtiene el horario de iluminación configurado"""
        try:
            return get_schedule()
        except Exception as e:
            print(f"Error obteniendo horario: {e}")
            return {"hora_inicio": 0, "minuto_inicio": 0, "hora_fin": 0, "minuto_fin": 0}
    
    @staticmethod
    def guardar_horario(hora_inicio, minuto_inicio, hora_fin, minuto_fin):
        """Guarda el horario de iluminación"""
        from controllers.scheduler import guardar_horario as guardar_horario_scheduler
        try:
            success = guardar_horario_scheduler(hora_inicio, minuto_inicio, hora_fin, minuto_fin)
            if success:
                return {"success": True, "message": "Horario guardado correctamente"}
            else:
                return {"success": False, "message": "Error al guardar horario. Verifica que los valores sean correctos."}
        except Exception as e:
            return {"success": False, "message": f"Error al guardar horario: {str(e)}"}

    @staticmethod
    def guardar_datos_pulsometro(frecuencia_cardiaca, presion_sistolica, presion_diastolica):
        return add_pulsometro_data(frecuencia_cardiaca, presion_sistolica, presion_diastolica)

    @staticmethod
    def obtener_datos_pulsometro(limit=20):
        return get_pulsometro_data(limit)

    @staticmethod
    def actualizar_datos_pulsometro(id_pulsometro, frecuencia_cardiaca, presion_sistolica, presion_diastolica):
        return update_pulsometro_data(
            id_pulsometro,
            frecuencia_cardiaca,
            presion_sistolica,
            presion_diastolica
        )

