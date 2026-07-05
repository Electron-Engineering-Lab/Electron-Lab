from machine import Pin, PWM, UART
import time

# 1. Setup Bluetooth (UART0)
bluetooth = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# 2. Setup Motor Pins (PWM)
m_a1 = PWM(Pin(2))
m_a2 = PWM(Pin(3))
m_b1 = PWM(Pin(4))
m_b2 = PWM(Pin(5))

# Set frequency for all motors
m_a1.freq(1000)
m_a2.freq(1000)
m_b1.freq(1000)
m_b2.freq(1000)

# Speed value (0 to 65535) -> 45000 is about 70% speed
speed = 45000

print("Car is ready...")

while True:
    if bluetooth.any():
        # Read 1 character from phone
        command = bluetooth.read(1).decode('utf-8')
        
        if command == 'F':    # Move Forward
            m_a1.duty_u16(speed)
            m_a2.duty_u16(0)
            m_b1.duty_u16(speed)
            m_b2.duty_u16(0)
            
        elif command == 'B':  # Move Backward
            m_a1.duty_u16(0)
            m_a2.duty_u16(speed)
            m_b1.duty_u16(0)
            m_b2.duty_u16(speed)
            
        elif command == 'L':  # Turn Left
            m_a1.duty_u16(0)
            m_a2.duty_u16(speed)
            m_b1.duty_u16(speed)
            m_b2.duty_u16(0)
            
        elif command == 'R':  # Turn Right
            m_a1.duty_u16(speed)
            m_a2.duty_u16(0)
            m_b1.duty_u16(0)
            m_b2.duty_u16(speed)
            
        elif command == 'S':  # Stop All Motors
            m_a1.duty_u16(0)
            m_a2.duty_u16(0)
            m_b1.duty_u16(0)
            m_b2.duty_u16(0)
            
    time.sleep(0.05)