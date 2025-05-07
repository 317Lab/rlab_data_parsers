import serial
import subprocess
import platform
import time

def detect_port():
    baud = 230400
    operating_system = platform.system()

    if operating_system == "Linux":
        try:
            ports = subprocess.check_output('ls /dev/ttyUSB*', shell=True, text=True).strip().splitlines()
        except subprocess.CalledProcessError:
            print("Port not detected. Please check the connection.")
            exit(1)
        for port in ports:
            ser = serial.Serial(port, baudrate=baud, timeout=1)
            time.sleep(0.5)
            if ser.in_waiting>0:
                # print(f"Connected on port {port}")
                ser.reset_input_buffer() 
                return port
                # break
            print("Could not detect data.")
            exit(1)
    elif operating_system == "Darwin":
        try:
            ports = subprocess.check_output('ls /dev/tty.usbserial*', shell=True, text=True).strip().splitlines()
        except subprocess.CalledProcessError:
            print("Port not detected. Please check the connection.")
            exit(1)
        for port in ports:
            ser = serial.Serial(port, baudrate=baud, timeout=1)
            time.sleep(0.5)
            if ser.in_waiting>0:
                # print(f"Connected on port {port}")
                ser.reset_input_buffer() 
                return port
                break
            print("Could not detect data.")
            exit(1)

