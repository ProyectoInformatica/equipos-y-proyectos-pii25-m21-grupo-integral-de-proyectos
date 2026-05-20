import time
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import (
    get_access_distance, get_latest_sensor_value, set_access_state,
    get_access_manual_state, add_access_log
)

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

# Funciones eliminadas - ahora usamos database directamente

def log_access_event(barrera, tipo="Vehículo Detectado"):
    """Registra un evento de acceso con el identificador de barrera"""
    try:
        add_access_log(barrera, tipo, "Acceso Permitido")
        print(f"[LOG {barrera.upper()}] Nuevo registro: {tipo}")
    except:
        pass

def set_barrier_state(barrera, is_open, distance, msg_extra=""):
    """Guarda el estado de una barrera específica"""
    msg = "BARRERA ABIERTA" if is_open else "BARRERA CERRADA"
    if msg_extra:
        msg += f" ({msg_extra})"

    try:
        set_access_state(barrera, is_open, msg, distance)
    except Exception as e:
        print(f"[ERROR] No se pudo guardar estado de {barrera}: {e}")

def procesar_barrera(barrera):
    """Procesa la lógica de control para una barrera específica"""
    global barreras_fisicas_abiertas, tiempos_cierre
    
    # 1. Leer sensor de distancia para esta barrera
    distances = get_access_distance()
    sensor_data = distances.get(barrera, {})
    dist = sensor_data.get("distance_cm", 500) if sensor_data else 500

    # 2. Leer viento (compartido para ambas barreras)
    viento_actual = get_latest_sensor_value("viento")

    # 3. Leer Modo Manual para esta barrera
    manual_config = get_access_manual_state(barrera)

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
