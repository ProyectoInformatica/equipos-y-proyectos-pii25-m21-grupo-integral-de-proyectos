// ============================================================
//  SISTEMA DE PEAJE AUTOMATIZADO — WiFi + MySQL
//  Plataforma : ESP32 NodeMCU WROOM-32 (38 pines)
//  IDE        : Arduino IDE
//  Baudios    : 115200
// ============================================================
//  LIBRERIAS NECESARIAS (Gestor de Librerias Arduino IDE):
//    - ESP32Servo        -> Kevin Harrington
//    - DHT sensor library -> Adafruit
//    - Adafruit Unified Sensor -> Adafruit (dependencia DHT)
//    - MySQL Connector/Arduino -> ChuckBell
// ============================================================
//
//  BASE DE DATOS MySQL (Docker / XAMPP):
//    - Nombre BD  : smart_residencial
//    - Usuario    : root
//    - Contrasena : rootpassword
//    - Puerto     : 3306
//
//  IDs en la BD:
//    Tipos sensor:
//      Id_Tipos 1 -> Temperatura
//      Id_Tipos 2 -> Humedad
//      Id_Tipos 3 -> Luminosidad
//      Id_Tipos 4 -> Gas
//      Id_Tipos 5 -> Viento
//    Barreras:
//      id_Barrera 1 -> Norte-Entrada  (entrada-norte)
//      id_Barrera 2 -> Norte-Salida   (salida-norte)
//      id_Barrera 3 -> Sur-Entrada    (entrada-sur)
//      id_Barrera 4 -> Sur-Salida     (salida-sur)
//    Conf_Luminosidad:
//      id 1 -> configuracion activa (umbral + horario)
//    Conf_Alertas:
//      id 1 -> umbral Temperatura
//      id 2 -> umbral Humedad
//      id 3 -> umbral Luminosidad
//      id 4 -> umbral Gas
// ============================================================

#include <WiFi.h>
#include <MySQL_Connection.h>
#include <MySQL_Cursor.h>
#include <ESP32Servo.h>
#include <DHT.h>

// ============================================================
//  CONFIGURACION WiFi
// ============================================================
const char* WIFI_SSID     = "iPhone de Daniel";
const char* WIFI_PASSWORD = "peaje2024";

// ============================================================
//  CONFIGURACION MySQL
// ============================================================
IPAddress DB_IP(192, 168, 1, 100);   // IP del ordenador con Docker/XAMPP
const int     DB_PORT = 3306;
const char*   DB_USER = "root";
const char*   DB_PASS = "rootpassword";
const char*   DB_NAME = "smart_residencial";

// ============================================================
//  MAPA DE PINES
// ============================================================
#define PIN_SERVO_NE   4
#define PIN_SERVO_NS  18
#define PIN_SERVO_SE   5
#define PIN_SERVO_SS  21

#define TRIG_NE  13
#define TRIG_NS  27
#define TRIG_SE  25
#define TRIG_SS  32

#define ECHO_NE  14
#define ECHO_NS  26
#define ECHO_SE  33
#define ECHO_SS  35

#define PIN_LDR   34
#define PIN_GAS   36
#define PIN_FAN   39
#define PIN_DHT   22
#define PIN_LEDS  23
#define DHT_TYPE  DHT11

// ============================================================
//  PARAMETROS FISICOS
// ============================================================
const int   DIST_UMBRAL_CM            = 2;
const unsigned long TIEMPO_ABIERTA_MS = 3000;
const int   SERVO_ABIERTO             = 100;
const int   SERVO_CERRADO             = 10;
const unsigned long DESFASE_SERVO_MS  = 75;
const unsigned long INTERVALO_ULTRA   = 60;

const unsigned long INTERVALO_SENSORES = 10000;  // cada 10 s guarda sensores
const unsigned long INTERVALO_CONF     = 30000;  // cada 30 s recarga config BD
const unsigned long INTERVALO_SERIAL   = 500;

// ============================================================
//  VARIABLES DE CONFIGURACION (cargadas desde BD)
// ============================================================
float umbralLuz         = 1500.0;
float umbralTemperatura = 35.0;
float umbralHumedad     = 80.0;
float umbralGas         = 2000.0;
String controlLuz       = "automatico";

// ============================================================
//  OBJETOS
// ============================================================
Servo servoNE, servoNS, servoSE, servoSS;
DHT   dht(PIN_DHT, DHT_TYPE);

WiFiClient       wifiClient;
MySQL_Connection dbConn(&wifiClient);

// ============================================================
//  ESTRUCTURA DE BARRERA
//  modoManual  : true si Barreras.Control = 'manual'
//  estadoManual: true si Barreras.Estado  = 'abierta' (orden desde la app)
// ============================================================
struct Barrera {
  const char*   nombre;
  const char*   ubicacion;
  int           id_bd;
  Servo*        servo;
  int           pinTrig, pinEcho;
  bool          abierta;
  unsigned long ultimaLectura;
  unsigned long tiempoApertura;
  long          distancia;
  bool          modoManual;    // leido desde BD
  bool          estadoManual;  // estado deseado cuando modoManual=true
};

Barrera barreras[4] = {
  {"Norte-Entrada", "Norte-Entrada", 1, &servoNE, TRIG_NE, ECHO_NE, false, 0, 0, 0, false, false},
  {"Norte-Salida",  "Norte-Salida",  2, &servoNS, TRIG_NS, ECHO_NS, false, 0, 0, 0, false, false},
  {"Sur-Entrada",   "Sur-Entrada",   3, &servoSE, TRIG_SE, ECHO_SE, false, 0, 0, 0, false, false},
  {"Sur-Salida",    "Sur-Salida",    4, &servoSS, TRIG_SS, ECHO_SS, false, 0, 0, 0, false, false},
};

unsigned long ultimoSerial   = 0;
unsigned long ultimoSensores = 0;
unsigned long ultimoConf     = 0;

// ============================================================
//  FUNCION: conectar WiFi
// ============================================================
void conectarWifi() {
  Serial.print("  Conectando a WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n  WiFi conectado. IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n  ERROR: No se pudo conectar al WiFi.");
  }
}

// ============================================================
//  FUNCION: conectar MySQL
// ============================================================
bool conectarDB() {
  if (dbConn.connected()) return true;
  Serial.print("  Conectando a MySQL...");
  if (dbConn.connect(DB_IP, DB_PORT, (char*)DB_USER, (char*)DB_PASS)) {
    Serial.println(" OK");
    return true;
  } else {
    Serial.println(" ERROR");
    return false;
  }
}

// ============================================================
//  FUNCION: ejecutar query sin resultado (INSERT / UPDATE)
// ============================================================
void ejecutarQuery(const char* sql) {
  if (!conectarDB()) return;
  MySQL_Cursor cursor(&dbConn);
  cursor.execute(sql);
  cursor.close();
}

// ============================================================
//  FUNCION: guardar valor de sensor en BD
//  Siempre INSERT para conservar historial.
//  Si supera el umbral -> INSERT Notificacion.
// ============================================================
void guardarSensor(int id_tipo, float valor, float umbral,
                   const char* tituloAlerta, bool superaUmbral) {
  if (!conectarDB()) return;

  char sql[250];

  snprintf(sql, sizeof(sql),
    "INSERT INTO `smart_residencial`.`Sensores` "
    "(`Valor`,`Fecha`,`Id_Tipo`,`Activo`) "
    "VALUES (%.2f,NOW(),%d,1);",
    valor, id_tipo);
  ejecutarQuery(sql);

  if (superaUmbral) {
    snprintf(sql, sizeof(sql),
      "INSERT INTO `smart_residencial`.`Notificaciones` "
      "(`Fecha`,`Dato`,`Titulo`,`Id_Sensor`,`Activo`) "
      "VALUES (NOW(),%.2f,'%s',LAST_INSERT_ID(),1);",
      valor, tituloAlerta);
    ejecutarQuery(sql);
    Serial.print("  ALERTA: ");
    Serial.println(tituloAlerta);
  }
}

// ============================================================
//  FUNCION: guardar estado de barrera en BD
//  Solo actualiza Estado; NO toca el campo Control para
//  respetar el modo manual configurado desde la app.
// ============================================================
void guardarBarrera(int id_barrera, bool abierta, const char* motivo) {
  if (!conectarDB()) return;

  char sql[300];
  const char* estado = abierta ? "abierta" : "cerrada";

  // Actualiza solo Estado, preserva Control (manual/automatico)
  snprintf(sql, sizeof(sql),
    "UPDATE `smart_residencial`.`Barreras` "
    "SET `Estado`='%s' "
    "WHERE `id_Barrera`=%d AND `Activo`=1;",
    estado, id_barrera);
  ejecutarQuery(sql);

  // INSERT historial
  snprintf(sql, sizeof(sql),
    "INSERT INTO `smart_residencial`.`Historial_Barreras` "
    "(`Fecha`,`Control`,`id_Barrera`) "
    "VALUES (NOW(),'%s',%d);",
    motivo, id_barrera);
  ejecutarQuery(sql);
}

// ============================================================
//  FUNCION: cargar configuracion desde BD
//  Lee Conf_Luminosidad, Conf_Alertas y modo de cada barrera.
// ============================================================
void cargarConfiguracion() {
  if (!conectarDB()) return;

  MySQL_Cursor cursor(&dbConn);
  column_names* cols;
  row_values*   row;

  Serial.println("  Cargando configuracion desde BD...");

  // -- Conf_Luminosidad ---------------------------------------
  cursor.execute(
    "SELECT `Control`, `Umbral` FROM `smart_residencial`.`Conf_Luminosidad` "
    "WHERE `Activo`=1 ORDER BY `id` ASC LIMIT 1;"
  );
  cols = cursor.get_columns();
  row  = cursor.get_next_row();
  if (row != NULL) {
    controlLuz = String(row->values[0]);
    umbralLuz  = atof(row->values[1]);
    Serial.print("  Luz -> Control: ");
    Serial.print(controlLuz);
    Serial.print(" | Umbral ADC: ");
    Serial.println(umbralLuz);
  }
  cursor.close();

  // -- Conf_Alertas temperatura (Id_Tipo=1) -------------------
  cursor.execute(
    "SELECT `Valor` FROM `smart_residencial`.`Conf_Alertas` "
    "WHERE `Id_Tipo`=1 AND `Activo`=1 LIMIT 1;"
  );
  cols = cursor.get_columns();
  row  = cursor.get_next_row();
  if (row != NULL) {
    umbralTemperatura = atof(row->values[0]);
    Serial.print("  Umbral Temp: "); Serial.println(umbralTemperatura);
  }
  cursor.close();

  // -- Conf_Alertas humedad (Id_Tipo=2) -----------------------
  cursor.execute(
    "SELECT `Valor` FROM `smart_residencial`.`Conf_Alertas` "
    "WHERE `Id_Tipo`=2 AND `Activo`=1 LIMIT 1;"
  );
  cols = cursor.get_columns();
  row  = cursor.get_next_row();
  if (row != NULL) {
    umbralHumedad = atof(row->values[0]);
    Serial.print("  Umbral Hum: "); Serial.println(umbralHumedad);
  }
  cursor.close();

  // -- Conf_Alertas gas (Id_Tipo=4) ---------------------------
  cursor.execute(
    "SELECT `Valor` FROM `smart_residencial`.`Conf_Alertas` "
    "WHERE `Id_Tipo`=4 AND `Activo`=1 LIMIT 1;"
  );
  cols = cursor.get_columns();
  row  = cursor.get_next_row();
  if (row != NULL) {
    umbralGas = atof(row->values[0]);
    Serial.print("  Umbral Gas: "); Serial.println(umbralGas);
  }
  cursor.close();

  // -- Modo de cada barrera (Control + Estado) ----------------
  // Lee las 4 barreras para saber si estan en modo manual y
  // cual es el estado deseado (abierta/cerrada) desde la app.
  cursor.execute(
    "SELECT `id_Barrera`, `Control`, `Estado` "
    "FROM `smart_residencial`.`Barreras` "
    "WHERE `Activo`=1 ORDER BY `id_Barrera` ASC;"
  );
  cols = cursor.get_columns();
  row  = cursor.get_next_row();
  while (row != NULL) {
    int id = atoi(row->values[0]);
    if (id >= 1 && id <= 4) {
      int idx = id - 1;
      barreras[idx].modoManual   = (strcmp(row->values[1], "manual") == 0);
      barreras[idx].estadoManual = (strcmp(row->values[2], "abierta") == 0);
      Serial.print("  Barrera ");
      Serial.print(barreras[idx].nombre);
      Serial.print(": Control=");
      Serial.print(row->values[1]);
      Serial.print(" Estado=");
      Serial.println(row->values[2]);
    }
    row = cursor.get_next_row();
  }
  cursor.close();
}

// ============================================================
//  FUNCION: medir distancia HC-SR04
// ============================================================
long medirDistancia(int pinTrig, int pinEcho) {
  digitalWrite(pinTrig, LOW);  delayMicroseconds(2);
  digitalWrite(pinTrig, HIGH); delayMicroseconds(10);
  digitalWrite(pinTrig, LOW);
  long dur = pulseIn(pinEcho, HIGH, 30000UL);
  return (dur == 0) ? -1 : dur * 0.0343f / 2.0f;
}

// ============================================================
//  FUNCION: abrir barrera (modo automatico)
// ============================================================
void abrirBarrera(int i) {
  Barrera& b = barreras[i];
  if (b.abierta) return;
  unsigned long espera = (unsigned long)i * DESFASE_SERVO_MS;
  if (espera > 0) delay(espera);
  b.servo->write(SERVO_ABIERTO);
  b.abierta        = true;
  b.tiempoApertura = millis();

  char motivo[80];
  snprintf(motivo, sizeof(motivo),
    "Apertura automatica: vehiculo detectado en %s", b.nombre);
  guardarBarrera(b.id_bd, true, motivo);
}

// ============================================================
//  FUNCION: cerrar barrera (modo automatico)
// ============================================================
void cerrarBarrera(int i) {
  Barrera& b = barreras[i];
  if (!b.abierta) return;
  b.servo->write(SERVO_CERRADO);
  b.abierta = false;

  char motivo[80];
  snprintf(motivo, sizeof(motivo),
    "Cierre automatico tras 3 segundos en %s", b.nombre);
  guardarBarrera(b.id_bd, false, motivo);
}

// ============================================================
//  FUNCION: aplicar estado manual de una barrera
//  Lee estadoManual (cargado desde BD) y mueve el servo.
// ============================================================
void aplicarModoManual(int i) {
  Barrera& b = barreras[i];
  if (b.estadoManual && !b.abierta) {
    unsigned long espera = (unsigned long)i * DESFASE_SERVO_MS;
    if (espera > 0) delay(espera);
    b.servo->write(SERVO_ABIERTO);
    b.abierta = true;
    Serial.print("  [MANUAL] Abriendo ");
    Serial.println(b.nombre);
  } else if (!b.estadoManual && b.abierta) {
    b.servo->write(SERVO_CERRADO);
    b.abierta = false;
    Serial.print("  [MANUAL] Cerrando ");
    Serial.println(b.nombre);
  }
}

// ============================================================
//  FUNCION: velocidad del viento
// ============================================================
float leerVelocidadViento() {
  long suma = 0;
  for (int i = 0; i < 8; i++) {
    suma += analogRead(PIN_FAN);
    delayMicroseconds(500);
  }
  int prom = suma / 8;
  return (prom < 30) ? 0.0f : ((float)prom / 4095.0f) * 60.0f;
}

// ============================================================
//  SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  Serial.println("\n======================================");
  Serial.println("  SISTEMA DE PEAJE — Iniciando...");
  Serial.println("======================================");

  for (int i = 0; i < 4; i++) {
    pinMode(barreras[i].pinTrig, OUTPUT);
    pinMode(barreras[i].pinEcho, INPUT);
    digitalWrite(barreras[i].pinTrig, LOW);
  }

  pinMode(PIN_LEDS, OUTPUT);
  digitalWrite(PIN_LEDS, LOW);
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  servoNE.attach(PIN_SERVO_NE, 500, 2400); delay(50);
  servoNS.attach(PIN_SERVO_NS, 500, 2400); delay(50);
  servoSE.attach(PIN_SERVO_SE, 500, 2400); delay(50);
  servoSS.attach(PIN_SERVO_SS, 500, 2400); delay(50);
  servoNE.write(SERVO_CERRADO); delay(DESFASE_SERVO_MS);
  servoNS.write(SERVO_CERRADO); delay(DESFASE_SERVO_MS);
  servoSE.write(SERVO_CERRADO); delay(DESFASE_SERVO_MS);
  servoSS.write(SERVO_CERRADO);

  dht.begin();
  delay(2000);

  conectarWifi();

  if (conectarDB()) {
    cargarConfiguracion();
  }

  Serial.println("  Sistema listo.");
  Serial.println("======================================\n");
}

// ============================================================
//  LOOP PRINCIPAL
// ============================================================
void loop() {
  unsigned long ahora = millis();

  // Reconectar WiFi si se pierde
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("  WiFi perdido, reconectando...");
    conectarWifi();
  }

  // ── 1. BARRERAS ─────────────────────────────────────────
  for (int i = 0; i < 4; i++) {
    Barrera& b = barreras[i];

    if (b.modoManual) {
      // Modo manual: aplica el estado deseado leido desde la BD
      aplicarModoManual(i);
    } else {
      // Modo automatico: sensor ultrasonico decide
      if (ahora - b.ultimaLectura >= INTERVALO_ULTRA) {
        b.ultimaLectura = ahora;
        long dist   = medirDistancia(b.pinTrig, b.pinEcho);
        b.distancia = (dist < 0) ? 400 : dist;
        bool hayVehiculo = (b.distancia > 0 && b.distancia < DIST_UMBRAL_CM);
        if (hayVehiculo && !b.abierta) {
          abrirBarrera(i);
          b.tiempoApertura = ahora;
        }
      }
      // Cerrar tras TIEMPO_ABIERTA_MS
      if (b.abierta && (ahora - b.tiempoApertura >= TIEMPO_ABIERTA_MS)) {
        cerrarBarrera(i);
      }
    }
  }

  // ── 2. ILUMINACION ──────────────────────────────────────
  int valorLDR = analogRead(PIN_LDR);
  bool lucesEncendidas = false;

  if (controlLuz == "encendido") {
    lucesEncendidas = true;
  } else if (controlLuz == "apagado") {
    lucesEncendidas = false;
  } else {
    lucesEncendidas = (valorLDR < (int)umbralLuz);
  }
  digitalWrite(PIN_LEDS, lucesEncendidas ? HIGH : LOW);

  // ── 3. GUARDAR SENSORES EN BD (cada 10 s) ───────────────
  if (ahora - ultimoSensores >= INTERVALO_SENSORES) {
    ultimoSensores = ahora;

    float temp  = dht.readTemperature();
    float hum   = dht.readHumidity();
    int   gas   = analogRead(PIN_GAS);
    float viento = leerVelocidadViento();

    // Temperatura (Id_Tipo=1)
    if (!isnan(temp)) {
      bool alerta = temp > umbralTemperatura;
      guardarSensor(1, temp, umbralTemperatura, "Temperatura alta", alerta);
    }
    // Humedad (Id_Tipo=2)
    if (!isnan(hum)) {
      bool alerta = hum > umbralHumedad;
      guardarSensor(2, hum, umbralHumedad, "Humedad critica", alerta);
    }
    // Luminosidad escalada a 0-1000 (Id_Tipo=3)
    float ldrEscalado = map(valorLDR, 0, 4095, 0, 1000);
    bool alertaLuz = ldrEscalado < 100;
    guardarSensor(3, ldrEscalado, 100, "Luminosidad baja", alertaLuz);

    // Gas / Calidad de aire (Id_Tipo=4)
    bool alertaGas = gas > (int)umbralGas;
    guardarSensor(4, (float)gas, umbralGas, "Gas elevado detectado", alertaGas);

    // Viento (Id_Tipo=5) — siempre guarda, alerta si supera 50 km/h
    bool alertaViento = viento > 50.0f;
    guardarSensor(5, viento, 50.0f, "Viento peligroso", alertaViento);
  }

  // ── 4. RECARGAR CONFIGURACION DESDE BD (cada 30 s) ──────
  // Incluye modos manuales de cada barrera
  if (ahora - ultimoConf >= INTERVALO_CONF) {
    ultimoConf = ahora;
    cargarConfiguracion();
  }

  // ── 5. SERIAL MONITOR (cada 500 ms) ─────────────────────
  if (ahora - ultimoSerial >= INTERVALO_SERIAL) {
    ultimoSerial = ahora;

    float temp   = dht.readTemperature();
    float hum    = dht.readHumidity();
    int   gas    = analogRead(PIN_GAS);
    float viento = leerVelocidadViento();

    Serial.print("  ");
    for (int i = 0; i < 4; i++) {
      Serial.print(barreras[i].nombre);
      Serial.print(barreras[i].modoManual ? "[MAN]" : "[AUT]");
      Serial.print(": ");
      if (barreras[i].distancia >= 400) Serial.print(">4m");
      else { Serial.print(barreras[i].distancia); Serial.print(" cm"); }
      Serial.print(" [");
      Serial.print(barreras[i].abierta ? "ABIERTA" : "CERRADA");
      Serial.print("]");
      if (i < 3) Serial.print(" | ");
    }
    Serial.println();

    Serial.print("  LDR: "); Serial.print(analogRead(PIN_LDR));
    Serial.print(" (Luces: "); Serial.print(lucesEncendidas ? "ON" : "OFF");
    Serial.print(") | Temp: ");
    if (isnan(temp)) Serial.print("ERR");
    else { Serial.print(temp, 1); Serial.print(" C"); }
    Serial.print(" | Hum: ");
    if (isnan(hum)) Serial.print("ERR");
    else { Serial.print(hum, 1); Serial.print(" %"); }
    Serial.print(" | Gas: "); Serial.print(gas);
    Serial.print(" | Viento: "); Serial.print(viento, 1); Serial.println(" km/h");
    Serial.print("  WiFi: ");
    Serial.print(WiFi.status() == WL_CONNECTED ? "OK" : "SIN CONEXION");
    Serial.print(" | DB: ");
    Serial.println(dbConn.connected() ? "OK" : "SIN CONEXION");
    Serial.println("  ──────────────────────────────────────────────────────");
  }
}
