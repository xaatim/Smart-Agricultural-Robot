import cv2
from ultralytics import YOLOWorld

# Initialize YOLO-World
print("[INFO] Loading YOLO-World model...")
model = YOLOWorld('yolov8s-worldv2.pt')  # Using smallest model for speed

# Define your crop classes - using more specific terms
crop_classes = [
    "tomato", 
    "tomato plant", 
    "chili", 
    "chili pepper", 
    "green chili", 
    "lettuce", 
    "lettuce leaf", 
    "leafy lettuce",
    "hot pepper"
]

model.set_classes(crop_classes)

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

print("[INFO] Running detection. Press 'q' to quit...")
print("[TIP] Show tomatoes, chili peppers, or lettuce to the camera")
try: 
  while True:
      ret, frame = cap.read()
      if not ret:
          print("❌ Failed to grab frame")
          break

      # Perform detection with lower confidence threshold
      results = model.predict(frame, conf=0.15, verbose=False)  # Lower confidence = more detections
      
      # Get annotated frame with bounding boxes
      annotated_frame = results[0].plot()  # This adds boxes automatically
      
      # Display detection status
      if len(results[0].boxes) > 0:
          detected_items = [model.names[int(box.cls)] for box in results[0].boxes]
          status = f"Detected: {', '.join(detected_items)}"
      else:
          status = "No crops detected"
      
      # Put status text on frame
      cv2.putText(annotated_frame, status, (10, 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
      
      # Show the output
      cv2.imshow("Crop Detector (YOLO-World)", annotated_frame)

      # Exit on 'q' key
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break
except: 
  KeyboardInterrupt()
  print("exit 0")
  # Clean up
  cap.release()
  cv2.destroyAllWindows()