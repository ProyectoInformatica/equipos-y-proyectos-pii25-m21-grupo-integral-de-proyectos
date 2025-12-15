import json
import time
import random
import os
from datetime import datetime

# Configuración
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "resource_power.json")

# Simulación de carga (Watts)
# Base: 2000W (consumo residual)
# Pico noche: +5000W (farolas encendidas)
def leer_simulacion_potencia():
    hora_actual = datetime.now().hour
    
    # Consumo base (servidores, sensores, standby)
    consumo = 2000 + random.uniform(-100, 100)
    
    # Si es de noche (aprox 20:00 - 07:00), sumamos farolas
    if hora_actual >= 20 or hora_actual < 7:
        consumo += 5000 + random.uniform(-200, 200)
        
    # Picos aleatorios (ej. bomba de agua activada)
    if random.random() > 0.8:
        consumo += 1500

    return round(consumo, 2)

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    print("Sensor de Energía Iniciado")
    
    historial = []
    
    while True:
        valor_w = leer_simulacion_potencia()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        registro = {
            "hora": timestamp,
            "value": valor_w,
            "unit": "W"
        }
        
        historial.append(registro)
        # Guardamos solo las últimas 24 lecturas (ej. 24 horas si fuera 1 por hora, aquí es rápido para demo)
        if len(historial) > 50: 
            historial.pop(0)
            
        try:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(historial, f, indent=4)
            print(f"POWER Consumo actual: {valor_w} W")
        except Exception as e:
            print(f"Error escribiendo JSON: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    main()