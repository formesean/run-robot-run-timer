#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>
#include <VL53L0X.h>

// I2C LCD
const byte LCDAddress = 0x27, LCDRows = 16, LCDColumns = 2;
LiquidCrystal_I2C lcd(LCDAddress, LCDRows, LCDColumns);

// VL53L0X
#define GET_DISTANCE distanceSensor.readRangeContinuousMillimeters()
VL53L0X distanceSensor;
const int sensorTimeout = 500;
const int sensorThreshold = 300;

// Bluetooth UART
#define BT_RX_PIN 3
#define BT_TX_PIN 2
SoftwareSerial BTSerial(BT_RX_PIN, BT_TX_PIN);

// State
bool isTimerRunning = false;
unsigned long startTime = 0;

void stopAndReport();
String formatElapsed(long ms);

void setup()
{
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  BTSerial.begin(9600);

  distanceSensor.setTimeout(sensorTimeout);
  while (!distanceSensor.init())
  {
    BTSerial.println("NO SENSOR");
    delay(100);
  }
  distanceSensor.startContinuous();

  BTSerial.println("WAITING");
  lcd.print("Waiting for");
  lcd.setCursor(0, 1);
  lcd.print("BT Connection...");
}

void loop()
{
  // 1) Handle incoming BT commands
  if (BTSerial.available())
  {
    String cmd = BTSerial.readStringUntil('\n');
    cmd.trim();
    Serial.println("[BT] " + cmd);

    if (cmd == "WAITING" && !isTimerRunning)
    {
      lcd.clear();
      lcd.print("Waiting for");
      lcd.setCursor(0, 1);
      lcd.print("Player...");
    }
    else if (cmd == "START" && !isTimerRunning)
    {
      // start race
      startTime = millis();
      isTimerRunning = true;
      BTSerial.print("START ");
      BTSerial.println(startTime);

      lcd.clear();
      lcd.print("Player passed!");
      lcd.setCursor(0, 1);
      lcd.print("Recording time...");
    }
    else if (cmd == "STOPPED" && isTimerRunning)
    {
      // external stop request
      stopAndReport();
    }
  }

  // 2) If running, poll the sensor each loop for pass-by
  if (isTimerRunning)
  {
    int dist = GET_DISTANCE;
    if (dist < sensorThreshold)
    {
      // player passed
      stopAndReport();
    }
  }

  delay(10); // small debounce
}

// Shared stop/report logic
void stopAndReport()
{
  unsigned long endTime = millis();
  long elapsed = endTime - startTime;

  // send STOP and TIME
  BTSerial.print("STOP ");
  BTSerial.println(endTime);
  BTSerial.print("TIME ");
  BTSerial.println(formatElapsed(elapsed));

  // display on LCD
  lcd.clear();
  lcd.print("Recorded Time:");
  lcd.setCursor(0, 1);
  lcd.print(formatElapsed(elapsed));

  isTimerRunning = false;
}

// Helper to format mm:ss:MS
String formatElapsed(long ms)
{
  int m = ms / 60000;
  ms %= 60000;
  int s = ms / 1000;
  ms %= 1000;
  char buf[16];
  sprintf(buf, "%d:%02d:%03d", m, s, ms);
  return String(buf);
}
