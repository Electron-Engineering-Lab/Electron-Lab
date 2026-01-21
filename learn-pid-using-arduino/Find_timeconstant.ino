#include <OneWire.h>
#include <DallasTemperature.h>

OneWire oneWire(2);           // DS18B20 data on pin D2
DallasTemperature sensors(&oneWire);

unsigned long sec = 0;

void setup() 
{
  Serial.begin(9600);
  sensors.begin();
}

void loop()
 {
  sensors.requestTemperatures();
  float t = sensors.getTempCByIndex(0);

  Serial.print(sec);
  Serial.print(" sec  -  ");
  Serial.print(t);
  Serial.println(" C");

  sec++;
  delay(1000);   // 1 second
}

