import time
import random
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import add_sensor_data

MAX_RECORDS = 24

# Nivel base
current_smoke = 2

def simulate_smoke():
    global current_smoke
    
    # Probabilidad muy baja de incendio (1%), si ocurre, sube rápido
    if random.random() > 0.99:
        current_smoke += 20 # Sube rápido
    else:
        # Si no hay incendio, tiende a bajar a niveles normales (0-5)
        if current_smoke > 5:
            current_smoke -= 5 # Se disipa
        else:
            # Ruido normal del sensor (0-5)
            current_smoke = random.randint(0, 5)
            
    current_smoke = max(0, min(100, current_smoke))
    return current_smoke

def main():
    print("Sensor de Humo Iniciado")
    
    while True:
        level = simulate_smoke()
        add_sensor_data("humo", level)
        print(f"Humo Nivel: {level}")
        time.sleep(5)

if __name__ == "__main__":
    main()