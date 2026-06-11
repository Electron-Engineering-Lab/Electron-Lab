from machine import Pin
import time


led = Pin("LED", Pin.OUT)

while True:
    led.value(1)  # Turn LED ON
    print("LED is ON")
    time.sleep(1) # Wait 1 second
    
    led.value(0)  # Turn LED OFF
    print("LED is OFF")
    time.sleep(1) # Wait 1 second