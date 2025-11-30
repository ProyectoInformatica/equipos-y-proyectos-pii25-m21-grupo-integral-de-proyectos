import json
import time
import random
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "envhumo.json")
MAX_RECORDS = 24

# Nivel base
current_smoke = 2

def simulate_smoke():
    global current_smoke
    
    # Probabilidad muy baja de incendio (1%), si ocurre, sube rápido
    if random.random() > 0.99:
        current_smoke += 20 # Sube rápido
    else:
        # Si no hay incendio, tiende a bajar a niveles normales (0-5)
        if current_smoke > 5:
            current_smoke -= 5 # Se disipa
        else:
            # Ruido normal del sensor (0-5)
            current_smoke = random.randint(0, 5)
            
    current_smoke = max(0, min(100, current_smoke))
    return current_smoke

def main():
    print("--- Sensor de Humo (Estable) ---")
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    while True:
        level = simulate_smoke()
        
        data = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f: data = json.load(f)
            except: data = []

        data.append({"hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "value": level})
        if len(data) > MAX_RECORDS: data = data[-MAX_RECORDS:]

        with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)
        
        print(f"[Humo] Nivel: {level}")
        time.sleep(5)

if __name__ == "__main__":
    main()