import cv2
import csv
import time
import os
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

def configure_hand_detector():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "hand_landmarker.task")
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    return vision.HandLandmarker.create_from_options(options)

# NOUVEAU : On extrait les coordonnées brutes (déjà entre 0.0 et 1.0 par MediaPipe)
def extract_raw_landmarks(landmarks):
    return [(lm.x, lm.y, lm.z) for lm in landmarks]

def setup_csv(output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    if not os.path.exists(output_file):
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["gesture", "sequence_id"]
            for i in range(21):
                header += [f"x{i}", f"y{i}", f"z{i}"]
            writer.writerow(header)

def resample_sequence(sequence, target_length=30):
    sequence_np = np.array(sequence)
    original_length = len(sequence_np)
    if original_length == target_length: return sequence_np.tolist()
    
    original_indices = np.linspace(0, original_length - 1, num=original_length)
    target_indices = np.linspace(0, original_length - 1, num=target_length)
    resampled_sequence = np.zeros((target_length, 63))
    
    for i in range(63):
        resampled_sequence[:, i] = np.interp(target_indices, original_indices, sequence_np[:, i])
    return resampled_sequence.tolist()

def remove_old_gesture_data(gesture, output_file):
    rows = []
    if os.path.exists(output_file):
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

def collect_dynamic_gesture(gesture_name, num_sequences=10, target_frames=30, output_file="data/dynamic_gestures.csv"):
    detector = configure_hand_detector()
    setup_csv(output_file)
    remove_old_gesture_data(gesture_name, output_file)

    cap = cv2.VideoCapture(0)
    sequences_done = 0
    current_sequence_buffer = []
    is_recording = False
    
    last_space_press_time = 0 
    debounce_delay = 0.5 
    last_known_landmarks = [0.0] * 63 

    print(f"Prêt pour : {gesture_name} | Appuyez sur ESPACE pour START/STOP.")

    while sequences_done < num_sequences:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        if result.hand_landmarks:
            raw_coords = extract_raw_landmarks(result.hand_landmarks[0])
            flat = []
            for x, y, z in raw_coords: flat += [x, y, z]
            last_known_landmarks = flat 
            
            for p in result.hand_landmarks[0]:
                cv2.circle(frame, (int(p.x * w), int(p.y * h)), 3, (0, 255, 0), -1)

        if is_recording:
            current_sequence_buffer.append(last_known_landmarks) 

        color = (0, 0, 255) if is_recording else (0, 255, 0)
        status = "ENREGISTREMENT..." if is_recording else "PRET"
        cv2.putText(frame, f"{status} | Seq: {sequences_done}/{num_sequences}", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if is_recording: cv2.rectangle(frame, (0,0), (w,h), (0,0,255), 5)

        cv2.imshow("Capture Dynamique Start/Stop", frame)
        key = cv2.waitKey(1)
        current_time = time.time()
        
        if key == 32 and (current_time - last_space_press_time) > debounce_delay:
            last_space_press_time = current_time
            if not is_recording:
                is_recording = True
                current_sequence_buffer = []
                print("Enregistrement...")
            else:
                is_recording = False
                if len(current_sequence_buffer) > 5:
                    resampled_data = resample_sequence(current_sequence_buffer, target_frames)
                    with open(output_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        for frame_data in resampled_data:
                            writer.writerow([gesture_name, sequences_done] + frame_data)
                    sequences_done += 1
                    print(f"Séquence {sequences_done}/{num_sequences} sauvegardée.")
        elif key == 27: break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    g_name = sys.argv[1] if len(sys.argv) > 1 else "geste_test"
    collect_dynamic_gesture(g_name, num_sequences=15, target_frames=30)