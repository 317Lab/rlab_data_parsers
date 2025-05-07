"""
Stripped down version of Jules' shield_feed.py for shield testing.
Author: Sean Wallace
Date: April 2025
"""
import sys
import os
from serial import Serial
from datetime import datetime
from bitstring import BitArray
import numpy as np
import io
import platform
import time

# main routine
def read(port, file_name, read_time=None):
    baud = 230400 # baud rate
    initial_timeout = 120 # seconds before initial serial timeout, allows user to start recording and wait for shield power on
    runtime_timeout = 10 # seconds before timeout after initial capture
    num_bytes_target = 2048 # number of feed bytes, should be much less than parser reads
    io.DEFAULT_BUFFER_SIZE = 16_777_216 # 16 MB, might be overkill TBD

    # check OS
    operating_system = platform.system()

    # opening data port/file
    suffix = ''
    payload_id = 0
    bytes_tmp = BitArray()
    monitoring_only = False
    first_capture = True

    starttime = time.time()
    ser = Serial(port, baudrate=baud, timeout=initial_timeout)
    # directory = 'test_files/'
    # if operating_system == 'Darwin' or operating_system == 'Windows':
    #     file_name = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + '_data_' + port.split('.')[-1] + '_' + str(baud) + suffix + '.bin'
    # elif operating_system == 'Linux':
    #     port_basename = os.path.basename(port)  # safely gets port
    #     file_name = directory + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + '_data_' + port_basename + '_' + str(baud) + suffix + '.bin'
    if not monitoring_only:
        file = open(file_name,'ab')

    if read_time is None:
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
    else:
        while time.time()-starttime<read_time:
            try:
                bytes = ser.read(num_bytes_target)
                if first_capture:
                    ser.timeout = runtime_timeout # update timeout
                    first_capture = False
                if not monitoring_only:
                    file.write(bytes)
                if bytes != b'':
                    try:
                        #sys.stdout.buffer.write(bytes)
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
            #os.rename(file_name,file_name[:-4]+'_'+str(payload_id)+'.bin') # add payload ID to file_name

