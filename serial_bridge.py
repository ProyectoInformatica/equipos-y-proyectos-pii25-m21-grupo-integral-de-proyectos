import serial
import serial.tools.list_ports
import json
import time
import sys
import os

# Asegurar que importamos los controladores y base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from database import add_sensor_data, get_light_state, get_access_state

def auto_detect_esp32_port():
    """Busca inteligentemente puertos de dispositivos CP210x o CH340 comunes en ESP32"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = port.description.lower()
        if "cp210x" in desc or "ch340" in desc or "serial" in desc or "uart" in desc:
            return port.device
    
    # Fallback si no identifica por nombre, tomar el último conectado
    if ports:
        return ports[-1].device
    return None

def main():
    port_name = auto_detect_esp32_port()
    if not port_name:
        print("[SERIAL] No se detectó ninguna placa ESP32 conectada por USB.")
        sys.exit(1)
        
    print(f"[SERIAL] Conectando a placa ESP32 en puerto: {port_name}")
    
    try:
        ser = serial.Serial(port_name, 115200, timeout=1)
        time.sleep(2) # Tiempo para reiniciar tras abrir conexión
        print("[SERIAL] Conexión establecida. Escuchando...")
    except Exception as e:
        print(f"[SERIAL ERROR] No se pudo abrir {port_name}: {e}")
        sys.exit(1)

    tiempo_anterior = time.time()

    while True:
        try:
            # 1. Leer Sensores de la ESP32
            if ser.in_waiting > 0:
                linea = ser.readline().decode('utf-8').strip()
                if linea.startswith('{') and linea.endswith('}'):
                    try:
                        data = json.loads(linea)
                        
                        # Guardado en base de datos
                        if "temperatura" in data: add_sensor_data("Temperatura", float(data["temperatura"]))
                        if "humedad" in data: add_sensor_data("Humedad", float(data["humedad"]))
                        if "calidad_aire" in data: add_sensor_data("Calidad de Aire", float(data["calidad_aire"]))
                        if "humo" in data: add_sensor_data("Nivel de Humo", float(data["humo"]))
                        if "luminosidad" in data: add_sensor_data("Luminosidad", float(data["luminosidad"]))
                        if "distancia" in data: add_sensor_data("Distancia - norte", float(data["distancia"]), category="distancia")
                        if "caudal" in data: add_sensor_data("Flujo de Agua", float(data["caudal"]))
                        if "viento" in data: add_sensor_data("Velocidad de Viento", float(data["viento"]))
                        
                        print(f"[SERIAL RECIBIDO] Sensores actualizados.")
                    except json.JSONDecodeError:
                        print(f"[SERIAL] JSON inválido: {linea}")
                else:
                    # Mostrar mensajes de debug de la placa
                    print(f"[ESP32 Console] {linea}")

            # 2. Enviar Estado de Actuadores a la ESP32 (Cada 5 segundos)
            tiempo_actual = time.time()
            if tiempo_actual - tiempo_anterior > 5:
                tiempo_anterior = tiempo_actual
                
                # Leer la base de datos
                luz = get_light_state()
                encender_led = True if luz["estado"] == "on" else False
                
                acceso = get_access_state("norte")
                abrir_barrera = acceso.get("barrera_abierta", False)
                
                comando_json = json.dumps({
                    "led": encender_led,
                    "motor": abrir_barrera,
                    "ventilador": False
                })
                
                ser.write((comando_json + '\n').encode('utf-8'))
                
        except Exception as e:
            print(f"[SERIAL LOOP ERROR] {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
