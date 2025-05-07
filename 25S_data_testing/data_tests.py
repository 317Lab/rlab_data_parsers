from bitstring import BitArray
import numpy as np
import matplotlib.pyplot as plt
import parse_binary as pb
import utilities as util
# gyr - above .1 std
# mag - above .05 std
# acc - above .01 std
freq = 45 # approximate message frequency in Hz
#binary_file = "test_files/test_results_20250507T104141Z/shield_test.bin"
#binary_file = "test_files/test_results_20250507T103714Z/shield_test.bin"
#binary_file = "test_files/test_results_20250507T105716Z/shield_test.bin"
binary_file = "binary_files/20250402T190425Z_data_COM13_230400_60.bin"
#binary_file = "test_files/shield_test_20250506T143827Z.bin"


swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(binary_file)
steps_0, steps_1 = util.get_sweep_steps(volts=volts)
print(util.get_step_std(steps=steps_0))
print(util.get_step_std(steps=steps_1))
# stds = util.get_step_std(steps=steps)
# stds_mv = stds * 1000
# np.savetxt("noise.csv", stds_mv, delimiter=",")
# print(np.std(acc[0,0,:]), np.std(acc[0,1,:]), np.std(acc[0,2,:]))
# print(np.std(mag[0,0,:]), np.std(mag[0,1,:]), np.std(mag[0,2,:]))
# print(np.std(gyr[0,0,:]), np.std(gyr[0,1,:]), np.std(gyr[0,2,:]))
# acc_std = np.array([np.std(acc[0,0,:]), np.std(acc[0,1,:]), np.std(acc[0,2,:])])
# print(np.any(acc_std < 0.01))
# print(swp_time[0,0], swp_time[0,nonzer[-1]])
# print(imu_time[0,0], imu_time[0,-1])
#util.check_buffers(swp_time, volts, imu_time, acc, mag, gyr)
# steps = util.get_sweep_steps(volts=volts)
# print(steps.shape)
# volts_list = []
# numtests = 5
# for i in range(1,numtests+1):
# 	binary_file = f"binary_files/DC_test_{i}.bin"
# 	_, _, volts, _, _, _, _ = pb.parse_all(binary_file)
# 	volts_list.append(volts)


# test1 = util.DCTest(
# 	test_id = 1,
# 	voltages = volts_list[0][0,1,:],
# 	resistor_reading = 2.1,
# 	supply_voltage = 1.4
# )
# test2 = util.DCTest(
# 	test_id = 2,
# 	voltages = volts_list[1][0,1,:],
# 	resistor_reading = 1.35,
# 	supply_voltage = 2.5
# )

# test3 = util.DCTest(
# 	test_id = 3,
# 	voltages = volts_list[2][0,1,:],
# 	resistor_reading = 0.68,
# 	supply_voltage = 3.5
# )

# test4 = util.DCTest(
# 	test_id = 4,
# 	voltages = volts_list[3][0,1,:],
# 	resistor_reading = 0.32,
# 	supply_voltage = 4.0
# )
# test5 = util.DCTest(
# 	test_id = 5,
# 	voltages = volts_list[4][0,1,:],
# 	resistor_reading = 1.33,
# 	supply_voltage = 2.5
# )

# test2 had very strange behavior, test5 is a rerun with the same parameters
# tests = [test1, test5, test3, test4]
# util.show_dc_noise(tests=tests)

# util.show_step_noise(volts=volts)