import json
import time
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "alert_config.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")

def load_json(filepath):
    if not os.path.exists(filepath): return None
    try:
        with open(filepath, "r") as f: return json.load(f)
    except: return None

def load_last_value(filename):
    data = load_json(os.path.join(DATA_DIR, filename))
    if data and isinstance(data, list) and len(data) > 0:
        return data[-1].get("value", 0)
    return 0

def registrar_alerta(titulo, mensaje, nivel="crítico"):
    """Guarda la alerta en notifications.json"""
    nueva_alerta = {
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "titulo": titulo,
        "mensaje": mensaje,
        "nivel": nivel  # 'crítico', 'advertencia', 'info'
    }
    
    # Leer historial existente
    historial = []
    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, "r") as f: historial = json.load(f)
        except: pass
    
    # Evitar duplicados recientes (alertas cada 5 segundos)
    if historial:
        ultimo = historial[0]
        # Si es el mismo título y ha pasado menos de 1 minuto, no duplicamos
        fmt = "%Y-%m-%d %H:%M:%S"
        t_ultimo = datetime.strptime(ultimo["hora"], fmt)
        t_ahora = datetime.strptime(nueva_alerta["hora"], fmt)
        diferencia = (t_ahora - t_ultimo).total_seconds()
        
        if ultimo["titulo"] == titulo and diferencia < 60:
            return # Ignorar alerta repetida

    # Insertar al principio y guardar (máx 50 registros)
    historial.insert(0, nueva_alerta)
    historial = historial[:50]
    
    try:
        with open(NOTIFICATIONS_FILE, "w") as f: json.dump(historial, f, indent=4)
        print(f"ALERTA GUARDADA {titulo}: {mensaje}")
    except Exception as e:
        print(f"Error guardando alerta: {e}")

def check_alarms():
    # 1. Cargar Configuración
    config = load_json(CONFIG_FILE) or {}
    
    # 2. Leer sensores
    val_humo = load_last_value("envhumo.json")
    val_viento = load_last_value("envviento.json")
    val_temp = load_last_value("envtemperatura.json")
    val_iaq = load_last_value("envcalidadaire.json")
    val_agua = load_last_value("resource_water.json") 

    # REGLAS DE ALERTA

    # Humo
    umbral_humo = config.get("humo_max", 25)
    if val_humo > umbral_humo:
        registrar_alerta("Incendio Detectado", f"Nivel de humo: {val_humo}", "crítico")

    # Viento
    umbral_viento = config.get("viento_max", 50)
    if val_viento > umbral_viento:
        registrar_alerta("Viento Peligroso", f"Velocidad: {val_viento} km/h", "crítico")

    # Temperatura
    umbral_temp = config.get("temp_max", 35)
    if val_temp > umbral_temp:
        registrar_alerta("Temperatura Alta", f"Valor: {val_temp} ºC", "advertencia")

    # Aire
    umbral_iaq = config.get("iaq_max", 100)
    if val_iaq > umbral_iaq:
        registrar_alerta("Mala Calidad Aire", f"IAQ: {val_iaq}", "advertencia")
        
    # Agua (Fuga)
    if val_agua > 45:
        registrar_alerta("Fuga de Agua", f"Consumo anómalo: {val_agua} L/min", "crítico")

def main():
    print("Controlador de Alarmas Iniciado")
    while True:
        try:
            check_alarms()
        except Exception as e:
            print(f"Error en ciclo de alarmas: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()