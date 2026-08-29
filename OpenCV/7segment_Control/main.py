import sys
import select
from machine import Pin
import time

# Pin mapping: GP0-GP7 (Segments a-g, dp), GP8-GP9 (Digit 1 Tens, Digit 2 Units)
segment_pins = [0, 1, 2, 3, 4, 5, 6, 7]
digit_pins = [8, 9]

seg_objs = [Pin(p, Pin.OUT) for p in segment_pins]
dig_objs = [Pin(p, Pin.OUT) for p in digit_pins]

NUMBERS = {
    0: [1, 1, 1, 1, 1, 1, 0],
    1: [0, 1, 1, 0, 0, 0, 0],
    2: [1, 1, 0, 1, 1, 0, 1],
    3: [1, 1, 1, 1, 0, 0, 1],
    4: [0, 1, 1, 0, 0, 1, 1],
    5: [1, 0, 1, 1, 0, 1, 1],
    6: [1, 0, 1, 1, 1, 1, 1],
    7: [1, 1, 1, 0, 0, 0, 0],
    8: [1, 1, 1, 1, 1, 1, 1],
    9: [1, 1, 1, 1, 0, 1, 1]
}

current_count = 0

def clear_display():
    for seg in seg_objs:
        seg.value(0)
    for dig in dig_objs:
        dig.value(0)

def display_digit(digit_index, number):
    clear_display()
    pattern = NUMBERS.get(number, [0, 0, 0, 0, 0, 0, 0])
    for i in range(7):
        seg_objs[i].value(pattern[i])
    dig_objs[digit_index].value(1)

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)

buffer = ""

# Main display multiplexing loop
while True:
    # 1. Non-blocking check for new count from USB Serial
    events = poll.poll(0)
    if events:
        char = sys.stdin.read(1)
        if char == '\n':
            data = buffer.strip()
            buffer = ""
            if data.isdigit():
                val = int(data)
                current_count = max(0, min(10, val))
        else:
            buffer += char

    # 2. Multiplex two digits (e.g., 00, 01, ..., 10)
    tens = current_count // 10
    units = current_count % 10

    # Display Tens digit (Left)
    display_digit(0, tens)
    time.sleep_ms(2)

    # Display Units digit (Right)
    display_digit(1, units)
    time.sleep_ms(2)