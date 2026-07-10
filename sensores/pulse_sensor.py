"""
Sensor de Pulsómetro.

Registra en cada lectura tres valores que forman una sola medición:
  - Frecuencia cardíaca -> pulsaciones por minuto (ppm)
  - Presión sistólica   -> presión máxima al latir el corazón, en mm Hg
  - Presión diastólica  -> presión entre latido y latido, en mm Hg

"""
import json
import time
import random
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "pulsometro.json")
MAX_RECORDS = 24

# Permite importar database.py (que está en la raíz del proyecto).
sys.path.insert(0, BASE_DIR)

# Valores iniciales dentro de rangos normales para un adulto en reposo.
current_values = {
    "frecuencia_cardiaca": 75,   # ppm
    "presion_sistolica": 120,    # mm Hg
    "presion_diastolica": 80,    # mm Hg
}


def simulate_smooth_values():
    """Genera variaciones suaves basadas en la lectura anterior."""
    global current_values

    # Frecuencia cardíaca: cambia moderado (+- 3 ppm), rango 55-110.
    current_values["frecuencia_cardiaca"] += random.randint(-3, 3)
    current_values["frecuencia_cardiaca"] = max(55, min(110, current_values["frecuencia_cardiaca"]))

    # Presión sistólica: cambia lento (+- 2 mm Hg), rango 100-140.
    current_values["presion_sistolica"] += random.randint(-2, 2)
    current_values["presion_sistolica"] = max(100, min(140, current_values["presion_sistolica"]))

    # Presión diastólica: cambia lento (+- 2 mm Hg), rango 60-90.
    current_values["presion_diastolica"] += random.randint(-2, 2)
    current_values["presion_diastolica"] = max(60, min(90, current_values["presion_diastolica"]))

    # La diastólica nunca debe superar a la sistólica.
    if current_values["presion_diastolica"] >= current_values["presion_sistolica"]:
        current_values["presion_diastolica"] = current_values["presion_sistolica"] - 20

    return dict(current_values)


def guardar_json(lectura):
    data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = []

    registro = {"hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    registro.update(lectura)
    data.append(registro)
    if len(data) > MAX_RECORDS:
        data = data[-MAX_RECORDS:]

    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error escribiendo {DATA_FILE}: {e}")


def guardar_bd(lectura):
    """Inserta la lectura en la BD. Best-effort: si la BD no está disponible,
    el sensor sigue funcionando solo con el JSON (igual que los demás)."""
    try:
        import database
        database.add_pulsometro_data(
            lectura["frecuencia_cardiaca"],
            lectura["presion_sistolica"],
            lectura["presion_diastolica"],
        )
    except Exception as e:
        print(f"[Pulsómetro] BD no disponible, solo JSON: {e}")


def main():
    print("Sensor de Pulsómetro Iniciado")
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    while True:
        lectura = simulate_smooth_values()
        print(
            f"[Pulsómetro] FC:{lectura['frecuencia_cardiaca']} ppm | "
            f"Presión: {lectura['presion_sistolica']}/{lectura['presion_diastolica']} mm Hg"
        )
        guardar_json(lectura)
        guardar_bd(lectura)
        time.sleep(5)


if __name__ == "__main__":
    main()
