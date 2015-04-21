import serial
import time
import threading

data = {}

def update_watcher():
    global data
    ser = serial.Serial('/dev/ttyACM0', 9600)
    seen_hello_msg = False
    while True:
        msg = ser.readline().rstrip()
        line = msg.split('--')
        if seen_hello_msg is False and 'Connection established' in line:
            seen_hello_msg = True
        elif seen_hello_msg:
            sensor, reading = line
            data[sensor] = reading
        time.sleep(1)

def run():
    updates = threading.Thread(target=update_watcher)
    updates.daemon = True
    updates.start()

def last_reading():
    global data
    return data

