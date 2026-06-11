from machine import Pin
import time

# 1. Setup Pins
# IR sensor is an INPUT to the Pico
ir_sensor = Pin(6, Pin.IN) 
# LED is an OUTPUT from the Pico
led = Pin(15, Pin.OUT)

print("System Ready: Place your hand in front of the IR sensor")

while True:
    # Most IR sensors go LOW (0) when they detect something
    if ir_sensor.value() == 0:
        led.value(1)  # Turn LED on
        print("Obstacle detected!")
    else:
        led.value(1)  # Turn LED off
        # Wait, if I want it OFF when nothing is there, use:
        led.value(0) 
        
    time.sleep(0.05) # Fast checking for better response