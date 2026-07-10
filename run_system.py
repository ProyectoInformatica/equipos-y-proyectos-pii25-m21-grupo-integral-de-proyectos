"""
Lanzador del sistema.
El ESP32 gestiona sensores y barreras directamente via MySQL.
Python solo arranca los controladores de monitoreo y la interfaz grafica.
"""
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Controladores Python que corren en paralelo a la app
CONTROLLERS = [
    "controllers/alarm_control.py",
    "controllers/usage_analyzer.py",
    "controllers/scheduler.py",
    "controllers/data_cleaner.py",
]

procesos = []


def iniciar():
    print("=" * 50)
    print("  Sistema Residencial Inteligente")
    print("  Modo: REAL (ESP32 + MySQL directo)")
    print("=" * 50)

    for script in CONTROLLERS:
        ruta = os.path.join(BASE_DIR, script)
        if os.path.exists(ruta):
            try:
                p = subprocess.Popen([sys.executable, ruta])
                procesos.append(p)
                print(f"  Iniciado: {script}")
            except Exception as e:
                print(f"  Error al iniciar {script}: {e}")
        else:
            print(f"  No encontrado: {ruta}")

    print("\n  Iniciando Interfaz Grafica...")
    try:
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "app.py")])
    except KeyboardInterrupt:
        print("\n  Cierre detectado.")
    finally:
        cerrar_todo()


def cerrar_todo():
    print("\n  Cerrando procesos...")
    for p in procesos:
        try:
            p.terminate()
        except:
            pass
    print("  Sistema apagado.")


if __name__ == "__main__":
    iniciar()
