#include <Arduino.h>

//const int BAUD_RATE = 115200;

class MecanumMotor {
    public:
    MecanumMotor (byte _MOTOR_NUMBER, bool _FWD);
    void setSpeed(byte _motorSpeed);
    byte getSpeed(void);
    void setDirection(bool _motorDirection);
    void setState(bool _state);
    static void initialize(void);
    void startMotor(void);
    void run(void);
    void stop(void);

    private:
    void updateSR(void);
    byte MOTOR_NUMBER;
    bool FWD; //software set the motor polarity. Default: FWD=1. 
    byte DIR_BIT_A;
    byte DIR_BIT_B;

    // Microcontroller constants
    const byte MOTOR_PIN_ARRAY[4] = {17, 18, 19, 23};
    byte MOTOR_PIN;

    byte motorSpeed;
    bool motorDirection;
    bool state;

    // 74HC595 Shift Register constants
    static const byte DATA_PIN = 25; 
    static const byte ENABLE_PIN = 32; 
    static const byte LATCH_PIN = 26;  
    static const byte CLOCK_PIN = 27; 

    static byte output;
};

MecanumMotor::MecanumMotor (byte _MOTOR_NUMBER, bool _FWD) {
    MOTOR_NUMBER = _MOTOR_NUMBER;
    FWD = _FWD;
    MOTOR_PIN = MOTOR_PIN_ARRAY[MOTOR_NUMBER - 1];
    
    state = 0;
    motorDirection = FWD;
    motorSpeed = 0;

    //M1->Bits 0 and 1, M2->Bits 2 and 3, M3->Bits 4 and 5, M4->Bits 6 and 7,
    DIR_BIT_A = 2 * (MOTOR_NUMBER - 1);
    DIR_BIT_B = DIR_BIT_A + 1;
}

void MecanumMotor::setSpeed(byte _motorSpeed)
{
    motorSpeed = _motorSpeed;
}

byte MecanumMotor::getSpeed(void) {
    return motorSpeed;
}

void MecanumMotor::setDirection(bool _motorDirection)
{
    motorDirection = _motorDirection;

    if (FWD == 0)
    {
        motorDirection = !motorDirection;
    }

    bitWrite(output, DIR_BIT_A, motorDirection);
    bitWrite(output, DIR_BIT_B, !motorDirection);
    updateSR();  
}

void MecanumMotor::run()
{
    if (state == 1)
    {
        analogWrite(MOTOR_PIN, motorSpeed);
    }
}

void MecanumMotor::stop()
{
    bitWrite(output, DIR_BIT_A, 0);
    bitWrite(output, DIR_BIT_B, 0);
    updateSR();    
}

void MecanumMotor::setState(bool _state) {
    state = _state;
}

void MecanumMotor::initialize() {
    //Serial.begin(BAUD_RATE);

    // Set all the pins of 74HC595 Shift Register as OUTPUT
    pinMode(DATA_PIN, OUTPUT);
    pinMode(ENABLE_PIN, OUTPUT);
    pinMode(LATCH_PIN, OUTPUT);
    pinMode(CLOCK_PIN, OUTPUT);

    digitalWrite(ENABLE_PIN, LOW);
}

void MecanumMotor::startMotor() {
    pinMode(MOTOR_PIN, OUTPUT);
}

void MecanumMotor::updateSR() {
    digitalWrite(LATCH_PIN, LOW);
    shiftOut(DATA_PIN, CLOCK_PIN, MSBFIRST, output);
    digitalWrite(LATCH_PIN, HIGH);
}
