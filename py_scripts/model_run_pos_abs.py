import cv2
import numpy as np
import os
import joblib
import tensorflow as tf
from collections import deque
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

def configure_hand_detector():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "hand_landmarker.task")
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options, num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    return vision.HandLandmarker.create_from_options(options)

# NOUVEAU : Extraction brute
def extract_raw_landmarks(landmarks):
    return [(lm.x, lm.y, lm.z) for lm in landmarks]

def run_realtime_inference(model_path="gesture_model_1dcnn.keras", labels_path="gesture_labels_dynamic.pkl", seq_length=30):
    print("Chargement du modèle...")
    model = tf.keras.models.load_model(model_path)
    label_encoder = joblib.load(labels_path)
    detector = configure_hand_detector()
    cap = cv2.VideoCapture(0)
    
    buffer = deque(maxlen=seq_length)
    motion_raw_buffer = deque(maxlen=seq_length)
    prediction_history = deque(maxlen=7) 
    
    stable_gesture = None
    last_detection_time = 0
    DISPLAY_DURATION = 3.0 
    
    current_display_text = "En attente..."
    color = (255, 255, 255)

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        hand_detected = False
        if result.hand_landmarks:
            hand_detected = True
            lm = result.hand_landmarks[0]
            
            raw_coords = extract_raw_landmarks(lm)
            flat = []
            for x, y, z in raw_coords: flat += [x, y, z]
            buffer.append(flat)
            
            motion_raw_buffer.append([lm[0].x, lm[0].y, lm[4].x, lm[4].y, lm[8].x, lm[8].y])
            for p in lm: cv2.circle(frame, (int(p.x * w), int(p.y * h)), 3, (0, 255, 0), -1)
        else:
            buffer.append([0.0] * 63)
            motion_raw_buffer.append([0.0] * 6)

        current_time = time.time()
        time_since_detection = current_time - last_detection_time

        if stable_gesture and time_since_detection < DISPLAY_DURATION:
            remaining = DISPLAY_DURATION - time_since_detection
            current_display_text = f"ACTION : {stable_gesture.upper()}"
            color = (0, 255, 0) 
            bar_width = int((remaining / DISPLAY_DURATION) * 200)
            cv2.rectangle(frame, (15, 50), (15 + bar_width, 55), (0, 255, 0), -1)
            
        else:
            stable_gesture = None 
            if len(buffer) == seq_length:
                recent_motion = list(motion_raw_buffer)[-10:]
                total_movement = np.var(recent_motion, axis=0).sum()
                
                if hand_detected and total_movement < 0.0005:
                    current_display_text = "Immobile..."
                    color = (255, 255, 0)
                    prediction_history.clear()
                elif hand_detected:
                    buffer_np = np.array(buffer, dtype=np.float32)
                    
                    # NOUVEAU : Normalisation séquentielle sur la fenêtre glissante
                    wrist_t0 = buffer_np[0, 0:3]
                    wrist_t0_tiled = np.tile(wrist_t0, 21)
                    buffer_norm = buffer_np - wrist_t0_tiled
                    
                    # On calcule les deltas sur la version normalisée
                    buffer_deltas = np.diff(buffer_norm, axis=0, prepend=buffer_norm[0:1, :])
                    buffer_combined = np.concatenate((buffer_norm, buffer_deltas), axis=1)
                    input_data = buffer_combined[np.newaxis, ...]
                    
                    predictions = model.predict(input_data, verbose=0)[0]
                    class_index = np.argmax(predictions)
                    confidence = predictions[class_index]
                    
                    raw_pred = label_encoder.inverse_transform([class_index])[0] if confidence > 0.75 else "Inconnu"
                    prediction_history.append(raw_pred)
                    
                    if len(prediction_history) == prediction_history.maxlen:
                        pred_counts = {p: prediction_history.count(p) for p in set(prediction_history)}
                        best_pred = max(pred_counts, key=pred_counts.get)
                        if pred_counts[best_pred] >= 5 and best_pred != "Inconnu":
                            stable_gesture = best_pred
                            last_detection_time = time.time()
                            prediction_history.clear() 
                    current_display_text = "Analyse du mouvement..."
                    color = (0, 165, 255)
                else:
                    current_display_text = "Aucune main"
                    color = (0, 0, 255)
                    prediction_history.clear()

        cv2.rectangle(frame, (0, 0), (w, 65), (0, 0, 0), -1)
        cv2.putText(frame, current_display_text, (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.imshow("Detection de Gestes", frame)
        if cv2.waitKey(1) == 27: break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_realtime_inference()