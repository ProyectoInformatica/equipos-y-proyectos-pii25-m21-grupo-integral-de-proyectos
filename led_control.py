# led_control.py
import json
import os

# Ruta absoluta al directorio donde está este archivo.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIGHT_FILE = os.path.join(BASE_DIR, "light.json")

def read_luminosity_from_json(file_path=LIGHT_FILE):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get("luminosity", None)
    except:
        return None

def control_led(umbral, json_path=LIGHT_FILE):
    luminosidad = read_luminosity_from_json(json_path)

    if luminosidad is None:
        return None, "error"

    if luminosidad >= umbral:
        return luminosidad, "off"   # es de día
    else:
        return luminosidad, "on"    # es de noche
