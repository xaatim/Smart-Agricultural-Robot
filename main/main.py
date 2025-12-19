import cv2
from ultralytics import YOLOWorld #type: ignore 
import socket
import time
import keyboard

# --- ESP8266 Wi-Fi Configuration ---
ESP_IP = "192.168.0.125"  # Your IP, this is correct
ESP_PORT = 8888

# --- NEW: Watering Schedule Configuration ---
# Set watering times (in seconds) for each *detected class name*
WATERING_TIMES = {
    # Tomato classes
    "tomato": 5,
    "tomato plant": 5,
    
    # Chili classes
    "chili": 3,
    "chili pepper": 3,
    "green chili": 3,
    "hot pepper": 3,
    
    # Lettuce classes
    "lettuce": 4,
    "lettuce leaf": 4,
    "leafy lettuce": 4,
}
DEFAULT_WATERING_TIME = 2  # For any other detected crop
POST_WATERING_PAUSE = 5  # Seconds to pause *after* watering

# Setup UDP Socket
print(f"[INFO] Setting up UDP socket for ESP8266 at {ESP_IP}:{ESP_PORT}...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_command(cmd):
    """Sends a single character command to the ESP8266."""
    try:
        sock.sendto(cmd.encode(), (ESP_IP, ESP_PORT))
    except Exception as e:
        print(f"[ERROR] Could not send command: {e}")

# --- YOLO-World Setup ---
print("[INFO] Loading YOLO-World model...")
model = YOLOWorld('yolov8s-worldv2.pt')

crop_classes = [
    "tomato", "tomato plant", "chili", "chili pepper", 
    "green chili", "lettuce", "lettuce leaf", "leafy lettuce", "hot pepper"
]
model.set_classes(crop_classes)

# --- Webcam Setup ---
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

print("[INFO] Running detection. Press 'q' to quit.")
print("[CONTROLS] Drive with W, A, S, D. Robot will auto-water on detection.")

# --- State Machine Variables ---
is_watering = False
is_paused = False
watering_start_time = 0
pause_start_time = 0
current_watering_crop = ""
current_watering_duration = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        annotated_frame = frame.copy()
        status = "Driving... (No crops detected)" # Default status

        # --- NEW: STATE 1 - PAUSED (Post-Watering) ---
        if is_paused:
            elapsed_pause = time.time() - pause_start_time
            if elapsed_pause > POST_WATERING_PAUSE:
                print("[AUTO] Pause finished. Resuming detection.")
                is_paused = False
            else:
                # Show pause status
                send_command('S')
                send_command('X')
                
                status = f"PAUSED... {int(POST_WATERING_PAUSE - elapsed_pause)}s left"
                # Stop motors during pause
                cv2.putText(annotated_frame, status, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
                cv2.imshow("Crop Detector (YOLO-World)", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue # Skip the rest of the loop

        # --- STATE 2: WATERING ---
        if is_watering:
            elapsed_time = time.time() - watering_start_time
            
            if elapsed_time > current_watering_duration:
                # Time's up! Stop watering and start pause
                print(f"[AUTO] Watering for {current_watering_crop} complete.")
                send_command('X')  # Stop water
                is_watering = False
                
                # --- Start Pause ---
                print(f"[AUTO] Pausing for {POST_WATERING_PAUSE} seconds...")
                is_paused = True
                pause_start_time = time.time()
            else:
                # --- UPDATED: Show specific crop being watered ---
                status = f"Watering {current_watering_crop}... {int(current_watering_duration - elapsed_time)}s left"
                cv2.putText(annotated_frame, status, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("Crop Detector (YOLO-World)", annotated_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue # Skip the rest of the loop

        # --- STATE 3: DRIVING & DETECTING ---
        # (Only runs if not watering and not paused)
        results = model.predict(frame, conf=0.15, verbose=False)
        annotated_frame = results[0].plot() # Draw boxes
        
        if len(results[0].boxes) > 0: # type: ignore
            # --- CROP DETECTED! ---
            detected_items = [model.names[int(box.cls)] for box in results[0].boxes] # type: ignore
            
            # --- UPDATED: Get crop-specific duration ---
            detected_crop_name = detected_items[0] # Get the first detected item
            current_watering_duration = WATERING_TIMES.get(detected_crop_name, DEFAULT_WATERING_TIME)
            current_watering_crop = detected_crop_name

            status = f"Detected: {current_watering_crop}"
            print(f"[AUTO] '{current_watering_crop}' detected! Watering for {current_watering_duration}s.")
            
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
                send_command('S') # Stop if no keys pressed

        # Put status text on frame
        # (Use green only if driving, otherwise it's handled in the state)
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