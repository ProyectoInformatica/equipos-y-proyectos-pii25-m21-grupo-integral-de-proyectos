import re
from datetime import datetime, timedelta

def main():
    sql_file = "Script-Smart Residencial.sql"
    with open(sql_file, "r", encoding="utf-8") as f:
        content = f.read()

    # We need 19 users total: 5 admins (role 1), 9 operadores (role 2), 5 invitados (role 3)
    # The current file has:
    # (1, 'Ana García',   'ana@sistema.com',   SHA2('password123', 256), 1, 1, '2024-01-10 09:00:00'),
    # (2, 'Luis Martínez','luis@sistema.com',  SHA2('operador456', 256), 2, 1, '2024-02-15 10:30:00'),
    # (3, 'Carlos Ruiz',  'carlos@sistema.com',SHA2('invitado789', 256), 3, 0, '2024-03-01 08:00:00');
    
    # Let's replace the Usuarios block
    users_insert_block = """-- Usuarios (contraseña hasheada con SHA2-256: 'password123' → hash)
INSERT INTO `Usuarios` (`Id_User`, `Nombre`, `Email`, `Contrasena`, `Id_Rol`, `Activo`, `Fecha_Alta`) VALUES
  (1, 'Ana García',   'ana@sistema.com',   SHA2('password123', 256), 1, 1, '2024-01-10 09:00:00'),
  (4, 'Admin Dos',    'admin2@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-11 09:00:00'),
  (5, 'Admin Tres',   'admin3@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-12 09:00:00'),
  (6, 'Admin Cuatro', 'admin4@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-13 09:00:00'),
  (7, 'Admin Cinco',  'admin5@sistema.com',SHA2('password123', 256), 1, 1, '2024-01-14 09:00:00'),
  (2, 'Luis Martínez','luis@sistema.com',  SHA2('operador456', 256), 2, 1, '2024-02-15 10:30:00'),
  (8, 'Operador Dos', 'op2@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-16 10:30:00'),
  (9, 'Operador Tres','op3@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-17 10:30:00'),
  (10,'Operador Cua', 'op4@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-18 10:30:00'),
  (11,'Operador Cin', 'op5@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-19 10:30:00'),
  (12,'Operador Sei', 'op6@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-20 10:30:00'),
  (13,'Operador Sie', 'op7@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-21 10:30:00'),
  (14,'Operador Och', 'op8@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-22 10:30:00'),
  (15,'Operador Nue', 'op9@sistema.com',   SHA2('password123', 256), 2, 1, '2024-02-23 10:30:00'),
  (3, 'Carlos Ruiz',  'carlos@sistema.com',SHA2('invitado789', 256), 3, 1, '2024-03-01 08:00:00'),
  (16,'Invitado Dos', 'inv2@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-02 08:00:00'),
  (17,'Invitado Tre', 'inv3@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-03 08:00:00'),
  (18,'Invitado Cua', 'inv4@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-04 08:00:00'),
  (19,'Invitado Cin', 'inv5@sistema.com',  SHA2('password123', 256), 3, 1, '2024-03-05 08:00:00');"""

    content = re.sub(r"-- Usuarios.*?;\n", users_insert_block + "\n", content, flags=re.DOTALL)
    
    # 57 sensor records (3 per user as requested roughly, let's say temperature)
    # plus 20 of each other sensor
    sensores_vals = []
    base_time = datetime(2024, 6, 1, 8, 0, 0)
    for i in range(1, 60):
        t = base_time + timedelta(minutes=i*10)
        sensores_vals.append(f"({4+i}, {20+i%5}, '{t.strftime('%Y-%m-%d %H:%M:%S')}', 1, 1)")
    for i in range(1, 20):
        t = base_time + timedelta(minutes=i*15)
        sensores_vals.append(f"({63+i}, {50+i%20}, '{t.strftime('%Y-%m-%d %H:%M:%S')}', 2, 1)")
    for i in range(1, 20):
        t = base_time + timedelta(minutes=i*20)
        sensores_vals.append(f"({82+i}, {200+i*10}, '{t.strftime('%Y-%m-%d %H:%M:%S')}', 3, 1)")

    sensores_insert_block = """-- Sensores
INSERT INTO `Sensores` (`Id_Sensor`, `Valor`, `Fecha`, `Id_Tipo`, `Activo`) VALUES
  (1, 22.5,  '2024-06-01 08:00:00', 1, 1),
  (2, 65.0,  '2024-06-01 08:00:00', 2, 1),
  (3, 300.0, '2024-06-01 08:00:00', 3, 1),
  (4, 0.0,   '2024-06-01 08:00:00', 4, 0),
  """ + ",\n  ".join(sensores_vals) + ";"
    
    content = re.sub(r"-- Sensores.*?;\n", sensores_insert_block + "\n", content, flags=re.DOTALL)
    
    # Relaciones entre usuarios: 9 conversaciones, cada una con 1 OP, 1 ADMIN, 1 INVITADO
    conversaciones_vals = []
    participantes_vals = []
    mensajes_vals = []
    
    # Existing ones
    conversaciones_vals.append("(1, 'Incidencia barrera 3',  '2024-06-01 10:35:00', 1)")
    conversaciones_vals.append("(2, 'Revisión sensores',     '2024-06-02 09:00:00', 1)")
    conversaciones_vals.append("(3, 'Chat eliminado',        '2024-05-01 08:00:00', 0)")
    
    participantes_vals.append("(1, 1, 1, '2024-06-01 10:35:00', 1)")
    participantes_vals.append("(2, 2, 1, '2024-06-01 10:36:00', 1)")
    participantes_vals.append("(3, 1, 2, '2024-06-02 09:00:00', 1)")
    participantes_vals.append("(4, 2, 2, '2024-06-02 09:05:00', 1)")

    mensajes_vals.append("(1, 1, 'La barrera 3 sigue dando error, revisar sensor.',   '2024-06-01 10:36:00', 1, 1)")
    mensajes_vals.append("(2, 2, 'Confirmado, voy a revisarlo ahora mismo.',          '2024-06-01 10:40:00', 1, 1)")
    mensajes_vals.append("(3, 1, 'Los sensores de humedad están por encima del umbral.','2024-06-02 09:01:00', 2, 1)")
    
    op_ids = [2, 8, 9, 10, 11, 12, 13, 14, 15]
    ad_ids = [1, 4, 5, 6, 7, 1, 4, 5, 6]
    in_ids = [3, 16, 17, 18, 19, 3, 16, 17, 18]
    
    pid = 5
    mid = 4
    for idx, (op, ad, inv) in enumerate(zip(op_ids, ad_ids, in_ids)):
        cid = idx + 4
        conversaciones_vals.append(f"({cid}, 'Relación Operador {op}', '2024-06-03 10:00:00', 1)")
        participantes_vals.append(f"({pid}, {op}, {cid}, '2024-06-03 10:00:00', 1)"); pid+=1
        participantes_vals.append(f"({pid}, {ad}, {cid}, '2024-06-03 10:00:00', 1)"); pid+=1
        participantes_vals.append(f"({pid}, {inv}, {cid}, '2024-06-03 10:00:00', 1)"); pid+=1
        mensajes_vals.append(f"({mid}, {op}, 'Hola, inicio chat de relacion', '2024-06-03 10:05:00', {cid}, 1)"); mid+=1
        
    conversaciones_block = "-- Conversaciones\nINSERT INTO `Conversacion` (`Id_Conversacion`, `Titulo`, `Fecha`, `Activo`) VALUES\n  " + ",\n  ".join(conversaciones_vals) + ";"
    participantes_block = "-- Participantes (con fecha de unión)\nINSERT INTO `Participantes` (`Id_Participantes`, `Id_User`, `Id_Conversacion`, `Fecha_Union`, `Activo`) VALUES\n  " + ",\n  ".join(participantes_vals) + ";"
    mensajes_block = "-- Mensajes\nINSERT INTO `Mensajes` (`Id`, `Id_User`, `Descripcion`, `Fecha`, `Id_Conversacion`, `Activo`) VALUES\n  " + ",\n  ".join(mensajes_vals) + ";"
    
    content = re.sub(r"-- Conversaciones.*?;\n", conversaciones_block + "\n", content, flags=re.DOTALL)
    content = re.sub(r"-- Participantes \(con fecha de unión\).*?;\n", participantes_block + "\n", content, flags=re.DOTALL)
    content = re.sub(r"-- Mensajes.*?;(\n|$)", mensajes_block + "\n", content, flags=re.DOTALL)

    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("SQL File modified successfully.")

if __name__ == '__main__':
    main()
