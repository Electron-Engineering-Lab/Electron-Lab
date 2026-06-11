from machine import Pin
import utime

# 1. Setup Pins
trig = Pin(17, Pin.OUT)
echo = Pin(16, Pin.IN)

def get_distance():
    # Ensure trigger is low
    trig.value(0)
    utime.sleep_us(5)
    
    # Send a 10 microsecond pulse
    trig.value(1)
    utime.sleep_us(10)
    trig.value(0)
    
    # Wait for echo to go HIGH and record the start time
    while echo.value() == 0:
        pulse_start = utime.ticks_us()
        
    # Wait for echo to go LOW and record the end time
    while echo.value() == 1:
        pulse_end = utime.ticks_us()
        
    # Calculate the duration of the pulse
    pulse_duration = pulse_end - pulse_start
    
    # Distance = (Time * Speed of Sound) / 2 (for the return trip)
    # Speed of sound is approx 0.0343 cm per microsecond
    distance = (pulse_duration * 0.0343) / 2
    
    return distance

while True:
    dist = get_distance()
    print("Distance: {:.2f} cm".format(dist))
    utime.sleep(0.5)