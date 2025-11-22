import json
import argparse
import parse_binary as pb
import plot_utils as pu
import matplotlib.pyplot as plt
import numpy as np

fs = 15

parser = argparse.ArgumentParser(description="317 Lab PIP Plots with sensor calibration")
parser.add_argument("filename", help="Data file name.")
parser.add_argument("bob_num", help="Rocket/bob number in the form [ROCKET_NUM]_[BOB_NUM]. Eg: 397_D1")
parser.add_argument("-t","--title", help="Optional Plot Title")
parser.add_argument("-b", "--buffer", type=int, help="Set to 1 if you want buffered data")
args = parser.parse_args()
bob_num = args.bob_num
filename = args.filename

if args.buffer == 1:
    buffered = 1
else:
    buffered = 0

rocket_num = bob_num.split('_', 1)[0].replace('.', '').upper()
stream_num = bob_num.split('_', 1)[1].replace('.', '').upper()

with open("offsets.json", "r") as f:
    offsets = json.load(f)
mag_offsets = offsets[bob_num]["mag"]
acc_offsets = offsets[bob_num]["acc"]
gyr_offsets = offsets[bob_num]["gyr"]
#temporary fix for gyro offset
gyr_offsets[1] = gyr_offsets[1]/2
swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(filename)

if args.title is not None:
    plot_title = args.title
else:
    if not buffered == 1:
        plot_title = f"Rocket {rocket_num}, Shield {payload_id[0,0]}, Stream {stream_num}\n File: {filename}"
    else:
        plot_title = f"Rocket {rocket_num}, Shield {payload_id[0,0]}, Stream {stream_num}\n File: {filename}, buffered data"
# reshape offsets tuple for Numpy broadcasting
mag_cal = mag[buffered,:,:]-np.asarray(mag_offsets)[:,None]
acc_cal = acc[buffered,:,:]-np.asarray(acc_offsets)[:,None]
gyr_cal = gyr[buffered,:,:]-np.asarray(gyr_offsets)[:,None]

fig, axs = plt.subplots(5,sharex=True, figsize=(10,12))
pu.plot_data(axs[0],imu_time[buffered],acc_cal,1,"IMU TIME SINCE POWER (s)","ACC [g]",False,fs, True)
# pu.plot_data(axs[0],imu_time[0],acc_mag, 5, "","", False, 8)
axs[0].xaxis.set_label_position('top')

pu.plot_data(axs[1],imu_time[buffered],mag_cal,1,"","MAG [G]",False,fs,)
pu.plot_data(axs[2],imu_time[buffered],gyr_cal,1,"","GYR [Hz]",False,fs)
pu.plot_data(axs[3],swp_time[buffered],volts[buffered,0],1,"","P0 [V]", False, fs)
pu.plot_data(axs[4],swp_time[buffered],volts[buffered,1],1,"SWEEP TIME SINCE POWER (s)","P1 [V]", False, fs)
# not sure why standard axis setting isn't working
axs[0].set_xlim(np.nanmin(swp_time[buffered]),np.nanmax(swp_time[buffered]))
axs[0].set_ylim(np.min(acc_cal),np.max(acc_cal))
axs[1].set_ylim(np.min(mag_cal),np.max(mag_cal))
axs[2].set_ylim(np.min(gyr_cal),np.max(gyr_cal))
for i in range(5):
    axs[i].tick_params(axis='both', which='major', labelsize=12)
fig.suptitle(plot_title, fontsize=20)
plt.subplots_adjust(wspace=0.1, hspace=0.1)
plt.show()