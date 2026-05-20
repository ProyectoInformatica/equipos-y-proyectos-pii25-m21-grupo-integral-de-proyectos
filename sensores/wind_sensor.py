import time
import random
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import add_sensor_data

MAX_RECORDS = 24

# Velocidad actual del viento
current_speed = 10.0

def calculate_smooth_wind():
    global current_speed
    
    # El viento cambia más bruscamente que la temperatura
    change = random.uniform(-3.0, 3.0)
    current_speed += change
    
    # A veces hay una ráfaga fuerte (5% de probabilidad)
    if random.random() > 0.95:
        current_speed += random.uniform(5.0, 15.0)
        
    # El viento baja naturalmente si está muy alto
    if current_speed > 20:
        current_speed -= 1.0

    # Límites (0 a 100 km/h)
    current_speed = max(0.0, min(100.0, current_speed))
    
    return round(current_speed, 2)

def main():
    print("Sensor de Viento Iniciado")
    
    while True:
        speed = calculate_smooth_wind()
        add_sensor_data("viento", speed)
        print(f"[Viento] {speed} km/h")
        time.sleep(5)

if __name__ == "__main__":
    main()