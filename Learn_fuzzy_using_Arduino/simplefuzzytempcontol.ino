#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2
#define HEATER_PWM 3

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

float setpoint = 40.0;
float temperature;
float error;
int pwmOutput;

void setup() {
  Serial.begin(9600);
  sensors.begin();
  pinMode(HEATER_PWM, OUTPUT);
}

void loop() {
  sensors.requestTemperatures();
  temperature = sensors.getTempCByIndex(0);
  error = setpoint - temperature;

  // ===== VERY SIMPLE FUZZY (IMPROVED) =====

  if (error > 6) {                 // Very cold
    pwmOutput = 70;               // was 255 → now LIMITED
  }
  else if (error > 3) {            // Cold
    pwmOutput = 40;
  }
  else if (error > 1) {            // Near setpoint
    pwmOutput = 20;
  }
  else if (error > 0) {            // Very near
    pwmOutput = 10;
  }
  else {                           // Above setpoint
    pwmOutput = 0;
  }

  analogWrite(HEATER_PWM, pwmOutput);

  Serial.print("Set: "); Serial.print(setpoint);
  Serial.print("  Temp: "); Serial.print(temperature);
  Serial.print("  Error: "); Serial.print(error);
  Serial.print("  PWM: "); Serial.println(pwmOutput);

  delay(500);
}

