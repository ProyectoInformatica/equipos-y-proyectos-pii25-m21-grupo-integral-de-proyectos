import json
from datetime import datetime, timedelta
import random
import time

# Archivos JSON
FILE_TEMP = "envtemperatura.json"
FILE_HUM = "envhumedad.json"
FILE_AIR = "envcalidadaire.json"

# Horario de simulación
HORA_INICIO = datetime.strptime("08:00", "%H:%M")
HORA_FIN = datetime.strptime("21:00", "%H:%M")

# Número de registros simulados por hora (puedes cambiar a 1 por hora o 2 por media hora)
INTERVALO_MINUTOS = 60  # cada hora

# Funciones de simulación de sensores
def leer_temperatura():
    """Simula lectura de DHT11/DHT22"""
    return round(random.uniform(15.0, 35.0), 2)

def leer_humedad():
    """Simula lectura de DHT11/DHT22"""
    return round(random.uniform(30.0, 80.0), 2)

def leer_calidad_aire():
    """Simula lectura de MQ135 en ppm"""
    return random.randint(50, 400)


# Función para guardar en JSON
def guardar_json(filename, clave, valor, timestamp):
    data = []
    if json_exists(filename):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []

    data.append({
        "timestamp": timestamp,
        clave: valor
    })

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def json_exists(filename):
    return True if filename and os.path.exists(filename) else False


# Simulación completa
def simulacion_esp32():
    registros = []

    hora_actual = HORA_INICIO
    while hora_actual <= HORA_FIN:
        # Generar lecturas simuladas
        temp = leer_temperatura()
        hum = leer_humedad()
        aire = leer_calidad_aire()
        ts = hora_actual.strftime("%Y-%m-%d %H:%M:%S")

        # Guardar en JSON
        guardar_json(FILE_TEMP, "temperatura", temp, ts)
        guardar_json(FILE_HUM, "humedad", hum, ts)
        guardar_json(FILE_AIR, "aire_ppm", aire, ts)

        print(f"[ESP32 Simulado] {ts} → Temp: {temp}°C, Hum: {hum}%, Aire: {aire}ppm")

        # Avanzar al siguiente intervalo
        hora_actual += timedelta(minutes=INTERVALO_MINUTOS)

        # Simulación de tiempo real (opcional: sleep 1s por registro)
        # time.sleep(1)


if __name__ == "__main__":
    import os
    print("=== ESP32 Simulado Iniciado ===")
    simulacion_esp32()
    print("=== Simulación completada ===")
