import os
import time
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import clean_sensor_data

MAX_RECORDS = 24  # Mantenemos las últimas 24 lecturas

# Lista de sensores que queremos mantener limpios
SENSORS_TO_CLEAN = [
    "temp",
    "hum",
    "iaq",
    "viento",
    "humo"
]

def clean_sensor(sensor_type):
    try:
        clean_sensor_data(sensor_type, MAX_RECORDS)
    except Exception as e:
        print(f"[Error Limpieza] {sensor_type}: {e}")

def main():
    print("Servicio de Limpieza de Datos (Controller) Iniciado")
    while True:
        for sensor in SENSORS_TO_CLEAN:
            clean_sensor(sensor)
        time.sleep(10) # Revisa cada 10 segundos

if __name__ == "__main__":
    main()