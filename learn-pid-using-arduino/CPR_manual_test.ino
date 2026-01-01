// Encoder pins
const int ENCODER_A = 2;
const int ENCODER_B = 3;

volatile long encoderCount = 0;

void setup() {
  Serial.begin(9600);
  pinMode(ENCODER_A, INPUT_PULLUP);
  pinMode(ENCODER_B, INPUT_PULLUP);

  // Count only A channel
  attachInterrupt(digitalPinToInterrupt(ENCODER_A), encoderISR, RISING);

  Serial.println("Rotate motor shaft slowly ONE full turn by hand...");
}

void loop()
 {

  Serial.print("Pulses counted: ");
  Serial.println(encoderCount);
  delay(500);
}

void encoderISR() {
  encoderCount++;
}
