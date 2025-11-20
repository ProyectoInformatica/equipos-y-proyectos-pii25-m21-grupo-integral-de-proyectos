import json
import os
import time

# Máximo establecido en 10 registros para probar si borra correctamente
MAX_RECORDS = 10 
HISTORY_FILES = ['history_wind.json'] 

def clean_file(filename):
    if not os.path.exists(filename):
        print(f"Esperando a que se cree {filename}...")
        return

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            count = len(data)
            if count > MAX_RECORDS:
                # Cortar la lista para dejar solo los últimos 10
                cleaned_data = data[-MAX_RECORDS:]
                
                with open(filename, 'w') as f:
                    json.dump(cleaned_data, f, indent=4)
                
                print(f"LIMPIEZA: Se borraron {count - len(cleaned_data)} registros antiguos en {filename}.")
            else:
                print(f"El archivo {filename} tiene {count} registros (Límite: {MAX_RECORDS}). No se limpia todavía.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("Iniciando servicio de limpieza...")
    while True:
        for file in HISTORY_FILES:
            clean_file(file)
        time.sleep(5) # Revisa cada 5 segundos

if __name__ == "__main__":
    main()