from bitstring import BitArray
import numpy as np
import matplotlib.pyplot as plt
import parse_binary as pb
import utilities as util
import shield_test_plot as sp
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

# binary_file = "/home/sean-wallace/Documents/rlab_data_parsers/25S_data_testing/36397_PIP_Handshake.bin"
binary_file = "/home/sean-wallace/Documents/rlab_data_parsers/handshake_test/R1_PIP1_19_Sep_2025_15_37_47.bin"
with open(binary_file, 'rb') as f:
    bytes = BitArray(f.read())
offset = 0x00000070+0x0b
# print(offset*8)
# print(f"first imu offset in file: {offset*8}")
# print(bytes[offset*8:offset*8+24])
# print(bytes[offset*8+3*8:offset*8+3*8+4*8])
# print("findall first 10 imu offsets: ")
imu_idx = list(bytes.findall('0x232349',bytealigned=False))
# imu_ts_1 = bytes[imu_idx[0]+8*3:imu_idx[0]+8*3+8*4].uintle*1e-6
# print(imu_ts_1)
# imu_idx_buf = list(bytes.findall('0x23234a',bytealigned=False))
# imu_ts_1_buf = bytes[imu_idx_buf[0]+8*3:imu_idx_buf[0]+8*3+8*4].uintle*1e-6
# print(imu_ts_1_buf)

num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2
sentinel_size=3
ind=imu_idx[0]
imu_bytes = bytes[imu_idx[0]+3*8:imu_idx[0]+(num_imu_bytes+sentinel_size)*8]

imu_ts_1 = imu_bytes[0:4*8].uintle*1e-6
print(imu_ts_1)

next_sentinel = bytes[ind+(num_imu_bytes+sentinel_size)*8-8:ind+(num_imu_bytes+2*sentinel_size)*8-8]
print(next_sentinel)

swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(binary_file)
# print(imu_time[0,0])
sp.show_plots(swp_time, volts, imu_time, acc, mag, gyr)
# plt.plot(imu_time[0],acc[0,0,:])
# plt.show()
# print(np.where(volts[0,1,:]==0)[0].size)
# print(volts[0,1,:].size)
# plt.plot(swp_time[0], volts[0,1,:])
# # plt.plot(swp_time[0], volts[1,0,:])
# plt.show()
# test_range = np.where((swp_time[0]>43) & (swp_time[0]<44))[0]
# print(np.where(volts[0,1,:]>1)[0].size)
# print(np.where(np.isnan(volts[0,1,:]))[0].size)
# fig, ax = plt.subplots(1,2,figsize=(14,6))
# ax[0].plot(swp_time[0],volts[0,1,:])
# ax[0].set_title("Raw")
# ax[0].set_xlabel("Time")
# ax[0].set_ylabel("Volts")
# volts[0,0,np.where((volts[0,1,:]>1) | (volts[0,1,:]<=0.6))[0]] = 0.625
# ax[1].plot(swp_time[0],volts[0,0,:])
# ax[1].set_title("Processed")
# ax[1].set_xlabel("Time")
# plt.tight_layout()
# plt.show()
# stp.show_plots(swp_time=swp_time, volts=volts, imu_time=imu_time, acc=acc, mag=mag, gyr=gyr)
