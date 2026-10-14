import sys
import select
from machine import Pin

relay = Pin(16, Pin.OUT)
relay.value(0)  # Start with relay OFF

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
            if data == '1':
                relay.value(1)  # Turn ON
            elif data == '0':
                relay.value(0)  # Turn OFF
        else:
            buffer += char