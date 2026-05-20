"""
Configuración del Sistema
Permite cambiar entre modo SIMULACIÓN y modo REAL (ESP32)
"""
import os

# ==================== MODO DE OPERACIÓN ====================
# Cambiar a False cuando se conecte el ESP32 real
MODO_SIMULACION = True

# ==================== CONFIGURACIÓN MYSQL ====================
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "rootpassword"
MYSQL_DB = "smart_residencial"

# ==================== CONFIGURACIÓN ESP32 ====================
# Opción 1: Comunicación Serial/USB
ESP32_SERIAL_PORT = "COM3"  # Windows: COM3, COM4, etc. | Linux: /dev/ttyUSB0, /dev/ttyACM0
ESP32_BAUDRATE = 115200

# Opción 2: Comunicación WiFi (si el ESP32 tiene servidor HTTP)
ESP32_WIFI_IP = "192.168.1.100"  # IP del ESP32 en la red local
ESP32_WIFI_PORT = 80
ESP32_USE_WIFI = False  # True para usar WiFi, False para Serial

# ==================== PUENTE WIFI PYTHON <-> ESP32 ====================
# Servicio HTTP local que recibe telemetría de la ESP32 y expone comandos.
# Debe ser alcanzable por la ESP32 dentro de la misma red WiFi.
BRIDGE_HOST = "0.0.0.0"
BRIDGE_PORT = 8765

# Seguridad básica para requests HTTP entre ESP32 y puente.
# En la ESP32 envía: Header "X-API-Key: <valor>"
ESP32_API_KEY = "cambia-esta-clave"

# Identificador lógico del dispositivo (para logs/telemetría)
ESP32_DEVICE_ID = "esp32-maqueta-1"

# ==================== CONFIGURACIÓN DE SENSORES ====================
# Intervalos de lectura (en segundos)
SENSOR_READ_INTERVAL = {
    "ambiental": 5,      # Temp, Humedad, IAQ
    "viento": 5,
    "humo": 5,
    "distancia": 2,      # Sensores de acceso
    "luz": 5,           # Sensor LDR
    "agua": 2,          # Sensor de flujo
    "energia": 5        # Sensor de potencia
}

# ==================== MAPEO DE SENSORES ESP32 ====================
# Define qué pines/IDs del ESP32 corresponden a cada sensor
ESP32_SENSOR_MAP = {
    "temp": "DHT22_TEMP",      # Pin del sensor de temperatura
    "hum": "DHT22_HUM",        # Pin del sensor de humedad
    "iaq": "MQ135",            # Sensor de calidad de aire
    "viento": "ANEMOMETER",    # Sensor de viento
    "humo": "MQ2",             # Sensor de humo
    "luz": "LDR",              # Sensor de luz (LDR)
    "agua": "FLOW_SENSOR",     # Sensor de flujo de agua
    "energia": "POWER_METER",  # Medidor de energía
    "distancia_norte": "ULTRASONIC_N",  # Sensor ultrasónico barrera norte
    "distancia_sur": "ULTRASONIC_S"     # Sensor ultrasónico barrera sur
}

# ==================== CONFIGURACIÓN DE BASE DE DATOS ====================
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sistema.db")

# ==================== LOGGING ====================
DEBUG_MODE = True  # Activa mensajes de depuración
