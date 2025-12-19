/*
 * AGRI-ROBOT FIRMWARE (ESP8266 / NodeMCU)
 * --------------------
 * Connects to Wi-Fi and listens for UDP commands to drive motors and a water pump.
 *
 * HARDWARE:
 * - NodeMCU (ESP8266)
 * - L298N Motor Driver
 * - 5V Relay Module (for water pump)
 *
 * WIRING (NodeMCU D-pins):
 * L298N:
 * - ENA: D1 (GPIO 5 - PWM)
 * - IN1: D2 (GPIO 4)
 * - IN2: D3 (GPIO 0)
 * - IN3: D5 (GPIO 14)
 * - IN4: D6 (GPIO 12)
 * - ENB: D7 (GPIO 13 - PWM)
 *
 * RELAY:
 * - IN:  D8 (GPIO 15)
 *
 * POWER:
 * - Connect external battery (e.g., 7.4V) to L298N 12V terminal.
 * - Connect L298N GND and NodeMCU GND together.
 * - Power NodeMCU via USB or from L298N 5V output (if your L298N has a good 5V regulator).
 */

#include <WiFi.h> // <-- Correct library for ESP8266
#include <WiFiUdp.h>

// --- CONFIGURATION ---
const char* ssid = "Unkown";       
const char* password = "kkkkkkkk"; 
const int localPort = 8888;              // Port to listen on

// --- MOTOR PIN DEFINITIONS (NodeMCU D-Pins) ---
const int ENA = 13; 
const int IN1 = 35; 
const int IN2 = 14; 
const int IN3 = 27; 
const int IN4 = 26; 
const int ENB = 25; 

// --- WATER PUMP PIN ---
const int PUMP_PIN1 = 33; 
const int PUMP_PIN2 = 32; 

// --- GLOBAL VARIABLES ---
WiFiUDP udp;
char packetBuffer[255]; // Buffer to hold incoming packets
int motorSpeed = 100;   // Default speed for ESP8266 (0-1023 for PWM)

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

  // Ensure everything is off
  digitalWrite(PUMP_PIN1, LOW); // Pump OFF
  digitalWrite(PUMP_PIN2, LOW); // Pump OFF

  executeCommand('S');         // Motors STOP

  // Connect to WiFi
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP()); // <-- IMPORTANT! Note this IP for Python script.

  // Start UDP listener
  udp.begin(localPort);
  Serial.printf("UDP Server started at port %d\n", localPort);
}

void loop() {
  // Check for incoming UDP packet
  int packetSize = udp.parsePacket();
  if (packetSize) {
    // Read the packet into the buffer
    int len = udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0; // Null-terminate the string
    }

    Serial.print("Received command: ");
    char cmd = packetBuffer[0]; // Get the first character
    Serial.println(cmd);

    // Act on the command
    executeCommand(cmd);
  }
}

/**
 * @brief Executes a motor or pump command
 * @param cmd The command character (F, B, L, R, S, W, X)
 */
void executeCommand(char cmd) {
  // NOTE: ESP8266 analogWrite is 0-1023 by default
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
      digitalWrite(IN2, HIGH); // Left motor backward
      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);  // Right motor forward
      analogWrite(ENA, motorSpeed);
      analogWrite(ENB, motorSpeed);
      break;

    case 'R': // Right (Zero-point turn)
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);  // Left motor forward
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH); // Right motor backward
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

    case 'W': // Water ON
      digitalWrite(PUMP_PIN1, HIGH);
      digitalWrite(PUMP_PIN2, LOW);
      break;

    case 'X': // Water OFF
      digitalWrite(PUMP_PIN1, LOW);
      digitalWrite(PUMP_PIN2, LOW);

      break;
  }
}