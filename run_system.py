import subprocess
import time
import sys
import os

# Definir la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SENSORES_DIR = os.path.join(BASE_DIR, "sensores")

# Lista COMPLETA de scripts (Sensores + Controladores)
sensores = [
    # --- Sensores ---
    "ldr_read.py",
    "env_read.py",
    "smoke_sensor.py",
    "wind_sensor.py",
    "distance_sensor.py",
    "flow_sensor.py",
    "power_sensor.py",

    "controllers/alarm_control.py",  # Gestión de alarmas
    "controllers/scheduler.py",     # Control horario de luces
    "controllers/data_cleaner.py"    # Limpieza de datos antiguos
]

procesos = []

def iniciar_sensores():
    print(f"Iniciando Sistema Residencial Inteligente")
    print(f"Directorio base: {BASE_DIR}")
    
    # 1. Iniciar cada script en un proceso independiente
    for script in sensores:
        # Detectar si es ruta relativa (controllers/...) o sensor directo
        if "/" in script or "\\" in script:
             ruta_script = os.path.join(BASE_DIR, script)
        else:
             ruta_script = os.path.join(SENSORES_DIR, script)

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
    ruta_app = os.path.join(BASE_DIR, "main.py")
    try:
        subprocess.run([sys.executable, ruta_app])
    except KeyboardInterrupt:
        print("\nCierre manual detectado.")
    finally:
        cerrar_todo()

def cerrar_todo():
    print("\n--- Cerrando procesos... ---")
    for p in procesos:
        try:
            p.terminate()
        except:
            pass
    print("Sistema apagado correctamente.")

if __name__ == "__main__":
    iniciar_sensores()