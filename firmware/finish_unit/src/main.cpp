#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>
#include <VL53L0X.h>

// I2C LCD
const byte LCDAddress = 0x27;
const byte LCDRows = 16;
const byte LCDColumns = 2;

LiquidCrystal_I2C lcd(LCDAddress, LCDRows, LCDColumns);

// VL53L0X
#define GET_DISTANCE distanceSensor.readRangeContinuousMillimeters()

VL53L0X distanceSensor;
const int sensorTimeout = 500;

// Bluetooth UART
#define BT_RX_PIN 3
#define BT_TX_PIN 2
#define BT_EN_PIN 5

SoftwareSerial BTSerial(BT_RX_PIN, BT_TX_PIN);

// Others
#define BUTTON_PIN 4
String inputString;
const int sensorThreshold = 300;
long startTime = 0;
long endTime = 0;

void setup()
{
  Serial.begin(9600);
  // pinMode(BT_EN_PIN, OUTPUT);

  // LCD SETUP
  lcd.init();
  lcd.backlight();

  // BT UART Setup
  // digitalWrite(BT_EN_PIN, HIGH);
  // BTSerial.begin(38400);
  // delay(1000);
  // BTSerial.println("AT+NAME=FinishUnit");
  // delay(500);
  // digitalWrite(BT_EN_PIN, LOW);
  // delay(500);
  BTSerial.begin(9600);

  // VL53L0X SETUP
  distanceSensor.setTimeout(sensorTimeout);

  while (!distanceSensor.init())
  {
    BTSerial.println("NO SENSOR");
  }

  distanceSensor.startContinuous();

  // OTHER SETUP
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  BTSerial.println("WAITING");

  lcd.print("Waiting for");
  lcd.setCursor(0, 1);
  lcd.print("BT Connection...");
}

void loop()
{
  if (BTSerial.available())
  {
    inputString = BTSerial.readStringUntil('\n');
    inputString.replace("\r", "");
    inputString.trim();

    BTSerial.println(inputString);
    Serial.println("[DEBUG] Received START");

    if (inputString == "WAITING")
    {
      lcd.clear();
      lcd.print("Waiting for");
      lcd.setCursor(0, 1);
      lcd.print("Player...");
    }

    if (inputString == "START")
    {
      startTime = millis();
      BTSerial.print("START ");
      BTSerial.println(startTime);

      lcd.clear();
      lcd.print("Player passed!");
      lcd.setCursor(0, 1);
      lcd.print("Recording time...");

      delay(2000);

      while (GET_DISTANCE < sensorThreshold)
        delay(10);

      while (GET_DISTANCE > sensorThreshold)
        delay(10);

      endTime = millis();
      BTSerial.print("STOP ");
      BTSerial.println(endTime);

      long actualTime = endTime - startTime;
      long minutes = actualTime / 60000;
      actualTime %= 60000;
      long seconds = actualTime / 1000;
      actualTime %= 1000;

      lcd.clear();
      lcd.print("Recorded Time:");
      lcd.setCursor(0, 1);

      // Print to LCD
      lcd.clear();
      lcd.print("Recorded Time:");
      lcd.setCursor(0, 1);

      lcd.print(minutes);
      lcd.print(":");

      if (seconds < 10)
      {
        lcd.print("0");
      }
      lcd.print(seconds);
      lcd.print(":");

      if (actualTime < 100)
      {
        lcd.print("0");
      }
      if (actualTime < 10)
      {
        lcd.print("0");
      }
      lcd.print(actualTime);

      // Print to BTSerial
      BTSerial.print("TIME ");
      BTSerial.print(minutes);
      BTSerial.print(":");
      if (seconds < 10)
        BTSerial.print("0");
      BTSerial.print(seconds);
      BTSerial.print(":");
      if (actualTime < 100)
        BTSerial.print("0");
      if (actualTime < 10)
        BTSerial.print("0");
      BTSerial.println(actualTime);
    }
  }
}

// EOF
