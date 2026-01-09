// Position PID-Control with Anti-Windup
const int ENA = 9, IN1 = 8, IN2 = 7;
const int ENCODER_A = 2;
volatile long encoderCount = 0;

const int CPR = 2973;          // counts per revolution
unsigned long lastTime = 0;
const unsigned long sampleTime = 50; // ms

// Target position (degrees)
float setpoint = 90.0;

// PID gains
float Kp = 1.0;
float Ki = 0.0;
float Kd = 0.0;

// PID terms
float Iterm = 0.0;
float lastError = 0.0;

void encoderISR() { encoderCount++; }

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENCODER_A, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A), encoderISR, RISING);

  Serial.begin(115200);
  lastTime = millis();
}

void loop() {
  unsigned long now = millis();
  if (now - lastTime >= sampleTime) {
    unsigned long dt = now - lastTime;
    lastTime = now;
    float dt_s = dt / 1000.0;  // convert ms → seconds

    // Current angle (degrees)
    noInterrupts();
    long count = encoderCount;
    interrupts();
    float angle = (count * 360.0) / CPR;

    // Error
    float error = setpoint - angle;

    // Derivative
    float derivative = (error - lastError) / dt_s;
    lastError = error;

    // PID control (compute first, before constrain)
    float control = Kp * error + Iterm + Kd * derivative;

    // Clamp output
    int u = constrain((int)control, 0, 255);

    // Anti-windup: only integrate if not saturated
    if (u > 0 && u < 255) {
      Iterm += Ki * error * dt_s;
    }

    // Direction control
    if (control > 0) {
      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);   // forward
    } else {
      digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);  // reverse
    }

    analogWrite(ENA, u);

    // Debug
    Serial.print(" "); Serial.print(setpoint);
    Serial.print("  "); Serial.println(angle);
    //Serial.print(" | PWM: "); Serial.println(u);
  }
}
