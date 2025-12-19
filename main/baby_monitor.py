import cv2
from ultralytics import YOLOWorld # type: ignore


model = YOLOWorld("yolov8m-worldv2.pt") 

keywords = ["baby","infant","todler","child","kid"]



model.set_classes(keywords)

cap = cv2.VideoCapture(0)

print("Starting Baby Detection... Press 'q' to exit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    results = model.track(frame, persist=True, conf=0.35)

    annotated_frame = results[0].plot()

    cv2.imshow("YOLO-World Baby Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()