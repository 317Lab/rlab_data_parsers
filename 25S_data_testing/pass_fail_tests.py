import serial
import time
import shield_test_feed as feed
import datetime
import parse_binary as pb
import numpy as np
baud = 230400
initial_timeout = 120  # seconds before initial serial timeout, allows user to start recording and wait for shield power on
test_file_directory = 'test_files/'
imu_read_time = 10
imu_diff_cutoff = 0.0001
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

testImu = input("Enter 'go' when ready for IMU test. \n")
if testImu == 'go':
    now = datetime.datetime.now()
    now = now.strftime("%Y%m%dT%H%M%SZ")
    filename = test_file_directory+"imu_test_"+str(now)+".bin"
    print("wiggle the IMU!!!")
    print("reading data, wait " +str(imu_read_time)+" seconds...")
    feed.read(port, file_name=filename, read_time=10)
    print("data saved. checking...")
    time.sleep(0.5)
    _, _, _, imu_time, acc, _, gyr = pb.parse_all(filename)
    avg_diffs = []
    for i in range(0,3):
        avg_diffs.append(np.abs(np.mean(np.diff(acc[0,i,:]))))
    if all(flag>imu_diff_cutoff for flag in avg_diffs):
        print("IMU test PASSED")
    else:
        failing_indices = [i for i, flag in enumerate(avg_diffs) if flag <= imu_diff_cutoff]
        failed_diffs = [avg_diffs[i] for i in failing_indices]
        print("IMU test FAILED. Mean acceleration variation in ", failing_indices, " coordinate: ", failed_diffs)
    
    

