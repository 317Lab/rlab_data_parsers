import sys
import os
from serial import Serial
from datetime import datetime
from bitstring import BitArray
import numpy as np
import io

io.DEFAULT_BUFFER_SIZE = 1_048_576 # 1 MB

# user settings
baud = 230400
timeout = 5
num_bytes_target = 1024 # feed bytes faster than parser reads

# opening data port/file
suffix = ''
bytes_tmp = BitArray()
payload_id = 0
reading = True
monitoring_only = False
if len(sys.argv) == 3: # optional argument
    if sys.argv[2] == '-m':
        monitoring_only = True
    else:
        suffix = '_' + sys.argv[2]
try:
    port = sys.argv[1]
    ser = Serial(port, baud, timeout=timeout) # wait until all bytes are read or x seconds pass
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
                    sys.stdout.buffer.write(b'TIMEOUT\n')
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
