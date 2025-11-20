import json
import time
import os

# Archivos de entrada (generados por otros scripts)
ENV_FILE = 'env.json'   # Debe contener: {"temperature": 25, "gas_level": 100}
WIND_FILE = 'wind.json' # Generado por wind_sensor.py

# Umbrales de seguridad, se pueden cambiar, por ahora están fijos
TEMP_MAX = 35.0       # Grados Celsius
GAS_MAX = 400         # PPM
WIND_MAX = 60.0       # km/h (Para cerrar compuertas)

# Función para cargar datos JSON de un archivo
# Devuelve None si el archivo no existe o hay error
# en la lectura
def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

# Función para verificar condiciones y generar alertas
# según los umbrales definidos
# Las alertas se imprimen en consola
# y se podrían extender para enviar emails, guardar en logs o mostrar en frontend
def check_alerts():
    alerts = []
    
    # 1. Verificar Ambientales (Temperatura y Gases)
    env_data = load_json(ENV_FILE)
    if env_data:
        temp = env_data.get('temperature', 0)
        gas = env_data.get('gas_level', 0)
        
        if temp > TEMP_MAX:
            alerts.append(f"[PELIGRO] Temperatura alta: {temp}°C")
        if gas > GAS_MAX:
            alerts.append(f"[PELIGRO] Nivel de gas tóxico: {gas} PPM")
            
    # 2. Verificar Viento 
    wind_data = load_json(WIND_FILE)
    if wind_data:
        speed = wind_data.get('speed_kmh', 0)
        if speed > WIND_MAX:
            alerts.append(f"[ALERTA] Viento fuerte: {speed} km/h - CERRAR COMPUERTAS")

    # Mostrar alertas
    if alerts:
        print("\n--- ALERTAS ACTIVAS ---")
        for alert in alerts:
            print(alert)
            # Aquí se añadira código para enviar un email o guardar en un log, etc
            # por simplicidad, de momento, solo imprimimos
    else:
        print(f"Estado normal. (Temp: {env_data.get('temperature') if env_data else '?'}°C, Viento: {wind_data.get('speed_kmh') if wind_data else '?'} km/h)")

def main():
    # Bucle principal para revisar alertas cada 5 segundos
    print("Iniciando Monitor de Alertas...")
    while True:
        check_alerts()
        time.sleep(5)

if __name__ == "__main__":
    main()