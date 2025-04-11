from bitstring import BitArray
import numpy as np
import matplotlib.pyplot as plt
import parse_binary as pb
import utilities as util

freq = 45 # approximate message frequency in Hz
binary_file = "binary_files/3_volts_raw.bin"

# swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(binary_file)

    
# start_time = 40
# end_time = 40 + (5/freq)
#util.check_buffers(start_time=start_time,end_time=end_time,swp_time=swp_time,volts=volts,imu_time=imu_time,acc=acc,mag=mag,gyr=gyr)

# steps = util.get_sweep_steps(volts=volts)
# print(steps.shape)
volts_list = []
for i in range(1,6):
	binary_file = f"binary_files/DC_test_{i}.bin"
	_, _, volts, _, _, _, _ = pb.parse_all(binary_file)
	volts_list.append(volts)


test1 = util.DCTest(
	test_id = 1,
	voltages = volts_list[0][0,1,:],
	resistor_reading = 2.1,
	supply_voltage = 1.4
)
test2 = util.DCTest(
	test_id = 2,
	voltages = volts_list[1][0,1,:],
	resistor_reading = 1.35,
	supply_voltage = 2.5
)

test3 = util.DCTest(
	test_id = 3,
	voltages = volts_list[2][0,1,:],
	resistor_reading = 0.68,
	supply_voltage = 3.5
)

test4 = util.DCTest(
	test_id = 4,
	voltages = volts_list[3][0,1,:],
	resistor_reading = 0.32,
	supply_voltage = 4.0
)
test5 = util.DCTest(
	test_id = 5,
	voltages = volts_list[4][0,1,:],
	resistor_reading = 1.33,
	supply_voltage = 2.5
)

# test2 had very strange behavior, test5 is a rerun with the same parameters
tests = [test1, test5, test3, test4]
util.show_dc_noise(tests=tests)