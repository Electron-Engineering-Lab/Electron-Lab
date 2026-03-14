#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2
#define HEATER_PWM 3

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

float setpoint = 40.0;
float temperature;
float error;

// ===== MEMBERSHIP FUNCTIONS =====
float coldMF(float e) {
  if (e <= 0) return 0;
  if (e >= 6) return 1;
  return e / 6.0;
}

float warmMF(float e) {
  if (e <= -2 || e >= 2) return 0;
  if (e == 0) return 1;
  if (e < 0) return (e + 2) / 2.0;
  return (2 - e) / 2.0;
}

float hotMF(float e) {
  if (e >= 0) return 0;
  if (e <= -6) return 1;
  return -e / 6.0;
}

void setup() {
  Serial.begin(9600);
  sensors.begin();
  pinMode(HEATER_PWM, OUTPUT);
}

void loop() {
  sensors.requestTemperatures();
  temperature = sensors.getTempCByIndex(0);
  error = setpoint - temperature;

  // ===== FUZZIFICATION =====
  float cold = coldMF(error);
  float warm = warmMF(error);
  float hot  = hotMF(error);

  // ===== RULE BASE =====
  // IF Cold → PWM High (70)
  // IF Warm → PWM Medium (40)
  // IF Hot  → PWM Low (10)

  float pwm =
    (cold * 25 + warm * 5 + hot * 0) /
    (cold + warm + hot + 0.0001);   // avoid divide by zero

  analogWrite(HEATER_PWM, (int)pwm);

  Serial.print("    "); Serial.print(setpoint);
  Serial.print("      "); Serial.print(temperature);
  Serial.print(" Error: "); Serial.print(error);
  Serial.print(" PWM: "); Serial.println(pwm);

  delay(500);
}

