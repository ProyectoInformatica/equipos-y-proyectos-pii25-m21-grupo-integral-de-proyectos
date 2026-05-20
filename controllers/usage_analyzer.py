import time
import os
import sys

# Añadir el directorio raíz al path para importar database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from database import get_latest_resource_value, add_notification

# Configuración de detección
MAX_LECTURAS_CONTINUAS = 5  
UMBRAL_CAUDAL_FUGA = 0.5    
UMBRAL_POTENCIA_ALTA = 4000 # Watts (Umbral de alerta de consumo eléctrico)

def generar_alerta(mensaje, modulo="RECURSOS"):
    """Genera una alerta y la guarda en la base de datos"""
    nivel = "crítico" if modulo == "RECURSOS" else "advertencia"
    add_notification(f"Alerta {modulo}", mensaje, nivel)
    print(f"[ALERTA GENERADA] {mensaje}")

def main():
    print("Iniciando analizador de recursos (Agua y Energía)...")
    
    contador_flujo_continuo = 0
    contador_potencia_alta = 0
    
    while True:
        # --- ANÁLISIS DE AGUA ---
        flujo_actual = get_latest_resource_value("water")
        
        if flujo_actual > UMBRAL_CAUDAL_FUGA:
            contador_flujo_continuo += 1
        else:
            contador_flujo_continuo = 0 
            
        if contador_flujo_continuo >= MAX_LECTURAS_CONTINUAS:
            generar_alerta(f"POSIBLE FUGA DE AGUA: Flujo continuo de {flujo_actual} L/min")
            contador_flujo_continuo = 0 
            time.sleep(5) 

        # --- ANÁLISIS DE ENERGÍA (NUEVO) ---
        potencia_actual = get_latest_resource_value("power")
        
        # Si supera el umbral, incrementamos contador (para evitar picos de 1 segundo)
        if potencia_actual > UMBRAL_POTENCIA_ALTA:
            contador_potencia_alta += 1
            print(f"[AVISO] Pico de consumo detectado: {potencia_actual} W")
        else:
            contador_potencia_alta = 0

        # Si el pico dura 3 ciclos (aprox 9 segundos), generamos alerta
        if contador_potencia_alta >= 3:
             generar_alerta(f"CONSUMO ELÉCTRICO CRÍTICO: {potencia_actual} W sostenidos", "ENERGIA")
             contador_potencia_alta = 0
             time.sleep(5)

        time.sleep(3) 

if __name__ == "__main__":
    main()