import json
import os
import random
from datetime import datetime, timedelta

# Archivos JSON
FILE_HUMO = "envhumo.json"
FILE_GASES = "envgases.json"
FILE_VIENTO = "envviento.json"

# Horario del día simulado
HORA_INICIO = datetime.strptime("08:00", "%H:%M")
HORA_FIN = datetime.strptime("21:00", "%H:%M")

# Umbrales para emergencias
UMBRAL_HUMO_EMERGENCIA = 300       # MQ-2 (ppm)
UMBRAL_GASES_PELIGRO = 250         # MQ-135 (ppm)
UMBRAL_VIENTO_FUERTE = 45          # km/h

# ================================
#     SIMULACIÓN DE SENSORES
# ================================
def leer_mq2_humo():
    """MQ-2 -> Humo/Gas inflamable (ppm)"""
    return random.randint(50, 500)

def leer_mq135_gases():
    """MQ-135 -> Contaminantes / gases tóxicos (ppm)"""
    return random.randint(30, 400)

def leer_anemometro_viento():
    """Velocidad del viento (km/h)"""
    return round(random.uniform(5.0, 80.0), 2)

# ================================
#     GUARDAR JSON
# ================================
def cargar_o_crear(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_json(filename, registro):
    datos = cargar_o_crear(filename)
    datos.append(registro)
    with open(filename, "w") as f:
        json.dump(datos, f, indent=4)

# ================================
#     LÓGICA DE EMERGENCIAS
# ================================
def evaluar_emergencias(humo, gases, viento):
    acciones = []

    # Aviso a bomberos si MQ-2 detecta humo muy alto
    if humo >= UMBRAL_HUMO_EMERGENCIA:
        acciones.append("AVISO_A_BOMBEROS")

    # Aviso por gases tóxicos
    if gases >= UMBRAL_GASES_PELIGRO:
        acciones.append("ALERTA_GASES_TOXICOS")

    # Cerrar compuertas si viento fuerte
    if viento >= UMBRAL_VIENTO_FUERTE:
        acciones.append("CERRAR_COMPUERTAS")

    if not acciones:
        acciones.append("SIN_ALERTA")

    return acciones

# ================================
#     ESP32 SIMULADO
# ================================
def simulacion_emergencias():
    hora_actual = HORA_INICIO

    while hora_actual <= HORA_FIN:
        ts = hora_actual.strftime("%Y-%m-%d %H:%M:%S")

        # Lecturas simuladas
        humo = leer_mq2_humo()
        gases = leer_mq135_gases()
        viento = leer_anemometro_viento()

        # Guardar en JSON
        guardar_json(FILE_HUMO,  {"timestamp": ts, "humo_ppm": humo})
        guardar_json(FILE_GASES, {"timestamp": ts, "gases_ppm": gases})
        guardar_json(FILE_VIENTO, {"timestamp": ts, "viento_kmh": viento})

        # Evaluación de emergencias
        acciones = evaluar_emergencias(humo, gases, viento)

        print(f"[ESP32] {ts} → MQ2={humo}ppm | MQ135={gases}ppm | Viento={viento}km/h → {acciones}")

        # Siguiente hora
        hora_actual += timedelta(hours=1)

if __name__ == "__main__":
    print("=== Simulación de Emergencias ESP32 Iniciada ===")
    simulacion_emergencias()
    print("=== Simulación Finalizada ===")
