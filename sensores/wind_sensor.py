import json
import time
import random
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "envviento.json")
MAX_RECORDS = 24

# Velocidad actual del viento
current_speed = 10.0

def calculate_smooth_wind():
    global current_speed
    
    # El viento cambia más bruscamente que la temperatura
    change = random.uniform(-3.0, 3.0)
    current_speed += change
    
    # A veces hay una ráfaga fuerte (5% de probabilidad)
    if random.random() > 0.95:
        current_speed += random.uniform(5.0, 15.0)
        
    # El viento baja naturalmente si está muy alto
    if current_speed > 20:
        current_speed -= 1.0

    # Límites (0 a 100 km/h)
    current_speed = max(0.0, min(100.0, current_speed))
    
    return round(current_speed, 2)

def main():
    print("--- Sensor de Viento (Simulación Realista) ---")
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    while True:
        speed = calculate_smooth_wind()
        
        data = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f: data = json.load(f)
            except: data = []
        
        data.append({"hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "value": speed})
        if len(data) > MAX_RECORDS: data = data[-MAX_RECORDS:]
        
        with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
        
        print(f"[Viento] {speed} km/h")
        time.sleep(5)

if __name__ == "__main__":
    main()