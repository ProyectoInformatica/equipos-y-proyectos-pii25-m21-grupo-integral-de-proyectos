import json
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "alert_config.json")

def load_json(filepath):
    if not os.path.exists(filepath): return None
    try:
        with open(filepath, "r") as f: return json.load(f)
    except: return None

def load_last_value(filename):
    """Lee el último valor registrado de un sensor."""
    data = load_json(os.path.join(DATA_DIR, filename))
    if data and isinstance(data, list) and len(data) > 0:
        return data[-1].get("value", 0)
    return 0

def check_alarms():
    # 1. Cargar Configuración de Umbrales (definidos en la App)
    config = load_json(CONFIG_FILE)
    if not config:
        # Valores por defecto seguros si no hay config
        config = {
            "temp_max": 35, 
            "hum_max": 70,
            "iaq_max": 100,
            "humo_max": 25, 
            "viento_max": 50
        }

    # 2. Leer todos los sensores
    val_humo = load_last_value("envhumo.json")
    val_viento = load_last_value("envviento.json")
    val_temp = load_last_value("envtemperatura.json")
    val_hum = load_last_value("envhumedad.json")
    val_iaq = load_last_value("envcalidadaire.json")

    sistema_ok = True
    
    # Imprimimos estado general (opcional, para depurar)
    # print(f"Estado: H:{val_hum}% T:{val_temp}ºC V:{val_viento}km/h Aire:{val_iaq} Humo:{val_humo}")

    # GRUPO 1: GESTIÓN DE EMERGENCIAS 
    
    # Alerta por HUMO (Incendio)
    umbral_humo = config.get("humo_max", 25)
    if val_humo > umbral_humo:
        print(f"[EMERGENCIA] ¡HUMO DETECTADO! (Nivel {val_humo} > {umbral_humo})")
        sistema_ok = False

    # Alerta por VIENTO (Seguridad Estructural)
    umbral_viento = config.get("viento_max", 50)
    if val_viento > umbral_viento:
        print(f"[EMERGENCIA] VIENTO PELIGROSO ({val_viento} km/h > {umbral_viento} km/h)")
        sistema_ok = False

    
    # GRUPO 2: CONTROL AMBIENTAL 

    # Alerta por TEMPERATURA
    umbral_temp = config.get("temp_max", 35)
    if val_temp > umbral_temp:
        print(f"[AVISO AMBIENTAL] Temperatura alta: {val_temp}ºC (Límite: {umbral_temp}ºC)")
        sistema_ok = False

    # Alerta por HUMEDAD (Nueva comprobación añadida)
    umbral_hum = config.get("hum_max", 70)
    if val_hum > umbral_hum:
        print(f"[AVISO AMBIENTAL] Humedad excesiva: {val_hum}% (Límite: {umbral_hum}%)")
        sistema_ok = False

    # Alerta por CALIDAD DEL AIRE
    umbral_iaq = config.get("iaq_max", 100)
    if val_iaq > umbral_iaq:
        print(f"[AVISO AMBIENTAL] Mala calidad del aire: IAQ {val_iaq} (Límite: {umbral_iaq})")
        sistema_ok = False

    if sistema_ok:
        print("✅ Sistema en parámetros normales")
    else:
        print("-" * 40) # Separador visual si hay alertas

def main():
    print("Controlador de Alarmas y Ambiente Iniciado")
    while True:
        check_alarms()
        time.sleep(5) # Comprobar cada 5 segundos

if __name__ == "__main__":
    main()