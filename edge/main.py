import os
import time
import base64
import cv2
import requests
from vision import VisionEngine
from sensors import SensorManager
from actuators import ActuatorManager
from cloud_link import CloudLink

# Safety thresholds
TEMP_WARNING  = 35.0
TEMP_DANGER   = 40.0
GAS_WARNING   = 300.0

def evaluate_safety(vision_data, env_data, vib_data, gas_data):
    reasons = []
    alert_level = "SAFE"

    # PPE checks
    if vision_data.get("person_count", 0) > 0 and vision_data.get("helmet_count", 0) == 0:
        reasons.append("no_helmet")
        alert_level = "DANGER"
        
    if vision_data.get("person_count", 0) > 0 and vision_data.get("vest_count", 0) == 0:
        reasons.append("no_vest")
        alert_level = "DANGER"

    # Temperature checks
    temp = env_data.get("temperature")
    if temp is not None:
        if temp >= TEMP_DANGER:
            reasons.append("high_temperature")
            alert_level = "DANGER"
        elif temp >= TEMP_WARNING:
            reasons.append("temperature_warning")
            if alert_level == "SAFE":
                alert_level = "WARNING"

    # Gas check
    if gas_data.get("gas_detected"):
        reasons.append("gas_detected")
        if alert_level == "SAFE":
            alert_level = "WARNING"

    # Vibration check
    if vib_data.get("vibration_detected"):
        reasons.append("vibration_detected")
        if alert_level == "SAFE":
            alert_level = "WARNING"

    is_safe = alert_level == "SAFE"
    return is_safe, alert_level, reasons

def background_logic_loop(vision, sensors, actuators, cloud_link):
    loop_count = 0
    while True:
        # 1. Read all sensors
        env_data = sensors.read_environment()
        vib_data = sensors.read_vibration()
        gas_data = sensors.read_gas()

        # 2. Get latest vision data
        frame, vision_data = vision.process_frame()

        # 3. Evaluate safety
        is_safe, alert_level, reasons = evaluate_safety(
            vision_data, env_data, vib_data, gas_data
        )

        # 4. Trigger actuators
        if not is_safe:
            actuators.trigger_alarm()
        else:
            actuators.set_state_safe()

        print(f"[{alert_level}] Temp: {env_data['temperature']}C | "
              f"Humidity: {env_data['humidity']}% | "
              f"Gas: {gas_data['gas_detected']} | "
              f"Vibration: {vib_data['vibration_detected']} | "
              f"Vests: {vision_data.get('vest_count', 0)} | "
              f"Reasons: {reasons}")

        # 6. Encode frame as base64 JPEG
        frame_b64 = None
        if frame is not None:
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            frame_b64 = __import__("base64").b64encode(buffer).decode("utf-8")

        payload = {
            "helmet_detected": vision_data.get("helmet_count", 0) > 0,
            "vest_detected":   vision_data.get("vest_count", 0) > 0,
            "temperature_c":   env_data.get("temperature"),
            "humidity_pct":    env_data.get("humidity"),
            "gas_ppm":         gas_data.get("ppm"),
            "vibration_g":     1.0 if vib_data.get("vibration_detected") else 0.0,
            "is_safe":         is_safe,
            "alert_level":     alert_level,
            "alert_reasons":   reasons,
            "frame_b64":       frame_b64,
        }

        # 7. Publish to AWS every 10 seconds (every 20 loops at 0.5s interval)
        if loop_count % 20 == 0:
            cloud_link.publish_telemetry(payload)

        # 8. Push to local FastAPI every loop for smooth dashboard feed
        try:
            r = requests.post("http://127.0.0.1:8000/readings", json=payload, timeout=2)
            if r.status_code == 200:
                print("✅ Synchronized data to local dashboard")
        except Exception:
            pass

        loop_count += 1
        time.sleep(0.5)

def main():
    print("Initializing Headless Edge AI System...")

    sensors    = SensorManager()
    actuators  = ActuatorManager()
    cloud_link = CloudLink()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    engine = VisionEngine(model_path=os.path.join(BASE_DIR, "models/yolo11n_ncnn_model"))

    print("🤖 Edge Loop Started (No UI)... Press Ctrl+C to stop.")
    try:
        # Run straight on the main thread
        background_logic_loop(engine, sensors, actuators, cloud_link)
    except KeyboardInterrupt:
        print("\nStopping Edge AI system...")

if __name__ == "__main__":
    main()
