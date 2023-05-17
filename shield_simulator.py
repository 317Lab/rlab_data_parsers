import serial
import sys

port = 'COM1'
baud = 230400
size = 2048
ser = serial.Serial(port, baud)

try:
    while True:
        feed = sys.stdin.buffer.read(-1)
        ser.write(feed)
except KeyboardInterrupt:
    ser.close()
    pass