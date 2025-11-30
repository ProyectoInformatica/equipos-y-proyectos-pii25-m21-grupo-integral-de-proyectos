import subprocess
import sys
import time
import os

# Definimos las rutas correctas
scripts_to_run = [
    # Sprint 1 y 2
    os.path.join("sensores", "ldr_read.py"),
    os.path.join("sensores", "env_read.py"),
    os.path.join("sensores", "wind_sensor.py"),
    os.path.join("sensores", "smoke_sensor.py"),
    os.path.join("controllers", "alarm_control.py"),
    os.path.join("controllers", "data_cleaner.py"),
    os.path.join("controllers", "scheduler.py"),
    
    # Sprint 3 
    os.path.join("sensores", "distance_sensor.py"),
    os.path.join("sensores", "flow_sensor.py"),
    os.path.join("controllers", "access_control.py"),
    os.path.join("controllers", "resource_monitor.py")
]

procesos = []

def main():
    print("GIP: Sistema Smart Residential (Sprint 3)")

    try:
        for script in scripts_to_run:
            if os.path.exists(script):
                print(f"   [+] Iniciando {script}...")
                p = subprocess.Popen([sys.executable, script])
                procesos.append(p)
            else:
                print(f"   [!] Error: No se encuentra {script}")

        print("Sistema completo corriendo en segundo plano.")
        
        time.sleep(2)

        print("Abriendo aplicación principal (main.py)...")
        subprocess.run([sys.executable, "main.py"])

    except KeyboardInterrupt:
        print("\n\nInterrupción.")

    finally:
        print("\n🧹 Cerrando sistema...")
        for p in procesos:
            try: p.terminate(); p.wait()
            except: pass
        print("Hasta luego.")

if __name__ == "__main__":
    main()