# Edge AI Safety Monitor — Deployment Guide

This document outlines the exact commands required to run the Edge AI Safety Monitor system in its dual-deployment architecture (Local Edge vs. Remote Cloud).

---

## 🏗️ 1. Running on the Raspberry Pi (Local Edge)
The Raspberry Pi acts as the physical edge node. It reads the camera, calculates AI inferences, controls the physical sensors/actuators, and provides a raw, live Dashboard directly to onsite workers.

To spin up the full Edge node, you must open **3 separate terminal windows** on the Pi.

### Terminal 1: Local Backend & Database
This runs the local API server and SQLite database that stores events from the AI engine.
```bash
# Navigate to project root
source env/bin/activate
uvicorn cloud.app:app --host 0.0.0.0 --port 8000
```

### Terminal 2: AI Engine (The Brain)
This runs the headless `main.py` daemon. It opens the webcam, reads sensors, triggers the buzzer on PPE violations, pushes data to `localhost:8000` (for the local Streamlit), and simultaneously pushes a payload to AWS IoT Core over MQTT.
```bash
# Navigate to project root
source env/bin/activate
python edge/main.py
```

### Terminal 3: Local Dashboard (Streamlit)
This launches the frontend dashboard. Because this is the *Local Setup*, it will actively stream the live 30FPS camera feed with bounding boxes.
```bash
# Navigate to project root
source env/bin/activate
cd frontEnd
streamlit run app.py
```
👉 Open your browser to `http://localhost:8501` on the Pi to view the live dashboard.

---

## ☁️ 2. Running on the EC2 Instance (Remote Cloud)
The EC2 instance is completely independent of the physical factory environment. It acts purely as a remote receiver for managers. 

To spin up the Cloud node, you need **2 separate terminal windows** connected via SSH to your EC2 instance.

### Terminal 1: Cloud Backend & MQTT Subscriber
This runs the cloud database. Because it is connected to AWS IoT, it idly waits and automatically saves any MQTT payloads beamed up by the physical Raspberry Pi.
```bash
# SSH into EC2, activate environment
uvicorn cloud.app:app --host 0.0.0.0 --port 8000
```

### Terminal 2: Cloud Dashboard (Streamlit - Bandwidth Saver Mode)
This launches the same standard dashboard but uses the `DASHBOARD_MODE=CLOUD` environment variable. 
This flag intelligently disables the live video player to save server bandwidth, leaving a clean dashboard that only shows graphs, counters, and high-res snapshots captured exactly at the moment of an active violation.
```bash
# SSH into EC2, activate environment
cd frontEnd
DASHBOARD_MODE=CLOUD streamlit run app.py --server.port 8501
```
👉 Open your browser to `http://<EC2_PUBLIC_IP>:8501` to access the remote management view.

---

## 💻 3. Local Desktop Testing (Mac / PC)
If you want to instantly test how *both* dashboards look side-by-side on your own computer without touching AWS or Raspberry Pis:

1. Start your local backend `uvicorn cloud.app:app --host 0.0.0.0 --port 8000`
2. Start the AI engine `python edge/main.py`
3. Launch the Local dashboard: `streamlit run frontEnd/app.py --server.port 8501`
4. Launch the Cloud dashboard concurrently: `DASHBOARD_MODE=CLOUD streamlit run frontEnd/app.py --server.port 8502`

You can now view the **Live Local Version** at `localhost:8501` and the **Bandwidth-Saving Cloud Version** at `localhost:8502`!
