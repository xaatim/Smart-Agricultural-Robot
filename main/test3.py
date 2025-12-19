import cv2
from ultralytics import YOLOWorld # type: ignore
import socket
import time
import keyboard  # <-- NEW IMPORT for driving

# --- ESP32 Wi-Fi Configuration ---\
CAMERA_URL = "http://192.168.0.175:81/stream"
ESP_IP = "10.49.226.43"  # <-- IMPORTANT: Change this to the IP from ESP32 Serial Monitor
ESP_PORT = 8888
WATERING_DURATION = 3  # Seconds to water for

# Setup UDP Socket
print(f"[INFO] Setting up UDP socket for ESP32 at {ESP_IP}:{ESP_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_command(cmd):
    """Sends a single character command to the ESP32."""
    try:
        sock.sendto(cmd.encode(), (ESP_IP, ESP_PORT))
    except Exception as e:
        print(f"[ERROR] Could not send command: {e}")

# --- YOLO-World Setup (Your Code) ---
print("[INFO] Loading YOLO-World model...")
model = YOLOWorld('yolov8s-worldv2.pt')

crop_classes = [
    "tomato", "tomato plant", "chili", "chili pepper", 
    "green chili", "lettuce", "lettuce leaf", "leafy lettuce", "hot pepper"
]
model.set_classes(crop_classes)

# --- Webcam Setup (Your Code) ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("❌ Cannot open camera")
    

print("[INFO] Running detection. Press 'q' to quit.")
print("[CONTROLS] Drive with W, A, S, D. Robot will auto-water on detection.")

# --- State Machine Variables ---
is_watering = False
watering_start_time = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        annotated_frame = frame.copy() # Make a copy for annotations
        crop_detected = False

        # --- STATE 1: WATERING ---
        if is_watering:
            # Robot is in automatic watering mode
            elapsed_time = time.time() - watering_start_time
            
            if elapsed_time > WATERING_DURATION:
                # Time's up! Stop watering and return control
                print("[AUTO] Watering complete.")
                send_command('X')  # Stop water
                is_watering = False
            else:
                # Still watering, show status and skip driving/detection
                status = f"WATERING... {int(WATERING_DURATION - elapsed_time)}s left"
                cv2.putText(annotated_frame, status, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("Crop Detector (YOLO-World)", annotated_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue # Skip the rest of the loop

        # --- STATE 2: DRIVING & DETECTING ---
        # Perform detection
        results = model.predict(frame, conf=0.15, verbose=False)
        annotated_frame = results[0].plot() # Draw boxes
        
        status = "Driving... (No crops detected)"
        
        if len(results[0].boxes) > 0: # type: ignore
            # --- CROP DETECTED! ---
            crop_detected = True
            detected_items = [model.names[int(box.cls)] for box in results[0].boxes] # type: ignore
            status = f"Detected: {', '.join(detected_items)}"
            
            print(f"[AUTO] Crop detected! Stopping and watering for {WATERING_DURATION}s.")
            
            # Start the watering sequence
            send_command('S')  # STOP motors
            send_command('W')  # Start water
            is_watering = True
            watering_start_time = time.time()

        else:
            # --- NO CROP DETECTED: Manual Driving ---
            if keyboard.is_pressed('w'):
                send_command('F')
                status = "Driving: FORWARD"
            elif keyboard.is_pressed('s'):
                send_command('B')
                status = "Driving: BACKWARD"
            elif keyboard.is_pressed('a'):
                send_command('L')
                status = "Driving: LEFT"
            elif keyboard.is_pressed('d'):
                send_command('R')
                status = "Driving: RIGHT"
            else:
                # Send STOP only if no keys are pressed AND not watering
                send_command('S')

        # Put status text on frame
        cv2.putText(annotated_frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Show the output
        cv2.imshow("Crop Detector (YOLO-World)", annotated_frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Clean up
    print("[INFO] Cleaning up... Stopping robot.")
    send_command('S')  # Stop motors
    send_command('X')  # Stop water
    cap.release()
    cv2.destroyAllWindows()