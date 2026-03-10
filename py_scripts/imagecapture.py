import cv2
import os
import time

output_folder = "stream_frames"
os.makedirs(output_folder, exist_ok=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not access the webcam.")
    exit()

save_every_seconds = 0.1 
last_save_time = 0
frame_count = 0

print("Streaming... Press ESC to stop.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    cv2.imshow("Webcam Stream", frame)

    current_time = time.time()

    if current_time - last_save_time >= save_every_seconds:
        img_name = f"frame_{frame_count:06d}.jpg"
        img_path = os.path.join(output_folder, img_name)
        cv2.imwrite(img_path, frame)
        frame_count += 1
        last_save_time = current_time

    if cv2.waitKey(1) == 27:
        print("Stopping stream...")
        break

cap.release()
cv2.destroyAllWindows()
