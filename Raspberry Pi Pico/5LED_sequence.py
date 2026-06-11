from machine import Pin
import time

led_pins = [11, 12, 13, 14, 15]

leds = [Pin(p, Pin.OUT) for p in led_pins]

while True:
    for x in range(len(leds)):
        leds[x].value(1)
        time.sleep(0.3) 
        

        leds[x].value(0)
        time.sleep(0.3)