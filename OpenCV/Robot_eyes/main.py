import sys
import select
from machine import Pin, PWM

# Servo 1: Left Eye (GP15), Servo 2: Right Eye (GP14)
eye1 = PWM(Pin(15))
eye2 = PWM(Pin(14))
eye1.freq(50)
eye2.freq(50)

def set_eyes(angle1, angle2):
    angle1 = max(0, min(180, angle1))
    angle2 = max(0, min(180, angle2))
    
    duty1 = int(1638 + (angle1 / 180.0) * (8191 - 1638))
    duty2 = int(1638 + (angle2 / 180.0) * (8191 - 1638))
    
    eye1.duty_u16(duty1)
    eye2.duty_u16(duty2)

# Center both eyes straight ahead at start (90°, 90°)
set_eyes(90, 90)

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)

buffer = ""

while True:
    events = poll.poll(10)
    if events:
        char = sys.stdin.read(1)
        if char == '\n':
            data = buffer.strip()
            buffer = ""
            if ',' in data:
                parts = data.split(',')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    set_eyes(int(parts[0]), int(parts[1]))
        else:
            buffer += char