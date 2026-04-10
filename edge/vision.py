import cv2
import time
from ultralytics import YOLO

class VisionEngine:
    def __init__(self, model_path="models/yolo11n_ncnn", camera_index=0):
        """
        Initializes the YOLOv11 NCNN model and connects to the USB Webcam.
        """
        print(f"Load NCNN model from: {model_path}")
        # Load the exported NCNN model
        # Note: Ultralytics seamlessly handles the _ncnn folder if we pass the folder path
        self.model = YOLO(model_path, task='detect')
        
        # Connect to webcam
        self.cap = cv2.VideoCapture(camera_index)
        
        # Optimize camera props for Raspberry Pi
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            print("ERROR: Could not open the USB Webcam.")

        # PPE classes mapping from the construction-ppe.yaml
        self.ppe_classes = {
            0: "helmet",
            1: "gloves",
            2: "vest",
            3: "boots",
            4: "goggles",
            5: "none",
            6: "Person",
            7: "no_helmet",
            8: "no_goggle",
            9: "no_gloves",
            10: "no_boots"
        }

    def process_frame(self):
        """
        Grabs a frame from the webcam, runs YOLO inference, and returns compliance data.
        Returns a tuple: (frame, detections_dict)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, {}

        # Run inference
        # Setting conf=0.5 to filter out weak detections
        # Filtering for Specific Classes: 0 (helmet), 6 (Person), 7 (no_helmet)
        results = self.model(frame, conf=0.5, classes=[0, 6, 7], verbose=False)[0]

        detections = {
            "helmet_count": 0,
            "person_count": 0,
            "no_helmet_violations": 0
        }

        # Parse the results
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.ppe_classes.get(class_id, "unknown")
            
            if class_name == "helmet":
                detections["helmet_count"] += 1
            elif class_name == "Person":
                detections["person_count"] += 1
            elif class_name == "no_helmet":
                detections["no_helmet_violations"] += 1

        # Optionally draw bounding boxes on the frame for debugging
        annotated_frame = results.plot()

        return annotated_frame, detections

    def cleanup(self):
        """Release the camera resources."""
        self.cap.release()
        cv2.destroyAllWindows()


# --- Quick Test Loop ---
if __name__ == "__main__":
    print("Starting Vision Engine test...")
    engine = VisionEngine()
    
    try:
        while True:
            start_time = time.time()
            
            frame, data = engine.process_frame()
            if frame is None:
                print("Failed to grab frame.")
                break
                
            fps = 1.0 / (time.time() - start_time)
            
            # Print state to console
            print(f"FPS: {fps:.1f} | People: {data['person_count']} | Helmets: {data['helmet_count']} | Violations: {data['no_helmet_violations']}")
            
            # Show the frame on Mac screen (Will fail headless on Pi unless X11 is forwarded, but good for local MAC dev!)
            cv2.imshow("Vision Engine Test", frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        engine.cleanup()
        print("Vision Engine shutdown.")
