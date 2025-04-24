# Run Robot Run Timer System

A dual-unit timing system for measuring and displaying completion times for run robot run robots or similar track-based projects. The system consists of a start unit and a finish unit, each with its own Bluetooth connectivity, working together to provide precise timing measurements.

## Hardware Requirements

### For Each Unit (Start and Finish)
- Arduino Uno
- VL53L0X Time-of-Flight Distance Sensor
- HC-05 Bluetooth Module
- Push Button (for Start Unit)
- LCD Display (I2C interface, 16x2) (for Finish Unit)
- Appropriate power supply

## Initial Bluetooth Setup

1. **Pair HC-05 Modules:**

   - Go to Windows Settings → "Bluetooth & other devices"
   - Click "Add Bluetooth or other device"
   - Select "Bluetooth"
   - Look for "StartUnit" and "FinishUnit" in the device list
   - When prompted, enter the default password: `1234`
   - **Note:** It's normal for the HC-05 to show as "Paired" but not "Connected" in Bluetooth settings

2. **Find the Correct COM Ports:**
   - Go to Windows Settings → "Bluetooth & other devices"
   - Click "More Bluetooth settings"
   - Select the "COM Ports" tab
   - Look for both "StartUnit" and "FinishUnit" in the list
   - Note the COM port numbers that have "Outgoing" direction
   - These are the port numbers you'll need for the next step

## Software Installation

1. Clone or download this repository

2. Navigate to the `www` folder:

   ```bash
   cd www
   ```

3. Install dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the COM ports:
   - Open `relay.py` from the `www` folder
   - Locate the COM port configuration:
     ```python
     START_UNIT_PORT = 'COM21'  # Change this to your Start Unit's Outgoing COM port
     FINISH_UNIT_PORT = 'COM24'  # Change this to your Finish Unit's Outgoing COM port
     ```
   - Update them to match the Outgoing COM port numbers you found in the Bluetooth settings

## Running the Web Server

1. Make sure you're in the `www` folder

2. Start the Flask server:

   ```bash
   python flask_timer.py
   ```

3. Access the web interface at: `http://localhost:5000`

## Using the System

### Main Features

- Real-time timer display (MM:SS:mmm format)
- Status indicator showing current system state
- "Ready" button to start new timing sessions
- Automatic start/stop detection using ToF sensors
- Dual-unit coordination via Bluetooth

### How to Use

1. Open `http://localhost:5000` in your web browser
2. Click the "Ready" button to prepare the system
3. The timer will:
   - Start automatically when the line follower crosses the start line
   - Update in real-time during the run
   - Display the final time when the finish line is crossed

### Display Information

- **Status Messages:**
  - "Waiting for signal..." - Initial state
  - "Timer running..." - During active run
  - "Final recorded time:" - After run completion
- **Timer Format:** MM:SS:mmm (minutes:seconds:milliseconds)

## Hardware Setup

### Start Unit Connections
- VL53L0X sensor: Connect to I2C pins (SDA/SCL)
- Push Button: Connect to pin 4
- HC-05 Bluetooth Module:
  - RX: Connect to pin 3
  - TX: Connect to pin 2
  - EN: Connect to pin 5

### Finish Unit Connections
- VL53L0X sensor: Connect to I2C pins (SDA/SCL)
- LCD Display: Connect to I2C pins (SDA/SCL)
- HC-05 Bluetooth Module:
  - RX: Connect to pin 3
  - TX: Connect to pin 2
  - EN: Connect to pin 5

### Sensor Placement

- Position the VL53L0X sensors at the start and finish lines of your track
- Ensure the sensors have a clear line of sight to detect passing objects
- Recommended height: 100-200mm above the track surface

## Troubleshooting

### Bluetooth Connection Issues

- Verify both HC-05 modules are properly paired in Windows Bluetooth settings
- Double-check you're using the correct Outgoing COM ports
- Try removing and re-pairing the HC-05 devices
- Restart the Arduinos if the connections seem unstable

### COM Port Issues

- Verify no other applications are using the COM ports
- Check if the COM port numbers in `relay.py` match the Outgoing ports in Bluetooth settings
- Try unplugging and reconnecting the Arduinos

### Web Interface Issues

- Verify the Flask server is running
- Check if port 5000 is available
- Try refreshing the browser

### Hardware Issues

- Check all wire connections
- Verify the Arduinos are properly powered
- Ensure the HC-05 modules are receiving power
- Check if the VL53L0X sensors are properly connected and responding
- Verify the LCD display is properly connected to I2C

## System Features

- Dual-unit timing system with start and finish detection
- Real-time timing display on both LCD and web interface
- Bluetooth communication between units and computer
- Manual override using physical button on start unit
- Millisecond precision timing
- Clean, responsive web interface design

## Notes

- The system uses a threshold of 300mm for object detection
- The web interface updates every 300ms
- The LCD displays time in MM:SS:mmm format
- Both units communicate via Bluetooth through a central relay server
- The system is designed for easy setup and maintenance
