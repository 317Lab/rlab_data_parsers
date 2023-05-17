import sys
import os
from serial import Serial
from datetime import datetime
from bitstring import BitArray
import numpy as np
import io

# user settings
baud = 230400
initial_timeout = 30
runtime_timeout = 10
num_bytes_target = 2048 # feed bytes faster than parser reads
io.DEFAULT_BUFFER_SIZE = 16_777_216 # 16 MB

# opening data port/file
suffix = ''
payload_id = 0
bytes_tmp = BitArray()
monitoring_only = False
first_capture = True
if len(sys.argv) == 3: # optional argument
    if sys.argv[2] == '-m':
        monitoring_only = True
    else:
        suffix = '_' + sys.argv[2]
try:
    port = sys.argv[1]
    ser = Serial(port, baud, timeout=initial_timeout) # wait until all bytes are read or x seconds pass
    ser.reset_input_buffer() # flush serial port
except:
    print('Serial port not found.')
    exit()

file_name = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + '_data_' + port.split('.')[-1] + '_' + str(baud) + suffix + '.bin'
if not(monitoring_only):
    file = open(file_name,'ab')

while True:
    try:
        bytes = ser.read(num_bytes_target)
        if first_capture:
            ser.timeout = runtime_timeout
            first_capture = False
        if not(monitoring_only):
            file.write(bytes)
        if bytes != b'':
            try:
                sys.stdout.buffer.write(bytes)
                bytes_tmp = BitArray(bytes)
            except (BrokenPipeError, OSError):
                pass # if pipe breaks keep writing to file until user interupt
        else:
            try:
                for _ in range(10*num_bytes_target):
                    sys.stdout.buffer.write(b'TIMEOUT\n') # pass-through timeout message
            except (BrokenPipeError, OSError):
                break
            break
    except KeyboardInterrupt:
        break

# close and rename file with payload ID
if not(monitoring_only):
    file.close()
    ids = list(bytes_tmp.findall('0x2353'))
    if len(ids)!=0:
        payload_ids = np.zeros(len(ids),dtype='uint8')
        i=0
        for id in ids:
            payload_ids[i] = bytes_tmp[id+(2+4)*8:id+(2+5)*8].uintle
            i+=1
        payload_id = int(np.median(payload_ids))
    os.rename(file_name,file_name[:-4]+'_'+str(payload_id)+'.bin') # add payload ID to file_name