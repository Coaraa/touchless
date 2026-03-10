import cv2
import joblib
import pyautogui
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

CAMERA_MARGIN = 0.15  


model = joblib.load("gesture_model_xgb.pkl")
label_encoder = joblib.load("gesture_labels.pkl")

base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)

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

screen_w, screen_h = pyautogui.size()
smooth_x, smooth_y = 0, 0
alpha = 0.25

mouse_held = False
drawing_mode = False 

last_good_landmarks = None
frames_since_seen = 0
MAX_MISSED_FRAMES = 8

cap = cv2.VideoCapture(0)

print("Gesture mouse control active. Press ESC to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

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

    flat = []
    for x, y, z in norm:
        flat += [x, y, z]

    pred = model.predict([flat])[0]
    gesture_name = label_encoder.inverse_transform([pred])[0]

    for p in lm:
        h, w, _ = frame.shape
        cx, cy = int(p.x * w), int(p.y * h)
        cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

    px, py = get_palm_center(lm)

    left = CAMERA_MARGIN
    right = 1 - CAMERA_MARGIN
    top = CAMERA_MARGIN
    bottom = 1 - CAMERA_MARGIN

    px = min(max(px, left), right)
    py = min(max(py, top), bottom)

    norm_x = (px - left) / (right - left)
    norm_y = (py - top) / (bottom - top)

    screen_x = int((1 - norm_x) * screen_w)
    screen_y = int(norm_y * screen_h)

    smooth_x = int(smooth_x + alpha * (screen_x - smooth_x))
    smooth_y = int(smooth_y + alpha * (screen_y - smooth_y))

    if gesture_name == "pinch":
        drawing_mode = True
    else:
        drawing_mode = False

    if mouse_held and drawing_mode:
        pyautogui.dragTo(smooth_x, smooth_y, duration=0, button='left')
    else:
        pyautogui.moveTo(smooth_x, smooth_y)

    if gesture_name == "click":
        pyautogui.click()


    if gesture_name in ["fist", "pinch"]:
        if not mouse_held:
            pyautogui.mouseDown()
            mouse_held = True
    else:
        if mouse_held:
            pyautogui.mouseUp()
            mouse_held = False

    cv2.putText(frame, f"Gesture: {gesture_name}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

    cv2.imshow("Gesture Mouse Control", frame)
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()

