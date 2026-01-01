// ------------------------
// MOTOR & ENCODER PINS
// ------------------------
const int ENA = 9, IN1 = 8, IN2 = 7;
const int ENCODER_A = 2;

// ------------------------
// VARIABLES
// ------------------------
volatile long encoderPos = 0;
const float CPR = 330.0;   // encoder counts per revolution

float Kp = 5.0;            
float Ki = 1.5;             
float targetRPM = 20.0;     // <-- set desired RPM here

long lastEncoderPos = 0;
unsigned long lastTime = 0;

float integral = 0.0;
float integralLimit = 150.0;   // anti-windup clamp (tune)

// ------------------------
// ENCODER INTERRUPT
// ------------------------
void encoderISR() { encoderPos++; }

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENCODER_A, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_A), encoderISR, RISING);

  Serial.begin(115200);

  // always forward direction for speed test
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  lastTime = millis();
}

void loop() {
  // fixed sample time approach
  unsigned long now = millis();
  unsigned long elapsed = now - lastTime;
  if (elapsed < 50) return;    // sample every 50 ms
  float dt = elapsed / 1000.0;   // seconds
  lastTime = now;

  // read encoder safely (shared with ISR)
  noInterrupts();
  long currentPos = encoderPos;
  interrupts();

  long deltaCounts = currentPos - lastEncoderPos;
  lastEncoderPos = currentPos;

  // counts per second -> RPM
  float cps = deltaCounts / dt;
  float rpm = (cps * 60.0) / CPR;

  // ---------- PI controller ----------
  float error = targetRPM - rpm;

  // integral accumulation with anti-windup (clamped)
  integral += error * dt;
  if (integral > integralLimit) integral = integralLimit;
  if (integral < -integralLimit) integral = -integralLimit;

  float control = (Kp * error) + (Ki * integral);

  // optional: add feedforward estimate (helps reach target faster)
  // float pwm_ff = targetRPM * 5.0; // comment out until you tune

  int pwm = constrain((int)control, 0, 255);

  analogWrite(ENA, pwm);

  // ---------- SERIAL ----------
  Serial.print("   ");
  Serial.print(targetRPM);
  Serial.print("   ");
  Serial.println(rpm);
  
}

