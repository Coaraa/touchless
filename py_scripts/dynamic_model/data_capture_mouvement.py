import cv2
import csv
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import math

import random
import math

 


def compute_motion_first_last(first_frame, last_frame):
    features = []

    for i in range(21):
        x0, y0, z0 = first_frame[i]
        x1, y1, z1 = last_frame[i]
        distance_x = x1 - x0
        distance_y = y1 - y0
        distance_z = z1 - z0
        magnitude = math.sqrt(distance_x*distance_x + distance_y*distance_y + distance_z*distance_z)
        angle = math.atan2(distance_y, distance_x)
        features.extend([magnitude, angle])

    return features

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
                header += [f"mag_{i}", f"angle_{i}"]

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

def collect_gesture(gesture_name, num_samples=30, output_file="data/gesture_data_movement.csv"):
    detector = configure_hand_detector()
    setup_csv(output_file)
    remove_old_gesture_data(gesture_name, output_file)

    cap = cv2.VideoCapture(0)

    print("Press SPACE to record one gesture sample.")
    print("Press ESC to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, f"Gesture: {gesture_name}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        cv2.putText(frame, "SPACE = record sample", (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, "ESC = quit", (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Data Collector", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break

        if key == 32:  # SPACE
            print("Recording gesture sample...")

            first_frame = None
            last_frame = None
            frame_counter = 0

            while frame_counter <= num_samples:
                ret, frame = cap.read()
                if not ret:
                    break

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                result = detector.detect(mp_image)

                if result.hand_landmarks:
                    lm = result.hand_landmarks[0]
                    norm = normalize_landmarks(lm)

                    if frame_counter == 0:
                        first_frame = norm
                    if frame_counter == num_samples:
                        last_frame = norm

                frame_counter += 1
                cv2.imshow("Data Collector", frame)
                cv2.waitKey(1)

            if first_frame is not None and last_frame is not None:
                motion_vector = compute_motion_first_last(first_frame, last_frame)

                with open(output_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([gesture_name] + motion_vector)

                print("Sample saved.")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python collect.py <gesture_name> [num_samples] [output_file]")
        sys.exit(1)

    gesture_name = sys.argv[1]
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    output_file = sys.argv[3] if len(sys.argv) > 3 else "data/gesture_data_mouvement.csv"

    collect_gesture(gesture_name, num_samples, output_file)