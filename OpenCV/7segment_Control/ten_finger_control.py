import cv2
import serial
import time
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- 1. COM PORT SETUP ---
SERIAL_PORT = 'COM5'  # Set to your Pico COM port from Device Manager
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print(f"Connected to Pico on {SERIAL_PORT}")
except Exception as e:
    print(f"Serial Error: {e}")
    exit()

# --- 2. MEDIAPIPE MODEL SETUP (Set max 2 hands) ---
MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,  # Set to track BOTH hands (up to 10 fingers)
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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror frame
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    total_fingers = 0

    if detection_result.hand_landmarks:
        # Loop through detected hands (up to 2 hands)
        for hand_idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
            
            # Determine if current hand is Left or Right
            is_right_hand = False
            if detection_result.handedness:
                label = detection_result.handedness[hand_idx][0].category_name
                # Note: Flipped frame swaps Left and Right labels
                is_right_hand = (label == "Left")

            # Draw Skeletal Lines in RED (0, 0, 255)
            for connection in HAND_CONNECTIONS:
                start_p = get_coords(hand_landmarks[connection[0]], w, h)
                end_p = get_coords(hand_landmarks[connection[1]], w, h)
                cv2.line(frame, start_p, end_p, (0, 0, 255), 3)

            # Draw Joint Dots
            for lm in hand_landmarks:
                cx, cy = get_coords(lm, w, h)
                cv2.circle(frame, (cx, cy), 5, (255, 255, 255), -1)

            # --- THUMB DETECTION (Direction depends on hand) ---
            if is_right_hand:
                if hand_landmarks[tip_ids[0]].x < hand_landmarks[pip_ids[0]].x:
                    total_fingers += 1
            else:
                if hand_landmarks[tip_ids[0]].x > hand_landmarks[pip_ids[0]].x:
                    total_fingers += 1

            # --- OTHER 4 FINGERS DETECTION (Vertical Y height) ---
            for i in range(1, 5):
                if hand_landmarks[tip_ids[i]].y < hand_landmarks[pip_ids[i]].y:
                    total_fingers += 1

    # Send total count to Pico (e.g., "7\n")
    command = f"{total_fingers}\n"
    ser.write(command.encode('utf-8'))

    # Display count on camera screen in 2-digit format (00 to 10)
    formatted_str = f"{total_fingers:02d}"
    cv2.putText(frame, f"Fingers Count: {formatted_str}", (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("10-Finger 7-Segment Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()