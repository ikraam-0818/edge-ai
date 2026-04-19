import time
import threading
from vision import VisionEngine
from sensors import SensorManager
from actuators import ActuatorManager
from cloud_link import CloudLink
from gui import LocalDashboard
import tkinter as tk

# Safety thresholds
TEMP_WARNING  = 35.0
TEMP_DANGER   = 40.0
GAS_WARNING   = 300.0

def evaluate_safety(vision_data, env_data, vib_data, gas_data):
    reasons = []
    alert_level = "SAFE"

    # PPE checks
    if vision_data.get("no_helmet_violations", 0) > 0:
        reasons.append("no_helmet")
        alert_level = "DANGER"
    elif vision_data.get("person_count", 0) > 0 and vision_data.get("helmet_count", 0) == 0:
        reasons.append("no_helmet")
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

def background_logic_loop(vision, sensors, actuators, cloud_link, app):
    while True:
        # 1. Read all sensors
        env_data = sensors.read_environment()
        vib_data = sensors.read_vibration()
        gas_data = sensors.read_gas()

        # 2. Get latest vision data
        _, vision_data = vision.process_frame()

        # 3. Evaluate safety
        is_safe, alert_level, reasons = evaluate_safety(
            vision_data, env_data, vib_data, gas_data
        )

        # 4. Trigger actuators
        if not is_safe:
            actuators.trigger_alarm()
        else:
            actuators.set_state_safe()

	# Update GUI with sensor data
        app.update_sensor_display(
            {
                "temperature": env_data.get("temperature"),
                "humidity": env_data.get("humidity"),
                "gas_detected": gas_data.get("gas_detected"),
                "vibration_detected": vib_data.get("vibration_detected"),
            },
            alert_level
        )

        # 5. Log to console
        print(f"[{alert_level}] Temp: {env_data['temperature']}C | "
              f"Humidity: {env_data['humidity']}% | "
              f"Gas: {gas_data['gas_detected']} | "
              f"Vibration: {vib_data['vibration_detected']} | "
              f"Helmet violations: {vision_data.get('no_helmet_violations', 0)} | "
              f"Reasons: {reasons}")

        # 6. Publish to cloud
        payload = {
            "helmet_detected": vision_data.get("helmet_count", 0) > 0,
            "vest_detected":   False,
            "temperature_c":   env_data.get("temperature"),
            "humidity_pct":    env_data.get("humidity"),
            "gas_ppm":         gas_data.get("ppm"),
            "vibration_g":     1.0 if vib_data.get("vibration_detected") else 0.0,
            "is_safe":         is_safe,
            "alert_level":     alert_level,
            "alert_reasons":   reasons,
        }
        cloud_link.publish_telemetry(payload)

        time.sleep(2)

def main():
    print("Initializing Edge AI System...")

    sensors    = SensorManager()
    actuators  = ActuatorManager()
    cloud_link = CloudLink()

    print("Starting Tkinter Dashboard...")
    root   = tk.Tk()
    engine = VisionEngine(model_path="../models/yolo11n_ncnn_model")
    app    = LocalDashboard(root, engine)

    logic_thread = threading.Thread(
        target=background_logic_loop,
        args=(engine, sensors, actuators, cloud_link, app),
        daemon=True
    )
    logic_thread.start()

    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
