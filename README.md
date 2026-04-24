# Edge AI Construction Safety Monitoring System
### Group 11 — CM3603 Edge Artificial Intelligence

> A proactive Edge-AI prototype that uses a **Raspberry Pi 5** for real-time PPE detection and environmental sensing, with a cloud dashboard for remote oversight.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Resource Requirements](#3-resource-requirements)
4. [File Structure](#4-file-structure)
5. [How to Run](#5-how-to-run)
6. [Web Dashboard](#6-web-dashboard)
7. [Login Credentials](#7-login-credentials)
8. [API Endpoints](#8-api-endpoints)
9. [Data Flow](#9-data-flow)
10. [Functional Requirements Coverage](#10-functional-requirements-coverage)

---

## 1. Project Overview

Current industrial safety solutions are **reactive** — they record incidents after the fact. This system is **proactive**: the Raspberry Pi runs AI inference locally, detects PPE violations and environmental hazards in real time (sub-100ms), triggers on-site alarms, and simultaneously reports to a cloud dashboard accessible by supervisors.

**Key capabilities:**
- Real-time YOLOv11 (NCNN) detection of **Person**, **Helmet**, and **Safety Vest**
- Environmental monitoring via **DHT22** (temperature/humidity) and **MPU6050** (vibration)
- Local **buzzer + LED** actuators triggered immediately on violation
- **MQTT over AWS IoT Core** for secure cloud telemetry every 10 seconds
- **Streamlit web dashboard** with role-based access (Staff / Admin)
- **Live camera feed** streamed to the dashboard with PPE bounding boxes
- **Violation capture** — last unsafe frame stored and displayed as an alert image

---

## 2. System Architecture

The project follows a **three-tier architecture**:

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1 — End-Device Layer                              │
│  Camera (5MP) │ DHT22 Sensor │ Buzzer + Red/Green LEDs  │
└───────────────────────┬─────────────────────────────────┘
                        │ raw frames / sensor readings / GPIO
┌───────────────────────▼─────────────────────────────────┐
│  Tier 2 — Edge Layer (Raspberry Pi 5)                   │
│  VisionEngine (YOLOv11 NCNN)                            │
│  SensorManager (DHT22 polling + MPU6050)                │
│  MainController (data fusion + safety score)            │
│  LocalDashboard (Tkinter GUI)                           │
│  CloudLink (MQTT publisher + command subscriber)        │
└───────────────────────┬─────────────────────────────────┘
                        │ MQTT telemetry (JSON + frame_b64)
┌───────────────────────▼─────────────────────────────────┐
│  Tier 3 — Cloud Layer (AWS)                             │
│  AWS IoT Core → FastAPI (EC2) → SQLite DB               │
│  Streamlit Web Dashboard (Staff View + Admin View)      │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Resource Requirements

### Hardware
| Component | Specification |
|---|---|
| Edge Device | Raspberry Pi 5 (4 GB RAM) |
| Vision Sensor | Raspberry Pi Camera Module v1.3 (5 MP) |
| Temperature/Humidity | DHT22 sensor |
| Vibration | MPU6050 accelerometer |
| Actuators | 5V Active Buzzer + Red/Green LEDs |
| Connectivity | USB-C Power Supply, 32 GB+ Micro-SD |

### Software
| Component | Technology |
|---|---|
| OS | Raspberry Pi OS 64-bit |
| Language | Python 3.11 |
| ML Framework | Ultralytics YOLOv11 → exported to NCNN |
| Cloud | AWS IoT Core (MQTT) + AWS EC2 (FastAPI) |
| Edge Libraries | `opencv-python-headless`, `gpiozero`, `AWSIoTPythonSDK` |
| Dashboard | `streamlit`, `plotly`, `pandas` |

---

## 4. File Structure

```
edge-ai/
├── README.md                            # This file
├── requirements.txt                     # All project dependencies
├── train_and_export.py                  # YOLOv11 training & NCNN export script
├── train_colab.ipynb                    # Google Colab training notebook
├── test_output.jpg                      # Sample detection output image
├── safety_monitor.db                    # SQLite database (auto-created at runtime)
├── .gitignore                           # Ignores env/, certs/, model weights
│
├── models/
│   └── yolo11n_ncnn_model/              # Quantized NCNN model
│       ├── metadata.yaml                # Model metadata
│       ├── model.ncnn.bin               # NCNN binary weights
│       ├── model.ncnn.param             # NCNN network parameters
│       └── model_ncnn.py               # NCNN inference wrapper
│
├── edge/                                # Raspberry Pi codebase
│   ├── main.py                          # MainController — data fusion & orchestration
│   ├── vision.py                        # VisionEngine — YOLOv11 NCNN inference
│   ├── sensors.py                       # SensorManager — DHT22 & MPU6050
│   ├── actuators.py                     # GPIO — buzzer & LED control
│   ├── cloud_link.py                    # CloudLink — AWS IoT MQTT publisher
│   └── gui.py                           # Local Tkinter dashboard (runs on Pi)
│
├── cloud/
│   ├── app.py                           # FastAPI backend — active, deployed on EC2
│   ├── main.py                          # FastAPI backend — reference (commented out)
│   └── cloud_dashboard.py              # Alternative lightweight Streamlit dashboard
│
├── frontEnd/                            # Streamlit web dashboard
│   ├── app.py                           # Login page — entry point for all users
│   ├── requirements.txt                 # Frontend-only dependencies
│   ├── .streamlit/
│   │   └── config.toml                  # Streamlit theme & server configuration
│   ├── pages/
│   │   ├── 1_Staff_View.py              # Staff — live camera, PPE badges, sensors, alerts
│   │   ├── 2_Admin_View.py              # Admin — full dashboard, charts, quick controls
│   │   ├── 3_Analytics.py              # Historical trends, compliance, heatmap
│   │   ├── 4_Alerts.py                 # Alert log with filters & CSV export
│   │   └── 5_Control.py               # Emergency stop, commands, thresholds, simulation
│   └── utils/
│       ├── api_client.py               # HTTP client for all backend API calls
│       ├── auth.py                     # Login, session state, role-based page guards
│       ├── styles.py                   # Dark industrial theme CSS + Plotly layout
│       └── __init__.py
│
└── Sensors Test/
    └── sensors_test.py                 # Standalone sensor calibration & test script
```

---

## 5. How to Run

### Prerequisites
```bash
pip install fastapi uvicorn sqlalchemy scikit-learn numpy
pip install streamlit streamlit-autorefresh plotly pandas requests
```

### Step 1 — Start the Cloud Backend

Open **Terminal 1** from the project root:
```bash
cd edge-ai
uvicorn cloud.app:app --reload --host 0.0.0.0 --port 8000
```
Backend runs at `http://localhost:8000`

### Step 2 — Start the Web Dashboard

Open **Terminal 2**:
```bash
cd edge-ai/frontEnd
streamlit run app.py
```
Dashboard opens at `http://localhost:8501`

### Step 3 — Test Without a Raspberry Pi

1. Log in as **admin / admin123**
2. Navigate to **🎛️ Control Panel**
3. Click **Inject 10 Random Readings** to populate the dashboard with sample data
4. Switch to **Admin View** or **Staff View** to see live data

### Step 4 — Run on Raspberry Pi (Edge Device)

```bash
cd edge-ai/edge
python main.py
```
The Pi will start the VisionEngine, read sensors, display the local Tkinter GUI, and publish telemetry to AWS IoT Core.

> **Note:** AWS IoT certificates must be placed in `edge-ai/certs/` before connecting to the cloud.

---

## 6. Web Dashboard

The dashboard has **role-based access** with two views:

### Staff View (`/pages/1_Staff_View.py`)
Designed for on-site workers — **read-only**.

| Section | Description |
|---|---|
| Status Banner | SAFE / WARNING / DANGER with timestamp |
| Violation Alert | Red alert box listing missing PPE when unsafe |
| Live Camera Feed | Real-time frame from edge device with YOLO bounding boxes; **green border** when safe, **pulsing red border** when violated |
| PPE Compliance | Helmet ✅/❌ and Safety Vest ✅/❌ badges |
| Latest Violation Capture | Saved frame from the moment a violation was detected |
| Environmental Sensors | Temperature, Humidity, Gas (PPM), Vibration with colour-coded thresholds |

### Admin / Manager View (`/pages/2_Admin_View.py`)
Full access for supervisors.

| Section | Description |
|---|---|
| Factory Header | Factory location + Device health status |
| Everything in Staff View | Live feed, PPE status, sensors |
| Safety Compliance % Chart | Rolling compliance % over last 24 hours |
| Sensor Trend Charts | Temperature, Humidity, Gas, Vibration over time |
| Recent Alert History | Last 15 unsafe events with full details |
| Quick Controls | Emergency Stop, Remote Reset, Capture Frame, Threshold Adjuster |

### Admin-Only Pages
| Page | Description |
|---|---|
| Analytics | Historical PPE compliance, sensor stats, alert distribution, correlation heatmap |
| Alert Log | Filterable event history with CSV export and alert reasons breakdown |
| Control Panel | Emergency Stop, device commands, threshold sliders (Temp/Gas/Vibration), simulation tools |

---

## 7. Login Credentials

| Username | Password | Role | Access |
|---|---|---|---|
| `admin` | `admin123` | Admin | All pages |
| `manager` | `manager123` | Admin | All pages |
| `staff` | `staff123` | Staff | Staff View only |
| `worker` | `worker123` | Staff | Staff View only |

> Credentials are defined in `frontEnd/utils/auth.py` — update them before deployment.

---

## 8. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/stats` | Aggregate stats (total, unsafe count, safe %, current status) |
| `GET` | `/readings/latest?limit=N` | Last N readings with all sensor + PPE fields |
| `POST` | `/readings` | Submit a new reading (from edge or simulation) |
| `GET` | `/frame/latest` | Latest JPEG camera frame |
| `GET` | `/frame/alert` | Last frame captured during a violation |
| `POST` | `/commands` | Queue a command for the edge device via MQTT |

### Reading payload fields
```json
{
  "helmet_detected": true,
  "vest_detected": false,
  "temperature_c": 36.5,
  "humidity_pct": 62.0,
  "gas_ppm": 120.0,
  "vibration_g": 0.3,
  "is_safe": false,
  "alert_level": "DANGER",
  "alert_reasons": ["no_vest"],
  "frame_b64": "<base64-encoded JPEG>"
}
```

### Supported edge commands
| Command | Payload | Description |
|---|---|---|
| `EMERGENCY_STOP` | — | Halt inference + trigger alarm |
| `RESET_SAFE` | — | Clear alert state |
| `TEST_ALARM` | `{"duration_s": 3}` | Test buzzer |
| `CAPTURE_FRAME` | — | Force a frame capture |
| `RESTART_VISION` | — | Restart the VisionEngine |
| `SET_TEMP_THRESHOLD` | `{"celsius": 35}` | Update temperature threshold |
| `SET_GAS_THRESHOLD` | `{"ppm": 300}` | Update gas threshold |
| `SET_VIB_THRESHOLD` | `{"g": 1.5}` | Update vibration threshold |

---

## 9. Data Flow

```
Raspberry Pi
  │
  ├─ Camera → VisionEngine (YOLOv11 NCNN)
  │             └─ DetectionResult (helmet, vest, person, frame_b64)
  │
  ├─ DHT22/MPU6050 → SensorManager
  │                    └─ SensorReading (temp, humidity, vibration)
  │
  └─ MainController
       ├─ Data fusion (PPE + sensors → safety score)
       ├─ GPIO → Buzzer/LED (local alert)
       ├─ LocalDashboard → Tkinter GUI (on-device display)
       └─ CloudLink → MQTT → AWS IoT Core
                               └─ FastAPI (EC2)
                                    ├─ SQLite (persist readings)
                                    ├─ IsolationForest (anomaly detection)
                                    ├─ /frame/latest (JPEG cache)
                                    └─ /frame/alert (violation snapshot)
                                         └─ Streamlit Dashboard
                                              ├─ Staff View (read-only)
                                              └─ Admin View (full control)
```

---

## 10. Functional Requirements Coverage

| FR | Requirement | Status |
|---|---|---|
| FR-1 | Real-time detection of Person, Helmet, Safety Vest (≥70% confidence) |  VisionEngine |
| FR-2 | PPE violation identification and labelling |  Bounding boxes + PPE badges |
| FR-3 | Continuous sensor data monitoring (temp, gas, vibration) |  SensorManager |
| FR-4 | Sensor threshold evaluation |  MainController + Control Panel |
| FR-5 | Sensor fusion (PPE + temp > 35°C → alert) |  MainController, 35°C default |
| FR-6 | On-screen safety alert generation |  Status banner + violation box |
| FR-7 | Edge AI inference without internet |  NCNN local inference |
| FR-8 | Cloud telemetry every 10 seconds |  CloudLink MQTT |
| FR-9 | Supervisor dashboard access |  Admin View |
| FR-10 | Remote Emergency Stop command |  Control Panel + Admin View |
| FR-11 | Threshold configuration for all sensors |  Temp, Gas, Vibration sliders |
| FR-12 | System maintenance and AI model update |  Control Panel commands |

---

## Team

| Name | Student ID |
|---|---|
| Ikraam Imtiaz | 20231249 |
| Ahamed Ammaar | 20221721 |
| Angathan Peranantham | 20231978 |
| Manuga Perera | 20210970 |

**Module:** CM3603 Edge Artificial Intelligence — Robert Gordon University / IIT
