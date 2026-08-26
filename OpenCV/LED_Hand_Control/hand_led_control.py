import cv2
import serial
import time
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- 1. COM PORT CONFIGURATION ---
# Change 'COM3' to your Pico's actual port from Device Manager
SERIAL_PORT = 'COM5'
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print(f"Connected successfully to Pi Pico on {SERIAL_PORT}!")
except Exception as e:
    print(f"Serial Connection Error: {e}")
    print("Make sure Thonny is closed and the COM port number is correct!")
    exit()

# --- 2. DOWNLOAD HAND MODEL IF NEEDED ---
MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)

# --- 3. INITIALIZE MEDIAPIPE TASKS ---
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

# Finger connections for skeletal drawing style
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (0, 9), (9, 10), (10, 11), (11, 12),    # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
    (0, 17), (17, 18), (18, 19), (19, 20)   # Pinky
]

tip_ids = [4, 8, 12, 16, 20]
pip_ids = [2, 6, 10, 14, 18]

# --- 4. CAMERA LOOP ---
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror frame
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    finger_states = [0, 0, 0, 0, 0]

    if detection_result.hand_landmarks:
        hand_landmarks = detection_result.hand_landmarks[0]

 # Draw skeletal style connections (Red lines: BGR format (0, 0, 255))
        for connection in HAND_CONNECTIONS:
            start_p = get_coords(hand_landmarks[connection[0]], w, h)
            end_p = get_coords(hand_landmarks[connection[1]], w, h)
            cv2.line(frame, start_p, end_p, (0, 0, 255), 3)

        # Draw joints
        for lm in hand_landmarks:
            cx, cy = get_coords(lm, w, h)
            cv2.circle(frame, (cx, cy), 6, (0, 0, 0), cv2.FILLED)
            cv2.circle(frame, (cx, cy), 5, (255, 255, 255), cv2.FILLED)

        # Thumb detection (x-axis distance)
        if hand_landmarks[tip_ids[0]].x < hand_landmarks[pip_ids[0]].x:
            finger_states[0] = 1

        # Other 4 fingers (y-axis height)
        for i in range(1, 5):
            if hand_landmarks[tip_ids[i]].y < hand_landmarks[pip_ids[i]].y:
                finger_states[i] = 1

    # Format 5-bit string (e.g. "11000\n") and send over Serial to Pico
    command = "".join(map(str, finger_states)) + "\n"
    ser.write(command.encode('utf-8'))

    # Visual display on camera screen
    cv2.putText(frame, f"LED State: {command.strip()}", (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("Hand Control LEDs (GP16-GP20)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()