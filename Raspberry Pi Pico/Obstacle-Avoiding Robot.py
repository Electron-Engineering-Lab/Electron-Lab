from machine import Pin, PWM
import time

# --- 1. Setup Ultrasonic Sensor Pins ---
trig = Pin(16, Pin.OUT)
echo = Pin(17, Pin.IN)

# --- 2. Setup Motor Pins 
m_a1 = PWM(Pin(2))
m_a2 = PWM(Pin(3))
m_b1 = PWM(Pin(4))
m_b2 = PWM(Pin(5))

# Set PWM frequency
m_a1.freq(1000)
m_a2.freq(1000)
m_b1.freq(1000)
m_b2.freq(1000)

# Speed value
speed = 45000

# --- Movement Functions Built from Your Code ---
def move_forward():
    m_a1.duty_u16(0)
    m_a2.duty_u16(speed)
    m_b1.duty_u16(speed)
    m_b2.duty_u16(0)

def turn_right():
    m_a1.duty_u16(0)
    m_a2.duty_u16(speed)
    m_b1.duty_u16(0)
    m_b2.duty_u16(speed)

def stop_robot():
    m_a1.duty_u16(0)
    m_a2.duty_u16(0)
    m_b1.duty_u16(0)
    m_b2.duty_u16(0)

# --- Distance Calculation ---
def get_distance():
    trig.value(0)
    time.sleep_us(2)
    
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    countdown = 10000
    while echo.value() == 0:
        countdown -= 1
        if countdown <= 0:
            return 999
            
    start_time = time.ticks_us()
    
    countdown = 10000
    while echo.value() == 1:
        countdown -= 1
        if countdown <= 0:
            return 999
            
    end_time = time.ticks_us()
    
    duration = time.ticks_diff(end_time, start_time)
    distance = (duration * 0.0343) / 2
    return distance

# --- Main Logic Loop ---
print("Obstacle Car Started...")
time.sleep(2) # 2 seconds to put the car on the floor safely

while True:
    dist = get_distance()
    print("Distance:", dist, "cm")
    
    if dist <= 15: # If an obstacle is 15cm or closer
        print("Obstacle! Turning Right")
        stop_robot()      # Stop first to protect gears
        time.sleep(0.2)
        
        turn_right()      # Execute your Right turn logic
        time.sleep(0.6)   # Adjust this time to get a perfect 90-degree turn
        
        stop_robot()      # Stabilize
        time.sleep(0.2)
    else:
        # Path is clear, move forward using your forward logic
        move_forward()
        
    time.sleep(0.05) # Small loop delay