import json
import time
import random
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILES = {
    "temp": os.path.join(DATA_DIR, "envtemperatura.json"),
    "hum": os.path.join(DATA_DIR, "envhumedad.json"),
    "iaq": os.path.join(DATA_DIR, "envcalidadaire.json")
}
MAX_RECORDS = 24

# Valores iniciales (para empezar la simulación)
current_values = {
    "temp": 22.0,
    "hum": 45.0,
    "iaq": 60
}

def simulate_smooth_values():
    """Genera variaciones suaves basadas en el valor anterior."""
    global current_values
    
    # Temperatura: cambia lento (+- 0.2 grados)
    change_t = random.uniform(-0.3, 0.3)
    current_values["temp"] += change_t
    # Limitar rango real (ej: entre 18 y 30 grados)
    current_values["temp"] = max(18.0, min(30.0, current_values["temp"]))

    # Humedad: cambia moderado (+- 1%)
    change_h = random.uniform(-1.5, 1.5)
    current_values["hum"] += change_h
    # Limitar rango real (ej: 30% a 70%)
    current_values["hum"] = max(30.0, min(70.0, current_values["hum"]))

    # Calidad Aire: Estable, a veces sube
    # 90% del tiempo baja o se mantiene, 10% sube (simula coche pasando)
    if random.random() > 0.9:
        current_values["iaq"] += random.randint(5, 15)
    else:
        current_values["iaq"] -= random.randint(1, 5)
    
    # Limitar rango (0 excelente - 300 peligroso)
    current_values["iaq"] = max(20, min(150, current_values["iaq"]))

    return {
        "temp": round(current_values["temp"], 1),
        "hum": round(current_values["hum"], 1),
        "iaq": int(current_values["iaq"])
    }

def update_json_file(filepath, new_value):
    data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except:
            data = []
    
    new_record = {"hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "value": new_value}
    data.append(new_record)
    if len(data) > MAX_RECORDS:
        data = data[-MAX_RECORDS:]
        
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error en {filepath}: {e}")

def main():
    print("--- Estación Meteorológica (Datos Suaves) ---")
    os.makedirs(DATA_DIR, exist_ok=True)
    while True:
        sensors = simulate_smooth_values()
        print(f"[Ambiente] T:{sensors['temp']}°C | H:{sensors['hum']}% | Aire:{sensors['iaq']}")
        update_json_file(FILES["temp"], sensors["temp"])
        update_json_file(FILES["hum"], sensors["hum"])
        update_json_file(FILES["iaq"], sensors["iaq"])
        time.sleep(5)

if __name__ == "__main__":
    main()