import json
import time
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Archivos
SENSOR_FILE = os.path.join(DATA_DIR, "access_distance.json")
STATE_FILE = os.path.join(DATA_DIR, "access_state.json")
LOG_FILE = os.path.join(DATA_DIR, "access_log.json")
MANUAL_FILE = os.path.join(DATA_DIR, "access_manual_state.json")

# Configuración
DISTANCIA_APERTURA = 100
TIEMPO_PASO_VEHICULO = 5

barrera_fisica_abierta = False

def get_json_data(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f: return json.load(f)
        except: pass
    return default

def log_access_event(tipo="Vehículo Detectado"):
    nuevo_registro = {
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evento": "Acceso Permitido",
        "tipo": tipo
    }
    registros = get_json_data(LOG_FILE, [])
    registros.insert(0, nuevo_registro)
    registros = registros[:20]
    try:
        with open(LOG_FILE, "w") as f: json.dump(registros, f, indent=4)
        print(f"[LOG] Nuevo registro: {tipo}")
    except: pass

def set_barrier_state(is_open, distance, msg_extra=""):
    msg = "BARRERA ABIERTA" if is_open else "BARRERA CERRADA"
    # Si está en manual, lo indicamos en el mensaje para que la UI lo sepa
    if msg_extra == "MANUAL":
        msg += " (MANUAL)"
    
    state = {
        "barrera_abierta": is_open,
        "mensaje": msg,
        "distancia_detectada": distance
    }
    try:
        with open(STATE_FILE, "w") as f: json.dump(state, f, indent=4)
    except: pass

def main():
    global barrera_fisica_abierta
    print("Controlador de Accesos (DEBUG MODE)")
    
    tiempo_para_cerrar = 0
    
    while True:
        # Leemos los estados
        raw_sensor = get_json_data(SENSOR_FILE, {"distance_cm": 500})
        dist = raw_sensor.get("distance_cm", 500)
        
        # Leemos el archivo manual
        manual_config = get_json_data(MANUAL_FILE, {"modo_manual": False, "abrir": False})
        
        estado_final = False
        origen = "AUTO"

        # LÓGICA DE DECISIÓN DE APERTURA/CIERRE
        if manual_config.get("modo_manual") is True:
            # MODO MANUAL ACTIVO
            origen = "MANUAL"
            if manual_config.get("abrir") is True:
                estado_final = True
                if not barrera_fisica_abierta:
                    print(f"MANUAL Orden de ABRIR recibida.")
                    log_access_event("Apertura Manual")
                    barrera_fisica_abierta = True
            else:
                estado_final = False
                if barrera_fisica_abierta:
                    print(f"MANUAL Orden de CERRAR recibida.")
                    barrera_fisica_abierta = False
        else:
            # MODO AUTOMÁTICO
            if dist < DISTANCIA_APERTURA:
                tiempo_para_cerrar = time.time() + TIEMPO_PASO_VEHICULO
                if not barrera_fisica_abierta:
                    log_access_event("Vehículo Detectado")
                    print(f"AUTO Coche a {dist}cm -> Abriendo")
                    barrera_fisica_abierta = True
            
            if time.time() < tiempo_para_cerrar:
                estado_final = True
            else:
                estado_final = False
                if barrera_fisica_abierta:
                    print("AUTO Tiempo agotado -> Cerrando")
                    barrera_fisica_abierta = False

        # Guardar estado
        set_barrier_state(estado_final, dist, origen)
        
        # Pequeño debug en consola si está en manual para confirmar que lo lee
        if origen == "MANUAL":
            # print(f"Estado Manual: {manual_config}") 
            pass
            
        time.sleep(0.5)

if __name__ == "__main__":
    main()