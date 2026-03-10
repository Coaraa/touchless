import cv2
import csv
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
GESTURE_NAME = "fist"      # change this for each gesture
OUTPUT_FILE = "gesture_data.csv"
SAMPLE_INTERVAL = 0.1       # record every 0.5 seconds



# ---------------------------------------------------------
# Load HandLandmarker (new API)
# ---------------------------------------------------------
base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)

# ---------------------------------------------------------
# Normalization helper
# ---------------------------------------------------------
def normalize_landmarks(landmarks):
    wrist = landmarks[0]
    rel = [(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z) for lm in landmarks]
    max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in rel)
    norm = [(x / max_val, y / max_val, z / max_val) for x, y, z in rel]
    return norm

# ---------------------------------------------------------
# Create CSV header if needed
# ---------------------------------------------------------
try:
    with open(OUTPUT_FILE, "x", newline="") as f:
        writer = csv.writer(f)
        header = ["gesture"]
        for i in range(21):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        writer.writerow(header)
except FileExistsError:
    pass

# ---------------------------------------------------------
# Main loop
# ---------------------------------------------------------
cap = cv2.VideoCapture(0)
sample_count = 0
last_sample_time = 0

print("Recording automatically every", SAMPLE_INTERVAL, "seconds.")
print("Press ESC to stop.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        lm = result.hand_landmarks[0]
        norm = normalize_landmarks(lm)

        # Draw landmarks for feedback
        for p in lm:
            h, w, _ = frame.shape
            cx, cy = int(p.x * w), int(p.y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        # Auto‑record every X seconds
        now = time.time()
        if now - last_sample_time >= SAMPLE_INTERVAL:
            flat = []
            for x, y, z in norm:
                flat += [x, y, z]

            with open(OUTPUT_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([GESTURE_NAME] + flat)

            sample_count += 1
            last_sample_time = now
            print(f"Saved sample #{sample_count}")

    cv2.imshow("Data Collector", frame)
    key = cv2.waitKey(1)

    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
