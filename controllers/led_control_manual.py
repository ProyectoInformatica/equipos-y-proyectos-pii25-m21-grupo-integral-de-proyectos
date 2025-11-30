# led_control_manual.py
import json
import os

# Archivo donde guardaremos el estado manual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "light_manual_state.json")

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump({"state": state}, f)

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("state", "off")
    except:
        return "off"  # Estado por defecto

def set_light_manual(on):
    """
    Cambia el estado manual de la luz.
    on=True -> encender
    on=False -> apagar
    Retorna "on" o "off"
    """
    state = "on" if on else "off"
    save_state(state)
    return state
