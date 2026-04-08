Edge AI Construction Safety Monitoring System

---

## 1. Project Overview
This is a proactive prototype Edge-AI system that uses a **Raspberry Pi 5** to perform real-time Computer Vision for PPE compliance and environmental sensing for temperature and vibration monitoring.

---

## 2. System Architecture
The project follows a **three-tier architecture**:

1.  **Tier 1 - End-Device Layer:** Handles raw data collection from the USB Webcam, DHT22 (Temp/Humidity), and MPU6050 (Vibration).
2.  **Tier 2 - Edge Layer:** The "Brain" (Raspberry Pi 5) which manages image preprocessing, YOLOv11 inference via NCNN, and local GPIO actuators.
3.  **Tier 3 - Cloud Layer:** AWS environment utilizing IoT Core for MQTT messaging and EC2 for the web dashboard.

---

## 3. Resource Requirements

### Hardware Requirements
* **Edge Device:** Raspberry Pi 5 (4GB RAM).
* **Vision Sensor:** USB Webcam (replaces the Pi Camera Module v1.3 for this implementation).
* **Environmental Sensors:** DHT22 (Temperature/Humidity) and MPU6050 (Vibration/Accelerometer).
* **Actuators:** 5V Active Buzzer and Red/Green LEDs.
* **Connectivity:** USB-C Power Supply and 32GB+ Micro-SD Card.

### Software Requirements
* **OS:** Raspberry Pi OS (64-bit).
* **Language:** Python 3.11.
* **ML Frameworks:** Ultralytics YOLOv11 (optimized with NCNN).
* **Cloud Services:** AWS IoT Core (MQTT) and AWS EC2 (Hosting).
* **Libraries:** `opencv-python-headless`, `adafruit-circuitpython-dht`, `AWSIoTPythonSDK`, `Tkinter`, `gpiozero`.

---

## 4. File Structure
```text
edge-ai/
├── .gitignore               # Ignores env/, certs/, and model weights
├── README.md                # Project documentation
├── requirements.txt         # Project dependencies
│
├── edge/                    # Raspberry Pi Codebase
│   ├── main.py              # Main Controller & Data Fusion
│   ├── vision.py            # VisionEngine (YOLOv11 & Webcam)
│   ├── sensors.py           # SensorManager (DHT22 & MPU6050)
│   ├── actuators.py         # GPIO Logic (Buzzer & LEDs)
│   └── cloud_link.py        # CloudLink (AWS IoT MQTT)
│
├── models/                  # AI Model storage
│   └── yolo11n_ncnn/        # Quantized NCNN model files
│
└── cloud/                   # AWS Side Implementation
    └── app.py               # FastAPI backend for EC2 dashboard

