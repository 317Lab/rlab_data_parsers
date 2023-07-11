# Reader/writer of shield asynchronous data.
# Data read from communication port and writen to data file named:
#   "YYYYMMDDThhmmssZ_data_<port>_<baud>_<suffix>_<id>.bin"
# Data also sent to standard output to be piped into shield_realtime.py.
# Example usages:
#   Normal usage:  python shield_feed.py <port> <suffix (optional)> | python shield_realtime.py
#   Monitor only:  python shield_feed.py <port> -m | python shield_realtime.py
# For Windows, <port> is "COM##". Check "Device Manager" under "Ports" and look for e.g. "(COM2)".
# For iOS, <port> is under /dev/, e.g. "/dev/tty.usbserial-FT611XTT0%".
# Known issues:
#   - sometimes payload id fails and returns 0 in filename
#   - for iOS, broken pipe error is sent to standard error and writen to log, even though it's handled
#       - poor form... be sure to check shield_feed_stderr.log if their are any problems
# Contact: jules.van.irsel.gr@dartmouth.edu

import sys
import os
from serial import Serial
from datetime import datetime
from bitstring import BitArray
import numpy as np
import io

# user settings
baud = 230400 # baud rate
initial_timeout = 20 # seconds before initial serial timeout, allows user to start recording and wait for shield power on
runtime_timeout = 5 # seconds before timeout after initial capture
num_bytes_target = 2048 # number of feed bytes, should be much less than parser reads
io.DEFAULT_BUFFER_SIZE = 16_777_216 # 16 MB, might be overkill TBD

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
    ser = Serial(port, baud, timeout=initial_timeout)
    ser.reset_input_buffer() # flush serial port
except:
    print('Serial port not found.')
    exit()

file_name = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + '_data_' + port.split('.')[-1] + '_' + str(baud) + suffix + '.bin'
if not monitoring_only:
    file = open(file_name,'ab')

# log errors
log = open('shield_feed_stderr.log', 'a')
log.write('\n'+file_name[:-4]+'\n')
sys.stderr = log

# main routine
while True:
    try:
        bytes = ser.read(num_bytes_target)
        if first_capture:
            ser.timeout = runtime_timeout # update timeout
            first_capture = False
        if not monitoring_only:
            file.write(bytes)
        if bytes != b'':
            try:
                sys.stdout.buffer.write(bytes)
                bytes_tmp = BitArray(bytes) # for grabbing shield ID post loop
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