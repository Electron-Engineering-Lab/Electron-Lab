import cv2
import serial
import time
import urllib.request
import os
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- 1. COM PORT SETUP ---
SERIAL_PORT = 'COM5'  # Update to your Pico COM port if different
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

cap = cv2.VideoCapture(0)
current_angle1, current_angle2 = 90, 90

print("Two-Eye Horizontal Tracking Active. Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror frame
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    target_angle1, target_angle2 = current_angle1, current_angle2

    if detection_result.hand_landmarks:
        hand_landmarks = detection_result.hand_landmarks[0]

        # Get Index Fingertip (Landmark ID 8)
        index_tip = hand_landmarks[8]
        cx, cy = get_coords(index_tip, w, h)

        # Draw red dot on fingertip
        cv2.circle(frame, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

        # Map X position of finger (0 to width) to Eye Angles (0 to 180 degrees)
        base_angle = int(np.interp(cx, [0, w], [0, 180]))
        
        # Both eyes track the horizontal position of the finger
        target_angle1 = base_angle
        target_angle2 = base_angle  

        # Smooth movement to prevent jitter
        current_angle1 = int(current_angle1 * 0.7 + target_angle1 * 0.3)
        current_angle2 = int(current_angle2 * 0.7 + target_angle2 * 0.3)

    # Send command string "Angle1,Angle2\n" over serial
    command = f"{current_angle1},{current_angle2}\n"
    ser.write(command.encode('utf-8'))

    # Visual display on screen
    cv2.putText(frame, f"Left Eye: {current_angle1} | Right Eye: {current_angle2}", (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Two Eyes Horizontal Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()