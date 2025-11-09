"""
ldr_read.py
Módulo para manejar la lectura de un sensor de luminosidad (LDR) desde un ESP32
vía puerto serie. También soporta un modo "simulado" si el ESP32 no está conectado,
de forma que el módulo no falle si se ejecuta en un equipo sin hardware.

Estructura del JSON usado:
    lights.json -> { "iluminosidad": <int> }

Requisitos:
    - Python 3.x
    - pyserial (opcional, necesario si quieres conectar a un ESP32 real)
      Instalar: pip install pyserial

Diseño:
    - Este fichero NO ejecuta nada al importarlo (main vacío).
    - Funciones principales:
        conectar_esp32(puerto, baudrate) -> intenta devolver objeto serial o None
        obtener_iluminacion(esp32) -> intenta leer del ESP32; si falla, usa simulado
        leer_iluminacion() / guardar_iluminacion(valor) -> interaccion con lights.json

Protocolo esperado con el ESP32:
    - Al enviar el comando "READ_LDR\n" por serie, el ESP32 responde con una línea
      que contiene un número entero (por ejemplo: "37\n").
    - Si el ESP32 usa otro protocolo, adapta 'obtener_iluminacion' a lo que envíe.
"""

import json
import time
import random

# Intentamos importar pyserial. Si no está instalado, seguiremos en modo simulado.
# No hacemos 'from serial import Serial' porque queremos capturar el error si falta.
try:
    import serial  # type: ignore
except Exception:
    serial = None  # marcar que la librería no está disponible

# Nombre del fichero JSON donde vamos a guardar/leer la última lectura.
# Se usa una estructura simple: {"iluminosidad": 37}
ARCHIVO_JSON = "lights.json"


def conectar_esp32(puerto: str = "/dev/ttyUSB0", baudrate: int = 9600, timeout: float = 2.0):
    """
    Intenta abrir un puerto serie con los parámetros dados y devuelve el objeto Serial.
    - puerto: ejemplo en Linux '/dev/ttyUSB0', en Windows 'COM3'.
    - baudrate: velocidad en baudios; debe coincidir con la del ESP32.
    - timeout: tiempo máximo de espera para lecturas en segundos.

    Si pyserial no está instalado, o no se puede abrir el puerto, devuelve None.
    Nunca lanza una excepción hacia el importador (se maneja internamente).
    """
    # Si pyserial no está disponible, informamos y devolvemos None.
    if serial is None:
        print("pyserial no instalado. Instalalo con 'pip install pyserial' si quieres conectar un ESP32.")
        return None

    try:
        print(f"Intentando conectar al ESP32 en '{puerto}' a {baudrate} baudios...")
        esp32 = serial.Serial(port=puerto, baudrate=baudrate, timeout=timeout)
        # Pequeña pausa para que el puerto tenga tiempo de estabilizar (algunos dispositivos reinician)
        time.sleep(1.0)
        if esp32.is_open:
            print("Conexión serie abierta correctamente ")
            return esp32
        else:
            # Caso raro: Serial devuelto pero no abierto
            print("El puerto serie se abrió pero no está marcado como abierto. Usando modo simulado.")
            return None
    except serial.SerialException as e:
        # Error típico al no encontrar el puerto o permiso denegado
        print(f"No se pudo abrir el puerto serie ({puerto}): {e}. Usando modo simulado.")
        return None
    except Exception as e:
        # Cualquier otra excepción (por ejemplo, permisos, dispositivo ocupado, etc.)
        print(f"Error inesperado al conectar por serie: {e}. Usando modo simulado.")
        return None


def leer_iluminacion():
    """
    Lee el valor de 'iluminosidad' desde ARCHIVO_JSON.
    - Si el fichero no existe, lo crea con valor 0 y devuelve 0.
    - Si el JSON está mal formado o falta la clave, maneja la excepción y devuelve None.
    """
    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            datos = json.load(f)
            # Usamos get para evitar KeyError si la clave no existe
            return datos.get("iluminosidad", 0)
    except FileNotFoundError:
        # Archivo no encontrado -> creamos uno nuevo con valor por defecto
        print(f"No se encontró {ARCHIVO_JSON}. Creando uno nuevo con valor 0.")
        try:
            with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
                json.dump({"iluminosidad": 0}, f, indent=4)
        except Exception as e:
            print(f"Error al crear {ARCHIVO_JSON}: {e}")
        return 0
    except json.JSONDecodeError:
        # JSON corrupto -> informar y devolver None para que el llamador sepa que hubo problema
        print(f"El archivo {ARCHIVO_JSON} contiene JSON inválido. Corrígelo manualmente.")
        return None
    except Exception as e:
        # Capturamos cualquier otro error de lectura/IO
        print(f"Error leyendo {ARCHIVO_JSON}: {e}")
        return None


def guardar_iluminacion(valor):
    """
    Guarda un valor entero de iluminacion en ARCHIVO_JSON.
    - Intenta sobreescribir el fichero. Si falla, imprime el error.
    - No devuelve nada.
    """
    try:
        with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
            json.dump({"iluminosidad": int(valor)}, f, indent=4)
    except Exception as e:
        print(f"Error guardando {ARCHIVO_JSON}: {e}")


def obtener_iluminacion(esp32=None, max_retries: int = 1):
    """
    Intenta obtener la lectura real del LDR:
    - Si 'esp32' es un objeto Serial válido, intenta comunicarse.
      Se envía el comando "READ_LDR\n" (puedes adaptar esto al firmware que uses)
      y se espera una línea con un entero.
    - Si la lectura falla por cualquier motivo (timeout, parseo, excepción),
      se vuelve al modo simulado y se genera un valor aleatorio entre 0 y 100.
    - Guarda en ARCHIVO_JSON el valor obtenido (real o simulado).

    Parámetros:
      esp32: objeto devuelto por conectar_esp32() o None
      max_retries: número de reintentos al leer del puerto serie (útil si hay ruido)

    Retorna:
      entero >= 0 con la iluminacion leída (real o simulada)
    """
    # Si no hay objeto serial, directamente usamos modo simulado
    if esp32 is None:
        valor_sim = random.randint(0, 100)
        guardar_iluminacion(valor_sim)
        return valor_sim

    # Intentamos leer del ESP32
    for intento in range(max_retries):
        try:
            # Enviamos un comando simple; adapta esto si tu firmware usa otro protocolo.
            # Nota: usamos bytes explícitos y una nueva línea para marcar el fin de comando.
            esp32.write(b"READ_LDR\n")

            # Leemos una línea completa. decode y strip para limpiar '\r\n'
            linea = esp32.readline().decode(errors="ignore").strip()

            # Si la línea está vacía -> timeout o nada recibido
            if not linea:
                # Si hay más intentos, lo intentamos de nuevo; si no, pasamos a simulado.
                if intento < max_retries - 1:
                    continue
                else:
                    print("Timeout o linea vacía desde ESP32. Usando valor simulado.")
                    valor_sim = random.randint(0, 100)
                    guardar_iluminacion(valor_sim)
                    return valor_sim

            # Intentamos convertir la línea en entero
            try:
                valor = int(linea)
                # Guardamos la lectura en el JSON
                guardar_iluminacion(valor)
                return valor
            except ValueError:
                # Línea recibida no es un entero válido
                print(f"Datos recibidos no válidos desde ESP32: '{linea}'. Usando valor simulado.")
                valor_sim = random.randint(0, 100)
                guardar_iluminacion(valor_sim)
                return valor_sim

        except Exception as e:
            # Cualquier error de E/S o comunicación con el puerto -> modo simulado
            print(f"Error comunicando con ESP32: {e}. Usando valor simulado.")
            valor_sim = random.randint(0, 100)
            guardar_iluminacion(valor_sim)
            return valor_sim

    # Si por alguna razón salimos del bucle sin retorno, devolvemos simulado
    valor_sim = random.randint(0, 100)
    guardar_iluminacion(valor_sim)
    return valor_sim


# MAIN vacío: este módulo está pensado para importarse desde otro script.
def main():
    """
    MAIN VACÍO. NO ejecutar nada aquí:
    - El script principal (por ejemplo main.py) debe importar este módulo y usar:
        esp32 = ldr_read.conectar_esp32(puerto="COM3")  # ejemplo Windows
        valor = ldr_read.obtener_iluminacion(esp32)
    - Dejar main vacío evita que el módulo haga cosas al importarlo en pruebas o tests.
    """
    pass


# Si alguien ejecuta el archivo directamente, mostramos un mensaje simple y no ejecutamos bucles.
if __name__ == "__main__":
    print("Este fichero es un módulo. Importalo desde tu main.py y usa sus funciones.")
    print("Ejemplo rápido:")
    print("  import ldr_read")
    print("  esp32 = ldr_read.conectar_esp32('/dev/ttyUSB0')")
    print("  valor = ldr_read.obtener_iluminacion(esp32)")
