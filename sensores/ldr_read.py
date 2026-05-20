import time
import random
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import set_light_sensor

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
    try:
        set_light_sensor(new_luminosity)
        print(f"Sensor LDR Luz: {new_luminosity}%")
    except Exception as e:
        print(f"Error LDR {e}")

def main():
    print("Sensor LDR Iniciado")
    while True:
        lux = simulate_light()
        update_light_data(lux)
        time.sleep(5)

if __name__ == "__main__":
    main()