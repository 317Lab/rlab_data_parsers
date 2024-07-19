from struct import *
import os
import matplotlib.pyplot as plt
import numpy as np

sweep_sentinel = [35,35,83]
sweep_buffer_sentinel = [35,35,84]
imu_sentinel = [35,35,73]
imu_buffer_sentinel = [35,35,74]

def find_sweep_indices(data):
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j]==35 and data[i][j+1]==35 and data[i][j+2]==83:
                print(j)

output_file = r"C:\Users\skwal\Documents\rlab_data_parsers\20240719T164628Z_data_COM21_230400_1.bin"
# B = byte, I = unsigned int, h = short, H = unsigned short
format = "<4BI56H3BI10h3BI10h4BI56H"

size = calcsize(format)
cycles = []
file_size = os.path.getsize(output_file)
strip_buffer = file_size % size

sequence = b'\x23\x23\x53'


with open(output_file, 'rb') as f:
    # search for first imu sentinel and start reading file there
    chunk_size = 1024
    buffer = b''
    while True:
        chunk = f.read(chunk_size)
        if not chunk: break
        buffer += chunk
        start = buffer.find(sequence)
        if start != -1:
            f.seek(f.tell() - (len(buffer) - start))
            break
    data = f.read()
    # strip extra data at end of file
    strip_buffer = len(data) % size
    stripped_data = data[:-strip_buffer]
    # unpack data into bytes
    m = iter_unpack(format, stripped_data)
    for i in m:
        cycles.append(i)

print(cycles[0])
print(cycles[1])
timestamps = []
for i in cycles:
    if not i[61] == 35 and i[62] == 35 and i[63] == 73:
        print("FAILED")
for i in range(0,len(cycles)-1):
    timestamps.append(cycles[i+1][4]-cycles[i][4])

greater = []
less = []
for i in timestamps:
    if i > 22200:
        greater.append(i)
    else:
        less.append(i)
#print(timestamps)
#print("greater: ", len(greater))
#print("less: ", len(less))
#plt.scatter(x_ind, sweep_timestamps)
#plt.show()
"""
flat_timestamps = []
flat_data = []
for i in range(len(sweep_timestamps)):
    for j in range(28):
        flat_timestamps.append(sweep_timestamps[i])
        flat_data.append(sweep_data[i][j])

x_index = list(range(len(sweep_data[0])))
plt.scatter(x_index, sweep_data[0])
plt.show() """
# add timestamp to format
# debugger send one known sweep and check it out. put first break point at when buffer timestamp boolean gets changed to make sure full sweep.






















    
