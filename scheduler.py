import time
import json
from datetime import datetime


def leer_horario():
    """Lee el horario desde schedule.json."""
    try:
        with open("schedule.json", "r") as f:
            data = json.load(f)
            return {
                "hora_inicio": int(data.get("hora_inicio", 0)),
                "minuto_inicio": int(data.get("minuto_inicio", 0)),
                "hora_fin": int(data.get("hora_fin", 0)),
                "minuto_fin": int(data.get("minuto_fin", 0))
            }
    except FileNotFoundError:
        print("[scheduler] No se encontró schedule.json, usando horario por defecto (00:00 - 00:00)")
        return {"hora_inicio": 0, "minuto_inicio": 0, "hora_fin": 0, "minuto_fin": 0}
    except json.JSONDecodeError:
        print("[scheduler] Error al leer schedule.json, formato inválido.")
        return {"hora_inicio": 0, "minuto_inicio": 0, "hora_fin": 0, "minuto_fin": 0}


def escribir_estado_luz(estado):
    """Actualiza el estado de la luz en light.json."""
    data = {"estado": estado}
    try:
        with open("light.json", "w") as f:
            json.dump(data, f, indent=4)
        print(f"[scheduler] Luz actualizada → {estado.upper()}")
    except Exception as e:
        print(f"[scheduler] Error escribiendo light.json: {e}")


def dentro_del_horario(hora_actual, minuto_actual, horario):
    """Verifica si la hora actual está dentro del horario establecido."""
    inicio = horario["hora_inicio"] * 60 + horario["minuto_inicio"]
    fin = horario["hora_fin"] * 60 + horario["minuto_fin"]
    actual = hora_actual * 60 + minuto_actual

    # Si el horario cruza la medianoche (ej: 22:00 → 06:00)
    if fin < inicio:
        return actual >= inicio or actual < fin
    else:
        return inicio <= actual < fin


def scheduler_loop():
    """Bucle principal del scheduler de luces."""
    print("[scheduler] Iniciando control horario...")

    while True:
        horario = leer_horario()
        ahora = datetime.now()
        hora_actual = ahora.hour
        minuto_actual = ahora.minute

        if dentro_del_horario(hora_actual, minuto_actual, horario):
            escribir_estado_luz("on")
        else:
            escribir_estado_luz("off")

        time.sleep(30)  # Verifica cada 30 segundos


if __name__ == "__main__":
    scheduler_loop()
