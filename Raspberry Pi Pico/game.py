from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
import random

# Initialize OLED
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# Buttons
btn_left = Pin(14, Pin.IN, Pin.PULL_UP)
btn_right = Pin(15, Pin.IN, Pin.PULL_UP)

# LEDs
led_green = Pin(16, Pin.OUT)
led_red = Pin(17, Pin.OUT)

def run_space_game():
    # Turn off indicator LEDs at start
    led_green.value(0)
    led_red.value(0)
    
    # Player Ship (Triangle at bottom)
    ship_x = 60
    ship_y = 56
    ship_w = 9
    
    # Laser Bullet
    bullet_x = -1
    bullet_y = -1
    bullet_active = False
    
    # Enemy Alien
    enemy_x = random.randint(0, 118)
    enemy_y = 0
    enemy_w = 10
    enemy_h = 6
    enemy_speed = 1.0
    
    score = 0
    target_score = 25

    while True:
        # 1. READ INPUTS
        if btn_left.value() == 0 and ship_x > 0:
            ship_x -= 3
        if btn_right.value() == 0 and ship_x < (128 - ship_w):
            ship_x += 3

        # 2. BULLET LOGIC (Auto-fire)
        if not bullet_active:
            bullet_x = ship_x + (ship_w // 2)
            bullet_y = ship_y
            bullet_active = True
        else:
            bullet_y -= 5  # Bullet speed going up
            if bullet_y < 0:
                bullet_active = False

        # 3. ENEMY MOVEMENT
        enemy_y += enemy_speed

        # 4. COLLISION: Bullet hits Enemy
        if bullet_active:
            if (bullet_x >= enemy_x and bullet_x <= enemy_x + enemy_w and
                bullet_y >= enemy_y and bullet_y <= enemy_y + enemy_h):
                score += 1
                bullet_active = False
                enemy_x = random.randint(0, 118)
                enemy_y = 0
                
                # Slightly increase enemy speed every 3 kills
                if score % 3 == 0:
                    enemy_speed += 0.3

        # 5. WIN CONDITION
        if score >= target_score:
            led_green.value(1)
            oled.fill(0)
            oled.text("GALAXY SAVED!", 16, 20)
            oled.text(f"Score: {score}/{target_score}", 24, 38)
            oled.show()
            break

        # 6. LOSE CONDITION (Enemy hits bottom/ship)
        if enemy_y + enemy_h >= ship_y:
            led_red.value(1)
            oled.fill(0)
            oled.text("SHIP DESTROYED!", 4, 20)
            oled.text(f"Final Score: {score}", 8, 38)
            oled.show()
            break

        # 7. DRAW GRAPHICS
        oled.fill(0)

        # Draw Ship (Custom Triangle / Rocket shape)
        oled.fill_rect(ship_x + 3, ship_y, 3, 6, 1)        # Nose
        oled.fill_rect(ship_x, ship_y + 4, ship_w, 3, 1)   # Wings

        # Draw Laser Bullet
        if bullet_active:
            oled.vline(bullet_x, bullet_y, 3, 1)

        # Draw Enemy Alien Box
        oled.rect(enemy_x, int(enemy_y), enemy_w, enemy_h, 1)
        oled.pixel(enemy_x + 2, int(enemy_y) + 2, 1)      # Alien eyes
        oled.pixel(enemy_x + 7, int(enemy_y) + 2, 1)

        # Draw Score Header
        oled.text(f"Kills:{score}/{target_score}", 0, 0)

        oled.show()
        time.sleep(0.03)  # ~30 FPS frame rate

    # Wait for either button press to restart
    time.sleep(1)
    while btn_left.value() == 1 and btn_right.value() == 1:
        time.sleep(0.1)

# Main Execution Loop
while True:
    run_space_game()