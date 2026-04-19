import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
from vision import VisionEngine

class LocalDashboard:
    def __init__(self, root, vision_engine):
        self.root = root
        self.root.title("Edge AI Safety Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg="#2d2d2d")
        
        self.vision = vision_engine
        self.sensor_data = {}

        # --- UI Layout ---
        self.lbl_title = tk.Label(root, text="Construction Safety Dashboard", 
                                   font=("Helvetica", 20, "bold"), bg="#2d2d2d", fg="white")
        self.lbl_title.pack(pady=10)

        # Main frame
        self.main_frame = tk.Frame(root, bg="#2d2d2d")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Left Side: Camera Feed
        self.video_frame = tk.Label(self.main_frame, bg="black")
        self.video_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Right Side: Statistics Panel
        self.stats_panel = tk.Frame(self.main_frame, bg="#3d3d3d", width=250)
        self.stats_panel.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Vision Stats
        tk.Label(self.stats_panel, text="👁 Vision", font=("Helvetica", 13, "bold"),
                 bg="#3d3d3d", fg="#58a6ff").pack(pady=(15,5), anchor="w", padx=10)
        self.lbl_people     = self._create_stat_label("People: 0")
        self.lbl_helmets    = self._create_stat_label("Helmets: 0", fg="#4CAF50")
        self.lbl_violations = self._create_stat_label("Violations: 0", fg="#f44336")

        # Divider
        tk.Label(self.stats_panel, text="─" * 28, bg="#3d3d3d", fg="gray").pack(pady=5)

        # Environment Stats
        tk.Label(self.stats_panel, text="🌡 Environment", font=("Helvetica", 13, "bold"),
                 bg="#3d3d3d", fg="#58a6ff").pack(pady=(5,5), anchor="w", padx=10)
        self.lbl_temp     = self._create_stat_label("Temp: -- °C", fg="orange")
        self.lbl_humidity = self._create_stat_label("Humidity: -- %", fg="cyan")
        self.lbl_gas      = self._create_stat_label("Gas: --", fg="yellow")
        self.lbl_vib      = self._create_stat_label("Vibration: --", fg="white")

        # Divider
        tk.Label(self.stats_panel, text="─" * 28, bg="#3d3d3d", fg="gray").pack(pady=5)

        # System Status
        tk.Label(self.stats_panel, text="⚡ Status", font=("Helvetica", 13, "bold"),
                 bg="#3d3d3d", fg="#58a6ff").pack(pady=(5,5), anchor="w", padx=10)
        self.lbl_status = self._create_stat_label("SAFE", fg="#4CAF50")

        self.running = True
        self.update_video_feed()

    def _create_stat_label(self, text, fg="white"):
        lbl = tk.Label(self.stats_panel, text=text, font=("Helvetica", 13),
                       bg="#3d3d3d", fg=fg)
        lbl.pack(pady=5, anchor="w", padx=10)
        return lbl

    def update_sensor_display(self, sensor_data, alert_level):
        """Called from main.py background thread to update sensor readings."""
        self.sensor_data = sensor_data
        self.root.after(0, self._refresh_sensors, sensor_data, alert_level)

    def _refresh_sensors(self, sensor_data, alert_level):
        temp     = sensor_data.get("temperature")
        humidity = sensor_data.get("humidity")
        gas      = sensor_data.get("gas_detected")
        vib      = sensor_data.get("vibration_detected")

        self.lbl_temp.config(
            text=f"Temp: {temp:.1f} °C" if temp is not None else "Temp: N/A"
        )
        self.lbl_humidity.config(
            text=f"Humidity: {humidity:.1f} %" if humidity is not None else "Humidity: N/A"
        )
        self.lbl_gas.config(
            text=f"Gas: {'⚠ DETECTED' if gas else 'Normal'}",
            fg="#f44336" if gas else "yellow"
        )
        self.lbl_vib.config(
            text=f"Vibration: {'⚠ DETECTED' if vib else 'Normal'}",
            fg="#f44336" if vib else "white"
        )

        # Status
        colors = {"SAFE": "#4CAF50", "WARNING": "#FFC107", "DANGER": "#f44336"}
        self.lbl_status.config(
            text=f"{'🚨' if alert_level == 'DANGER' else '⚠️' if alert_level == 'WARNING' else '✅'} {alert_level}",
            fg=colors.get(alert_level, "white")
        )

    def update_video_feed(self):
        if self.running:
            frame, data = self.vision.process_frame()

            if frame is not None:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                img = img.resize((500, 375))
                imgtk = ImageTk.PhotoImage(image=img)

                self.video_frame.imgtk = imgtk
                self.video_frame.configure(image=imgtk)

                self.lbl_people.config(text=f"People: {data.get('person_count', 0)}")
                self.lbl_helmets.config(text=f"Helmets: {data.get('helmet_count', 0)}")

                person_count = data.get('person_count', 0)
                helmet_count = data.get('helmet_count', 0)
                no_helmet = data.get('no_helmet_violations', 0)
                violations = no_helmet if no_helmet > 0 else (1 if person_count > 0 and helmet_count == 0 else 0)
                self.lbl_violations.config(
                    text=f"Violations: {violations}",
                    fg="#f44336" if violations > 0 else "#4CAF50"
                )

            self.root.after(30, self.update_video_feed)

    def on_closing(self):
        self.running = False
        self.vision.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    engine = VisionEngine("../models/yolo11n_ncnn_model", camera_index=0)
    root = tk.Tk()
    app = LocalDashboard(root, engine)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
