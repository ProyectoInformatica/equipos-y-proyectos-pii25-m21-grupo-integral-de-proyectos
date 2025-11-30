import json
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
WATER_FILE = os.path.join(DATA_DIR, "resource_water.json")

# Umbral de fuga (L/min)
UMBRAL_FUGA = 45.0

def load_last_flow():
    if not os.path.exists(WATER_FILE): return 0
    try:
        with open(WATER_FILE, "r") as f:
            data = json.load(f)
            if data and isinstance(data, list):
                return data[-1].get("value", 0)
    except: return 0
    return 0

def check_resources():
    flujo = load_last_flow()
    
    if flujo > UMBRAL_FUGA:
        print(f"[ALERTA RECURSOS] ¡POSIBLE FUGA DE AGUA! Consumo: {flujo} L/min")
    
    # Aquí se podría añadir electricidad en el futuro

def main():
    print("Monitor de Recursos Iniciado")
    while True:
        check_resources()
        time.sleep(5)

if __name__ == "__main__":
    main()