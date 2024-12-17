#include <Arduino.h>
#include <BluetoothSerial.h>

// BluetoothSerial Constants
BluetoothSerial SerialBT;
const int TX_SYNC_DELAY = 1;
const int BAUD_RATE = 115200; // ESP32 Primary Baud Rate for Bluetooth Serial
const int SERIAL_TIMEOUT_DELAY = 10;

class BTHeader {
    public:
    BTHeader (String _Program, String _Board);
    void setupBTSerial(void);

    private:
    String programName;
    String boardName;
};

BTHeader::BTHeader (String _Program, String _Board) {
    programName = _Program;
    boardName = _Board;
}

void BTHeader::setupBTSerial (void) {
// Serial Initialization
  Serial.begin(BAUD_RATE);
  Serial.print("Start ");
  Serial.print(programName);
  Serial.println(" program.");

  // BluetoothSerial Initialization
  SerialBT.setTimeout(SERIAL_TIMEOUT_DELAY);
  SerialBT.begin(boardName); // This is the broadcasted title of the Bluetooth Server (The ESP32 dev board)
}
