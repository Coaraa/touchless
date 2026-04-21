import cv2
import joblib
import pyautogui
import mediapipe as mp
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import csv
import time

# Configuration des chemins automatiques
# BASE_DIR sera le dossier 'py_scripts/static_model/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def init_logger():
    with open("gesture_runtime_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "n_hands",
            "gesture_pred",
            "gesture_name",
            "palm_x",
            "palm_y",
            "smooth_x",
            "smooth_y",
            "raw_vector_len",
            "model_activated"
        ])

def log_sample(n_hands, pred, gesture_name, palm_x, palm_y, smooth_x, smooth_y, vector_len, activated):
    with open("gesture_runtime_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.perf_counter(),
            n_hands,
            pred,
            gesture_name,
            palm_x,
            palm_y,
            smooth_x,
            smooth_y,
            vector_len,
            activated
        ])

def init_profile():
    with open("gesture_profile.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "frame",
            "dt_frame",
            "t_capture",
            "t_mediapipe",
            "t_normalize",
            "t_predict",
            "t_mouse",
            "t_total"
        ])

def log_profile(frame_id, dt_frame, t_cap, t_mp, t_norm, t_pred, t_mouse, t_total):
    with open("gesture_profile.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            frame_id,
            dt_frame,
            t_cap,
            t_mp,
            t_norm,
            t_pred,
            t_mouse,
            t_total
        ])


def init_mp_log():
    with open("mediapipe_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "status",
            "hand_label",
            "hand_confidence",
            "num_hands"
        ])

def log_mp(status, hand_label, hand_conf, num_hands):
    with open("mediapipe_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.perf_counter(),
            status,
            hand_label,
            hand_conf,
            num_hands
        ])


def get_path(filename):
    """Retourne le chemin absolu vers un fichier dans le même dossier que le script."""
    return os.path.join(BASE_DIR, filename)


def normalize_landmarks(landmarks):
    wrist = landmarks[0]
    rel = [(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z) for lm in landmarks]
    max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in rel)
    norm = [(x / max_val, y / max_val, z / max_val) for x, y, z in rel]
    return norm


def get_palm_center(lm):
    palm_ids = [0, 1, 5, 9, 13, 17]
    xs = [lm[i].x for i in palm_ids]
    ys = [lm[i].y for i in palm_ids]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def get_2h_center(lm, lm2):
    palm_ids = [0, 1, 5, 9, 13, 17]
    xs_1 = [lm[i].x for i in palm_ids]
    ys_1 = [lm[i].y for i in palm_ids]
    centerx1 = sum(xs_1) / len(xs_1)
    centery1 = sum(ys_1) / len(ys_1)

    xs_2 = [lm2[i].x for i in palm_ids]
    ys_2 = [lm2[i].y for i in palm_ids]
    centerx2 = sum(xs_2) / len(xs_2)
    centery2 = sum(ys_2) / len(ys_2)

    return (centerx1 +centerx2) / 2, (centery1 +centery2) / 2


def run_gesture_mouse (model_path="gesture_model_xgb.pkl", labels_path="gesture_labels.pkl", model_path_2h="gesture_model_xgb_2h.pkl", labels_path_2h="gesture_labels_2h.pkl", n_hands = 1):

    # Conversion des noms de fichiers en chemins absolus
    model_path = get_path(model_path)
    labels_path = get_path(labels_path)
    model_path_2h = get_path(model_path_2h)
    labels_path_2h = get_path(labels_path_2h)
    hand_task_path = get_path("hand_landmarker.task")

    if (n_hands == 1):
        model = joblib.load(model_path)
        label_encoder = joblib.load(labels_path)
        camera_margin = 0.15
        
    
    if (n_hands == 2):
        model = joblib.load(model_path_2h)
        label_encoder = joblib.load(labels_path_2h)
        camera_margin - 0.45

    base_options = python.BaseOptions(model_asset_path=hand_task_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=n_hands,
        min_hand_detection_confidence=0.3,
        min_hand_presence_confidence=0.3,
        min_tracking_confidence=0.3
    )
    detector = vision.HandLandmarker.create_from_options(options)

    screen_w, screen_h = pyautogui.size()
    smooth_x, smooth_y = 0, 0
    alpha = 0.4

    mouse_held = False
    drawing_mode = False 

    last_good_landmarks = None
    last_good_landmarks2 = None

    frames_since_seen = 0
    MAX_MISSED_FRAMES = 8

    model_activated = False

    cap = cv2.VideoCapture(0)

    print("Gesture mouse control active. Press ESC to quit.")

    init_logger()
    init_profile()
    init_mp_log()
    last_frame_time = time.perf_counter()
    frame_id = 0


    while True:
        frame_start = time.perf_counter()
        dt_frame = frame_start - last_frame_time
        last_frame_time = frame_start

        t0 = time.perf_counter()
        ret, frame = cap.read()
        t_capture = time.perf_counter() - t0
        if not ret:
            break

        cv2.putText(frame, "thumb up to activate", (10, 400),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.putText(frame, "thumb down to deactivate", (10, 420),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.putText(frame, "esc to stop completely", (10, 440),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)


        t0 = time.perf_counter()
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        if not result.hand_landmarks:
            log_mp("NO_HAND", "", 0.0, 0)
        else:
            num_hands = len(result.hand_landmarks)

            for i in range(num_hands):
                hand_info = result.handedness[i][0]
                hand_label = hand_info.category_name
                hand_conf = hand_info.score


                if hand_conf < 0.5:
                    status = "LOW_CONF"
                else:
                    status = "HAND_OK"

                log_mp(status, hand_label, hand_conf, num_hands)

                t_mediapipe = time.perf_counter() - t0


        if result.hand_landmarks:
            if(n_hands == 1):
                lm = result.hand_landmarks[0]
                frames_since_seen = 0
                last_good_landmarks = lm
            if(n_hands == 2 and len(result.hand_landmarks) == 2):
                lm = result.hand_landmarks[0]
                lm2 = result.hand_landmarks[1]
                frames_since_seen = 0
                last_good_landmarks = lm
                last_good_landmarks2 = lm2
            else:
                frames_since_seen += 1
        else:
            frames_since_seen += 1

        if frames_since_seen < MAX_MISSED_FRAMES and last_good_landmarks is not None:
            lm = last_good_landmarks
            if(n_hands == 2):
                if (last_good_landmarks2 == None): 
                    continue
                else:
                    lm2 = last_good_landmarks2
        else:
            cv2.putText(frame, "Hand lost...", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            if mouse_held:
                pyautogui.mouseUp()
                mouse_held = False
            cv2.imshow("Gesture Mouse Control", frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
            continue
        
        t0 = time.perf_counter()
        norm = normalize_landmarks(lm)
        t_normalize = time.perf_counter() - t0

        flat_vector = []
        for x, y, z in norm:
            flat_vector += [x, y, z]

        flat_vector2 = []
        if(n_hands == 2):
            norm2 = normalize_landmarks(last_good_landmarks2)
            for x, y, z in norm2:
                flat_vector2 += [x, y, z]

        t0 = time.perf_counter()
        if(n_hands == 1):    
            pred = model.predict([flat_vector])[0]
        if (n_hands == 2):
            pred = model.predict([flat_vector + flat_vector2])[0]
        t_predict = time.perf_counter() - t0

        gesture_name = label_encoder.inverse_transform([pred])[0]


        for position in lm:
            h, w, _ = frame.shape
            coordinates_x, coordinates_y = int(position.x * w), int(position.y * h)
            cv2.circle(frame, (coordinates_x, coordinates_y), 4, (0, 255, 0), -1)

        if (n_hands == 2):
            for position in lm2:
                h, w, _ = frame.shape
                coordinates_x, coordinates_y = int(position.x * w), int(position.y * h)
                cv2.circle(frame, (coordinates_x, coordinates_y), 4, (0, 255, 0), -1)

        if(n_hands == 1):
            palm_center_x, palm_center_y = get_palm_center(lm)
        if(n_hands == 2):
            palm_center_x, palm_center_y = get_2h_center(lm, lm2)

        vector_len = len(flat_vector) if n_hands == 1 else len(flat_vector + flat_vector2)

        smooth_x_norm = (1 -smooth_x / screen_w)
        smooth_y_norm = smooth_y / screen_h


        log_sample(
            n_hands,
            pred,
            gesture_name,
            palm_center_x,
            palm_center_y,
            smooth_x_norm,
            smooth_y_norm,
            vector_len,
            model_activated
        )

        left = camera_margin
        right = 1 - camera_margin
        top = camera_margin
        bottom = 1 - camera_margin

        palm_center_x = min(max(palm_center_x, left), right)
        palm_center_y = min(max(palm_center_y, top), bottom)

        norm_x = (palm_center_x - left) / (right - left)
        norm_y = (palm_center_y - top) / (bottom - top)

        screen_x = int((1 - norm_x) * screen_w)
        screen_y = int(norm_y * screen_h)

        smooth_x = int(smooth_x + alpha * (screen_x - smooth_x))
        smooth_y = int(smooth_y + alpha * (screen_y - smooth_y))

        if gesture_name == "Activate":
            model_activated = True

        if gesture_name == "Deactivate":
            model_activated = False

        if model_activated:

            if gesture_name == "oneHand":
                n_hands = 1
                camera_margin = 0.15
                model = joblib.load(model_path)
                label_encoder = joblib.load(labels_path)

                base_options = python.BaseOptions(model_asset_path=hand_task_path)
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    num_hands= 1,
                    min_hand_detection_confidence=0.3,
                    min_hand_presence_confidence=0.3,
                    min_tracking_confidence=0.3
                )
                detector = vision.HandLandmarker.create_from_options(options)

            if gesture_name == "twoHand":
                n_hands = 2
                camera_margin = 0.45
                last_good_landmarks2 = None
                model = joblib.load(model_path_2h)
                label_encoder = joblib.load(labels_path_2h)

                base_options = python.BaseOptions(model_asset_path=hand_task_path)
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    num_hands= 2,
                    min_hand_detection_confidence=0.3,
                    min_hand_presence_confidence=0.3,
                    min_tracking_confidence=0.3
                )
                detector = vision.HandLandmarker.create_from_options(options)
            
            if gesture_name == "Draw":
                drawing_mode = True
            else:
                drawing_mode = False

            t0 = time.perf_counter()
            if mouse_held and drawing_mode:
                pyautogui.dragTo(smooth_x, smooth_y, duration=0, button='left')
            else:
                pyautogui.moveTo(smooth_x, smooth_y)
            t_mouse = time.perf_counter() - t0

            if gesture_name == "Click":
                pyautogui.click()


            if gesture_name in ["Grab", "Draw"]:
                if not mouse_held:
                    pyautogui.mouseDown()
                    mouse_held = True
            else:
                if mouse_held:
                    pyautogui.mouseUp()
                    mouse_held = False

            t_total = time.perf_counter() - frame_start
            log_profile(
                frame_id,
                dt_frame,
                t_capture,
                t_mediapipe,
                t_normalize,
                t_predict,
                t_mouse,
                t_total
            )

        cv2.putText(frame, f"Gesture: {gesture_name}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)


        cv2.imshow("Gesture Mouse Control", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break       
        
    
        frame_id += 1

  

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys

    model_path = sys.argv[1] if len(sys.argv) > 1 else "gesture_model_xgb.pkl"
    labels_path = sys.argv[2] if len(sys.argv) > 2 else "gesture_labels.pkl"
    model_path_2h = sys.argv[3] if len(sys.argv) > 3 else "gesture_model_xgb_2h.pkl"
    labels_path_2h = sys.argv[4] if len(sys.argv) > 4 else "gesture_labels_2h.pkl"

    run_gesture_mouse(model_path, labels_path, model_path_2h, labels_path_2h)
