import json
import time
import os

# Archivos de datos
WATER_SENSOR_FILE = 'data/resource_water.json'
POWER_SENSOR_FILE = 'data/resource_power.json' # Nuevo archivo de energía
NOTIFICATIONS_FILE = 'data/notifications.json'

# Configuración de detección
MAX_LECTURAS_CONTINUAS = 5  
UMBRAL_CAUDAL_FUGA = 0.5    
UMBRAL_POTENCIA_ALTA = 4000 # Watts (Umbral de alerta de consumo eléctrico)

def leer_sensor(filepath):
    """Función genérica para leer el último valor de un JSON de sensores"""
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data[-1].get("value", 0)
            return 0
    except:
        return 0

def generar_alerta(mensaje, modulo="RECURSOS"):
    nueva_alerta = {
        "id": int(time.time()),
        "tipo": "CRITICO",
        "modulo": modulo,
        "mensaje": mensaje,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    lista_alertas = []
    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, 'r') as f:
                lista_alertas = json.load(f)
        except:
            lista_alertas = []
    
    lista_alertas.append(nueva_alerta)
    
    # Guardamos limitando a las últimas 20
    with open(NOTIFICATIONS_FILE, 'w') as f:
        json.dump(lista_alertas[-20:], f, indent=4)
    print(f"[ALERTA GENERADA] {mensaje}")

def main():
    print("Iniciando analizador de recursos (Agua y Energía)...")
    
    contador_flujo_continuo = 0
    contador_potencia_alta = 0
    
    while True:
        # --- ANÁLISIS DE AGUA ---
        flujo_actual = leer_sensor(WATER_SENSOR_FILE)
        
        if flujo_actual > UMBRAL_CAUDAL_FUGA:
            contador_flujo_continuo += 1
        else:
            contador_flujo_continuo = 0 
            
        if contador_flujo_continuo >= MAX_LECTURAS_CONTINUAS:
            generar_alerta(f"POSIBLE FUGA DE AGUA: Flujo continuo de {flujo_actual} L/min")
            contador_flujo_continuo = 0 
            time.sleep(5) 

        # --- ANÁLISIS DE ENERGÍA (NUEVO) ---
        potencia_actual = leer_sensor(POWER_SENSOR_FILE)
        
        # Si supera el umbral, incrementamos contador (para evitar picos de 1 segundo)
        if potencia_actual > UMBRAL_POTENCIA_ALTA:
            contador_potencia_alta += 1
            print(f"⚠️ Pico de consumo detectado: {potencia_actual} W")
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