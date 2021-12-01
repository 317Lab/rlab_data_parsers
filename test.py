import serial
import time
# import sys
# from serial.serialutil import to_bytes


# 2 PIPs with 28 2-byte samples + 4-byte timestamp + ID
sweepSamples = 28
numSweepBytes = sweepSamples * 2 * 2 + 4 + 1

# 9 2-byte data points + 2-byte temp + 4-byte timestamp
numIMUBytes = 24

ser = serial.Serial('COM4', 230400, timeout=None)
f = open('test.txt','wb')
rawdata = b''
while True:
    rawByte = ser.read()
    if rawByte == b'#':
        nextRawByte = ser.read()
        if nextRawByte == b'S':
            rawSweepBytes = ser.read(numSweepBytes)
            print(rawSweepBytes)
            f.write(rawSweepBytes)
            f.close()
            exit()


for i in range(500):
    data =ser.read()
    if data == b'#':
        f.write(data)
        print(data)
f.close()
# x = b'\xff\x00'
# y = b'\xd9\x00'
# X = int.from_bytes(x,byteorder=sys.byteorder)
# Y = int.from_bytes(y,byteorder=sys.byteorder)
# Z = (X << 8) | Y
# z = Z.to_bytes(2,byteorder=sys.byteorder)

# print(x,X)
# print(y,Y)
# print(z,Z)