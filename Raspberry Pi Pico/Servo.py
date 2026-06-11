from machine import Pin, PWM
import time

# Setup the servo on GP15
servo_pin = PWM(Pin(15))
servo_pin.freq(50)

# This is your "Servo.write" equivalent
def servo_write(degree):
    # Constraint to keep degrees between 0 and 180
    if degree < 0: degree = 0
    if degree > 180: degree = 180
    
    # The math that simulates Arduino's Servo.write
    duty = int((degree / 180 * 6554) + 1638)
    servo_pin.duty_u16(duty)

# Now you can use it just like Arduino!
while True:
    print("Going to 0")
    servo_write(0)
    time.sleep(1)
    
    print("Going to 90")
    servo_write(90)
    time.sleep(1)
    
    print("Going to 180")
    servo_write(180)
    time.sleep(1)