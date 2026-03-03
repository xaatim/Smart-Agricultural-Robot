/*
 * ESP32 AGRI-ROBOT (UDP + BLYNK) - SIMPLE VERSION + ULTRASONIC GATE FOR WATERING
 * - UDP commands: F,B,L,R,S,W,X
 * - Blynk buttons: V0..V6
 * - NEW RULE: Pump (W) only works if ultrasonic distance < 200 cm
 */

#define BLYNK_TEMPLATE_ID   "TMPL6X8nHlxtT"
#define BLYNK_TEMPLATE_NAME "Quickstart Template"
#define BLYNK_AUTH_TOKEN    "Ovnj6tJ3yVislDDAnaLc3OVQMNOmBiru"
#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <WiFiUdp.h>
#include <BlynkSimpleEsp32.h>

// --- CONFIGURATION ---
const char* ssid = "Unkown";
const char* password = "kkkkkkkk";
const int localPort = 8888;

// --- MOTOR PIN DEFINITIONS (ESP32 GPIO) ---
const int ENA = 13;   // PWM
const int IN1 = 14;
const int IN2 = 27;
const int IN3 = 26;
const int IN4 = 25;
const int ENB = 12;   // PWM (if boot issue, change to another pin like 23)

// --- WATER PUMP PINS ---
const int PUMP_PIN1 = 33;
const int PUMP_PIN2 = 32;

// --- ULTRASONIC (HC-SR04) ---
// TRIG can be any output pin; ECHO must be INPUT pin.
// IMPORTANT: HC-SR04 ECHO is 5V -> use voltage divider to ESP32 3.3V input.
const int TRIG_PIN = 4;
const int ECHO_PIN = 18;

const float WATER_ENABLE_DISTANCE_CM = 200.0;  // Pump allowed only if distance < 200 cm
float lastDistanceCm = 999.0;

// --- GLOBAL VARIABLES ---
WiFiUDP udp;
char packetBuffer[255];
int motorSpeed = 180;   // analogWrite range typically 0-255 on ESP32

// ===== ULTRASONIC READ =====
float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Timeout 30000us ~ 5 meters max
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return 999.0; // no echo -> treat as far

  return (duration * 0.0343f) / 2.0f; // cm
}

bool wateringAllowed() {
  lastDistanceCm = readDistanceCm();
  return (lastDistanceCm < WATER_ENABLE_DISTANCE_CM);
}

void pumpOff() {
  digitalWrite(PUMP_PIN1, LOW);
  digitalWrite(PUMP_PIN2, LOW);
}

/**
 * @brief Executes a motor or pump command
 * @param cmd The command character (F, B, L, R, S, W, X)
 */
void executeCommand(char cmd) {
  switch (cmd) {
    case 'F': // Forward
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);
      analogWrite(ENA, motorSpeed);
      analogWrite(ENB, motorSpeed);
      break;

    case 'B': // Backward
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
      analogWrite(ENA, motorSpeed);
      analogWrite(ENB, motorSpeed);
      break;

    case 'L': // Left (Zero-point turn)
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);
      analogWrite(ENA, motorSpeed);
      analogWrite(ENB, motorSpeed);
      break;

    case 'R': // Right (Zero-point turn)
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
      analogWrite(ENA, motorSpeed);
      analogWrite(ENB, motorSpeed);
      break;

    case 'S': // Stop Motors
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, LOW);
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, LOW);
      analogWrite(ENA, 0);
      analogWrite(ENB, 0);
      break;

    case 'W': // Water ON (ONLY if distance < 200cm)
      if (wateringAllowed()) {
        digitalWrite(PUMP_PIN1, HIGH);
        digitalWrite(PUMP_PIN2, LOW);
        Serial.print("[WATER] ON allowed. Distance(cm)=");
        Serial.println(lastDistanceCm);
      } else {
        pumpOff();
        Serial.print("[WATER] BLOCKED (too far). Distance(cm)=");
        Serial.println(lastDistanceCm);
      }
      break;

    case 'X': // Water OFF
      pumpOff();
      break;
  }
}

// ===== BLYNK BUTTONS =====
BLYNK_WRITE(V0) { if (param.asInt()) executeCommand('F'); else executeCommand('S'); }
BLYNK_WRITE(V1) { if (param.asInt()) executeCommand('B'); else executeCommand('S'); }
BLYNK_WRITE(V2) { if (param.asInt()) executeCommand('L'); else executeCommand('S'); }
BLYNK_WRITE(V3) { if (param.asInt()) executeCommand('R'); else executeCommand('S'); }
BLYNK_WRITE(V4) { if (param.asInt()) executeCommand('S'); }

// Pump controls
BLYNK_WRITE(V5) { if (param.asInt()) executeCommand('W'); }
BLYNK_WRITE(V6) { if (param.asInt()) executeCommand('X'); }

void setup() {
  Serial.begin(115200);

  // Pin Setup
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(PUMP_PIN1, OUTPUT);
  pinMode(PUMP_PIN2, OUTPUT);

  // Ultrasonic pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);

  // Ensure everything is off
  pumpOff();
  executeCommand('S');

  // Connect WiFi first so IP always prints
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // Connect Blynk (non-blocking style)
  Blynk.config(BLYNK_AUTH_TOKEN);
  Blynk.connect();

  // Start UDP listener once
  udp.begin(localPort);
  Serial.printf("UDP Server started at port %d\n", localPort);

  Serial.println("[READY] Motors via UDP/Blynk. Pump only works if distance < 200cm.");
}

void loop() {
  Blynk.run();

  // UDP receive loop
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;

    char cmd = packetBuffer[0];
    Serial.print("Received command: ");
    Serial.println(cmd);

    executeCommand(cmd);
  }
}
