import time
import random
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import get_light_state, get_light_manual_state, add_resource_data

# Configuración de consumo
CONSUMO_BASE = 2000  # Consumo residual (servidores, sensores, standby)
CONSUMO_LUCES_MAX = 5000  # Consumo máximo de las farolas cuando están al 100%
CONSUMO_PICO_AGUA = 1500  # Consumo adicional cuando se activa bomba de agua

def leer_estado_luces():
    """Lee el estado real de las luces desde la base de datos."""
    # Primero verificar si hay control manual activo
    manual_state = get_light_manual_state()
    if manual_state and manual_state == "on":
        return {
            "estado": "ON",
            "intensidad": 100,
            "modo": "MANUAL"
        }
    
    # Si no hay modo manual, leer el estado automático
    state_data = get_light_state()
    estado = state_data.get("estado", "off").upper()
    intensidad = state_data.get("intensidad", 0)
    return {
        "estado": estado,
        "intensidad": intensidad if estado == "ON" else 0,
        "modo": state_data.get("modo", "AUTOMATICO")
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
    print("Sensor de Energía Iniciado")
    print("Consumo basado en estado REAL de las luces")
    
    while True:
        valor_w = leer_simulacion_potencia()
        try:
            add_resource_data("power", valor_w)
            print(f"POWER Consumo total: {valor_w} W")
        except Exception as e:
            print(f"Error guardando consumo: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    main()
