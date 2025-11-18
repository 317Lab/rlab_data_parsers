import json
import argparse
import parse_binary as pb
import plot_utils as pu
import matplotlib.pyplot as plt
import numpy as np
import os



def save_plot(in_file, out_file, bob_num):
    fs = 15
    rocket_num = bob_num.split('_', 1)[0].replace('.', '').upper()
    stream_num = bob_num.split('_', 1)[1].replace('.', '').upper()

    with open("offsets.json", "r") as f:
        offsets = json.load(f)
    mag_offsets = offsets[bob_num]["mag"]
    acc_offsets = offsets[bob_num]["acc"]
    gyr_offsets = offsets[bob_num]["gyr"]
    #temporary fix for gyro offset
    gyr_offsets[1] = gyr_offsets[1]/2
    swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(in_file)


    plot_title = f"Rocket {rocket_num}, Shield {payload_id[0,0]}, Stream {stream_num}\n File: {in_file}"

    # reshape offsets tuple for Numpy broadcasting
    mag_cal = mag[0,:,:]-np.asarray(mag_offsets)[:,None]
    acc_cal = acc[0,:,:]-np.asarray(acc_offsets)[:,None]
    gyr_cal = gyr[0,:,:]-np.asarray(gyr_offsets)[:,None]

    fig, axs = plt.subplots(5,sharex=True, figsize=(10,12))
    pu.plot_data(axs[0],imu_time[0],acc_cal,1,"IMU TIME SINCE POWER (s)","ACC [g]",False,fs, True)
    # pu.plot_data(axs[0],imu_time[0],acc_mag, 5, "","", False, 8)
    axs[0].xaxis.set_label_position('top')

    pu.plot_data(axs[1],imu_time[0],mag_cal,1,"","MAG [G]",False,fs,)
    pu.plot_data(axs[2],imu_time[0],gyr_cal,1,"","GYR [Hz]",False,fs)
    pu.plot_data(axs[3],swp_time[0],volts[0,0],1,"","P0 [V]", False, fs)
    pu.plot_data(axs[4],swp_time[0],volts[0,1],1,"SWEEP TIME SINCE POWER (s)","P1 [V]", False, fs)
    # not sure why standard axis setting isn't working
    axs[0].set_xlim(np.nanmin(swp_time[0]),np.nanmax(swp_time[0]))
    axs[0].set_ylim(np.nanmin(acc_cal),np.nanmax(acc_cal))
    axs[1].set_ylim(np.nanmin(mag_cal),np.nanmax(mag_cal))
    axs[2].set_ylim(np.nanmin(gyr_cal),np.nanmax(gyr_cal))
    for i in range(5):
        axs[i].tick_params(axis='both', which='major', labelsize=12)
    fig.suptitle(plot_title, fontsize=20)
    out_file = os.path.expanduser(out_file)
    plt.tight_layout()
    plt.savefig(out_file)

save_path = "~/Documents/cal_plots/"
save_plot("397_Swarm_deploy_d1.bin", save_path+"397_77_D1_deploy.png", "397_D1")
save_plot("397_Swarm_deploy_d4.bin", save_path+"397_78_D4_deploy.png", "397_D4")
save_plot("398_swarm_deploy_11042025_d1.bin", save_path+"398_75_D1_deploy.png", "398_D1")
save_plot("398_swarm_deploy_11042025_d4.bin", save_path+"398_76_D4_deploy.png", "398_D4")
save_plot("36.397_MAG_CAL_D1_GL_D1_R4.bin", save_path+"397_77_D1_magcal.png", "397_D1")
save_plot("36.397_MAG_CAL_D4_GL_D4_R4.bin", save_path+"397_78_D4_magcal.png", "397_D4")
save_plot("36.398_MAG_CAL_D1_GL_D1_R4.bin", save_path+"398_75_D1_magcal.png", "398_D1")
save_plot("36.398_MAG_CAL_D4_GL_D4_R4.bin", save_path+"398_76_D4_magcal.png", "398_D4")


