import json
import time
import random
import os

# Archivos
WIND_FILE = 'wind.json'           # Dato actual (para alerts.py)
HISTORY_FILE = 'history_wind.json' # Historial (para data_cleaner.py)

def calculate_wind_speed():
    # Simulación de lectura, aqui se debería implementar la lógica real del sensor
    # Por ahora, generamos un valor aleatorio entre 0 y 100 km/h
    pulses = random.uniform(0, 40)
    return round(pulses * 2.4, 2)

def save_data(speed):
    # función para guardar datos en archivos JSON
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Guardar dato actual en wind.json
    current_data = {
        "speed_kmh": speed,
        "timestamp": timestamp,
        "sensor_status": "OK"
    }
    with open(WIND_FILE, 'w') as f:
        json.dump(current_data, f, indent=4)
    
    # 2. Guardar en historial (LO NUEVO)
    # Cargar historial existente
    # Si el archivo no existe, iniciamos una lista vacía
    # Luego añadimos el nuevo dato y guardamos de nuevo
    # todo el historial
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
    # Explicacion: Este script está diseñado para ejecutarse indefinidamente.
    # En un entorno real, se deberá manejar la terminación adecuada del proceso.
    # Se debe ejecutar en segundo plano