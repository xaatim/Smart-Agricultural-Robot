import cv2
from ultralytics import YOLOWorld #type:ignore 
import socket
import time
import threading

# --- CONFIG ---
ESP_IP = "10.240.214.43"
ESP_PORT = 8888
CAM_URL = "http://10.21.235.201:81/stream"

WATERING_TIMES = {"tomato": 5, "chilli": 3, "lettuce": 4}
DEFAULT_TIME = 2

# --- UDP FIRE-AND-FORGET ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def send(cmd): 
    sock.sendto(cmd.encode(), (ESP_IP, ESP_PORT))

# --- THE "FRAME TRASHER" (Prevents Lag) ---
# This variable always holds ONLY the newest frame.
latest_frame = None

def buffer_wiper():
    global latest_frame
    cap = cv2.VideoCapture(5)
    while True:
        # READ AND OVERWRITE IMMEDIATELY
        # We don't care if we overwrite a frame that wasn't processed.
        # Just keep the variable fresh.
        ret, frame = cap.read()
        if ret:
            latest_frame = frame

# Start the wiper in background
threading.Thread(target=buffer_wiper, daemon=True).start()
print("Waiting for stream...")
while latest_frame is None: time.sleep(0.1) # Wait for first frame

# --- MAIN LOGIC ---
model = YOLOWorld("yolov8s-worldv2.pt")
model.set_classes(list(WATERING_TIMES.keys()))

print("Ready. Keys: W/A/S/D | Q to Quit")

try:
    while True:
        # GRAB THE FRESH FRAME
        # We process a COPY so the thread can keep overwriting the original in background
        frame = latest_frame.copy()

        # 1. DETECT
        results = model.predict(frame, conf=0.15, verbose=False)
        annotated = results[0].plot()

        # 2. DECIDE
        crop_found = None
        if results[0].boxes is not None:
          for box in results[0].boxes:
              name = model.names[int(box.cls)]
              if name in WATERING_TIMES:
                  crop_found = name
                  break
        
        # 3. ACT
        if crop_found:
            duration = WATERING_TIMES.get(crop_found, DEFAULT_TIME)
            print(f"!!! FOUND {crop_found} !!! Watering {duration}s")
            
            send("S") # Stop Car
            start_t = time.time()
            
            # BLOCKING WATER LOOP (We don't care about video here)
            while time.time() - start_t < duration:
                send("W") # Pump ON
                cv2.imshow("Live", annotated)
                cv2.waitKey(100) 
            
            # COOLDOWN
            for _ in range(5): send("X") # Pump OFF (spam it)
            time.sleep(5) # Pause logic (video thread keeps running in background)

        else:
            # MANUAL DRIVE
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'): break
            elif k == ord('w'): send("F")
            elif k == ord('s'): send("B")
            elif k == ord('a'): send("L")
            elif k == ord('d'): send("R")
            else: send("S")
        
        cv2.imshow("Live", annotated)

finally:
    send("S"); send("X")
    cv2.destroyAllWindows()