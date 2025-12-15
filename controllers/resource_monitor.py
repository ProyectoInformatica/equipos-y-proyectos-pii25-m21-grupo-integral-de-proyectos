import json
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
WATER_FILE = os.path.join(DATA_DIR, "resource_water.json")
POWER_FILE = os.path.join(DATA_DIR, "resource_power.json")

# Umbrales
UMBRAL_FUGA_AGUA = 45.0
UMBRAL_SOBRECARGA = 8500.0 # Watts

def load_last_value(filepath):
    if not os.path.exists(filepath): return 0
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            if data and isinstance(data, list) and len(data) > 0:
                return data[-1].get("value", 0)
    except: return 0
    return 0

def check_resources():
    # 1. AGUA
    flujo = load_last_value(WATER_FILE)
    if flujo > UMBRAL_FUGA_AGUA:
        print(f"ALERTA RECURSOS ¡POSIBLE FUGA DE AGUA! Consumo: {flujo} L/min")
    
    # 2. ELECTRICIDAD 
    potencia = load_last_value(POWER_FILE)
    if potencia > UMBRAL_SOBRECARGA:
         print(f"ALERTA RECURSOS ¡SOBRECARGA ELÉCTRICA! Consumo: {potencia} W")

def main():
    print("Monitor de Recursos (Agua + Energía) Iniciado")
    while True:
        check_resources()
        time.sleep(5)

if __name__ == "__main__":
    main()