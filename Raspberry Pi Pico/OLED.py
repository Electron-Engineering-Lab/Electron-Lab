from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time

# Initialize I2C interface on bus 0 (SDA=GP0, SCL=GP1)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

WIDTH = 128
HEIGHT = 64

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def fade_in(text, x, y, delay=0.01):
    
    oled.fill(0)
    oled.text(text, x, y)
    oled.show()
    
  
    for level in range(0, 256, 15):
        oled.contrast(level)
        time.sleep(delay)

def fade_out(delay=0.01):
   
    
    for level in range(255, -1, -15):
        oled.contrast(level)
        time.sleep(delay)
    
    oled.fill(0)
    oled.show()

fade_in("Welcome", 36, 28)
time.sleep(0.8)  
fade_out()


fade_in("to", 56, 28)
time.sleep(0.8)  
fade_out()


fade_in("Electron Lab", 16, 28)
# Restore max contrast for normal use
oled.contrast(255)