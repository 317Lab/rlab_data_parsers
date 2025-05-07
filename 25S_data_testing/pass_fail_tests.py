# TODO: add automatic port detection.
import serial
import time
import shield_test_feed as feed
import datetime
import parse_binary as pb
import numpy as np
import pandas as pd
import os
import utilities as util
import shield_test_plot as plot
import warnings
baud = 230400
initial_timeout = 120  # seconds before initial serial timeout, allows user to start recording and wait for shield power on
test_file_directory = 'test_files'
imu_read_time = 10
imu_diff_cutoff = 0.0001

coord_axes = {0: 'X', 1: 'Y', 2: 'Z'}

def within_nominal(mean, benchmark_range):
    if hasattr(mean, '__len__'):
        for i in range(len(mean)):
            if not np.any((np.min(benchmark_range) <= mean) & (mean <= np.max(benchmark_range))):
                return False
        return True
    else:
        if not np.any((np.min(benchmark_range) <= mean) & (mean <= np.max(benchmark_range))):
            return False
        return True


port = input("input port\n")
print("connecting...\n")

try:
    ser = serial.Serial(port, baudrate=baud, timeout=1)
    #ser.reset_input_buffer()  # flush serial port
    time.sleep(1)
    if ser.in_waiting>0:
        print("Connected!")
        ser.reset_input_buffer() 
    else:
        print("No data available. Please check the connection.")
        exit()
except serial.SerialException as e:
    print(f"Serial port error: {e}")
    exit()

acc_benchmark = (0,0.5)
mag_benchmark = (-0.5, 0)
gyr_benchmark = (-0.05, 0.05)
cad_benchmark = (21,23)
acc_motion = 0.01
mag_motion = 0.05
gyr_motion = 0.1

start_test = input("Enter 'go' when ready to collect data. Wiggle IMU during entire collection. \n")
if start_test == 'go':
    now = datetime.datetime.now()
    now = now.strftime("%Y%m%dT%H%M%SZ")

    results_path = test_file_directory + "/test_results_" + str(now)
    os.system(f'mkdir -p {results_path}')
    filename = results_path + "/shield_test.bin"
    #filename = test_file_directory+"shield_test_"+str(now)+".bin"
    print("reading data, wait " +str(imu_read_time)+" seconds...")
    feed.read(port, file_name=filename, read_time=10)
    print("data saved. checking...")
    time.sleep(0.5)
    swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(filename)
    # avg_diffs = []
    acc_std = np.array([np.std(acc[0,0,:]), np.std(acc[0,1,:]), np.std(acc[0,2,:])])
    mag_std = np.array([np.std(mag[0,0,:]), np.std(mag[0,1,:]), np.std(mag[0,2,:])])
    gyr_std = np.array([np.std(gyr[0,0,:]), np.std(gyr[0,1,:]), np.std(gyr[0,2,:])])
    acc_mean = np.array([np.mean(acc[0,0,:]), np.mean(acc[0,1,:]), np.mean(acc[0,2,:])])
    mag_mean = np.array([np.mean(mag[0,0,:]), np.mean(mag[0,1,:]), np.mean(mag[0,2,:])])
    gyr_mean = np.array([np.mean(gyr[0,0,:]), np.mean(gyr[0,1,:]), np.mean(gyr[0,2,:])])
    acc_fails = np.where(acc_std < acc_motion)[0]
    mag_fails = np.where(mag_std < mag_motion)[0]
    gyr_fails = np.where(gyr_std < gyr_motion)[0]
    motion_flag = (len(acc_fails) == 0) and (len(mag_fails) == 0) and (len(gyr_fails) == 0)
    if motion_flag:
        print("IMU motion test PASSED.")
    else:
        print("IMU motion test FAILED. Failed axes:")
        if len(acc_fails) > 0:
            print("failed acceleration components:")
            for i in acc_fails:
                print(f"{coord_axes[i]} component")
        if len(mag_fails) > 0:
            print("failed magnetometer components:")
            for i in mag_fails:
                print(f"{coord_axes[i]} component")
        if len(gyr_fails) > 0:
            print("failed gyrometer components:")
            for i in gyr_fails:
                print(f"{coord_axes[i]} component")
    # mag_mean = []
    # gyr_mean = []
    # for i in range(0,3):
    #     # avg_diffs.append(np.abs(np.mean(np.diff(acc[0,i,:]))))
    #     acc_mean.append(np.mean(acc[0,i,:]))
    #     mag_mean.append(np.mean(mag[0,i,:]))
    #     gyr_mean.append(np.mean(gyr[0,i,:]))
    # if all(flag>imu_diff_cutoff for flag in avg_diffs):
    #     print("IMU motion test PASSED.")
    # else:
    #     failing_indices = [i for i, flag in enumerate(avg_diffs) if flag <= imu_diff_cutoff]
    #     failed_diffs = [avg_diffs[i] for i in failing_indices]
    #     print("IMU motion test FAILED.")
    nom_cond = (within_nominal(acc_mean, acc_benchmark), within_nominal(mag_mean, mag_benchmark), within_nominal(gyr_mean, gyr_benchmark))
    if all(nom_cond):
        print("IMU nominal test PASSED.")
    else:
        nom_fails = np.where(nom_cond == False)[0]
        print("IMU nominal test FAILED. Failed axes:")
        if 0 in nom_fails:
            print("acceleration")
        if 1 in nom_fails:
            print("magnetometer")
        if 2 in nom_fails:
            print("gyroscope")
    imu_cad = np.diff(imu_time,append=np.nan)*1e3 # imu cadence in ms
    imu_cad_avg = np.nanmedian(imu_cad)
    if within_nominal(imu_cad_avg, cad_benchmark):
        print("Cadence test PASSED.")
    else:
        print(f"Cadence test FAILED. Cadence: {imu_cad_avg:.3f} ms") 
    # saving data
    print("Saving data...")
    n = volts.shape[2]
    d = {
        'Pip 0 Voltage': volts[0,0,:],
        'Pip 1 Voltage': volts[0,1,:],
        'Mean Acceleration': [acc_mean] * n,
        'Mean Magnetic Field': [mag_mean] * n,
        'Mean Gyration': [gyr_mean] * n,
        'Median Cadence': [imu_cad_avg] * n
    }
    df = pd.DataFrame(data=d)
    df.to_csv(results_path + "/test_results.csv", index=False)
    util.check_buffers(swp_time=swp_time, volts=volts, imu_time=imu_time, acc=acc, mag=mag, gyr=gyr, save=True, save_path=f"{results_path}/test_buffers.png")
    # suppress ylim transformation warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plot.save_plots(swp_time=swp_time, volts=volts, imu_time=imu_time, acc=acc, mag=mag, gyr=gyr, save_path=f"{results_path}/shield_plot.png")
    steps_0, steps_1 = util.get_sweep_steps(volts=volts)
    noise_levels_0, noise_levels_1 = util.get_step_std(steps=steps_0), util.get_step_std(steps=steps_1)
    med_noise_mv_0, med_noise_mv_1 = np.median(noise_levels_0)*1e3, np.median(noise_levels_1)*1e3
    noise_mv = np.column_stack((noise_levels_0, noise_levels_1))*1e3
    print(f"PIP 0 STD: {med_noise_mv_0:.3f} mV, PIP 1 STD: {med_noise_mv_1:.3f} mV")
    noise_mv = pd.DataFrame(data=noise_mv, columns=['Pip 0 STD (mV)', 'Pip 1 STD (mV)'])
    noise_mv.to_csv(results_path + "/step_std_mV.csv", index=False)
    #np.savetxt(results_path + "/step_std_mV.csv", noise_mv, delimiter=",")
    nominal_volts = np.linspace(5, 0, 28)
    steps_0_med = np.zeros(28)
    steps_1_med = np.zeros(28)
    for i in range(28):
        steps_0_med[i] = np.median(steps_0[:,i])
        steps_1_med[i] = np.median(steps_1[:,i])
    offset_0 = nominal_volts- steps_0_med
    offset_1 = nominal_volts- steps_1_med
    offset_mv = np.column_stack((offset_0, offset_1))*1e3
    #np.savetxt(results_path + "/step_offset_mV.csv", offset_mv, delimiter=",")
    offset_mv = pd.DataFrame(data=offset_mv, columns=['Pip 0 Offset (mV)', 'Pip 1 Offset (mV)'])
    offset_mv.to_csv(results_path + "/step_offset_mV.csv", index=False)
    print("Data saved to " + results_path)
    print("Test complete. That's GNEISS!")
else:
    print("Test cancelled. Not GNEISS :(")
    exit()

    

