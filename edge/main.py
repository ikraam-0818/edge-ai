import os
import time
import base64
import cv2
import requests
import threading
from vision import VisionEngine
from sensors import SensorManager
from actuators import ActuatorManager
from cloud_link import CloudLink

# Safety thresholds
TEMP_WARNING = 35.0
TEMP_DANGER  = 40.0

# Shared state between threads
_frame_lock   = threading.Lock()
_latest_frame = None
_latest_vision = {"helmet_count": 0, "vest_count": 0, "person_count": 0}

def vision_thread(vision):
    """Runs YOLO inference continuously in its own thread."""
    global _latest_frame, _latest_vision
    print("Vision thread started.")
    while True:
        try:
            frame, detections = vision.process_frame()
            if frame is not None:
                with _frame_lock:
                    _latest_frame  = frame
                    _latest_vision = detections
        except Exception as e:
            print(f"Vision thread error: {e}")
        # No sleep — run as fast as the Pi allows

def evaluate_safety(vision_data, env_data, vib_data, gas_data):
    reasons     = []
    alert_level = "SAFE"

    if vision_data.get("person_count", 0) > 0:
        if vision_data.get("helmet_count", 0) == 0:
            reasons.append("no_helmet")
            alert_level = "DANGER"
        if vision_data.get("vest_count", 0) == 0:
            reasons.append("no_vest")
            alert_level = "DANGER"

    temp = env_data.get("temperature")
    if temp is not None:
        if temp >= TEMP_DANGER:
            reasons.append("high_temperature")
            alert_level = "DANGER"
        elif temp >= TEMP_WARNING:
            reasons.append("temperature_warning")
            if alert_level == "SAFE":
                alert_level = "WARNING"

    if gas_data.get("gas_detected"):
        reasons.append("gas_detected")
        if alert_level == "SAFE":
            alert_level = "WARNING"

    if vib_data.get("vibration_detected"):
        reasons.append("vibration_detected")
        if alert_level == "SAFE":
            alert_level = "WARNING"

    return alert_level == "SAFE", alert_level, reasons

def main_loop(sensors, actuators, cloud_link):
    loop_count = 0
    while True:
        # 1. Read sensors
        env_data = sensors.read_environment()
        vib_data = sensors.read_vibration()
        gas_data = sensors.read_gas()

        # 2. Grab latest vision data from vision thread
        with _frame_lock:
            vision_data = _latest_vision.copy()
            frame       = _latest_frame

        # 3. Evaluate safety
        is_safe, alert_level, reasons = evaluate_safety(
            vision_data, env_data, vib_data, gas_data
        )

        # 4. Actuators
        if not is_safe:
            actuators.trigger_alarm()
        else:
            actuators.set_state_safe()

        print(f"[{alert_level}] "
              f"Temp: {env_data.get('temperature')}C | "
              f"Humidity: {env_data.get('humidity')}% | "
              f"Gas: {gas_data.get('gas_detected')} | "
              f"Vib: {vib_data.get('vibration_detected')} | "
              f"Helmets: {vision_data.get('helmet_count',0)} | "
              f"Vests: {vision_data.get('vest_count',0)} | "
              f"Reasons: {reasons}")

        # 5. Encode frame
        frame_b64 = None
        if frame is not None and loop_count % 3 == 0:
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
            frame_b64 = base64.b64encode(buffer).decode("utf-8")

        payload = {
            "helmet_detected": vision_data.get("helmet_count", 0) > 0,
            "vest_detected":   vision_data.get("vest_count",  0) > 0,
            "temperature_c":   env_data.get("temperature"),
            "humidity_pct":    env_data.get("humidity"),
            "gas_ppm":         gas_data.get("ppm"),
            "vibration_g":     None,
            "is_safe":         is_safe,
            "alert_level":     alert_level,
            "alert_reasons":   reasons,
            "frame_b64":       frame_b64,
        }

        # 6. Publish to AWS every 10 seconds
        if loop_count % 20 == 0:
            cloud_link.publish_telemetry(payload)

        # 7. Push to local FastAPI every loop
        try:
            r = requests.post("http://127.0.0.1:8000/readings", json=payload, timeout=2)
            if r.status_code == 200:
                print("✅ Dashboard synced")
        except Exception:
            pass

        loop_count += 1
        time.sleep(0.3)  # 0.3s = ~3 updates/sec to dashboard

def main():
    print("Initializing Edge AI System...")

    sensors   = SensorManager()
    actuators = ActuatorManager()
    cloud_link = CloudLink()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vision = VisionEngine(
        model_path=os.path.join(BASE_DIR, "models/yolo11n_ncnn_model")
    )

    # Start vision in its own thread
    t = threading.Thread(target=vision_thread, args=(vision,), daemon=True)
    t.start()

    print("Edge loop started. Press Ctrl+C to stop.")
    try:
        main_loop(sensors, actuators, cloud_link)
    except KeyboardInterrupt:
        print("\nStopping Edge AI system...")
    finally:
        vision.cleanup()

if __name__ == "__main__":
    main()
