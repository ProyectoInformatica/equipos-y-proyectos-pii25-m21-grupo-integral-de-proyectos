import json
import time
import random
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "resource_water.json")
MAX_RECORDS = 24

current_flow = 0.0 # Litros por minuto

def simulate_water_flow():
    global current_flow
    
    # Variación suave
    current_flow += random.uniform(-2.0, 2.0)
    
    # Eventos aleatorios (alguien abre un grifo)
    if random.random() > 0.8:
        current_flow += random.uniform(5.0, 10.0)
    
    # Simulación de fuga (evento raro pero constante)
    # if random.random() > 0.98: current_flow = 40.0 

    # La presión tiende a bajar a 0 si no se usa
    if current_flow > 0:
        current_flow -= 1.0
    
    current_flow = max(0.0, min(60.0, current_flow))
    return round(current_flow, 2)

def main():
    print("Sensor de Caudal (Agua) Iniciado")
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    while True:
        flow = simulate_water_flow()
        
        data = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f: data = json.load(f)
            except: data = []
        
        data.append({"hora": datetime.now().strftime("%H:%M:%S"), "value": flow})
        if len(data) > MAX_RECORDS: data = data[-MAX_RECORDS:]
        
        with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
        
        # print(f"[Agua] Caudal: {flow} L/min")
        time.sleep(5)

if __name__ == "__main__":
    main()