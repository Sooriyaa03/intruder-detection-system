#include <Servo.h>

// Pin configuration
const int trigPin = 9;    // Ultrasonic Sensor Trig pin
const int echoPin = 10;   // Ultrasonic Sensor Echo pin
Servo myservo;            // Create Servo object

// Global variables
int currentAngle = 15;
bool sweepingForward = true;

bool objectDetected = false;
bool canPrintAgain = true;
unsigned long lastPrintedTime = 0;
const unsigned long printDelay = 5000;

void setup() {
  myservo.attach(7);     // Attach servo to pin 7

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  Serial.begin(9600);
}

void loop() {
  float distance = getDistance();
  unsigned long currentTime = millis();

  if (distance <= 20.0) {
    if (!objectDetected && canPrintAgain) {
      Serial.println(distance);
      lastPrintedTime = currentTime;
      objectDetected = true;
      canPrintAgain = false; // block future prints until object moves away + 5s
    }

    myservo.write(currentAngle); // Hold at current position
    delay(100);
  } else {
    if (objectDetected) {
      objectDetected = false;  // Object just left
    }

    // Check if 5 seconds have passed since last print
    if (!canPrintAgain && (currentTime - lastPrintedTime >= printDelay)) {
      canPrintAgain = true;
    }

    // Sweep the servo
    if (sweepingForward) {
      currentAngle++;
      if (currentAngle >= 165) {
        currentAngle = 165;
        sweepingForward = false;
      }
    } else {
      currentAngle--;
      if (currentAngle <= 15) {
        currentAngle = 15;
        sweepingForward = true;
      }
    }

    myservo.write(currentAngle);
    delay(15);
  }
}

// Function to get distance from Ultrasonic Sensor
float getDistance() {
  long duration;
  float distance;

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.0343 / 2;

  return distance;
}
