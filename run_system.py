import subprocess
import time
import sys
import os
from config import MODO_SIMULACION, ESP32_USE_WIFI

# Definir la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SENSORES_DIR = os.path.join(BASE_DIR, "sensores")

def build_process_list():
    """Selecciona procesos según simulación vs ESP32 real."""
    common_controllers = [
        "controllers/usage_analyzer.py",
        "controllers/alarm_control.py",
        "controllers/scheduler.py",
        "controllers/data_cleaner.py",
        "controllers/access_control.py",
    ]

    if MODO_SIMULACION:
        simulated_sensors = [
            "ldr_read.py",
            "env_read.py",
            "smoke_sensor.py",
            "wind_sensor.py",
            "distance_sensor.py",
            "flow_sensor.py",
            "power_sensor.py",
        ]
        return simulated_sensors + common_controllers

    # Modo real: nunca lanzar sensores simulados
    if ESP32_USE_WIFI:
        bridge = ["wifi_bridge.py"]
    else:
        bridge = ["serial_bridge.py"]

    return bridge + common_controllers

procesos = []

def iniciar_sensores():
    print(f"Iniciando Sistema Residencial Inteligente")
    print(f"Directorio base: {BASE_DIR}")
    scripts = build_process_list()
    print(f"Modo simulación: {MODO_SIMULACION} | Puente WiFi: {ESP32_USE_WIFI}")
    
    # 1. Iniciar cada script en un proceso independiente
    for script in scripts:
        # Detectar si es ruta relativa (controllers/...) o sensor directo
        if "/" in script or "\\" in script:
             ruta_script = os.path.join(BASE_DIR, script)
        else:
             ruta_script = os.path.join(SENSORES_DIR, script)
             # Archivos de puente viven en raíz
             if script in ("serial_bridge.py", "wifi_bridge.py"):
                 ruta_script = os.path.join(BASE_DIR, script)

        if os.path.exists(ruta_script):
            try:
                p = subprocess.Popen([sys.executable, ruta_script])
                procesos.append(p)
                print(f"Iniciado: {script}")
            except Exception as e:
                print(f"Falló al iniciar {script}: {e}")
        else:
            print(f"No encontrado: {ruta_script}")

    # 2. Iniciar la Interfaz Gráfica (Flet)
    print("Iniciando Interfaz Gráfica")
    ruta_app = os.path.join(BASE_DIR, "app.py")
    try:
        subprocess.run([sys.executable, ruta_app])
    except KeyboardInterrupt:
        print("\nCierre manual detectado.")
    finally:
        cerrar_todo()

def cerrar_todo():
    print("\nCerrando procesos...")
    for p in procesos:
        try:
            p.terminate()
        except:
            pass
    print("Sistema apagado correctamente.")

if __name__ == "__main__":
    iniciar_sensores()