// Motor pins
const int ENA = 9;      // Motor driver(ENA)
const int IN1 = 8;      // Motor driver
const int IN2 = 7;      // Motor driver

void setup() {
  Serial.begin(9600);

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  Serial.println("Base PWM test started");
}

void loop() {
  // Slowly increase PWM
  for (int pwm = 0; pwm <= 255; pwm += 5) {
    analogWrite(ENA, pwm);
    Serial.print("PWM: ");
    Serial.println(pwm);
    delay(1000);   // wait 1 second
  }

  // Stop motor after test
  analogWrite(ENA, 0);
  Serial.println("Test finished");
  delay(5000);
}
