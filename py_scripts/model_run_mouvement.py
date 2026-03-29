import cv2
import joblib
import pyautogui
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
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

def run_gesture_mouse (model_path="gesture_model_mouvement_xgb.pkl", labels_path="gesture_labels_mouvement.pkl", camera_index=0):

    CAMERA_MARGIN = 0.15
      


    model = joblib.load(model_path)
    label_encoder = joblib.load(labels_path)

    base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    detector = vision.HandLandmarker.create_from_options(options)

    screen_w, screen_h = pyautogui.size()
    smooth_x, smooth_y = 0, 0
    alpha = 0.25

    mouse_held = False
    drawing_mode = False 

    last_good_landmarks = None
    frames_since_seen = 0
    MAX_MISSED_FRAMES = 8

    model_activated = False

    cap = cv2.VideoCapture(0)
    first_frame = None
    last_frame = None
    frame_counter = 0
    num_samples = 20 
    gesture_name = "None"


    print("Gesture mouse control active. Press ESC to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, "thumb up to activate", (10, 400),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.putText(frame, "thumb down to deactivate", (10, 420),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.putText(frame, "esc to stop completely", (10, 440),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)


        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        if result.hand_landmarks:
            lm = result.hand_landmarks[0]
            frames_since_seen = 0
            last_good_landmarks = lm
        else:
            frames_since_seen += 1

        if frames_since_seen < MAX_MISSED_FRAMES and last_good_landmarks is not None:
            lm = last_good_landmarks
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

        norm = normalize_landmarks(lm)

        if frame_counter == 0:
            first_frame = norm

        elif frame_counter == num_samples:
            last_frame = norm

            motion_vector = compute_motion_first_last(first_frame, last_frame)

            pred = model.predict([motion_vector])[0]
            gesture_name = label_encoder.inverse_transform([pred])[0]

            frame_counter = -1

        for position in lm:
            h, w, _ = frame.shape
            coordinates_x, coordinates_y = int(position.x * w), int(position.y * h)
            cv2.circle(frame, (coordinates_x, coordinates_y), 4, (0, 255, 0), -1)

        palm_center_x, palm_center_y = get_palm_center(lm)

        left = CAMERA_MARGIN
        right = 1 - CAMERA_MARGIN
        top = CAMERA_MARGIN
        bottom = 1 - CAMERA_MARGIN

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

        if frame_counter == -1:
            
            if gesture_name == "Draw":
                drawing_mode = True
            else:
                drawing_mode = False

            if mouse_held and drawing_mode:
                pyautogui.dragTo(smooth_x, smooth_y, duration=0, button='left')
            else:
                pyautogui.moveTo(smooth_x, smooth_y)

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

        frame_counter += 1

        cv2.putText(frame, f"Gesture: {gesture_name}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        

        cv2.imshow("Gesture Mouse Control", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
  

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys

    model_path = sys.argv[1] if len(sys.argv) > 1 else "gesture_model_mouvement_xgb.pkl"
    labels_path = sys.argv[2] if len(sys.argv) > 2 else "gesture_labels_mouvement.pkl"

    run_gesture_mouse(model_path, labels_path)
