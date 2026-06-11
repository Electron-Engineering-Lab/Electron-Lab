from machine import Pin
import time

# Define the control pins for the L9110S driver
motor_in1 = Pin(14, Pin.OUT)
motor_in2 = Pin(15, Pin.OUT)

def motor_forward():
    print("Moving Forward...")
    motor_in1.value(1)
    motor_in2.value(0)

def motor_reverse():
    print("Moving Reverse...")
    motor_in1.value(0)
    motor_in2.value(1)

def motor_stop():
    print("Motor Stopped.")
    motor_in1.value(0)
    motor_in2.value(0)

# Main testing loop
try:
    print("Starting H-Bridge Forward/Reverse Test Loop...")
    while True:
        # 1. Test Forward
        motor_forward()
        time.sleep(3.0)
        
        # 2. Pause
        motor_stop()
        time.sleep(1.0)
        
        # 3. Test Reverse
        motor_reverse()
        time.sleep(3.0)
        
        # 4. Pause
        motor_stop()
        time.sleep(1.0)

except KeyboardInterrupt:
    # Ensure motor turns off safely if we stop the script in Thonny
    motor_stop()
    print("Test terminated safely.")