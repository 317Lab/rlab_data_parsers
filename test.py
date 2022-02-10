import time
import serial
import numpy as np
import _thread

# port = 'COM4'
# ser = serial.Serial(port, 230400, timeout=None)
# timeout_s = 10
# start_time = time.time()
# # with open('output.bin', 'ab') as f:
# while (time.time()-start_time) < timeout_s:
#     a = ser.read_all()
#     print(a)

port = 'COM4'
baud = 230400
# baud = 600
ser = serial.Serial(port, baud)
while True:
    a = ser.read(145*9)
    print(a)

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
# a=[0,1,2,3,4,5,6,7,8,9]
# print(a[0::2])

# import threading as th

# ser = serial.Serial('COM4', 230400, timeout=30)
# f = open('test.bin','ab')
# rawBytes = ser.read()
# plotting = True

# def read_thread():
#     global rawBytes
#     while True:
#         rawBytes = ser.read(1*45*145)
#         f.write(rawBytes)

# def key_capture_thread():
#     global plotting
#     input()
#     plotting = False

# def do_stuff():
#     th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
#     th.Thread(target=read_thread, args=(), name='read_thread', daemon=True).start()
#     while plotting:
#         print(rawBytes)
#         time.sleep(2)

# do_stuff()

# from bitstring import BitArray, BitStream

# c = BitArray(filename='d:\\Files\\Research\\LAMP\\rlab_data_parsers\\_output.bin')

# ind = list(c.findall('0x2353', bytealigned=False))

# for start_ind, end_ind in zip(ind[:-1], ind[1:]):
#     print(c[start_ind:start_ind+100], (end_ind-start_ind)/8)