import json
import time
import os

# Archivos de entrada (generados por otros scripts)
ENV_FILE = 'env.json'   # Debería contener: {"temperature": 25, "gas_level": 100}
WIND_FILE = 'wind.json' # Generado por wind_sensor.py

# Umbrales de seguridad (Caso de Uso 2 y 3)
TEMP_MAX = 35.0       # Grados Celsius
GAS_MAX = 400         # PPM
WIND_MAX = 60.0       # km/h (Para cerrar compuertas según caso 3)

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def check_alerts():
    alerts = []
    
    # 1. Verificar Ambientales (Temperatura y Gases)
    env_data = load_json(ENV_FILE)
    if env_data:
        temp = env_data.get('temperature', 0)
        gas = env_data.get('gas_level', 0)
        
        if temp > TEMP_MAX:
            alerts.append(f"[PELIGRO] Temperatura alta: {temp}°C")
        if gas > GAS_MAX:
            alerts.append(f"[PELIGRO] Nivel de gas tóxico: {gas} PPM")
            
    # 2. Verificar Viento 
    wind_data = load_json(WIND_FILE)
    if wind_data:
        speed = wind_data.get('speed_kmh', 0)
        if speed > WIND_MAX:
            alerts.append(f"[ALERTA] Viento fuerte: {speed} km/h - CERRAR COMPUERTAS")

    # Mostrar alertas
    if alerts:
        print("\n--- ALERTAS ACTIVAS ---")
        for alert in alerts:
            print(alert)
            # Aquí se añadira código para enviar un email o guardar en un log
            # por simplicidad solo imprimimos
    else:
        print(f"Estado normal. (Temp: {env_data.get('temperature') if env_data else '?'}°C, Viento: {wind_data.get('speed_kmh') if wind_data else '?'} km/h)")

def main():
    print("Iniciando Monitor de Alertas...")
    while True:
        check_alerts()
        time.sleep(5)

if __name__ == "__main__":
    main()