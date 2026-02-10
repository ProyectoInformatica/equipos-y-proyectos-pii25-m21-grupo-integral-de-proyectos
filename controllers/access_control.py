import json
import time
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Archivos
SENSOR_FILE = os.path.join(DATA_DIR, "access_distance.json")
WIND_FILE = os.path.join(DATA_DIR, "envviento.json")
STATE_FILE = os.path.join(DATA_DIR, "access_state.json")
LOG_FILE = os.path.join(DATA_DIR, "access_log.json")
MANUAL_FILE = os.path.join(DATA_DIR, "access_manual_state.json")

# Configuración
DISTANCIA_APERTURA = 100
TIEMPO_PASO_VEHICULO = 5
UMBRAL_VIENTO_PELIGROSO = 50.0  # km/h para bloqueo de seguridad

# Estado físico de cada barrera (para tracking de cambios)
barreras_fisicas_abiertas = {
    "norte": False,
    "sur": False
}

# Timers para cerrar automáticamente cada barrera
tiempos_cierre = {
    "norte": 0,
    "sur": 0
}

def get_json_data(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                return data
        except:
            pass
    return default

def get_latest_value(filepath, key="value"):
    """Ayuda a sacar el último valor de listas tipo log (como viento)"""
    data = get_json_data(filepath, [])
    if isinstance(data, list) and len(data) > 0:
        return data[-1].get(key, 0)
    return 0

def log_access_event(barrera, tipo="Vehículo Detectado"):
    """Registra un evento de acceso con el identificador de barrera"""
    nuevo_registro = {
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evento": "Acceso Permitido",
        "tipo": tipo,
        "barrera": barrera.upper()
    }
    registros = get_json_data(LOG_FILE, [])
    if not isinstance(registros, list):
        registros = []
    registros.insert(0, nuevo_registro)
    registros = registros[:20]  # Mantener solo los últimos 20
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(registros, f, indent=4)
        print(f"[LOG {barrera.upper()}] Nuevo registro: {tipo}")
    except:
        pass

def set_barrier_state(barrera, is_open, distance, msg_extra=""):
    """Guarda el estado de una barrera específica"""
    msg = "BARRERA ABIERTA" if is_open else "BARRERA CERRADA"
    if msg_extra:
        msg += f" ({msg_extra})"

    estado_barrera = {
        "barrera_abierta": is_open,
        "mensaje": msg,
        "distancia_detectada": distance
    }

    try:
        # Leer estado actual
        estados = get_json_data(STATE_FILE, {})
        
        # Si el formato es antiguo (sin norte/sur), convertirlo
        if "barrera_abierta" in estados:
            estados = {
                "norte": estados,
                "sur": {
                    "barrera_abierta": False,
                    "mensaje": "BARRERA CERRADA",
                    "distancia_detectada": 500
                }
            }
        
        # Actualizar la barrera específica
        estados[barrera] = estado_barrera
        
        # Guardar
        with open(STATE_FILE, "w") as f:
            json.dump(estados, f, indent=4)
    except Exception as e:
        print(f"[ERROR] No se pudo guardar estado de {barrera}: {e}")

def procesar_barrera(barrera):
    """Procesa la lógica de control para una barrera específica"""
    global barreras_fisicas_abiertas, tiempos_cierre
    
    # 1. Leer sensor de distancia para esta barrera
    raw_sensors = get_json_data(SENSOR_FILE, {})
    
    # Si el formato es antiguo (sin norte/sur), convertirlo
    if "distance_cm" in raw_sensors:
        raw_sensors = {
            "norte": raw_sensors,
            "sur": {"distance_cm": 500}
        }
    
    sensor_data = raw_sensors.get(barrera, {})
    if isinstance(sensor_data, dict):
        dist = sensor_data.get("distance_cm", 500)
    else:
        dist = 500

    # 2. Leer viento (compartido para ambas barreras)
    viento_actual = get_latest_value(WIND_FILE, "value")

    # 3. Leer Modo Manual para esta barrera
    raw_manual = get_json_data(MANUAL_FILE, {})
    
    # Si el formato es antiguo (sin norte/sur), convertirlo
    if "modo_manual" in raw_manual:
        raw_manual = {
            "norte": raw_manual,
            "sur": {"modo_manual": False, "abrir": False}
        }
    
    manual_config = raw_manual.get(barrera, {"modo_manual": False, "abrir": False})
    if isinstance(manual_config, list):
        manual_config = {}

    estado_final = False
    origen = "AUTO"

    # LÓGICA DE PRIORIDADES:
    # 1. SEGURIDAD (Viento) -> Prioridad Máxima
    if viento_actual > UMBRAL_VIENTO_PELIGROSO:
        estado_final = False  # Cerrar por seguridad
        origen = "ALERTA VIENTO"
        if barreras_fisicas_abiertas[barrera]:
            print(f"⚠️ [{barrera.upper()}] CIERRE DE EMERGENCIA: Viento fuerte ({viento_actual} km/h)")
            log_access_event(barrera, "Cierre Emergencia Viento")
            barreras_fisicas_abiertas[barrera] = False

    # 2. MODO MANUAL -> Prioridad Media (si no hay emergencia)
    elif manual_config.get("modo_manual") is True:
        origen = "MANUAL"
        if manual_config.get("abrir") is True:
            estado_final = True
            if not barreras_fisicas_abiertas[barrera]:
                log_access_event(barrera, "Apertura Manual")
                barreras_fisicas_abiertas[barrera] = True
        else:
            estado_final = False
            barreras_fisicas_abiertas[barrera] = False

    # 3. MODO AUTOMÁTICO -> Prioridad Baja
    else:
        if dist < DISTANCIA_APERTURA:
            tiempos_cierre[barrera] = time.time() + TIEMPO_PASO_VEHICULO
            if not barreras_fisicas_abiertas[barrera]:
                log_access_event(barrera, "Vehículo Detectado")
                print(f"[{barrera.upper()}] AUTO Coche a {dist}cm -> Abriendo")
                barreras_fisicas_abiertas[barrera] = True

        if time.time() < tiempos_cierre[barrera]:
            estado_final = True
        else:
            estado_final = False
            if barreras_fisicas_abiertas[barrera]:
                barreras_fisicas_abiertas[barrera] = False

    # Guardar estado de esta barrera
    set_barrier_state(barrera, estado_final, dist, origen)

def main():
    global barreras_fisicas_abiertas, tiempos_cierre
    
    print("Controlador de Accesos (Monitorizando Sensores y Clima)")
    print("Gestionando barreras: NORTE y SUR")
    
    while True:
        # Procesar ambas barreras independientemente
        procesar_barrera("norte")
        procesar_barrera("sur")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
