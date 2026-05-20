import time
import random
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import add_resource_data

MAX_RECORDS = 50  # Guardar historial para la gráfica

def main():
    print(f"Iniciando Sensor de Flujo (Simulado)...")

    while True:
        # Simulación: 80% del tiempo es 0, 20% hay consumo
        if random.random() > 0.8:
            flujo = round(random.uniform(5.0, 15.0), 2)
        else:
            flujo = 0.0

        try:
            add_resource_data("water", flujo)
            if flujo > 0:
                print(f"[SENSOR AGUA] Flujo: {flujo} L/min")
        except Exception as e:
            print(f"[ERROR AGUA] {e}")

        time.sleep(2)

if __name__ == "__main__":
    main()