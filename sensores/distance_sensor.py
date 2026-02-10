import json
import time
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "access_distance.json")
MANUAL_FILE = os.path.join(BASE_DIR, "data", "access_manual_state.json")

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

def get_json_data(filepath, default):
    """Lee datos JSON de un archivo"""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except:
            pass
    return default

def is_manual_mode(barrera):
    """Verifica si una barrera está en modo manual"""
    manual_data = get_json_data(MANUAL_FILE, {})
    
    # Si el formato es antiguo (sin norte/sur), convertirlo
    if "modo_manual" in manual_data:
        manual_data = {
            "norte": manual_data,
            "sur": {"modo_manual": False, "abrir": False}
        }
    
    barrera_config = manual_data.get(barrera, {"modo_manual": False, "abrir": False})
    return barrera_config.get("modo_manual", False)

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
    data = {
        "norte": {"distance_cm": current_distances["norte"]},
        "sur": {"distance_cm": current_distances["sur"]}
    }
    
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
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
