"""
Módulo de Base de Datos MySQL
Reescribe las llamadas originales de SQLite para hacer interface con la base de datos de Script-Smart Residencial.sql
Protección añadida: Try/Finally para salvaguardar el agotamiento del pool de conexiones MySQL.
"""
import mysql.connector
from mysql.connector import pooling
import os
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
import time

from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

_pool = None

_pool_name = "mypool_" + str(os.getpid())

def get_connection():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name=_pool_name,
            pool_size=3,  # Reducido de 15 a 3: al haber 15 subprocesos, 15x15=225 conexiones tiran el server.
            pool_reset_session=True,
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
    return _pool.get_connection()

def init_database(conn=None):
    pass

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def is_password_hashed(password_hash: str) -> bool:
    return len(password_hash) == 64

# ==================== SENSORES (Tipos & Sensores) ====================

# Alias: los nombres cortos del código Python apuntan a los nombres
# canónicos que el ESP32 escribe directamente en la BD.
_SENSOR_ALIASES: Dict[str, str] = {
    "temp":            "Temperatura",
    "hum":             "Humedad",
    "iaq":             "Gas",
    "humo":            "Gas",
    "luz":             "Luminosidad",
    "viento":          "Viento",
    "sensor_ordinario": "Viento",  
    "water":           "Flujo de Agua",
    "power":           "Potencia",
}

def _resolve_tipo(nombre: str) -> str:
    """Devuelve el nombre canónico de un tipo de sensor."""
    return _SENSOR_ALIASES.get(nombre, nombre)


def _get_or_create_tipo(nombre_tipo: str) -> int:
    nombre_tipo = _resolve_tipo(nombre_tipo)
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Id_Tipos FROM Tipos WHERE Nombre = %s AND Activo = 1", (nombre_tipo,))
        row = cursor.fetchone()
        if row:
            return row['Id_Tipos']
        cursor.execute("INSERT INTO Tipos (Nombre, Activo) VALUES (%s, 1)", (nombre_tipo,))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def add_sensor_data(sensor_type: str, value: float, category: str = 'sensor'):
    id_tipo = _get_or_create_tipo(sensor_type)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Sensores (Valor, Fecha, Id_Tipo, Activo) VALUES (%s, NOW(), %s, 1)", (value, id_tipo))
        conn.commit()
    finally:
        conn.close()

def get_sensor_data(sensor_type: str, limit: int = 24, category: str = 'sensor') -> List[Dict]:
    nombre = _resolve_tipo(sensor_type)
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT s.Valor as value, s.Fecha as hora
            FROM Sensores s
            JOIN Tipos t ON s.Id_Tipo = t.Id_Tipos
            WHERE t.Nombre = %s AND s.Activo = 1
            ORDER BY s.Fecha DESC LIMIT {int(limit)}
        """, (nombre,))
        rows = cursor.fetchall()
        return [{"value": r["value"], "hora": str(r["hora"])} for r in rows]
    finally:
        conn.close()

def get_latest_sensor_value(sensor_type: str, category: str = 'sensor') -> float:
    data = get_sensor_data(sensor_type, limit=1, category=category)
    return float(data[0]["value"]) if data else 0.0

# ==================== FUNCS RECURSOS ====================
def add_resource_data(resource_type: str, value: float):
    add_sensor_data(resource_type, value, category='resource')

def get_resource_data(resource_type: str, limit: int = 24) -> List[Dict]:
    return get_sensor_data(resource_type, limit, category='resource')

def get_latest_resource_value(resource_type: str) -> float:
    return get_latest_sensor_value(resource_type, category='resource')

# ==================== PULSÓMETRO ====================
# El pulsómetro guarda TRES valores por lectura que forman una sola medición:
#   - frecuencia_cardiaca -> pulsaciones por minuto (ppm)
#   - presion_sistolica   -> presión máxima al latir, en mm Hg
#   - presion_diastolica  -> presión entre latidos, en mm Hg


def add_pulsometro_data(frecuencia_cardiaca: int, presion_sistolica: int, presion_diastolica: int) -> int:
    """Inserta una nueva lectura del pulsómetro y devuelve su Id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Pulsometro
                (Frecuencia_Cardiaca, Presion_Sistolica, Presion_Diastolica, Fecha, Activo)
            VALUES (%s, %s, %s, NOW(), 1)
            """,
            (int(frecuencia_cardiaca), int(presion_sistolica), int(presion_diastolica)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_pulsometro_data(limit: int = 24) -> List[Dict]:
    """Devuelve las últimas lecturas del pulsómetro (más recientes primero)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT Id_Pulsometro as id,
                   Frecuencia_Cardiaca as frecuencia_cardiaca,
                   Presion_Sistolica as presion_sistolica,
                   Presion_Diastolica as presion_diastolica,
                   Fecha as hora
            FROM Pulsometro
            WHERE Activo = 1
            ORDER BY Fecha DESC LIMIT {int(limit)}
        """)
        rows = cursor.fetchall()
        for r in rows:
            r['hora'] = str(r['hora'])
        return rows
    finally:
        conn.close()

def get_latest_pulsometro() -> Optional[Dict]:
    """Devuelve la última lectura del pulsómetro, o None si no hay datos."""
    data = get_pulsometro_data(limit=1)
    return data[0] if data else None

def update_pulsometro_data(id_pulsometro: int, frecuencia_cardiaca: int = None,
                           presion_sistolica: int = None, presion_diastolica: int = None) -> bool:
    """Actualiza los campos indicados de una lectura existente del pulsómetro.

    Solo modifica los valores que se pasen (los None se ignoran). Devuelve True
    si se actualizó alguna fila.
    """
    campos = []
    valores = []
    if frecuencia_cardiaca is not None:
        campos.append("Frecuencia_Cardiaca = %s")
        valores.append(int(frecuencia_cardiaca))
    if presion_sistolica is not None:
        campos.append("Presion_Sistolica = %s")
        valores.append(int(presion_sistolica))
    if presion_diastolica is not None:
        campos.append("Presion_Diastolica = %s")
        valores.append(int(presion_diastolica))

    if not campos:
        return False

    valores.append(int(id_pulsometro))
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE Pulsometro SET {', '.join(campos)} WHERE Id_Pulsometro = %s",
            tuple(valores),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# ==================== ACCESOS ====================
# Claves internas → Ubicacion en BD
_BARRERA_MAP = {
    "entrada-norte": "Norte-Entrada",
    "salida-norte":  "Norte-Salida",
    "entrada-sur":   "Sur-Entrada",
    "salida-sur":    "Sur-Salida",
}
_BARRERA_MAP_INV = {v: k for k, v in _BARRERA_MAP.items()}
ALL_BARRERAS = list(_BARRERA_MAP.keys())

def _get_barrera_id(ubicacion: str) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        nombre_real = _BARRERA_MAP.get(ubicacion.lower(), ubicacion)
        cursor.execute("SELECT id_Barrera FROM Barreras WHERE Ubicacion = %s AND Activo = 1", (nombre_real,))
        row = cursor.fetchone()
        if row:
            return row['id_Barrera']
        cursor.execute("INSERT INTO Barreras (Estado, Control, Ubicacion, Activo) VALUES ('cerrada', 'automatico', %s, 1)", (nombre_real,))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def set_access_state(barrera: str, barrera_abierta: bool, mensaje: str, distancia_detectada: float = None):
    b_id = _get_barrera_id(barrera)
    estado = 'abierta' if barrera_abierta else 'cerrada'
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Barreras SET Estado = %s WHERE id_Barrera = %s", (estado, b_id))
        conn.commit()
    finally:
        conn.close()

def get_access_state(barrera: str = None) -> Dict:
    if barrera:
        b_id = _get_barrera_id(barrera)
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Estado FROM Barreras WHERE id_Barrera = %s", (b_id,))
            row = cursor.fetchone()
            st = row['Estado'] if row else 'cerrada'
        finally:
            conn.close()
        return {"barrera_abierta": (st == 'abierta'), "mensaje": f"BARRERA {st.upper()}", "distancia_detectada": None}
    else:
        res = {}
        for b in ALL_BARRERAS:
            res[b] = get_access_state(b)
        return res

def set_access_manual_state(barrera: str, modo_manual: bool, abrir: bool):
    b_id = _get_barrera_id(barrera)
    control = 'manual' if modo_manual else 'automatico'
    estado = 'abierta' if abrir else 'cerrada'
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Barreras SET Control = %s, Estado = IF(%s=1, %s, Estado) WHERE id_Barrera = %s",
                       (control, modo_manual, estado, b_id))
        conn.commit()
    finally:
        conn.close()

def get_access_manual_state(barrera: str = None) -> Dict:
    if barrera:
        b_id = _get_barrera_id(barrera)
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Control, Estado FROM Barreras WHERE id_Barrera = %s", (b_id,))
            row = cursor.fetchone()
            if row:
                return {"modo_manual": row['Control'] == 'manual', "abrir": row['Estado'] == 'abierta'}
            return {"modo_manual": False, "abrir": False}
        finally:
            conn.close()
    else:
        res = {}
        for b in ALL_BARRERAS:
            res[b] = get_access_manual_state(b)
        return res

def add_access_log(barrera: str, tipo: str, evento: str = "Acceso Permitido"):
    b_id = _get_barrera_id(barrera)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Historial_Barreras (Fecha, Control, id_Barrera) VALUES (NOW(), %s, %s)", (f"{evento} - {tipo}", b_id))
        conn.commit()
    finally:
        conn.close()

def get_access_log(limit: int = 20) -> List[Dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT h.Fecha as hora, h.Control as evento, '' as tipo, b.Ubicacion as barrera
            FROM Historial_Barreras h
            JOIN Barreras b ON h.id_Barrera = b.id_Barrera
            ORDER BY h.Fecha DESC LIMIT {int(limit)}
        """)
        rows = cursor.fetchall()
        res = []
        for r in rows:
            r['hora'] = str(r['hora'])
            parts = r['evento'].split(' - ', 1)
            if len(parts) == 2:
                r['evento'], r['tipo'] = parts[0], parts[1]
            r['barrera'] = _BARRERA_MAP_INV.get(r['barrera'], r['barrera'])
            res.append(r)
        return res
    finally:
        conn.close()

# ==================== ILUMINACION ====================
def set_light_state(estado: str, intensidad: int = 0, modo: str = "AUTOMATICO"):
    c = 'encendido' if estado == 'on' else 'apagado'
    if modo == 'AUTOMATICO': c = 'automatico'
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Conf_Luminosidad WHERE id = 1")
        if cursor.fetchone():
            cursor.execute("UPDATE Conf_Luminosidad SET Control = %s WHERE id = 1", (c,))
        else:
            cursor.execute("INSERT INTO Conf_Luminosidad (id, Control) VALUES (1, %s)", (c,))
        conn.commit()
    finally:
        conn.close()

def get_light_state() -> Dict:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Control FROM Conf_Luminosidad WHERE id = 1")
        row = cursor.fetchone()
        if row:
            c = row['Control']
            return {
                "estado": "on" if c == "encendido" else "off",
                "intensidad": 100 if c == "encendido" else 0,
                "modo": "AUTOMATICO" if c == "automatico" else "MANUAL"
            }
        return {"estado": "off", "intensidad": 0, "modo": "AUTOMATICO"}
    finally:
        conn.close()

def set_light_manual_state(state: str):
    set_light_state(state.lower(), 100 if state.lower() == "on" else 0, "MANUAL")

def get_light_manual_state() -> str:
    return get_light_state()["estado"]

def set_light_sensor(luminosity: float):
    add_sensor_data('Luminosidad', luminosity, category='light')

def get_light_sensor() -> Dict:
    v = get_latest_sensor_value('Luminosidad', category='light')
    return {"luminosity": v, "value": v}

# ==================== NOTIFICACIONES ====================
def add_notification(titulo: str, mensaje: str, nivel: str = "crítico"):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Notificaciones (Fecha, Dato, Titulo, Id_Sensor, Activo) VALUES (NOW(), 0, %s, 1, 1)", (f"[{nivel.upper()}] {titulo} - {mensaje}",))
        conn.commit()
    finally:
        conn.close()

def get_notifications(limit: int = 50) -> List[Dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT Fecha as hora, Titulo as mensaje, 'crítico' as nivel, '' as titulo FROM Notificaciones WHERE Activo = 1 ORDER BY Fecha DESC LIMIT {int(limit)}")
        rows = cursor.fetchall()
        for row in rows:
            row['hora'] = str(row['hora'])
            if "]" in row['mensaje']:
                s = row['mensaje'].split("]", 1)
                row['nivel'] = s[0].replace("[","").lower()
                idx = s[1].find(" - ")
                if idx != -1:
                    row['titulo'] = s[1][:idx].strip()
                    row['mensaje'] = s[1][idx+3:].strip()
                else:
                    row['titulo'] = s[1].strip()
            else:
                # Caso para notificaciones originales del script SQL
                row['titulo'] = row['mensaje']
                row['mensaje'] = ""
        return rows
    finally:
        conn.close()

def clear_notifications():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Notificaciones SET Activo = 0")
        conn.commit()
    finally:
        conn.close()

# ==================== CONFIGURACION ====================
def set_alert_config(key: str, value: float):
    id_tipo = _get_or_create_tipo(f"Conf_Alerta_{key}")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Conf_Alertas WHERE Id_Tipo = %s", (id_tipo,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE Conf_Alertas SET Valor = %s WHERE Id_Tipo = %s", (value, id_tipo))
        else:
            cursor.execute("INSERT INTO Conf_Alertas (Valor, Id_Tipo, Activo) VALUES (%s, %s, 1)", (value, id_tipo))
        conn.commit()
    finally:
        conn.close()

def get_alert_config() -> Dict[str, float]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.Nombre, c.Valor FROM Conf_Alertas c 
            JOIN Tipos t ON c.Id_Tipo = t.Id_Tipos 
            WHERE t.Nombre LIKE 'Conf_Alerta_%' AND c.Activo = 1
        """)
        rows = cursor.fetchall()
        res = {"temp_max": 35, "hum_min": 30, "hum_max": 70, "iaq_max": 100, "humo_max": 25, "viento_max": 50}
        for row in rows:
            k = row['Nombre'].replace("Conf_Alerta_", "")
            res[k] = float(row['Valor'])
        return res
    finally:
        conn.close()

def set_schedule(hora_inicio: int, minuto_inicio: int, hora_fin: int, minuto_fin: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Conf_Luminosidad WHERE id = 1")
        if cursor.fetchone():
            cursor.execute("""
                UPDATE Conf_Luminosidad SET 
                Hora_Inicial = %s, Minuto_Inicial = %s, Hora_Final = %s, Minuto_Final = %s 
                WHERE id = 1
            """, (hora_inicio, minuto_inicio, hora_fin, minuto_fin))
        else:
            cursor.execute("""
                INSERT INTO Conf_Luminosidad (id, Hora_Inicial, Minuto_Inicial, Hora_Final, Minuto_Final)
                VALUES (1, %s, %s, %s, %s)
            """, (hora_inicio, minuto_inicio, hora_fin, minuto_fin))
        conn.commit()
    finally:
        conn.close()

def get_schedule() -> Dict:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Hora_Inicial, Minuto_Inicial, Hora_Final, Minuto_Final FROM Conf_Luminosidad WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return {
                "hora_inicio": row['Hora_Inicial'],
                "minuto_inicio": row['Minuto_Inicial'],
                "hora_fin": row['Hora_Final'],
                "minuto_fin": row['Minuto_Final']
            }
        return {"hora_inicio": 0, "minuto_inicio": 0, "hora_fin": 0, "minuto_fin": 0}
    finally:
        conn.close()

def set_light_config(key: str, value: str):
    add_sensor_data(f"Conf_Light_{key}", 1.0 if value == 'true' else 0.0)

def get_light_config(key: str = None) -> Dict[str, str]:
    if key: return {key: str(get_latest_sensor_value(f"Conf_Light_{key}"))}
    return {}

# ==================== USUARIOS / AUTENTICACION ====================
def get_user(username: str, password: str) -> Optional[Dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.Id_User as id, u.Email as username, u.Nombre, r.Nombre as rol_nombre, u.Foto as avatar
            FROM Usuarios u
            JOIN Roles r ON u.Id_Rol = r.Id_Rol
            WHERE u.Email = %s AND u.Contrasena = SHA2(%s, 256) AND u.Activo = 1
        """, (username, password))
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("""
                SELECT u.Id_User as id, u.Email as username, u.Nombre, r.Nombre as rol_nombre, u.Foto as avatar
                FROM Usuarios u
                JOIN Roles r ON u.Id_Rol = r.Id_Rol
                WHERE u.Email = %s AND u.Contrasena = %s AND u.Activo = 1
            """, (username, password))
            row = cursor.fetchone()
            
        if row:
            rol_map = {'Administrador': 'admin', 'Operador': 'tecnico', 'Invitado': 'cliente'}
            return {
                "id": row["id"],
                "username": row["username"],
                "password": "", 
                "role": rol_map.get(row["rol_nombre"], "cliente"),
                "name": row["Nombre"],
                "avatar": row["avatar"]
            }
        return None
    finally:
        conn.close()

def get_all_users() -> List[Dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.Id_User as id, u.Email as username, u.Nombre as name, r.Nombre as rol_nombre
            FROM Usuarios u
            JOIN Roles r ON u.Id_Rol = r.Id_Rol
            WHERE u.Activo = 1
        """)
        rows = cursor.fetchall()
        rol_map = {'Administrador': 'admin', 'Operador': 'tecnico', 'Invitado': 'cliente'}
        for r in rows:
            r['role'] = rol_map.get(r['rol_nombre'], "cliente")
        return rows
    finally:
        conn.close()

def create_user(username: str, password: str, role: str, name: str) -> tuple:
    map_roles_nombres = {'admin': 'Administrador', 'tecnico': 'Operador', 'cliente': 'Invitado'}
    rol_nombre = map_roles_nombres.get(role, 'Invitado')
    
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Id_Rol FROM Roles WHERE Nombre = %s", (rol_nombre,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO Roles (Nombre, Activo) VALUES (%s, 1)", (rol_nombre,))
            id_rol = cursor.lastrowid
        else:
            id_rol = row['Id_Rol']
            
        try:
            cursor.execute("""
                INSERT INTO Usuarios (Nombre, Email, Contrasena, Id_Rol, Activo, Fecha_Alta)
                VALUES (%s, %s, SHA2(%s, 256), %s, 1, NOW())
            """, (name, username, password, id_rol))
            conn.commit()
            return (True, "Usuario creado exitosamente")
        except Exception as e:
            conn.rollback()
            return (False, f"Error BD: Verifica que el email '{username}' no exista ya o sea válido. Detalle: {e}")
    finally:
        conn.close()

# ==================== PETICIONES DE CLIENTES ====================
def create_client_request(usuario_id: int, titulo: str, descripcion: str) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Conversacion (Titulo, Fecha, Activo) VALUES (%s, NOW(), 1)", (f"Petición: {titulo}",))
        id_conv = cursor.lastrowid
        cursor.execute("INSERT INTO Participantes (Id_User, Id_Conversacion, Fecha_Union, Activo) VALUES (%s, %s, NOW(), 1)", (usuario_id, id_conv))
        cursor.execute("INSERT INTO Mensajes (Id_User, Descripcion, Fecha, Id_Conversacion, Activo) VALUES (%s, %s, NOW(), %s, 1)", (usuario_id, descripcion, id_conv))
        conn.commit()
        return id_conv
    finally:
        conn.close()

def _parse_peticion_estado(rows: List[Dict]) -> List[Dict]:
    for row in rows:
        row['timestamp'] = str(row['timestamp'])
        t = row['titulo']
        row['estado'] = "Pendiente"
        if t.startswith("["):
            idx = t.find("]")
            if idx != -1:
                row['estado'] = t[1:idx]
                row['titulo'] = t[idx+1:].strip()
    return rows

def get_client_requests(usuario_id: int) -> List[Dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.Id_Conversacion as id, c.Titulo as titulo, m.Descripcion as descripcion, m.Fecha as timestamp
            FROM Conversacion c
            JOIN Mensajes m ON c.Id_Conversacion = m.Id_Conversacion
            JOIN Participantes p ON c.Id_Conversacion = p.Id_Conversacion
            WHERE p.Id_User = %s AND c.Activo = 1 AND (c.Titulo LIKE 'Petición:%%' OR c.Titulo LIKE '[%%Petición:%%')
            ORDER BY c.Fecha DESC
        """, (usuario_id,))
        rows = cursor.fetchall()
        return _parse_peticion_estado(rows)
    finally:
        conn.close()

def get_all_client_requests() -> List[Dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.Id_Conversacion as id, c.Titulo as titulo, m.Descripcion as descripcion, m.Fecha as timestamp, u.Email as usuario, u.Nombre as nombre_usuario
            FROM Conversacion c
            JOIN Mensajes m ON c.Id_Conversacion = m.Id_Conversacion
            JOIN Usuarios u ON m.Id_User = u.Id_User
            WHERE c.Activo = 1 AND (c.Titulo LIKE 'Petición:%%' OR c.Titulo LIKE '[%%Petición:%%')
            ORDER BY c.Fecha DESC
        """)
        rows = cursor.fetchall()
        seen = set()
        res = []
        for r in rows:
            if r['id'] not in seen:
                seen.add(r['id'])
                res.append(r)
        return _parse_peticion_estado(res)
    finally:
        conn.close()

def update_request_status(request_id: int, nuevo_estado: str) -> bool:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Titulo FROM Conversacion WHERE Id_Conversacion = %s", (request_id,))
        row = cursor.fetchone()
        if not row: return False
        
        titulo_actual = row['Titulo']
        import re
        titulo_limpio = re.sub(r"^\[.*?\]\s*", "", titulo_actual)
        
        if nuevo_estado.lower() == "pendiente":
            nuevo_titulo = titulo_limpio
        else:
            nuevo_titulo = f"[{nuevo_estado}] {titulo_limpio}"
            
        cursor.execute("UPDATE Conversacion SET Titulo = %s WHERE Id_Conversacion = %s", (nuevo_titulo, request_id))
        conn.commit()
        return True
    finally:
        conn.close()

def clean_sensor_data(sensor_type: str, max_records: int = 24, category: str = 'sensor'):
    pass

def clean_resource_data(resource_type: str, max_records: int = 24):
    pass
