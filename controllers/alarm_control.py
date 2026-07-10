import time
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import get_latest_sensor_value, get_latest_resource_value, get_alert_config, add_notification

def registrar_alerta(titulo, mensaje, nivel="crítico"):
    """Guarda la alerta en la base de datos"""
    try:
        add_notification(titulo, mensaje, nivel)
        print(f"ALERTA GUARDADA {titulo}: {mensaje}")
    except Exception as e:
        print(f"Error guardando alerta: {e}")

def check_alarms():
    # 1. Cargar Configuración
    config = get_alert_config()
    
    # 2. Leer sensores
    val_humo = get_latest_sensor_value("humo")
    val_viento = get_latest_sensor_value("viento")
    val_temp = get_latest_sensor_value("temp")
    val_iaq = get_latest_sensor_value("iaq")
    val_agua = get_latest_resource_value("water") 

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