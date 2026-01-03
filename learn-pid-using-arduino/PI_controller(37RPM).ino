
// P + I control with base feedforward (no anti-windup)
const int ENA = 9, IN1 = 8, IN2 = 7;
const int ENCODER_A = 2;
volatile long encoderCount = 0;

const int CPR = 2973;
unsigned long lastTime = 0;
const unsigned long sampleTime = 100; // ms

float setpoint = 20.0;     // RPM target
float Kp = 30.0;           // proportional gain
float Ki = 1.0;            // integral gain (tune this value)
int basePWM = 60;         // from your Day2 test

// Integral accumulator
float Iterm = 0.0;

void encoderISR() { encoderCount++; }

void setup() {
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENCODER_A, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A), encoderISR, RISING);
  Serial.begin(115200);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); // forward
  lastTime = millis();
}

void loop() {
  unsigned long now = millis();
  if (now - lastTime >= sampleTime) {
    unsigned long dt = now - lastTime;
    lastTime = now;

    noInterrupts();
    long c = encoderCount;
    encoderCount = 0;
    interrupts();

    float rpm = (c * (60000.0 / dt)) / CPR;

    // Error
    float error = setpoint - rpm;

    // Integral term 
    Iterm += Ki * error * (dt / 1000.0);  // scale by seconds

    // PI control with base feed
    int u = basePWM + (int)(Kp * error + Iterm);

    // Limit PWM
    u = constrain(u, 0, 255);
    analogWrite(ENA, u);

  
    Serial.print(setpoint);
    Serial.print(" ");
    Serial.print(rpm);
    Serial.println(" ");

  }
}
