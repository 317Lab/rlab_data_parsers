from bitstring import BitArray
import numpy as np
import matplotlib.pyplot as plt
import parse_binary as pb
import utilities as util

freq = 45 # approximate message frequency in Hz
binary_file = "binary_files/20250402T191624Z_data_COM13_230400_60.bin"

swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(binary_file)

    
# start_time = 40
# end_time = 40 + (5/freq)
#util.check_buffers(start_time=start_time,end_time=end_time,swp_time=swp_time,volts=volts,imu_time=imu_time,acc=acc,mag=mag,gyr=gyr)

steps = util.get_sweep_steps(volts=volts)
print(steps.shape)