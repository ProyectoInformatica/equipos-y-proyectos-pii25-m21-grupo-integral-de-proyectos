import json
import time
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SENSOR_FILE = os.path.join(DATA_DIR, "access_distance.json")
STATE_FILE = os.path.join(DATA_DIR, "access_state.json")
LOG_FILE = os.path.join(DATA_DIR, "access_log.json")

# Configuración
DISTANCIA_APERTURA = 100
TIEMPO_PASO_VEHICULO = 5  # La barrera se mantiene verde 5 segundos

# Estado interno
barrera_fisica_abierta = False

def get_distance():
    if os.path.exists(SENSOR_FILE):
        try:
            with open(SENSOR_FILE, "r") as f:
                return json.load(f).get("distance_cm", 500)
        except: return 500
    return 500

def log_access_event():
    nuevo_registro = {
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evento": "Acceso Permitido",
        "tipo": "Vehículo Detectado"
    }
    registros = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f: registros = json.load(f)
        except: pass
    
    registros.insert(0, nuevo_registro)
    registros = registros[:20]
    
    try:
        with open(LOG_FILE, "w") as f: json.dump(registros, f, indent=4)
        print(f"[ACCESO] Registro guardado: {nuevo_registro['hora']}")
    except: pass

def set_barrier_state(is_open, distance):
    # AQUÍ ESTÁ EL CAMBIO DE TEXTO QUE PEDISTE
    state = {
        "barrera_abierta": is_open,
        "mensaje": "BARRERA ABIERTA" if is_open else "BARRERA CERRADA",
        "distancia_detectada": distance
    }
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except: pass

def main():
    global barrera_fisica_abierta
    print("Controlador de Accesos (5s Verde)")
    
    tiempo_para_cerrar = 0
    
    while True:
        dist = get_distance()
        
        # 1. Detectar coche
        if dist < DISTANCIA_APERTURA:
            # Renovamos los 5 segundos de "tiempo verde"
            tiempo_para_cerrar = time.time() + TIEMPO_PASO_VEHICULO
            
            if not barrera_fisica_abierta:
                log_access_event()
                print(f"COCHE DETECTADO ({dist}cm) -> ABRIENDO")
                barrera_fisica_abierta = True

        # 2. Gestionar tiempo
        if time.time() < tiempo_para_cerrar:
            estado_actual = True  # Mantenemos verde
        else:
            estado_actual = False # Cerramos
            if barrera_fisica_abierta:
                print("TIEMPO AGOTADO -> CERRANDO")
                barrera_fisica_abierta = False

        # 3. Guardar estado
        set_barrier_state(estado_actual, dist)
            
        time.sleep(0.5)

if __name__ == "__main__":
    main()