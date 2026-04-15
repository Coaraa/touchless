import cv2
import csv
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os

# Configuration des chemins automatiques
# BASE_DIR sera le dossier 'py_scripts/static_model/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_path(filename):
    """Retourne le chemin absolu vers un fichier dans le même dossier que le script."""
    return os.path.join(BASE_DIR, filename)

def preprocess(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)
    return cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)


def configure_hand_detector(n_hands):
    hand_task_path = get_path("hand_landmarker.task")
    base_options = python.BaseOptions(model_asset_path=hand_task_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=n_hands,
        min_hand_detection_confidence=0.3,
        min_hand_presence_confidence=0.3,
        min_tracking_confidence=0.3
    )
    return vision.HandLandmarker.create_from_options(options)

def normalize_landmarks(landmarks):
    wrist = landmarks[0]
    rel = [(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z) for lm in landmarks]
    max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in rel)
    norm = [(x / max_val, y / max_val, z / max_val) for x, y, z in rel]
    return norm

def setup_csv(output_file, n_hands):
    try:
        with open(output_file, "x", newline="") as f:
            writer = csv.writer(f)
            header = ["gesture"]
            for hand_idx in range(n_hands):
                prefix = f"h{hand_idx+1}"
                for i in range(21):
                    header += [f"{prefix}_x{i}", f"{prefix}_y{i}", f"{prefix}_z{i}"]
            writer.writerow(header)
    except FileExistsError:
        pass


def remove_old_gesture_data(gesture, output_file):
    rows = []
    with open(output_file, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row[0] != gesture:
                rows.append(row)

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def collect_gesture(gesture_name, num_samples = 500, n_hands = 1, output_file = "data/gesture_data"):

    sample_interval = 0.1       

    OUTPUT_FILE = os.path.join(BASE_DIR, output_file)

    detector = configure_hand_detector(n_hands)
    setup_csv(OUTPUT_FILE, n_hands)
    remove_old_gesture_data(gesture_name, OUTPUT_FILE)

    cap = cv2.VideoCapture(0)
    sample_count = 0
    last_sample_time = 0
    recording = False

    print("Recording automatically every", sample_interval, "seconds.")
    print("Press ESC to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if not recording:
            cv2.putText(frame, "Presse SPACE to Start recoding",(30, 50), cv2.FONT_HERSHEY_SIMPLEX,1.0, (0, 255, 255), 2)
            cv2.imshow("Data Collector", frame)
            key = cv2.waitKey(1)

            if key == 32:  # SPACE key
                    recording = True
                    print("Recording started.")
            elif key == 27:  # ESC
                    print("Cancelled.")
                    break
            continue
        
        frame = preprocess(frame)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        if result.hand_landmarks:
            now = time.time()

            lm = result.hand_landmarks[0]
            norm = normalize_landmarks(lm)

            for p in lm:
                h, w, _ = frame.shape
                cx, cy = int(p.x * w), int(p.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

            flat2 = []
            if(n_hands == 2 and len(result.hand_landmarks) == 2):
                lm2 = result.hand_landmarks[1]
                norm2 = normalize_landmarks(lm2)

                for p in lm2:
                    h, w, _ = frame.shape
                    cx, cy = int(p.x * w), int(p.y * h)
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

                if now - last_sample_time >= sample_interval:
                    for x, y, z in norm2:
                        flat2 += [x, y, z]

            if now - last_sample_time >= sample_interval:
                flat = []
                for x, y, z in norm:
                    flat += [x, y, z]

                with open(OUTPUT_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    if(n_hands == 2 and len(result.hand_landmarks) == 2):
                        writer.writerow([gesture_name] + flat + flat2)
                        sample_count += 1
                    elif(n_hands == 1):
                        writer.writerow([gesture_name] + flat)
                        sample_count += 1

                
                last_sample_time = now
                print(f"Saved sample {sample_count}/{num_samples}")

        cv2.putText(frame, f"Recording {gesture_name}: {sample_count}/{num_samples}",
                            (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1.0, (0, 255, 0), 2)

        cv2.imshow("Data Collector", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break

        if sample_count >= num_samples:
            print("Done.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python collect.py <gesture_name> [num_samples] [n_hands] [output_file]")
        sys.exit(1)

    gesture_name = sys.argv[1]
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    n_hands = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    output_file = sys.argv[4] if len(sys.argv) > 4 else "data/gesture_data.csv"

    collect_gesture(gesture_name, num_samples, n_hands, output_file)

