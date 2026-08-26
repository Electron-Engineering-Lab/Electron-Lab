import sys
import select
from machine import Pin, PWM

# Pin setup: Thumb (GP16), Index (GP17), Middle (GP18), Ring (GP19), Pinky (GP20)
led_pins = [16, 17, 18, 19, 20]
pwms = [PWM(Pin(p)) for p in led_pins]

# Set frequency to 1000Hz and turn all LEDs OFF at start
for pwm in pwms:
    pwm.freq(1000)
    pwm.duty_u16(0)

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
            
            # Case 1: Simple 5-bit binary string (e.g., "11000")
            if len(data) == 5 and ',' not in data:
                for i in range(5):
                    pwms[i].duty_u16(65535 if data[i] == '1' else 0)
            
            # Case 2: PWM comma-separated string (e.g., "255,128,0,0,0")
            elif ',' in data:
                parts = data.split(',')
                if len(parts) == 5:
                    try:
                        for i in range(5):
                            val = int(parts[i])
                            val = max(0, min(255, val))
                            pwms[i].duty_u16(int((val / 255.0) * 65535))
                    except ValueError:
                        pass
        else:
            buffer += char