import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading

# Import the VisionEngine we built earlier!
from vision import VisionEngine

class LocalDashboard:
    def __init__(self, root, vision_engine):
        self.root = root
        self.root.title("Edge AI Safety Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg="#2d2d2d")
        
        self.vision = vision_engine
        
        # --- UI Layout ---
        # 1. Top Header
        self.lbl_title = tk.Label(root, text="Construction Safety Dashboard", font=("Helvetica", 20, "bold"), bg="#2d2d2d", fg="white")
        self.lbl_title.pack(pady=10)
        
        # 2. Left Side: Camera Feed
        self.video_frame = tk.Label(root, bg="black")
        self.video_frame.pack(side=tk.LEFT, padx=20, pady=20)
        
        # 3. Right Side: Statistics Panel
        self.stats_panel = tk.Frame(root, bg="#3d3d3d", width=250, height=480)
        self.stats_panel.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.Y)
        
        # Stats Labels
        self.lbl_people = self._create_stat_label("Total People: 0")
        self.lbl_helmets = self._create_stat_label("Helmets: 0", fg="#4CAF50")
        self.lbl_vests = self._create_stat_label("Vests: 0", fg="#2196F3")
        self.lbl_violations = self._create_stat_label("VIOLATIONS: 0", fg="#f44336")
        
        # Environment Stats (Placeholders for Member 2 to fill)
        tk.Label(self.stats_panel, text="----------------", bg="#3d3d3d", fg="gray").pack(pady=5)
        self.lbl_temp = self._create_stat_label("Temp: -- °C", fg="orange")
        self.lbl_vib = self._create_stat_label("Vibration: Normal", fg="white")

        self.running = True
        
        # Start the video loop
        self.update_video_feed()

    def _create_stat_label(self, text, fg="white"):
        lbl = tk.Label(self.stats_panel, text=text, font=("Helvetica", 16), bg="#3d3d3d", fg=fg)
        lbl.pack(pady=10, anchor="w", padx=10)
        return lbl

    def update_video_feed(self):
        if self.running:
            # Grab a frame and detection data from the ML engine
            frame, data = self.vision.process_frame()
            
            if frame is not None:
                # Need to convert BGR (OpenCV) to RGB (Tkinter/PIL)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                
                # Resize slightly to fit the UI nicely
                img = img.resize((500, 375)) 
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update the video label
                self.video_frame.imgtk = imgtk
                self.video_frame.configure(image=imgtk)
                
                # Update stats panel
                self.lbl_people.config(text=f"Total People: {data.get('person_count', 0)}")
                self.lbl_helmets.config(text=f"Helmets: {data.get('helmet_count', 0)}")
                self.lbl_vests.config(text=f"Vests: {data.get('vest_count', 0)}")
                self.lbl_violations.config(text=f"VIOLATIONS: {data.get('no_helmet_violations', 0)}")
                
                # Highlight violations
                if data.get('no_helmet_violations', 0) > 0:
                    self.lbl_violations.config(fg="red", font=("Helvetica", 16, "bold"))
                else:
                    self.lbl_violations.config(fg="#f44336", font=("Helvetica", 16))

            # Call this function again after 30ms (~33 FPS)
            self.root.after(30, self.update_video_feed)
            
    def on_closing(self):
        self.running = False
        self.vision.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    print("Initializing Vision Engine...")
    engine = VisionEngine("../models/yolo11n_ncnn", camera_index=0)
    
    # Needs to run in main thread for Mac
    root = tk.Tk()
    app = LocalDashboard(root, engine)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    print("Launching Tkinter App...")
    root.mainloop()
