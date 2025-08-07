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
#binary_file = "test_files/test_results_20250507T135319Z/shield_test.bin"
#binary_file = "test_files/shield_test_20250506T143827Z.bin"
#binary_file = "binary_files/20250402T191624Z_data_COM13_230400_60.bin"

binary_file = "/Users/rocket/Documents/rlab_data_parsers/20250616T143602Z_data_usbserial-FT611XTT0_230400_69.bin"
import shield_test_plot as stp
swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(binary_file)
stp.show_plots(swp_time=swp_time, volts=volts, imu_time=imu_time, acc=acc, mag=mag, gyr=gyr)
### buf_slice not being found, good_idx and nonbuf_slice fine
# def good_slices(time, is_sweep=True):
#     if is_sweep:
#         num_steps = 28
#     else:
#         num_steps = 1
#     for i in range(10,1,-1):
#         time_buf = time[1, :]
#         time_step = np.median(np.diff(time[0,:]))

#         mask = (np.abs(np.diff(time[0,:])) <= 2*time_step) & (np.abs(np.diff(time[1,:])) <= 2*time_step)
#         good_idx = np.where(mask)[0]
#         print(good_idx.shape)
#         nonbuf_slice = util.find_consecutive_block(good_idx, i*num_steps)
#         print(nonbuf_slice.shape)
#         start_time = time[0, nonbuf_slice[0]]
#         end_time = time[0, nonbuf_slice[-1]]
#         print("start time: ", start_time)
#         print("time_buf: ", np.max(time_buf))
#         buf_slice = np.intersect1d(np.where(start_time <= time_buf)[0], np.where(time_buf <= end_time)[0])
#         print(buf_slice.shape)
#         if len(buf_slice)==len(nonbuf_slice):
#             return nonbuf_slice, buf_slice, start_time, end_time
#         else:
#             min_len = min(len(nonbuf_slice), len(buf_slice))
#             nonbuf_slice = nonbuf_slice[:min_len]
#             buf_slice = buf_slice[:min_len]
#     return None, None, None, None

# binary_file = "25S_data_testing/test_files/test_results_20250605T121819Z/shield_test.bin"
# swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(binary_file)
# print("min time 1: ", np.min(swp_time[0,:]), "max time: ", np.max(swp_time[0,:]))
# print("min time 2: ", np.min(swp_time[1,:]), "max time: ", np.max(swp_time[1,:]))

# exit()
# fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)


# buf_slice, nonbuf_slice, start_time, end_time = good_slices(swp_time)
# print(buf_slice.shape, nonbuf_slice.shape, start_time.shape, end_time.shape)
# time_slice = swp_time[0,nonbuf_slice]
# axs[0].plot(time_slice, volts[0, 0, nonbuf_slice], label="not buffered")
# axs[0].plot(time_slice, volts[1, 0, buf_slice], label="buffered")
# #axs[0].legend()
# axs[0].set_title(f"Sweep Data, Pip 0")
# axs[0].set_ylabel("Volts (V)")

# # pip 1 plot 
# axs[1].plot(time_slice, volts[0, 1, nonbuf_slice], label="not buffered")
# axs[1].plot(time_slice, volts[1, 1, buf_slice], label="buffered")
# axs[1].legend()
# axs[1].set_title(f"Sweep Data, Pip 1")
# axs[1].set_ylabel("Volts (V)")
# nonbuf_slice = np.where((imu_time[0,:]>=start_time)&(imu_time[0,:]<=end_time))[0]
# buf_slice = np.where((imu_time[1,:]>=start_time)&(imu_time[1,:]<=end_time))[0]
# if len(nonbuf_slice)!=len(buf_slice):
#     min_len = min(len(nonbuf_slice), len(buf_slice))
#     nonbuf_slice = nonbuf_slice[:min_len]
#     buf_slice = buf_slice[:min_len]
# time_slice=imu_time[0,nonbuf_slice]
# time_slice=imu_time[0,buf_slice]
# # Accelerometer plot
# for axis in range(3):
#     axs[4].plot(time_slice, acc[0, axis, nonbuf_slice], label=f"{['x','y','z'][axis]}, non-buf")
#     axs[4].plot(time_slice, acc[1, axis, buf_slice], label=f"{['x','y','z'][axis]}, buf")
# #axs[4].legend()
# axs[4].set_title("Acceleration")
# axs[4].set_ylabel("g")
# axs[4].set_xlabel("Time (s)")

# # Magnetometer plot
# for axis in range(3):
#     axs[2].plot(time_slice, mag[0, axis, nonbuf_slice], label=f"{['x','y','z'][axis]}, non-buf")
#     axs[2].plot(time_slice, mag[1, axis, buf_slice], label=f"{['x','y','z'][axis]}, buf")
# axs[2].legend()
# axs[2].set_title("Magnetic Field")
# axs[2].set_ylabel("MAG (G)")

# # Gyroscope plot
# for axis in range(3):
#     axs[3].plot(time_slice, gyr[0, axis, nonbuf_slice], label=f"{['x','y','z'][axis]}, non-buf")
#     axs[3].plot(time_slice, gyr[1, axis, buf_slice], label=f"{['x','y','z'][axis]}, buf")
# axs[3].legend()
# axs[3].set_title("Gyroscope")
# axs[3].set_ylabel("GYR (Hz)")

# plt.tight_layout()
# # if save:
# #     plt.savefig(save_path)
# # else:
# plt.show()


# nominal_volts = np.linspace(5, 0, 28)
# steps_0, steps_1 = util.get_sweep_steps(volts=volts)
# steps_0_med = np.zeros(28)
# steps_1_med = np.zeros(28)
# print(steps_1[:,3])
# for i in range(28):
#     steps_0_med[i] = np.median(steps_0[:,i])
#     steps_1_med[i] = np.median(steps_1[:,i])
# offset_0 = nominal_volts - steps_0_med
# offset_1 = nominal_volts - steps_1_med
# print(offset_1*1e3)


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