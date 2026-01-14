import json
import time
import os

STATE_FILE = 'data/access_state.json'

class BarreraMotor:
    def __init__(self):
        self.estado = "CERRADA" # CERRADA, ABRIENDO, ABIERTA, CERRANDO
        self.posicion = 0 # 0 grados (cerrada) a 90 grados (abierta)

    def actualizar_json(self):
        # 1. Leer datos existentes para no borrar información de sensores
        data = {}
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
            except: pass
        
        # 2. Actualizar solo los campos del motor
        data.update({
            "estado_barrera": self.estado,
            "angulo": self.posicion,
            "timestamp_motor": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 3. Guardar
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def abrir_barrera(self):
        if self.estado == "ABIERTA":
            return
        
        print(" Motor activado: Subiendo barrera...")
        self.estado = "ABRIENDO"
        self.actualizar_json()
        
        # Simulación de movimiento
        for angulo in range(0, 91, 15): # Pasos más grandes para ser menos lento
            self.posicion = angulo
            self.actualizar_json()
            time.sleep(0.3)
            
        self.estado = "ABIERTA"
        self.posicion = 90
        self.actualizar_json()
        print(" Barrera totalmente ABIERTA.")

    def cerrar_barrera(self):
        if self.estado == "CERRADA":
            return

        print(" Motor activado: Bajando barrera...")
        self.estado = "CERRANDO"
        self.actualizar_json()
        
        for angulo in range(90, -1, -15):
            self.posicion = angulo
            self.actualizar_json()
            time.sleep(0.3)
            
        self.estado = "CERRADA"
        self.posicion = 0
        self.actualizar_json()
        print(" Barrera totalmente CERRADA.")

if __name__ == "__main__":
    motor = BarreraMotor()
    motor.abrir_barrera()
    time.sleep(2)
    motor.cerrar_barrera()