
<div align="center">

# Beam Agri-Bot V1
### Precision Dosing & Vision System | YOLO-World + ESP32 + Teleoperation

![Python](https://img.shields.io/badge/python-3.10-blue?logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-YOLO--World-red)
![Status](https://img.shields.io/badge/Status-Archived--Prototype-yellow)
![License](https://img.shields.io/badge/License-MIT-blue)

*Note: This repository represents the archived Phase 1 Field Prototype. For the latest active development and ongoing ROS2 evolution of this platform, please see the **[Beam AgroBot V2 Workspace](https://github.com/xaatim/beam_agrobot_v2)**.*

</div>

---

## Overview

The **Beam Agri-Bot V1** is a teleoperated agricultural robot built to validate the core vision-to-actuation loop for precision crop dosing. A host laptop acts as the "brain" — running YOLO-World zero-shot detection on a live video feed — while an onboard ESP32 handles low-level hardware control, receiving fire commands over a Wi-Fi socket connection.

This is the field-tested prototype phase of the AgroBot platform, focused on proving that AI-driven detection could reliably trigger real-world pump actuation before investing in full autonomy. It is the direct predecessor to the fully autonomous **[AgroBot V2](https://github.com/xaatim/Beam-AgroBot-V2)**.

The Agri-Bot V1 is a core product of **[Beam Robotics](https://github.com/xaatim/Beam-Command-Center)** — an applied robotics initiative and prospective startup founded by **[Hatim Ahmed Hassan](https://www.linkedin.com/in/hatim-ahmed-713214194)**.

---

## System Architecture

V1 uses a split processing architecture — a host laptop for perception and decision-making, and an ESP32 for real-time actuation:

```
ESP32-CAM → Wi-Fi video stream → Laptop (Python)
                                      ↓
                          YOLO-World (zero-shot detection)
                                      ↓
                    Ultrasonic ToF sensor → confirms Dosing Zone
                                      ↓
                     Laptop calculates delay offset
                                      ↓
                  Socket command → ESP32 → Pump/Relay fires
```

**Core components:**

- **Host Laptop ("Brain")** — Runs Python + YOLO-World for zero-shot crop/weed detection on the incoming video stream. No local training required per crop type.
- **ESP32-CAM** — Streams live video over Wi-Fi to the laptop for inference.
- **ESP32 (Controller)** — Onboard low-level controller that receives socket commands and fires the pumps/relays. Does not run any AI itself.
- **Ultrasonic ToF Sensors** — Physically verify the plant is within the exact "Dosing Zone" distance before actuation is triggered, complementing the vision system.
- **Teleoperated Chassis** — Manually driven; no autonomous navigation in V1.

---

## Hardware Design

Custom 3D-printed components were designed for sensor integration and structural stability.

**Key components:**

- **Integrated Sensor Handle** — A specialized 3D-printed mount housing both the vision camera and ultrasonic sensors, keeping detection and distance-verification aligned.
- **Fixed-Position Actuation Arm** — A static 3D-printed arm that dispenses liquid to detected plant centers via peristaltic pumps and relays. No multi-axis movement.

| 3D Handle (Camera/Ultrasonic) | 3D Fixed Arm Design |
|---|---|
| ![Handle](docs/hardware/3d_sensor_handle.png) | ![Arm](docs/hardware/3d_fixed_arm.png) |

---

## Prototype Evolution

The project moved from a digital-twin phase into physical field testing. The prototype below validates the full software-to-hardware trigger loop.

<p align="center">
  <img src="docs/hardware/prototype_v1.png" width="45%" />
  <img src="docs/hardware/prototype_v2.png" width="45%" />
</p>

---

## Computer Vision & Trigger Loop

The system uses **YOLO-World** (zero-shot detection), allowing the robot to identify specific crops or weeds without dedicated per-crop training.

**Trigger logic:**
1. YOLO-World detects and classifies the target crop/weed in the live feed.
2. The ultrasonic sensor confirms the plant has physically entered the Dosing Zone.
3. The laptop calculates the required timing/delay offset.
4. A socket command is sent to the ESP32, which fires the pumps.

**Monitoring:** Live inference data is relayed to the cloud for performance auditing.

### System Demonstration

<div align="center">

[https://github.com/user-attachments/assets/c4a1654d-c4e3-4ebb-b27a-4d20b6db65e0](https://github.com/user-attachments/assets/c4a1654d-c4e3-4ebb-b27a-4d20b6db65e0)

</div>

---

## Limitations & Path to V2

V1 served its purpose as a proof of concept for the detection-to-actuation pipeline, but had clear structural limits that directly motivated the V2 redesign:

- **No autonomy** — chassis was fully teleoperated, no SLAM/Nav2.
- **Fixed-position arm** — no dexterity for varying crop heights or terrain.
- **Split-brain latency** — dependent on a stable Wi-Fi link between laptop and ESP32-CAM.
- **2D distance-only targeting** — ultrasonic confirmed proximity but gave no 3D XYZ localization.

These limitations were directly addressed in **[AgroBot V2](https://github.com/xaatim/Beam-AgroBot-V2)** with full ROS2 Humble migration, Nav2 autonomous navigation, a 5-DOF MoveIt2-controlled arm, and RGB-D 3D crop localization.

---

## Beam Robotics Ecosystem

The Agri-Bot V1 is registered and monitored through the **Beam Command Center** — a centralized platform for managing all Beam Robotics products. Each unit is paired via a cryptographic serial key and streams dosing logs, chemical levels, and battery health to the operator dashboard.

**Other Beam Robotics products:**
- [AgroBot V2](https://github.com/xaatim/Beam-AgroBot-V2) — fully autonomous ROS2 precision agricultural robot
- [Beam Access Control System](https://github.com/xaatim/SmartAccessControl) — biometric access, license plate recognition, surveillance
- [Beam Surveillance Bot](https://github.com/xaatim/Autonomous_security_robot) — autonomous patrol robot with face recognition

---

## Installation & Usage

1. **Hardware:** Flash the `firmware/` directory to your ESP32/ESP32-CAM.
2. **Software:**
```bash
pip install ultralytics socketio-client opencv-python
python agri_vision_main.py
```

---

## Author

**Hatim Ahmed Hassan**
Lead Architect & Co-Founder, Beam Robotics

[![GitHub](https://img.shields.io/badge/GitHub-xaatim-black)](https://github.com/xaatim)

---

*Licensed under the MIT License*
