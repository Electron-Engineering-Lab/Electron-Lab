#include <OneWire.h>
#include <DallasTemperature.h>

const int sensorPin = 2;
const int heaterPin = 3;

OneWire oneWire(sensorPin);
DallasTemperature sensors(&oneWire);

double Kp = 5.0;
double Ki = 0.001;       // start small (0.05–0.10)
double Setpoint = 40;

double integral = 0;    // integral memory
unsigned long lastTime = 0;
unsigned long seconds = 0;

void setup() {
  Serial.begin(115200);
  sensors.begin();
  pinMode(heaterPin, OUTPUT);
}

void loop() {
  sensors.requestTemperatures();
  double T = sensors.getTempCByIndex(0);

  double error = Setpoint - T;

  // ===== Integral =====
  integral += error;           // accumulate
  if (integral > 250) integral = 250;     // anti-windup
  if (integral < -250) integral = -250;

  // ===== PI Output =====
  double output = (Kp * error) + (Ki * integral);
  int pwm = (int)constrain(output, 0, 255);

  analogWrite(heaterPin, pwm);

  // print once per second
  if (millis() - lastTime >= 1000) {
    lastTime = millis();
    seconds++;
    
    Serial.print(seconds);
    Serial.print("s | Temp: ");
    Serial.print(T);
    Serial.print(" | Error: ");
    Serial.print(error);
    Serial.print(" | PWM: ");
    Serial.print(pwm);
    Serial.print(" | I: ");
    Serial.println(integral);
  }
}

