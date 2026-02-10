import json
import time
import random
import os
from datetime import datetime

# Rutas absolutas para evitar errores
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "resource_water.json")
MAX_RECORDS = 50  # Guardar historial para la gráfica

def main():
    print(f"Iniciando Sensor de Flujo (Simulado)...")
    
    # Asegurar que la carpeta existe
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    while True:
        # Simulación: 80% del tiempo es 0, 20% hay consumo
        if random.random() > 0.8:
            flujo = round(random.uniform(5.0, 15.0), 2)
        else:
            flujo = 0.0

        # FORMATO CORREGIDO: "hora" y "value" para coincidir con la UI
        nuevo_registro = {
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "value": flujo,  # Usamos 'value' para estandarizar
            "unit": "L/min"
        }

        # 1. Leer historial existente
        historial = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    content = f.read()
                    if content:
                        historial = json.loads(content)
                        # Si por error había un dict (formato antiguo), lo convertimos a lista
                        if isinstance(historial, dict):
                            historial = [] 
            except:
                historial = []

        # 2. Añadir nuevo dato y limitar tamaño
        historial.append(nuevo_registro)
        if len(historial) > MAX_RECORDS:
            historial = historial[-MAX_RECORDS:]

        # 3. Guardar la lista completa
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(historial, f, indent=4)
            
            if flujo > 0:
                print(f"[SENSOR AGUA] Flujo: {flujo} L/min")
        except Exception as e:
            print(f"[ERROR AGUA] {e}")

        time.sleep(2)

if __name__ == "__main__":
    main()