import json
import time
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "light.json")

# Empezamos con luz media
current_lux = 50

def simulate_light():
    global current_lux
    # Cambia muy poco a poco (simulando paso de nubes o atardecer)
    change = random.randint(-3, 3)
    current_lux += change
    current_lux = max(0, min(100, current_lux))
    return current_lux

def update_light_data(new_luminosity):
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: data = json.load(f)
        except: data = {}
    
    data["luminosity"] = new_luminosity
    
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"[Sensor LDR] Luz: {new_luminosity}%")
    except Exception as e:
        print(f"[Error LDR] {e}")

def main():
    print("--- Sensor LDR (Suave) ---")
    while True:
        lux = simulate_light()
        update_light_data(lux)
        time.sleep(5)

if __name__ == "__main__":
    main()