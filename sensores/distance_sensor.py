import json
import time
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "access_distance.json")

# Distancia en cm (sin coche = 500 cm)
current_distance = 500

def simulate_car_approach():
    global current_distance
    
    # 10% de probabilidad de que llegue un coche (baja la distancia rápidamente)
    if current_distance > 300 and random.random() > 0.9:
        current_distance = 50 # ¡Coche detectado en la barrera!
    elif current_distance < 100:
        # Si el coche ya está ahí, espera un poco y luego se va
        if random.random() > 0.7:
            current_distance = 500 # El coche pasó
    else:
        # Ruido normal del sensor
        current_distance = 500
        
    return current_distance

def update_data(dist):
    data = {"distance_cm": dist}
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        # print(f"[Sensor Distancia] {dist} cm") 
    except Exception as e:
        print(f"[Error Distancia] {e}")

def main():
    print("--- Sensor de Distancia (Acceso) Iniciado ---")
    while True:
        d = simulate_car_approach()
        update_data(d)
        time.sleep(2) # Reacciona rápido (2s)

if __name__ == "__main__":
    main()