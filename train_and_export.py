from ultralytics import YOLO
import shutil
import os

def main():
    print("--- Edge AI: YOLOv11 PPE Training & Export Script ---")
    
    # 1. Initialize a YOLOv11 nano model
    print("\n[1/3] Initializing YOLOv11n...")
    model = YOLO("yolo11n.pt")  # Loads the pretrained nano model

    # 2. Train the model on the PPE dataset
    # We use construction-ppe.yaml which Ultralytics will auto-download
    print("\n[2/3] Starting Training on Construction PPE Dataset...")
    print("Note: This may take a while depending on your Mac's hardware.")
    model.train(
        data="construction-ppe.yaml",
        epochs=15,  # Increased to 15 for a decent baseline. Feel free to increase to 50+ for better accuracy
        imgsz=640,
        device="mps" # Uses Mac's Metal Performance Shaders for faster training (if Apple Silicon). Use 'cpu' if it fails.
    )

    # 3. Export to NCNN
    print("\n[3/3] Exporting trained model to NCNN format...")
    # The best weights are saved in runs/detect/train/weights/best.pt
    # We load the best custom trained model and export it
    best_model = YOLO("runs/detect/train/weights/best.pt")
    
    # Export returns the path to the exported directory
    exported_path = best_model.export(format="ncnn")
    
    # Move the exported NCNN folder into our models directory for neatness
    target_dir = "models/yolo11n_ncnn"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
        
    print(f"\nMoving exported NCNN files from {exported_path} to {target_dir}...")
    shutil.move(exported_path, target_dir)
    
    print("\n--- ✅ Training and Export Complete! ---")
    print(f"Your optimized NCNN model is now ready in the '{target_dir}' directory.")

if __name__ == "__main__":
    main()
