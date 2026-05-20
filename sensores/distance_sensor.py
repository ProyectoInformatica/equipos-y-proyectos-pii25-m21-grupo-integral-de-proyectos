import time
import random
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import get_access_manual_state, set_access_distance

# Distancias en cm (sin coche = 500 cm) - una para cada barrera
current_distances = {
    "norte": 500,
    "sur": 500
}

# Timers para simular coches cada 30-60 segundos (solo en modo automático)
next_car_time = {
    "norte": 0,
    "sur": 0
}

# Timers para mantener el coche presente durante un tiempo visible
car_present_time = {
    "norte": 0,
    "sur": 0
}

TIEMPO_PRESENCIA_COCHE = 7  # Tiempo en segundos que el coche permanece visible

def is_manual_mode(barrera):
    """Verifica si una barrera está en modo manual"""
    manual_data = get_access_manual_state(barrera)
    return manual_data.get("modo_manual", False)

def simulate_car_approach(barrera):
    """Simula la aproximación de un coche a una barrera específica (solo en modo automático)"""
    global current_distances, next_car_time, car_present_time
    
    dist = current_distances[barrera]
    current_time = time.time()
    
    # Si está en modo manual, mantener distancia normal (sin coches)
    if is_manual_mode(barrera):
        if dist < 100:
            # Si había un coche, hacer que se vaya
            current_distances[barrera] = 500
            car_present_time[barrera] = 0
        else:
            # Mantener distancia normal
            current_distances[barrera] = 500
        return current_distances[barrera]
    
    # MODO AUTOMÁTICO: Simular coches cada 30-60 segundos
    if dist > 300:
        # No hay coche presente, verificar si es momento de que llegue uno
        if current_time >= next_car_time[barrera]:
            # ¡Llega un coche!
            current_distances[barrera] = 50  # Coche detectado
            car_present_time[barrera] = current_time + TIEMPO_PRESENCIA_COCHE  # Mantener presente durante X segundos
            # Programar próximo coche en 30-60 segundos
            next_car_time[barrera] = current_time + random.uniform(30, 60)
            print(f"[Sensor {barrera.upper()}] Coche detectado (distancia: 50 cm)")
        else:
            # Esperando próximo coche, mantener distancia normal
            current_distances[barrera] = 500
    elif dist < 100:
        # Coche presente, mantenerlo hasta que pase el tiempo de presencia
        if current_time >= car_present_time[barrera]:
            # Tiempo de presencia completado, el coche se va
            current_distances[barrera] = 500  # El coche pasó
            car_present_time[barrera] = 0
            print(f"[Sensor {barrera.upper()}] Coche pasó (distancia: 500 cm)")
        else:
            # Mantener el coche presente
            current_distances[barrera] = 50
    else:
        # Distancia intermedia, mantener normal
        current_distances[barrera] = 500
        
    return current_distances[barrera]

def update_data():
    """Actualiza los datos de distancia para ambas barreras"""
    try:
        set_access_distance("norte", current_distances["norte"])
        set_access_distance("sur", current_distances["sur"])
    except Exception as e:
        print(f"[Error Distancia] {e}")

def main():
    global next_car_time, car_present_time
    
    print("Sensor de Distancia (Acceso) Iniciado - Gestión de Barreras NORTE y SUR")
    print("Simulación de coches cada 30-60 segundos en modo automático")
    print(f"Coches permanecen visibles durante {TIEMPO_PRESENCIA_COCHE} segundos")
    
    # Inicializar timers para primera detección
    current_time = time.time()
    next_car_time["norte"] = current_time + random.uniform(30, 60)
    next_car_time["sur"] = current_time + random.uniform(30, 60)
    car_present_time["norte"] = 0
    car_present_time["sur"] = 0
    
    while True:
        # Simular ambas barreras
        simulate_car_approach("norte")
        simulate_car_approach("sur")
        update_data()
        time.sleep(2)  # Reacciona rápido (2s)

if __name__ == "__main__":
    main()
