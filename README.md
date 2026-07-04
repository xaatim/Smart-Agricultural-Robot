
<div align="center">

# Beam Agri-Bot (V1 Prototype)
### IoT-Enabled Precision Dosing & Vision System

[![Status](https://img.shields.io/badge/Status-Proof_of_Concept-yellow)]()
[![Hardware](https://img.shields.io/badge/Hardware-ESP32-blue?logo=espressif&logoColor=white)]()
[![Vision](https://img.shields.io/badge/Vision-YOLO--World-red)]()
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Beam Robotics](https://img.shields.io/badge/Beam-Robotics-darkblue)](https://github.com/xaatim)

*Note: This repository represents the archived Phase 1 Field Prototype. For the latest active development and ongoing ROS2 evolution of this platform, please see the **[Beam AgroBot V2 Workspace](https://github.com/xaatim/beam_agrobot_v2)**.*

</div>

---

## Overview

The Beam Agri-Bot V1 is an IoT-enabled mobile manipulation platform designed for high-precision agricultural intervention. By combining real-time object detection with targeted chemical dosing, the system minimizes waste and maximizes crop health through intelligent automation.

This Phase 1 prototype served as our initial hardware proof of concept to validate a remote software-to-hardware triggering loop: running heavy computer vision inference over an incoming video stream on a laptop server, which dynamically commands an onboard ESP32 microcontroller over Wi-Fi to actuate precision spraying.

The Agri-Bot V1 is a foundational milestone of **[Beam Robotics](https://github.com/xaatim)** — an applied robotics initiative founded by **[Hatim Ahmed Hassan](https://www.linkedin.com/in/hatim-ahmed-713214194)**. Beam Robotics serves as the unified development umbrella for a portfolio of advanced autonomous systems focused on agriculture, infrastructure, and industrial automation.

---

## Hardware Design & 3D Architecture

The V1 prototype was built on a lightweight microcontroller edge architecture, focusing heavily on modular physical component iteration:

* **Processing Split:** A laptop acts as the high-level brain running the primary Python script and AI model, while an onboard ESP32 handles low-level pin execution, sensor reading, and pump activation.
* **Navigation:** Manual / teleoperated driving. The operator guides the mobile chassis down a crop row to position the system over targets.
* **Actuation:** A fixed-position, rigid 3D-printed arm optimized for target delivery straight to plant centers.

### Custom 3D Components
The chassis houses custom-designed 3D-printed components optimized for structural stability and optical alignment:

- **Integrated Sensor Handle:** A specialized mount designed to house both the primary ESP32-CAM and the ultrasonic distance sensors, keeping the vision pipeline and physical measurement frames aligned.
- **Actuation Arm (v1):** A fixed-position vertical delivery mount that facilitates direct liquid micro-dosing to detected plant centers.

| 3D Handle (Camera/Ultrasonic) | 3D Fixed Arm Design |
| :---: | :---: |
| ![Handle](docs/hardware/3d_sensor_handle.png) | ![Arm](docs/hardware/3d_fixed_arm.png) |

---

## Computer Vision & Sensor Fusion Loop

The platform features a highly adaptive **YOLO-World (Zero-shot)** object detection engine, allowing it to instantly identify and extract crops or weeds without requiring localized pre-training datasets.


```

Onboard ESP32-CAM → streams live video over Wi-Fi → Laptop Python Server
↓
Onboard Ultrasonic → distance sensor cross-checks target → YOLO-World Model
↓
ESP32 activates pumps ← triggers micro-dose command ← AI confirms target

```

* **Trigger Logic:** The laptop handles incoming frames from the ESP32-CAM. When a targeted plant enters the camera's "Dosing Zone," an integrated **ultrasonic distance sensor** cross-checks the crop's spatial proximity. Once confirmed by the AI pipeline, the server calculates the exact physical delay offset and commands the ESP32 via sockets to actuate the relays.
* **Monitoring:** Live inference metadata and performance telemetry are pushed directly to the cloud for real-time remote auditing.

### 🎥 System Demonstration
[Watch the AI Detection Loop on GitHub](https://github.com/user-attachments/assets/c4a1654d-c4e3-4ebb-b27a-4d20b6db65e0)

---

## Evolution to V2

While successful in proving the viability of automated computer vision micro-dosing, field testing exposed physical and architectural constraints:
* **Manipulation Constraints:** The fixed-arm system lacked the mechanical dexterity required to maneuver over uneven terrain or handle varying crop heights.
* **Autonomy Limitations:** Manual teleoperation limited the platform's scalability for large-scale field deployment.
* **Middleware Bottlenecks:** Standard Python-to-ESP32 socket structures lacked the industrial-grade synchronization needed for full fleet operations.

**These limitations directly inspired the design of [Beam AgroBot V2](https://github.com/xaatim/beam_agrobot_v2):**
* **ROS2 Humble Migration:** Re-architecting the system into a standardized, distributed, and deterministic middleware ecosystem.
* **5-DOF Manipulator:** Transitioning from a static fixed nozzle to a fully articulated robotic arm driven by MoveIt2 and TRAC-IK kinematics.
* **Nav2 Autonomous Driving:** Upgrading the chassis navigation stack with LiDAR, SLAM Toolbox mapping, and AMCL localization.

---

## Architecture Stack

| Component | Technology |
|---|---|
| Edge Compute | ESP32 + ESP32-CAM |
| Host Processing | Python 3.10 + OpenCV |
| Core Vision | YOLO-World (Zero-shot Inference) |
| Networking | WebSockets / Socket.io Client |
| Local Sensing | Ultrasonic Time-of-Flight Sensors |
| Mechanical Actuation | Onboard Relays + Peristaltic Pumps |
| Dashboard Support | Beam Command Center Backend |

---

## Installation & Usage

**1. Firmware Setup:**
Open the `firmware/` directory in the Arduino IDE or PlatformIO, configure your Wi-Fi credentials, and flash the sketch to your ESP32 board.

**2. Host System Setup:**
Ensure your host machine is running Python 3.10+, then install the processing dependencies:
```bash
pip install ultralytics socketio-client opencv-python

```

**3. Run the Inference Engine:**

```bash
python agri_vision_main.py

```

---

## Beam Robotics Integration

The Agri-Bot V1 pairs directly with the **[Beam Command Center](https://github.com/xaatim/Beam-Command-Center)**. Each unit registers using a cryptographically signed serial key, allowing remote operators to monitor real-time dosing logs, chemical tank volumes, and general battery state of charge directly via the global Beam portal.

---

## Author

**Hatim Ahmed Hassan**
*Lead Architect & Co-Founder, Beam Robotics*

---

*Licensed under the MIT License*

