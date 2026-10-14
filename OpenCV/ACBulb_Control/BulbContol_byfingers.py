import cv2
import serial
import time
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- 1. COM PORT SETUP ---
SERIAL_PORT = 'COM5'  # Update if your Pico uses a different COM port
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print(f"Connected to Pico on {SERIAL_PORT}")
except Exception as e:
    print(f"Serial Error: {e}")
    exit()

# --- 2. MEDIAPIPE MODEL SETUP ---
MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

def get_coords(lm, w, h):
    return int(lm.x * w), int(lm.y * h)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (0, 9), (9, 10), (10, 11), (11, 12),    # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
    (0, 17), (17, 18), (18, 19), (19, 20)   # Pinky
]

tip_ids = [4, 8, 12, 16, 20]
pip_ids = [2, 6, 10, 14, 18]

cap = cv2.VideoCapture(0)
last_sent_state = -1  # To prevent spamming serial port

print("AC Bulb Hand Control Active. Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror frame
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    finger_count = 0

    if detection_result.hand_landmarks:
        hand_landmarks = detection_result.hand_landmarks[0]

        # Draw red skeletal connections
        for connection in HAND_CONNECTIONS:
            start_p = get_coords(hand_landmarks[connection[0]], w, h)
            end_p = get_coords(hand_landmarks[connection[1]], w, h)
            cv2.line(frame, start_p, end_p, (0, 0, 255), 3)

        for lm in hand_landmarks:
            cx, cy = get_coords(lm, w, h)
            cv2.circle(frame, (cx, cy), 5, (255, 255, 255), -1)

        # Thumb detection (x-axis)
        if hand_landmarks[tip_ids[0]].x < hand_landmarks[pip_ids[0]].x:
            finger_count += 1

        # Other 4 fingers (y-axis)
        for i in range(1, 5):
            if hand_landmarks[tip_ids[i]].y < hand_landmarks[pip_ids[i]].y:
                finger_count += 1

    # Determine Relay Action based on gesture rule
    # 5 fingers = ON (1), 0 fingers = OFF (0)
    target_state = last_sent_state
    if finger_count == 5:
        target_state = 1
    elif finger_count == 0:
        target_state = 0

    # Send command only if state changes
    if target_state != last_sent_state:
        ser.write(f"{target_state}\n".encode('utf-8'))
        last_sent_state = target_state

    # Visual display on screen
    bulb_status = "ON (Bulb Lit)" if last_sent_state == 1 else "OFF (Bulb Unlit)"
    cv2.putText(frame, f"Fingers: {finger_count} | Relay: {bulb_status}", (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("AC Bulb Hand Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()