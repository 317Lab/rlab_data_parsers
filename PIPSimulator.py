import serial
import time

# port = 'COM1'
# # baud = 230400
# baud = 1200
# ser = serial.Serial(port, baud, timeout=None)
# f = open('PIPSimulatorData.bin','rb') # 250850 bytes
# secondsPerByte = 1/(145*45)
# numBytes = len(f.read())
# secondsPerPass = round(secondsPerByte*numBytes,1)
# tuningFork = 2700
# while True:
#     byte = True
#     f.seek(0)
#     t0 = time.time()
#     while byte:
#         byte=f.read(1)
#         ser.write(byte)
#         for _ in range(tuningFork):
#             pass
#     t1 = time.time()
#     actualSecondsPerPass = round(t1-t0,1)
#     if actualSecondsPerPass < secondsPerPass:
#         tuningFork += 100
#     elif actualSecondsPerPass > secondsPerPass:
#         tuningFork -= 100
#     print('With tuningFork='+str(tuningFork)+' cadance accuracy is '+str(round(100*(actualSecondsPerPass-secondsPerPass)/secondsPerPass,2))+'%', flush=True)

port = 'COM2'
baud = 230400
# baud = 600
ser = serial.Serial(port,baud)
f = open('./data/20220111T151144_data_COM7_230400_vibe-Z-sine01_26.bin','rb') # 10*45*145 = 65,250 bytes
bytes = f.read()
for i in range(round(len(bytes)/(45*145/5))):
    ser.write(bytes[i*9*145:(i+1)*9*145])
    time.sleep(0.1)
ser.close()