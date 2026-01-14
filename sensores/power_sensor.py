import json
import time
import random
import os
from datetime import datetime

# Configuración
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "resource_power.json")
LIGHT_STATE_FILE = os.path.join(DATA_DIR, "light_state.json")
LIGHT_MANUAL_FILE = os.path.join(DATA_DIR, "light_manual_state.json")

# Configuración de consumo
CONSUMO_BASE = 2000  # Consumo residual (servidores, sensores, standby)
CONSUMO_LUCES_MAX = 5000  # Consumo máximo de las farolas cuando están al 100%
CONSUMO_PICO_AGUA = 1500  # Consumo adicional cuando se activa bomba de agua

def leer_estado_luces():
    """Lee el estado real de las luces desde los archivos de estado."""
    # Primero verificar si hay control manual activo
    manual_file = LIGHT_MANUAL_FILE
    if os.path.exists(manual_file):
        try:
            with open(manual_file, 'r') as f:
                manual_data = json.load(f)
                
                # Formato 1: {"modo_manual": True, "encender": True/False} (de map_view.py)
                if manual_data.get("modo_manual", False):
                    encender = manual_data.get("encender", False)
                    return {
                        "estado": "ON" if encender else "OFF",
                        "intensidad": 100 if encender else 0,
                        "modo": "MANUAL"
                    }
                
                # Formato 2: {"manual_mode": True} (compatibilidad con led_control.py)
                if manual_data.get("manual_mode", False):
                    # Si hay modo manual pero no especifica encender, asumir ON
                    return {
                        "estado": "ON",
                        "intensidad": 100,
                        "modo": "MANUAL"
                    }
                
                # Formato 3: {"state": "on"/"off"} (de led_control_manual.py)
                if "state" in manual_data:
                    state_str = manual_data.get("state", "off").lower()
                    encender = (state_str == "on")
                    return {
                        "estado": "ON" if encender else "OFF",
                        "intensidad": 100 if encender else 0,
                        "modo": "MANUAL"
                    }
        except Exception as e:
            print(f"Error leyendo manual_state: {e}")
    
    # Si no hay modo manual, leer el estado automático
    state_file = LIGHT_STATE_FILE
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)
                estado = state_data.get("estado", "OFF")
                intensidad = state_data.get("intensidad", 0)
                return {
                    "estado": estado,
                    "intensidad": intensidad if estado == "ON" else 0,
                    "modo": state_data.get("modo", "AUTOMATICO")
                }
        except Exception as e:
            print(f"Error leyendo light_state: {e}")
    
    # Si no se puede leer, asumir apagado
    return {
        "estado": "OFF",
        "intensidad": 0,
        "modo": "DESCONOCIDO"
    }

def leer_simulacion_potencia():
    """
    Calcula el consumo eléctrico basándose en:
    - Consumo base (siempre presente)
    - Estado real de las luces (ON/OFF e intensidad)
    - Picos aleatorios (bomba de agua, etc.)
    """
    # Consumo base (servidores, sensores, standby)
    consumo = CONSUMO_BASE + random.uniform(-100, 100)
    
    # Leer estado real de las luces
    estado_luces = leer_estado_luces()
    
    # Si las luces están encendidas, calcular consumo según intensidad
    if estado_luces["estado"] == "ON" and estado_luces["intensidad"] > 0:
        # Consumo proporcional a la intensidad
        # Si intensidad es 100%, consume CONSUMO_LUCES_MAX
        # Si intensidad es 50%, consume CONSUMO_LUCES_MAX * 0.5
        consumo_luces = CONSUMO_LUCES_MAX * (estado_luces["intensidad"] / 100)
        consumo += consumo_luces + random.uniform(-200, 200)  # Variación aleatoria
        
        print(f"[POWER] Luces {estado_luces['estado']} al {estado_luces['intensidad']}% -> +{consumo_luces:.0f}W")
    else:
        print(f"[POWER] Luces {estado_luces['estado']} -> Sin consumo adicional")
    
    # Picos aleatorios (ej. bomba de agua activada, otros equipos)
    if random.random() > 0.85:  # 15% de probabilidad
        consumo += CONSUMO_PICO_AGUA
        print(f"[POWER] Pico de consumo detectado (+{CONSUMO_PICO_AGUA}W)")

    return round(consumo, 2)

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    print("Sensor de Energía Iniciado")
    print("Consumo basado en estado REAL de las luces")
    
    historial = []
    
    while True:
        valor_w = leer_simulacion_potencia()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        registro = {
            "hora": timestamp,
            "value": valor_w,
            "unit": "W"
        }
        
        historial.append(registro)
        # Guardamos solo las últimas 50 lecturas
        if len(historial) > 50: 
            historial.pop(0)
            
        try:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(historial, f, indent=4)
            print(f"POWER Consumo total: {valor_w} W")
        except Exception as e:
            print(f"Error escribiendo JSON: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    main()
