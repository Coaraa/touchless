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

def normalize_landmarks(landmarks):
    wrist = landmarks[0]
    rel = [(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z) for lm in landmarks]
    max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in rel) or 1.0
    norm = [(x / max_val, y / max_val, z / max_val) for x, y, z in rel]
    return norm

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
    """
    Rééchantillonne une séquence de taille variable vers une taille fixe (target_length)
    en utilisant l'interpolation linéaire de numpy.
    """
    sequence_np = np.array(sequence)
    original_length = len(sequence_np)
    
    # Si par hasard la séquence fait déjà la bonne taille
    if original_length == target_length:
        return sequence_np.tolist()
    
    # Création des axes de temps d'origine et cible
    original_indices = np.linspace(0, original_length - 1, num=original_length)
    target_indices = np.linspace(0, original_length - 1, num=target_length)
    
    resampled_sequence = np.zeros((target_length, 63))
    
    # Interpolation pour chacune des 63 caractéristiques (x, y, z des 21 points)
    for i in range(63):
        resampled_sequence[:, i] = np.interp(target_indices, original_indices, sequence_np[:, i])
        
    return resampled_sequence.tolist()

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

def collect_dynamic_gesture(gesture_name, num_sequences=10, target_frames=30, output_file="data/dynamic_gestures.csv"):
    detector = configure_hand_detector()
    setup_csv(output_file)
    remove_old_gesture_data(gesture_name, output_file)


    cap = cv2.VideoCapture(0)
    sequences_done = 0
    current_sequence_buffer = []
    is_recording = False
    
    # Pour éviter le double-déclenchement de la touche Espace
    last_space_press_time = 0 
    debounce_delay = 0.5 # 500 ms de délai entre deux appuis sur Espace

    # Garde en mémoire la dernière position connue pour palier aux pertes de détection
    last_known_landmarks = [0.0] * 63 

    print(f"Prêt pour : {gesture_name}")
    print(f"Objectif : {num_sequences} séquences (Taille finale fixée à {target_frames} frames).")

    while sequences_done < num_sequences:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        # Extraction et affichage
        if result.hand_landmarks:
            norm = normalize_landmarks(result.hand_landmarks[0])
            flat = []
            for x, y, z in norm: flat += [x, y, z]
            last_known_landmarks = flat # Mise à jour de la dernière position connue
            
            for p in result.hand_landmarks[0]:
                cv2.circle(frame, (int(p.x * w), int(p.y * h)), 3, (0, 255, 0), -1)

        # Ajout au buffer si on enregistre
        if is_recording:
            # On utilise les derniers points connus même si la main disparaît 1 ou 2 frames
            current_sequence_buffer.append(last_known_landmarks) 

        # Affichage UI
        color = (0, 0, 255) if is_recording else (0, 255, 0)
        status = "ENREGISTREMENT... (ESPACE pour STOP)" if is_recording else "PRET (ESPACE pour START)"
        cv2.putText(frame, f"{status} | Seq: {sequences_done}/{num_sequences}", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if is_recording:
            cv2.rectangle(frame, (0,0), (w,h), (0,0,255), 5)

        cv2.imshow("Capture Dynamique Start/Stop", frame)
        key = cv2.waitKey(1)
        
        current_time = time.time()
        
        # Gestion de la touche ESPACE avec anti-rebond (debounce)
        if key == 32 and (current_time - last_space_press_time) > debounce_delay:
            last_space_press_time = current_time
            
            if not is_recording:
                # DEBUT DE L'ENREGISTREMENT
                is_recording = True
                current_sequence_buffer = []
                print("Début de l'enregistrement du geste...")
            else:
                # FIN DE L'ENREGISTREMENT
                is_recording = False
                
                # On ne sauvegarde que si l'utilisateur a capturé un minimum de données
                if len(current_sequence_buffer) > 5:
                    # Réechantillonage magique vers target_frames
                    resampled_data = resample_sequence(current_sequence_buffer, target_frames)
                    
                    # Sauvegarde dans le CSV
                    with open(output_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        for frame_data in resampled_data:
                            writer.writerow([gesture_name, sequences_done] + frame_data)
                    
                    sequences_done += 1
                    print(f"Séquence {sequences_done}/{num_sequences} terminée. (Taille originale: {len(current_sequence_buffer)} -> Redimensionnée à: {target_frames})")
                else:
                    print("Séquence trop courte ignorée.")
                    
        elif key == 27: # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Capture terminée !")

if __name__ == "__main__":
    import sys
    g_name = sys.argv[1] if len(sys.argv) > 1 else "geste_test"
    # Modifiez ici le nombre de frames cible et le nombre de séquences si besoin
    collect_dynamic_gesture(g_name, num_sequences=10, target_frames=30)