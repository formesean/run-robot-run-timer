import serial
import threading
import time
from queue import Queue

START_UNIT_PORT = 'COM21'
FINISH_UNIT_PORT = 'COM24'
BAUD_RATE = 9600

data_queue = Queue()  # Shared queue

start_unit = None
finish_unit = None

def relay(source_serial, destination_serial, label):
    while True:
        if source_serial.in_waiting:
            data = source_serial.readline().decode().strip()
            print(f"[{label}] {data}")

            if 'START' in data:
                timestamp = int(time.time() * 1000)
                data_queue.put({'event': 'START', 'timestamp': timestamp})
            elif 'STOP' in data:
                timestamp = int(time.time() * 1000)
                data_queue.put({'event': 'STOP', 'timestamp': timestamp})
            elif 'TIME' in data:
                try:
                    time_value = data[5:].strip()
                    data_queue.put({'event': 'TIME', 'value': time_value})
                except (IndexError, ValueError):
                    pass
            elif 'WAITING' in data:
                data_queue.put({'event': 'WAITING'})

            destination_serial.write((data + '\n').encode())

def start_relay():
    global start_unit, finish_unit

    try:
        start_unit = serial.Serial(START_UNIT_PORT, BAUD_RATE, timeout=1)
        finish_unit = serial.Serial(FINISH_UNIT_PORT, BAUD_RATE, timeout=1)

        print("[INFO] Connected to both Bluetooth devices.")

        threading.Thread(target=relay, args=(start_unit, finish_unit, 'Start -> Finish'), daemon=True).start()
        threading.Thread(target=relay, args=(finish_unit, start_unit, 'Finish -> Start'), daemon=True).start()

    except serial.SerialException as e:
        print(f"[ERROR] {e}")
