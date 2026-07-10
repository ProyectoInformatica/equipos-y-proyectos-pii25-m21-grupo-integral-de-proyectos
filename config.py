"""
Configuracion del Sistema — Entorno real con ESP32.
"""
import os

# Configuracion MySQL
MYSQL_HOST     = "localhost"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = "rootpassword"
MYSQL_DB       = "smart_residencial"

# Configuracion ESP32
# El ESP32 se conecta directamente a MySQL via TCP (conexion nativa).
# Ajusta DB_IP en el firmware (ESP32.ino) con la IP de este ordenador.

# -- Puente HTTP (alternativa si el ESP32 no puede conectar a MySQL directo) --
BRIDGE_HOST   = "0.0.0.0"
BRIDGE_PORT   = 8765
ESP32_API_KEY = "cambia-esta-clave"

# Mapeo de sensores ESP32
# Id_Tipo en BD -> nombre
ESP32_SENSOR_MAP = {
    1: "Temperatura",
    2: "Humedad",
    3: "Luminosidad",
    4: "Gas",
    5: "Viento",
}

# id_Barrera en BD -> clave interna Python
ESP32_BARRERA_MAP = {
    1: "entrada-norte",
    2: "salida-norte",
    3: "entrada-sur",
    4: "salida-sur",
}

# Otras opciones
DB_PATH    = os.path.join(os.path.dirname(__file__), "data", "sistema.db")
DEBUG_MODE = True
