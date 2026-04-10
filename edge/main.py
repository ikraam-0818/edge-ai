import time
import threading

# Import the team's modules!
from vision import VisionEngine
from sensors import SensorManager
from actuators import ActuatorManager
from cloud_link import CloudLink

# If running headlessly (no screen), Tkinter isn't needed.
# But since we built the GUI, we can import it here.
from gui import LocalDashboard
import tkinter as tk

def background_logic_loop(vision, sensors, actuators, cloud_link):
    """
    This loop runs in the background of the UI, continuously polling sensors 
    and enforcing the safety logic.
    """
    while True:
        # 1. Read Sensors
        env_data = sensors.read_environment()
        vib_data = sensors.read_vibration()
        
        # 2. Get Vision Stats (Assuming vision.process_frame updates an internal state, 
        # or we pull latest stats if the GUI is driving the camera)
        # For simplicity, we just aggregate the hardware stats here 
        # and push everything to AWS every 5 seconds.
        
        payload = {
            "timestamp": int(time.time()),
            "temperature": env_data["temperature"],
            "vibration_x": vib_data["accel_x"],
            # "violations": We grab this from vision engine if decoupled
        }
        
        # 3. Decision Logic 
        if env_data["temperature"] > 40.0:
            print(f"HOT TEMPERATURE DETECTED: {env_data['temperature']}C")
            actuators.trigger_alarm()
            
        # 4. Push to Cloud
        cloud_link.publish_telemetry(payload)
        
        time.sleep(5) # Delay for the background loop

def main():
    print("Initializing Edge AI System...")
    
    # Initialize all modules
    sensors = SensorManager()
    actuators = ActuatorManager()
    cloud_link = CloudLink()
    
    # Note: VisionEngine is initialized via the GUI if we use Tkinter
    print("Starting Tkinter Dashboard...")
    root = tk.Tk()
    
    # Needs absolute path depending on runtime loc
    engine = VisionEngine(model_path="../models/yolo11n_ncnn") 
    app = LocalDashboard(root, engine)
    
    # Start the logic thread concurrently with the GUI
    logic_thread = threading.Thread(
        target=background_logic_loop, 
        args=(engine, sensors, actuators, cloud_link),
        daemon=True
    )
    logic_thread.start()
    
    # Run UI
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
