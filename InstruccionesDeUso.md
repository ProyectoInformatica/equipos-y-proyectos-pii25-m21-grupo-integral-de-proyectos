# Proyecto Inteligente Residencial - Sistema GIP

Este sistema integral permite monitorizar y controlar aspectos residenciales, incluyendo accesos, barreras automáticas, sistemas de alarmas y datos ambientales empleando sensores y almacenamiento robusto en base de datos.

## Arquitectura (MVC)
El proyecto ha sido estrictamente refactorizado siguiendo el patrón **Modelo-Vista-Controlador**:
* **M (Modelo)**: Las conexiones, pools transaccionales (`try/finally`) y obtención de datos desde la base de datos MySQL se concentran en `database.py`.
* **C (Controladores)**: La lógica de negocio (`auth.py`, `data_controller.py`, `usuarios_controller.py`, etc.) separa las reglas complejas en la carpeta `controllers/`.
* **V (Vistas)**: El ecosistema de interfaces de usuario está contenido en la carpeta `views/` con la librería Flet abstrayendo los datos mediante el controlador.

Además, el monitoreo y simulación local del sistema de hardware recae en transacciones desprotegidas en la carpeta `sensores/`.

## Requisitos de Entorno
* **Python 3.10+**
* **Docker Desktop** (Obligatorio para simular el servidor MySQL remoto)

## Instrucciones de Instalación para el Corrector

1. **Base de Datos Automática (Docker)**:
   Abre una terminal directamente en la carpeta del proyecto y levanta de fondo la imagen Docker configurada usando el fichero `docker-compose.yml`. Para crear las tablas utilizará el código de "**Script-Smart Residencial.sql**" recién acoplado de forma nativa a este paquete.
   ```bash
   docker compose up -d
   ```

2. **Dependencias del Proyecto**:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución del Sistema
Para lanzar la aplicación con su interfaz de usuario y sus subprocesos de lectura de sensores simultáneamente:
```bash
python run_system.py
```

## Credenciales de Evaluación
Puedes autenticarte inmediatamente con perfiles multi-rol del propio esquema nativo:
* **Administrador:** `ana@sistema.com` | Clave: `password123` 
* **Técnico / Operador:** `luis@sistema.com` | Clave: `operador456`
* **Cliente / Invitado:** `carlos@sistema.com` | Clave: `invitado789` (El script fuerza a este usuario a estar de baja lógica, debe habilitarse en la BDD para pruebas o registrar nuevos usuarios desde el perfil del administrador)
