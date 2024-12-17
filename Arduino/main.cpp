#include "BluetoothHeader556.h"
#include "MotorHeader556.h"
#include <arduino-timer.h>   // Include the arduino-timer library

//Program and Board Configuration
String PROGRAM_NAME = "556 SLAM";
String BT_BOARD_NAME = "ESP32_BOARD_J (JAY)"; //This will rename the name that the board broadcasts
auto timer = timer_create_default(); // Create a timer instance

//Declare Bluetooth Program Object
BTHeader btStartUp(PROGRAM_NAME, BT_BOARD_NAME);

//Pythons Constants
const byte SEEKBAR_MIN = 0;
const byte SEEKBAR_MAX = 100;

const byte MOTOR_LEFT_FWD = 3;
const byte MOTOR_RIGHT_FWD = 2;
const byte MOTOR_LEFT_REAR = 4;
const byte MOTOR_RIGHT_REAR = 1;

const byte HIGH_SPEED = 120;
const byte LOW_SPEED = 100;

const bool MOTOR_LF_POL = 1;
const bool MOTOR_RF_POL = 1;
const bool MOTOR_LR_POL = 0;
const bool MOTOR_RR_POL = 1;

MecanumMotor LF(MOTOR_LEFT_FWD, MOTOR_LF_POL);
MecanumMotor RF(MOTOR_RIGHT_FWD, MOTOR_RF_POL);
MecanumMotor LR(MOTOR_LEFT_REAR, MOTOR_LR_POL);
MecanumMotor RR(MOTOR_RIGHT_REAR, MOTOR_RR_POL);

const int TEST_ROUTINE_RUN_TIME = 600;
const int TEST_ROUTINE_STOP_TIME = 500;

//Serial channel communication variables
char rxChannel;
int rxValue;
byte controlValue;
byte LSB = 0;
byte MSB = 0;
unsigned long currentTime = 0;
int updateRate = 75;

//Sensor Pin Numbers
const int R_TRIGGER_PIN = 13;
const int R_ECHO_PIN = 33;
const int L_TRIGGER_PIN = 14;
const int L_ECHO_PIN = 2;
const int F_TRIGGER_PIN = 15;
const int F_ECHO_PIN = 4;

//Sensor Duration and Distance Variables
// Timing constants
const int TIME_BASE = 500;
const int LEFT_SENSOR_DELAY = TIME_BASE * 1; // Delay for left sensor in ms
const int FORWARD_SENSOR_DELAY = TIME_BASE * 2; // Delay for forward sensor in ms
const int SAMPLE_TIME = TIME_BASE * 3; // Sample time for all sensors in ms

// Sensor Distance Variables
volatile int R_Distance;
volatile int L_Distance;
volatile int F_Distance;

/* #region Movement Definitions*/
void stopAll() {
  LF.stop();
  RF.stop();
  LR.stop();
  RR.stop();
}

void runAll() {
  LF.run();
  RF.run();
  LR.run();
  RR.run();
}

void goForward() {  
  LF.setDirection(1);
  RF.setDirection(1);
  LR.setDirection(1);
  RR.setDirection(1);
  runAll();
}

void goBack() {
  LF.setDirection(0);
  RF.setDirection(0);
  LR.setDirection(0);
  RR.setDirection(0);
  runAll();
}

void turnCW() {
  LF.setDirection(1);
  RF.setDirection(0);
  LR.setDirection(1);
  RR.setDirection(0);
  runAll();
}

void turnCCW() {
  LF.setDirection(0);
  RF.setDirection(1);
  LR.setDirection(0);
  RR.setDirection(1);
  runAll();
}

/*#endregion*/

// Function to calculate distance
int calculateDistance(int triggerPin, int echoPin) {
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2;
}

// Timer callback for right sensor
bool measureRightSensor(void *) {
  R_Distance = calculateDistance(R_TRIGGER_PIN, R_ECHO_PIN);
  Serial.print("R Distance: ");
  Serial.println(R_Distance);
  String message = "H" + String(R_Distance) + "\n";
  SerialBT.print(message);
  return true; // Repeat the task
}

// Timer callback for left sensor
bool measureLeftSensor(void *) {
  L_Distance = calculateDistance(L_TRIGGER_PIN, L_ECHO_PIN);
  Serial.print("L Distance: ");
  Serial.println(L_Distance);
  String message = "F" + String(L_Distance) + "\n";
  SerialBT.print(message);
  return true; // Repeat the task
}

// Timer callback for forward sensor
bool measureForwardSensor(void *) {
  F_Distance = calculateDistance(F_TRIGGER_PIN, F_ECHO_PIN);
  Serial.print("F Distance: ");
  Serial.println(F_Distance);
  String message = "G" + String(F_Distance) + "\n";
  SerialBT.print(message);
  return true; // Repeat the task
}

//Must initialize static variables outside of the class in Main. It is "GLOBAL"
byte MecanumMotor::output = 0;

void setup()
{
// Serial.begin() called
// Set shift register pins to output
// Pull SR ENABLE pin LOW
btStartUp.setupBTSerial();
MecanumMotor::initialize();

// Set motor pins to OUTPUT
LF.startMotor();
RF.startMotor();
LR.startMotor();
RR.startMotor();

// Turn on motors
LF.setState(1);
RF.setState(1);
LR.setState(1);
RR.setState(1);

// Turn on motors
LF.setSpeed(HIGH_SPEED);
RF.setSpeed(HIGH_SPEED);
LR.setSpeed(HIGH_SPEED);
RR.setSpeed(HIGH_SPEED);

// Set Ultrasonic Pins
pinMode(R_TRIGGER_PIN, OUTPUT);
pinMode(R_ECHO_PIN, INPUT);
pinMode(L_TRIGGER_PIN, OUTPUT);
pinMode(L_ECHO_PIN, INPUT);
pinMode(F_TRIGGER_PIN, OUTPUT);
pinMode(F_ECHO_PIN, INPUT);

// Schedule sensor measurements with staggered timings
timer.every(SAMPLE_TIME, measureRightSensor); // Measure every SAMPLE_TIME
timer.in(LEFT_SENSOR_DELAY, [](void *) -> bool { timer.every(SAMPLE_TIME, measureLeftSensor); return false; }); // Start left sensor LEFT_SENSOR_DELAY later/
timer.in(FORWARD_SENSOR_DELAY, [](void *) -> bool { timer.every(SAMPLE_TIME, measureForwardSensor); return false; }); // Start forward sensor FORWARD_SENSOR_DELAY later
}
bool moveFlag = true;
const int BASE_UPDATE_RATE = 75;
void loop() {
  timer.tick();
if (SerialBT.available() > 0)
  {
    rxChannel = SerialBT.read();
    rxValue = SerialBT.parseInt();

    switch (rxChannel)
    {
    case 'A':
      LF.setSpeed(map(rxValue, SEEKBAR_MIN, SEEKBAR_MAX, LOW_SPEED, HIGH_SPEED));
      Serial.print("Channel 0: ");
      Serial.println(LF.getSpeed());
      break;
    case 'B':
      RF.setSpeed(map(rxValue, SEEKBAR_MIN, SEEKBAR_MAX, LOW_SPEED, HIGH_SPEED));
      Serial.print("Channel 1: ");
      Serial.println(RF.getSpeed());
      break;
    case 'C':
      LR.setSpeed(map(rxValue, SEEKBAR_MIN, SEEKBAR_MAX, LOW_SPEED, HIGH_SPEED));
      Serial.print("Channel 2: ");
      Serial.println(LR.getSpeed());
      break;
    case 'D':
      RR.setSpeed(map(rxValue, SEEKBAR_MIN, SEEKBAR_MAX, LOW_SPEED, HIGH_SPEED));
      Serial.print("Channel 3: ");
      Serial.println(RR.getSpeed());
      break;
    case 'E':
      controlValue = rxValue;
      Serial.print("Channel 4: ");
      Serial.println(controlValue);
      break;
    }
  }

  switch (controlValue)
  {
  case 0:
    stopAll();
    break;
  case 1:
    goForward();
    break;
  case 2:
    goBack();
    break;
  case 9:
    turnCW();
    break;
  case 10:
    turnCCW();
    break;
  }
  delay(TX_SYNC_DELAY);
}
