import cv2
import csv
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision



def configure_hand_detector():
    base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    return vision.HandLandmarker.create_from_options(options)

def normalize_landmarks(landmarks):
    wrist = landmarks[0]
    rel = [(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z) for lm in landmarks]
    max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in rel)
    norm = [(x / max_val, y / max_val, z / max_val) for x, y, z in rel]
    return norm

def setup_csv(output_file):
    try:
        with open(output_file, "x", newline="") as f:
            writer = csv.writer(f)
            header = ["gesture"]
            for i in range(21):
                header += [f"x{i}", f"y{i}", f"z{i}"]
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

def collect_gesture(gesture_name, num_samples = 500, output_file = "data/gesture_data"):

    sample_interval = 0.1       


    detector = configure_hand_detector()
    setup_csv(output_file)
    remove_old_gesture_data(gesture_name, output_file)

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

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        if result.hand_landmarks:
            lm = result.hand_landmarks[0]
            norm = normalize_landmarks(lm)

            for p in lm:
                h, w, _ = frame.shape
                cx, cy = int(p.x * w), int(p.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

            now = time.time()
            if now - last_sample_time >= sample_interval:
                flat = []
                for x, y, z in norm:
                    flat += [x, y, z]

                with open(output_file, "a", newline="") as f:
                    writer = csv.writer(f)
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
        print("Usage: python collect.py <gesture_name> [num_samples] [output_file]")
        sys.exit(1)

    gesture_name = sys.argv[1]
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    output_file = sys.argv[3] if len(sys.argv) > 3 else "data/gesture_data.csv"

    collect_gesture(gesture_name, num_samples, output_file)


