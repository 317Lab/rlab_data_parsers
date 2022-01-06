import time
import serial
import numpy as np

# port = 'COM4'
# ser = serial.Serial(port, 230400, timeout=None)
# timeout_s = 10
# start_time = time.time()
# # with open('output.bin', 'ab') as f:
# while (time.time()-start_time) < timeout_s:
#     a = ser.read_all()
#     print(a)

# port = 'COM1'
# # baud = 230400
# baud = 600
# ser = serial.Serial(port, baud)
# ser.close()
# ser.open()
# print(ser)
# # while True:
# t0 = time.time()
# a = ser.read(2*120)
# print(time.time()-t0)
# print(a)
# ser.close()

# portOut = 'COM1'
# portIn = 'COM2'
# serOut = serial.Serial(portOut, 230400, timeout=None)
# serIn = serial.Serial(portIn, 230400, timeout=None)
# for i in range(100):
#     serOut.write(b'a')

# a = serIn.read_all()
# print(a)

# t0 = time.time()
# time.sleep(0.001)
# t1 = time.time()
# print(t1-t0)

# a = [None]*10
# for i in range(8):
#     a[i] = 0
# print(a)
# b = list(filter(None,a))
# # b = [i for i in a if i!=None]
# print(b)
# c = np.array(b,dtype='uint16')
# print(c)

# for i in range(-256,256):
#     print(np.array(i,dtype='int8'),end='   ')
a=[0,1,2,3,4,5,6,7,8,9]
print(a[0::2])