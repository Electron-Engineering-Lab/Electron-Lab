import machine
import onewire
import ds18x20
import time
import ssd1306

# ===== Hardware Setup =====
# 1. DS18B20 Temperature Sensor
sensor_pin = machine.Pin(15)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(sensor_pin))

roms = ds_sensor.scan()
if not roms:
    raise RuntimeError("No DS18B20 temperature sensor found! Check wiring and 4.7k resistor.")
print("Found DS18B20 device:", roms[0])

# 2. PWM Heater Output
heater_pwm = machine.PWM(machine.Pin(16))
heater_pwm.freq(1000)

# 3. I2C OLED Display (SDA = GP0 / Pin 1, SCL = GP1 / Pin 2)
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ===== PID Gains & Parameters =====
Kp = 5.0
Ki = 0.01
Kd = 0.0  # Set to 0.0 for PI control

Setpoint = 40.0

# ===== Controller State Variables =====
integral = 0.0
last_error = 0.0
seconds = 0

last_time = time.ticks_ms()

# Main Control Loop
while True:
    # 1. Trigger temperature conversion
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    
    # Calculate exact delta time (dt) in seconds
    current_time = time.ticks_ms()
    dt = time.ticks_diff(current_time, last_time) / 1000.0
    if dt <= 0:
        dt = 0.001
    last_time = current_time

    # 2. Read temperature
    temp = ds_sensor.read_temp(roms[0])
    if temp is None:
        heater_pwm.duty_u16(0)
        oled.fill(0)
        oled.text("SENSOR ERROR!", 10, 25)
        oled.show()
        continue

    # 3. Calculate Error
    error = Setpoint - temp

    # ===== Proportional Term =====
    P_out = Kp * error

    # ===== Integral Term =====
    integral += error * dt
    if integral > 250.0:
        integral = 250.0
    elif integral < -250.0:
        integral = -250.0
    I_out = Ki * integral

    # ===== Derivative Term =====
    derivative = (error - last_error) / dt
    D_out = Kd * derivative
    last_error = error

    # ===== Total PID Output =====
    output = P_out + I_out + D_out
    pwm_8bit = max(0.0, min(255.0, output))

    # Output to PWM Hardware
    duty_cycle_16bit = int((pwm_8bit / 255.0) * 65535)
    heater_pwm.duty_u16(duty_cycle_16bit)

    # ===== OLED Display Refresh =====
    oled.fill(0)
    oled.text("PID TEMP CONTROL", 0, 0)
    oled.text(f"Set: {Setpoint:.1f} C", 0, 16)
    oled.text(f"Temp:{temp:.2f} C", 0, 28)
    oled.text(f"PWM: {int(pwm_8bit)}/255", 0, 40)
    oled.text(f"P:{Kp:.1f} I:{Ki:.2f} D:{Kd:.1f}", 0, 52)
    oled.show()

    # Serial Telemetry Output
    seconds += dt
    print(f"{int(seconds)}s | Temp: {temp:.2f} C | Error: {error:.2f} | PWM: {int(pwm_8bit)}")