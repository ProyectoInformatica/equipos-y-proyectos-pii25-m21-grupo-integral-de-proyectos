import json
import time
import os

# Rutas de archivos (ajustar según tu estructura)
SENSOR_FILE = 'data/light.json'
STATE_FILE = 'data/light_state.json' # Archivo que guardará el estado real (ON/OFF)
MANUAL_OVERRIDE_FILE = 'data/light_manual_state.json'

# Umbral de oscuridad (0-100, donde menor valor es más oscuro)
UMBRAL_LUZ = 40 

def leer_json(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def guardar_estado(estado, intensidad):
    datos = {
        "estado": estado,  # "ON" o "OFF"
        "intensidad": intensidad,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "modo": "AUTOMATICO"
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(datos, f, indent=4)
    print(f"--> [AUTO] Luces {estado} (Intensidad: {intensidad}%)")

def main():
    print("Iniciando sistema automático de iluminación...")
    while True:
        # 1. Leer sensor LDR
        sensor_data = leer_json(SENSOR_FILE)
        
        # 2. Leer si hay control manual activo (Prioridad al admin)
        manual_data = leer_json(MANUAL_OVERRIDE_FILE)
        
        if manual_data and manual_data.get("manual_mode", False):
            print(f"[INFO] Modo MANUAL activo. Ignorando sensor.")
            # Aquí el led_control_manual.py es el que manda
            time.sleep(5)
            continue

        # 3. Lógica automática
        if sensor_data:
            luz_actual = sensor_data.get("value", 100) # Default a mucha luz
            
            if luz_actual < UMBRAL_LUZ:
                # Está oscuro -> Encender
                # Calculamos intensidad inversa: más oscuro = más luz
                intensidad = min(100, (100 - luz_actual) * 1.5) 
                guardar_estado("ON", int(intensidad))
            else:
                # Hay luz -> Apagar
                guardar_estado("OFF", 0)
        else:
            print("[WARN] No se pueden leer datos del sensor LDR.")

        time.sleep(5) # Revisar cada 5 segundos

if __name__ == "__main__":
    main()