import json
import argparse
import parse_binary as pb
import plot_utils as pu
import matplotlib.pyplot as plt
import numpy as np


parser = argparse.ArgumentParser(description="317 Lab PIP Plots with sensor calibration")
parser.add_argument("filename", help="Data file name.")
parser.add_argument("bob_num", help="Rocket/bob number in the form [ROCKET_NUM]_[BOB_NUM]. Eg: 397_D1")
parser.add_argument("-t","--title", help="Optional Plot Title")
args = parser.parse_args()
bob_num = args.bob_num
filename = args.filename

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
    plot_title = f"Rocket {rocket_num}, Shield {payload_id[0,0]}, Stream {stream_num}\n File: {filename}"

# reshape offsets tuple for Numpy broadcasting
mag_cal = mag[0,:,:]-np.asarray(mag_offsets)[:,None]
acc_cal = acc[0,:,:]-np.asarray(acc_offsets)[:,None]
gyr_cal = gyr[0,:,:]-np.asarray(gyr_offsets)[:,None]

fig, axs = plt.subplots(5,sharex=True)
pu.plot_data(axs[0],imu_time[0],acc_cal,1,"IMU TIME SINCE POWER (s)","ACC [g]",False,8, True)
# pu.plot_data(axs[0],imu_time[0],acc_mag, 5, "","", False, 8)
axs[0].xaxis.set_label_position('top')

pu.plot_data(axs[1],imu_time[0],mag_cal,1,"","MAG [G]",False,8,)
pu.plot_data(axs[2],imu_time[0],gyr_cal,1,"","GYR [Hz]",False,8)
pu.plot_data(axs[3],swp_time[0],volts[0,0],1,"","P0 [V]", False, 8)
pu.plot_data(axs[4],swp_time[0],volts[0,1],1,"SWEEP TIME SINCE POWER (s)","P1 [V]", False, 8)
# not sure why standard axis setting isn't working
axs[0].set_xlim(np.nanmin(swp_time[0]),np.nanmax(swp_time[0]))
axs[0].set_ylim(np.min(acc_cal),np.max(acc_cal))
axs[1].set_ylim(np.min(mag_cal),np.max(mag_cal))
axs[2].set_ylim(np.min(gyr_cal),np.max(gyr_cal))
fig.suptitle(plot_title)
plt.subplots_adjust(wspace=0.1, hspace=0.1)
plt.show()