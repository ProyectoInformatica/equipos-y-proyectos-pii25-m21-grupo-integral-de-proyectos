import time
import os
import sys
from datetime import datetime

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import get_schedule, set_schedule, set_light_sensor, get_light_sensor

def leer_horario():
    """Lee el horario desde la base de datos."""
    try:
        return get_schedule()
    except Exception as e:
        print(f"scheduler Error leyendo horario: {e}")
        return {"hora_inicio": 0, "minuto_inicio": 0, "hora_fin": 0, "minuto_fin": 0}

def guardar_horario(h_ini, m_ini, h_fin, m_fin):
    """
    Controlador: Recibe los datos de la vista y actualiza la base de datos.
    """
    try:
        # Validar que todos los valores estén presentes
        if h_ini is None or m_ini is None or h_fin is None or m_fin is None:
            print("scheduler Error: valores de horario None")
            return False
        
        # Convertir a enteros
        h_ini_int = int(h_ini)
        m_ini_int = int(m_ini)
        h_fin_int = int(h_fin)
        m_fin_int = int(m_fin)
        
        # Validar rangos
        if not (0 <= h_ini_int < 24 and 0 <= m_ini_int < 60 and 
                0 <= h_fin_int < 24 and 0 <= m_fin_int < 60):
            print("scheduler Error: valores de horario fuera de rango")
            return False
        
        set_schedule(h_ini_int, m_ini_int, h_fin_int, m_fin_int)
        print(f"scheduler Nuevo horario guardado: {h_ini_int:02d}:{m_ini_int:02d} - {h_fin_int:02d}:{m_fin_int:02d}")
        return True
    except (ValueError, TypeError) as e:
        print(f"scheduler Error: valores de horario inválidos: {e}")
        return False
    except Exception as e:
        print(f"scheduler Error guardando horario: {e}")
        return False

def escribir_estado_luz(estado):
    """Actualiza el estado de la luz en la base de datos."""
    try:
        # El estado de control se guarda en light_state, no en light_sensor
        # light_sensor solo guarda datos del sensor (luminosidad)
        from database import set_light_state
        intensidad = 100 if estado.lower() == "on" else 0
        set_light_state(estado.upper(), intensidad, "HORARIO")
        # print(f"scheduler Luz actualizada -> {estado.upper()}") # Comentado para no saturar consola
    except Exception as e:
        print(f"scheduler Error escribiendo estado luz: {e}")

def dentro_del_horario(hora_actual, minuto_actual, horario):
    inicio = horario["hora_inicio"] * 60 + horario["minuto_inicio"]
    fin = horario["hora_fin"] * 60 + horario["minuto_fin"]
    actual = hora_actual * 60 + minuto_actual

    if fin < inicio: # Cruza medianoche
        return actual >= inicio or actual < fin
    else:
        return inicio <= actual < fin

def scheduler_loop():
    print("Iniciando control horario...")
    while True:
        horario = leer_horario()
        ahora = datetime.now()
        
        # Lógica de control
        if dentro_del_horario(ahora.hour, ahora.minute, horario):
            escribir_estado_luz("on")
        else:
            escribir_estado_luz("off")

        time.sleep(10) # Revisa cada 10 segundos

if __name__ == "__main__":
    scheduler_loop()