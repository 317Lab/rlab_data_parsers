"""
Automated pass/fail tests and data/plot generation for GNEISS shield testing.
Author: Sean Wallace
Contact: sean.k.wallace.27@dartmouth.edu
Date: May 2025
"""
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
import detect_port as detect

# check if value is within benchmark range
# benchmark_range is a tuple of the form (min, max)
# mean is a scalar or a 1D array
def within_nominal(mean, benchmark_range):\
    # handle lists and scalars
    if hasattr(mean, '__len__'):
        for i in range(len(mean)):
            if not np.any((np.min(benchmark_range) <= mean) & (mean <= np.max(benchmark_range))):
                return False
        return True
    else:
        if not np.any((np.min(benchmark_range) <= mean) & (mean <= np.max(benchmark_range))):
            return False
        return True

# global variables
baud = 230400
test_file_directory = 'test_files'
read_time = 15
coord_axes = {0: 'X', 1: 'Y', 2: 'Z'}
acc_benchmark = (0,0.5)
mag_benchmark = (-0.5, 0)
gyr_benchmark = (-0.05, 0.05)
cad_benchmark = (21,23)
acc_motion = 0.01
mag_motion = 0.05
gyr_motion = 0.1



print("Detecting port...")
port = detect.detect_port()
print(f"Connected to {port}")


start_test = input("Enter 'go' when ready to collect data. Wiggle IMU for first five seconds. \n")
if start_test == 'go':
    now = datetime.datetime.now()
    now = now.strftime("%Y%m%dT%H%M%SZ")
    # make results directory
    results_path = test_file_directory + "/test_results_" + str(now)
    os.system(f'mkdir -p {results_path}')
    filename = results_path + "/shield_test.bin"

    # read data into binary file using Jules' serial feed program
    print("reading data, wait " +str(read_time)+" seconds...")
    feed.read(port, file_name=filename, read_time=10)
    print("data saved. checking...")
    time.sleep(0.5)

    # parse binary file
    swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(filename)
    start = imu_time[0,0]
    end = start + 5
    measure_idx = np.where((imu_time[0,:]>= start) & (imu_time[0,:] <= end))[0]


    # collect relevant data for pass/fail tests
    acc_std = np.array([np.std(acc[0,0,measure_idx]), np.std(acc[0,1,measure_idx]), np.std(acc[0,2,measure_idx])])
    mag_std = np.array([np.std(mag[0,0,measure_idx]), np.std(mag[0,1,measure_idx]), np.std(mag[0,2,measure_idx])])
    gyr_std = np.array([np.std(gyr[0,0,measure_idx]), np.std(gyr[0,1,measure_idx]), np.std(gyr[0,2,measure_idx])])
    acc_mean = np.array([np.mean(acc[0,0,measure_idx]), np.mean(acc[0,1,measure_idx]), np.mean(acc[0,2,measure_idx])])
    mag_mean = np.array([np.mean(mag[0,0,measure_idx]), np.mean(mag[0,1,measure_idx]), np.mean(mag[0,2,measure_idx])])
    gyr_mean = np.array([np.mean(gyr[0,0,measure_idx]), np.mean(gyr[0,1,measure_idx]), np.mean(gyr[0,2,measure_idx])])
    acc_fails = np.where(acc_std < acc_motion)[0]
    mag_fails = np.where(mag_std < mag_motion)[0]
    gyr_fails = np.where(gyr_std < gyr_motion)[0]


    # IMU motion test
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

    # IMU nominal value test
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

    # Cadence test
    imu_cad = np.diff(imu_time,append=np.nan)*1e3 
    imu_cad_avg = np.nanmedian(imu_cad)
    if within_nominal(imu_cad_avg, cad_benchmark):
        print("Cadence test PASSED.")
    else:
        print(f"Cadence test FAILED. Cadence: {imu_cad_avg:.3f} ms") 

    # save data
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

    # plot of corresponding buffered/non-buffered data
    util.check_buffers(swp_time=swp_time, volts=volts, imu_time=imu_time, acc=acc, mag=mag, gyr=gyr, save=True, save_path=f"{results_path}/test_buffers.png")
    # suppress ylim transformation warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # standard shield plot
        plot.save_plots(swp_time=swp_time, volts=volts, imu_time=imu_time, acc=acc, mag=mag, gyr=gyr, save_path=f"{results_path}/shield_plot.png")

    # voltage standard deviations
    steps_0, steps_1 = util.get_sweep_steps(volts=volts)
    noise_levels_0, noise_levels_1 = util.get_step_std(steps=steps_0), util.get_step_std(steps=steps_1)
    med_noise_mv_0, med_noise_mv_1 = np.median(noise_levels_0)*1e3, np.median(noise_levels_1)*1e3
    noise_mv = np.column_stack((noise_levels_0, noise_levels_1))*1e3
    print(f"PIP 0 STD: {med_noise_mv_0:.3f} mV, PIP 1 STD: {med_noise_mv_1:.3f} mV")
    # convert to pandas for headers
    noise_mv = pd.DataFrame(data=noise_mv, columns=['Pip 0 STD (mV)', 'Pip 1 STD (mV)'])
    noise_mv.to_csv(results_path + "/step_std_mV.csv", index=False)

    # voltage offsets from nominal DAC value
    nominal_volts = np.linspace(5, 0, 28)
    steps_0_med = np.zeros(28)
    steps_1_med = np.zeros(28)
    for i in range(28):
        steps_0_med[i] = np.median(steps_0[:,i])
        steps_1_med[i] = np.median(steps_1[:,i])
    offset_0 = nominal_volts- steps_0_med
    offset_1 = nominal_volts- steps_1_med
    offset_mv = np.column_stack((offset_0, offset_1))*1e3
    # convert to pandas for headers
    offset_mv = pd.DataFrame(data=offset_mv, columns=['Pip 0 Offset (mV)', 'Pip 1 Offset (mV)'])
    offset_mv.to_csv(results_path + "/step_offset_mV.csv", index=False)
    print("Data saved to " + results_path)
    print("Test complete. That's GNEISS!")
else:
    print("Test cancelled. Not GNEISS :(")
    exit()

    

