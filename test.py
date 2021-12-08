import serial

ser = serial.Serial('/dev/cu.usbserial-FT611XTTA', 230400, timeout=None)
f = open('test.txt','wb')
for i in range(1000):
    rawByte = ser.read()
    print(rawByte)
    f.write(rawByte)
f.close()

