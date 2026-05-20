#include <ArduinoJson.h>
#include <DHT.h>

// ===============================
// DEFINICIÓN DE PINES (ESP32)
// ===============================
// - Sensores Ambientales
#define DHTPIN 4
#define DHTTYPE DHT11 // O DHT22
DHT dht(DHTPIN, DHTTYPE);

#define LDR_PIN 34
#define MQ2_PIN 35
#define MQ135_PIN 32

// - HC-SR04 (Ultrasonido - Barrera)
#define TRIG_PIN 5
#define ECHO_PIN 18

// - Actuadores
#define LED_PIN 19
#define MOTOR_PIN 21 
#define FAN_PIN 22   

unsigned long anteriorMillis = 0;
const long intervalo = 3000; // Enviar datos cada 3 segundos

void setup() {
  Serial.begin(115200);
  
  // Inicialización de sensores
  dht.begin();
  pinMode(LDR_PIN, INPUT);
  pinMode(MQ2_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Inicialización de actuadores
  pinMode(LED_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
  digitalWrite(FAN_PIN, LOW);

  // Esperar a que el puerto serial local despierte bien
  delay(1000);
  Serial.println("ESP32 Inicializado correctamente.");
}

void loop() {
  unsigned long actualMillis = millis();

  // 1. Cada cierto tiempo transmitimos lectura de sensores
  if (actualMillis - anteriorMillis >= intervalo) {
    anteriorMillis = actualMillis;
    enviarDatosSerial();
  }

  // 2. Escuchar contínuamente si PySerial nos manda actuar
  if (Serial.available() > 0) {
    String payload = Serial.readStringUntil('\n');
    recibirComandos(payload);
  }
}

// ===============================
// FUNCIONES DE SENSORES Y RED
// ===============================
void enviarDatosSerial() {
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  float ldr = analogRead(LDR_PIN);
  float mq2 = analogRead(MQ2_PIN);
  float mq135 = analogRead(MQ135_PIN);

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duracion = pulseIn(ECHO_PIN, HIGH);
  float distancia_cm = duracion * 0.034 / 2;

  // Crear documento JSON
  StaticJsonDocument<200> doc;
  if (!isnan(t)) doc["temperatura"] = t;
  if (!isnan(h)) doc["humedad"] = h;
  doc["luminosidad"] = map(ldr, 0, 4095, 0, 100); 
  doc["humo"] = mq2;
  doc["calidad_aire"] = mq135;
  doc["distancia"] = distancia_cm;

  // Imprimir textualmente al puerto serie para que lo agarre Python
  serializeJson(doc, Serial);
  Serial.println(); // Salto de línea crucial para que readline() en python funcione
}

void recibirComandos(String jsonText) {
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, jsonText);

  if (!error) {
    bool luz = doc["led"];
    bool motor = doc["motor"];
    bool vent = doc["ventilador"];

    // Aplicar voltaje al hardware mediante el puente H / Relé / MOSFET
    digitalWrite(LED_PIN, luz ? HIGH : LOW);
    digitalWrite(MOTOR_PIN, motor ? HIGH : LOW);
    digitalWrite(FAN_PIN, vent ? HIGH : LOW);
    
    // Podemos omitir el println para no saturar la consola de texto inútil
  } else {
    Serial.println("Error parseando actuadores JSON proveniente del PC.");
  }
}
