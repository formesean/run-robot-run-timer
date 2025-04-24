#include <Arduino.h>
#include <Wire.h>
#include <SoftwareSerial.h>
#include <VL53L0X.h>

// VL53L0X
#define GET_DISTANCE distanceSensor.readRangeContinuousMillimeters()

VL53L0X distanceSensor;
const int sensorTimeout = 500;

// Bluetooth UART
#define BT_RX_PIN 3
#define BT_TX_PIN 2
#define BT_EN_PIN 5

SoftwareSerial BTSerial(BT_RX_PIN, BT_TX_PIN);

// Button
#define BUTTON_PIN 4

String inputString;
const int sensorThreshold = 300;

void setup()
{
  Serial.begin(9600);
  // pinMode(BT_EN_PIN, OUTPUT);

  // BT UART Setup
  // digitalWrite(BT_EN_PIN, HIGH);
  // BTSerial.begin(38400);
  // delay(1000);
  // BTSerial.println("AT+NAME=StartUnit");
  // delay(500);
  // digitalWrite(BT_EN_PIN, LOW);
  // delay(500);
  BTSerial.begin(9600);

  // VL53L0X Setup
  distanceSensor.setTimeout(sensorTimeout);

  while (!distanceSensor.init())
    BTSerial.println("NO SENSOR");

  distanceSensor.startContinuous();

  // Button Setup
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  BTSerial.println("WAITING");
}

void loop()
{
  bool button = digitalRead(BUTTON_PIN);

  if (BTSerial.available() || (button == LOW))
  {
    inputString = BTSerial.readStringUntil('\n');

    if (inputString == "STOP")
      return;

    if (inputString == "GO" || (button == LOW))
    {

      BTSerial.println("WAITING");

      while (GET_DISTANCE > sensorThreshold)
      {
      }

      BTSerial.println("START");
      Serial.println("[DEBUG] Sent START");
      // return;
    }
  }
}

// EOF
