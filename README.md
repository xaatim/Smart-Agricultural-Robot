---

# 🌾 Semi-Autonomous Agriculture Robot

<p align="center">
  <a href="https://www.espressif.com/"><img src="https://img.shields.io/badge/Microcontroller-ESP32-blue?logo=espressif"></a>
  <a href="https://www.raspberrypi.org/"><img src="https://img.shields.io/badge/Processing-Raspberry%20Pi-A22846?logo=raspberrypi"></a>
  <a href="https://pjreddie.com/darknet/yolo/"><img src="https://img.shields.io/badge/YOLO-Plant%20Detection-red?logo=pytorch"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
  <img src="https://img.shields.io/badge/Status-Prototype-orange">
</p>


A **vision-guided semi-autonomous robot** for **smart agriculture**.
It can **detect crops & weeds**, **monitor environmental conditions**, and **perform basic field tasks** like **localized spraying**, using **YOLO-based plant recognition**, **ESP32 microcontroller**, and **Raspberry Pi for processing**.

---

## 📖 Overview

This project aims to support **precision farming** by combining **computer vision**, **IoT**, and **mechanized tasks** in a single system:

* **YOLO-based plant recognition** to identify crops & weeds.
* **ESP32-controlled motion & spraying** for precise field operations.
* **Environmental monitoring** (soil moisture, temperature, humidity).
* **Semi-autonomous navigation** with **manual override** for user control.

---

## 🛠 Hardware Components

| Component                | Purpose                                           |
| ------------------------ | ------------------------------------------------- |
| **Raspberry Pi 4**       | Runs YOLO & high-level Python logic               |
| **ESP32**                | Handles motor control, sensors & spraying         |
| **Motor Driver (L298N)** | Drives DC motors for movement                     |
| **4WD Chassis**          | Field-ready mobile platform                       |
| **Camera Module**        | Captures images for YOLO                          |
| **Soil Moisture Sensor** | Monitors soil health                              |
| **DHT11/22 Sensor**      | Measures temperature & humidity                   |
| **Sprayer System**       | Enables localized chemical/fertilizer application |
| **Li-ion Battery Pack**  | Powers the robot                                  |

---

## ✨ Key Features

* **YOLO Plant Detection** – Identifies crops, weeds & plant health patterns.
* **ESP32 IoT Control** – Low-latency motor & actuator management with wireless updates.
* **Data Logging** – Environmental readings & detection results stored for later analysis.
* **Localized Spraying** – Targeted application to reduce chemical waste.
* **Manual Override Mode** – Switch between autonomous & user-driven control.

---

## 🔧 Setup Instructions

### 1. **Hardware Assembly**

1. Assemble the **4WD robot chassis**.
2. Mount **ESP32 & Raspberry Pi** securely.
3. Wire up **motors, sensors, sprayer & camera** (see [`docs/wiring_diagram.png`](./docs/wiring_diagram.png)).

### 2. **Software Installation**

1. Install YOLO & OpenCV on the Raspberry Pi:

   ```bash
   sudo apt update && sudo apt install python3-opencv
   pip install torch torchvision ultralytics
   ```
2. Clone this repository:

   ```bash
   git clone https://github.com/xaatim/agri-robot-yolo.git
   ```
3. Flash the ESP32 with the motion & sensor control code (`esp32/agri_bot.ino` or `main.cpp`).

### 3. **Run the System**

* **Start YOLO detection:**

  ```bash
  python3 plant_detection.py
  ```
* **Control navigation:** via **web dashboard** (ESP32 Wi-Fi server) or manual joystick.

---

## 📐 Prototype Sketch

> *(Located in `extras/Prototype_sketch.png`)*

![Prototype Sketch](./extras/Prototype_sketch.png)
*Figure: Mechanical design & assembly layout of the agriculture robot.*

---

## 📷 Images & Screenshots

* **Prototype Images:** `extras/prototype/`
* **YOLO Detection Samples:** `extras/detections/`

![Prototype](./extras/prototype/agri_bot_setup.jpg)
*Figure: Semi-Autonomous Agriculture Robot prototype in testing phase.*

---

## 🚀 Future Improvements

* **AI-based Crop Disease Detection** using CNNs.
* **GPS + Path Planning** for large-scale field navigation.
* **Solar-Powered Operation** for extended field time.
* **Cloud Dashboard** for remote monitoring & control.

---

## 📄 License

This project is licensed under the **MIT License**. See [`LICENSE`](./LICENSE) for details.

---

## 👤 Author

**Hatim Ahmed Hassan** – 2025
📧 **[xayari229@gmail.com](mailto:xayari229@gmail.com)**

---

