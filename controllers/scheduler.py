import time
import json
import os
from datetime import datetime

# Rutas absolutas para evitar errores de "archivo no encontrado"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULE_FILE = os.path.join(BASE_DIR, "data", "schedule.json")
LIGHT_FILE = os.path.join(BASE_DIR, "data", "light.json")

def leer_horario():
    """Lee el horario desde data/schedule.json."""
    try:
        with open(SCHEDULE_FILE, "r") as f:
            data = json.load(f)
            return {
                "hora_inicio": int(data.get("hora_inicio", 0)),
                "minuto_inicio": int(data.get("minuto_inicio", 0)),
                "hora_fin": int(data.get("hora_fin", 0)),
                "minuto_fin": int(data.get("minuto_fin", 0))
            }
    except Exception as e:
        print(f"scheduler Error leyendo horario: {e}")
        return {"hora_inicio": 0, "minuto_inicio": 0, "hora_fin": 0, "minuto_fin": 0}

def guardar_horario(h_ini, m_ini, h_fin, m_fin):
    """
    Controlador: Recibe los datos de la vista y actualiza el Modelo (JSON).
    """
    nuevo_horario = {
        "hora_inicio": str(h_ini),
        "minuto_inicio": str(m_ini),
        "hora_fin": str(h_fin),
        "minuto_fin": str(m_fin)
    }
    
    try:
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(nuevo_horario, f, indent=4)
        print(f"scheduler Nuevo horario guardado: {nuevo_horario}")
        return True
    except Exception as e:
        print(f"scheduler Error guardando horario: {e}")
        return False

def escribir_estado_luz(estado):
    """Actualiza el estado de la luz en data/light.json."""
    # Primero leemos para no borrar la luminosidad del sensor
    data = {}
    if os.path.exists(LIGHT_FILE):
        try:
            with open(LIGHT_FILE, "r") as f:
                data = json.load(f)
        except: pass
    
    data["estado"] = estado
    
    try:
        with open(LIGHT_FILE, "w") as f:
            json.dump(data, f, indent=4)
        # print(f"scheduler Luz actualizada -> {estado.upper()}") # Comentado para no saturar consola
    except Exception as e:
        print(f"scheduler Error escribiendo light.json: {e}")

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