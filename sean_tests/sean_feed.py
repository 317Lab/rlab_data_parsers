import serial
import sys
import signal
import time

def signal_handler(sig, frame):
    print('Exiting...')
    ser.close()
    out_file.close()
    sys.exit(0)

if len(sys.argv) != 2:
    print("Usage: python script.py <COM_PORT>")
    sys.exit(1)

com_port = sys.argv[1]

timestamp = time.strftime("%Y%m%d_%H%M%S")
output_file = f"output_{timestamp}.bin"

try:
    ser = serial.Serial(com_port, 9600, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port {com_port}: {e}")
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

print(f"Reading from {com_port} and writing to {output_file}. Press Ctrl+C to exit.")

out_file = open(output_file, 'wb')

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            out_file.write(data)
except Exception as e:
    print(f"Error: {e}")
finally:
    ser.close()
    out_file.close()
