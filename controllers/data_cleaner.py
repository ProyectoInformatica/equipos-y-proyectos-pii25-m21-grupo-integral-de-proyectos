import json
import os
import time

# Ruta dinámica a la carpeta data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

MAX_RECORDS = 24  # Mantenemos las últimas 24 lecturas (ej. 24 horas si es 1 por hora, o ajustar según frecuencia)

# Lista de archivos que queremos mantener limpios
FILES_TO_CLEAN = [
    "envtemperatura.json",
    "envhumedad.json",
    "envcalidadaire.json",
    "envviento.json",
    "envhumo.json"
]

def clean_file(filename):
    filepath = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(filepath):
        return

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            count = len(data)
            if count > MAX_RECORDS:
                # Cortar la lista para dejar solo los últimos MAX_RECORDS
                cleaned_data = data[-MAX_RECORDS:]
                
                with open(filepath, 'w') as f:
                    json.dump(cleaned_data, f, indent=4)
                
                # print(f"[LIMPIEZA] {filename}: {count} -> {len(cleaned_data)} registros.")
    except Exception as e:
        print(f"[Error Limpieza] {filename}: {e}")

def main():
    print("--- Servicio de Limpieza de Datos (Controller) Iniciado ---")
    while True:
        for file in FILES_TO_CLEAN:
            clean_file(file)
        time.sleep(10) # Revisa cada 10 segundos

if __name__ == "__main__":
    main()