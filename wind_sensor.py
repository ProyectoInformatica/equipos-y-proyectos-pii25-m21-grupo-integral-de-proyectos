import json
import time
import random
import os

# Archivos
WIND_FILE = 'wind.json'           # Dato actual (para alerts.py)
HISTORY_FILE = 'history_wind.json' # Historial (para data_cleaner.py)

def calculate_wind_speed():
    # Simulación de lectura
    pulses = random.uniform(0, 40)
    return round(pulses * 2.4, 2)

def save_data(speed):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Guardar dato actual 
    current_data = {
        "speed_kmh": speed,
        "timestamp": timestamp,
        "sensor_status": "OK"
    }
    with open(WIND_FILE, 'w') as f:
        json.dump(current_data, f, indent=4)
    
    # 2. Guardar en historial (LO NUEVO)
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    history.append(current_data) # Añadimos el nuevo dato a la lista
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

    print(f"Viento: {speed} km/h | Guardado en {WIND_FILE} y añadido a {HISTORY_FILE}")

def main():
    print("Iniciando sensor de viento...")
    while True:
        speed = calculate_wind_speed()
        save_data(speed)
        time.sleep(2) # Genera datos cada 2 segundos para probar rápido

if __name__ == "__main__":
    main()