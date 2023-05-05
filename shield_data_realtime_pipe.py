import sys
from bitstring import BitArray, BitStream
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

buffered = True
read_time = 1 # seconds
max_time = 50*60 # sweep time word errors have t > 3000 s which are removed.
freq = 45 # Hz

if buffered: # buffered data shown on second column of plots
    fig, axs = plt.subplots(6, 2, figsize=(8,6))
    ax0 = axs[0,0]; ax1 = axs[1,0]; ax2 = axs[2,0]
    ax3 = axs[3,0]; ax4 = axs[4,0]; ax5 = axs[5,0]
    ax0b = axs[0,1]; ax1b = axs[1,1]; ax2b = axs[2,1]
    ax3b = axs[3,1]; ax4b = axs[4,1]; ax5b = axs[5,1]
    dim = 2
else:
    fig, axs = plt.subplots(6, 1, figsize=(8,6))
    ax0 = axs[0]; ax1 = axs[1]; ax2 = axs[2]
    ax3 = axs[3]; ax4 = axs[4]; ax5 = axs[5]
    dim = 1

num_samples = 28 # how many samples per message
num_swp_bytes = 4 + 1 + num_samples * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
num_msg_bytes = (2 + num_swp_bytes + 2 + num_imu_bytes)*dim
t_scale = 1.e-6; a_scale = 4*9.8/2**15; m_scale = 1./2**15; g_scale = 2000./360/2**15; p_scale = 5/2**14 # data scales
num_bytes_target = read_time*freq*num_msg_bytes # N seconds worth of bytes

sentinels = ['0x2353','0x2349','0x2354','0x234A'] # [#S,#I,#T,#J]
plotting = True

# for closing on figure exit
def on_close(event):
    global plotting
    print('Close event captured at',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
    plotting = False

# history data arrays
swp_time_old = np.zeros([dim,0],dtype='single')
payload_id_old = np.zeros([dim,0],dtype='uint8')
volts_old = np.zeros([dim,2,0],dtype='single')
imu_time_old = np.zeros([dim,0],dtype='single')
acc_old = np.zeros([dim,3,0],dtype='single')
mag_old = np.zeros([dim,3,0],dtype='single')
gyr_old = np.zeros([dim,3,0],dtype='single')

while plotting:
    bytes = BitArray(sys.stdin.buffer.read(num_bytes_target))
    ids_swp = list(bytes.findall(sentinels[0], bytealigned=False))
    ids_imu = list(bytes.findall(sentinels[1], bytealigned=False))
    if buffered:
        ids_swp_buf = list(bytes.findall(sentinels[2], bytealigned=False))
        ids_imu_buf = list(bytes.findall(sentinels[3], bytealigned=False))
    num_dat_swp = max(len(ids_swp),len(ids_swp_buf))*num_samples
    num_dat_imu = max(len(ids_imu),len(ids_imu_buf))

    swp_time = np.zeros([dim,num_dat_swp],dtype='single')
    payload_id = np.zeros([dim,num_dat_swp],dtype='uint8')
    volts = np.zeros([dim,2,num_dat_swp],dtype='single')
    imu_time = np.zeros([dim,num_dat_imu],dtype='single')
    acc = np.zeros([dim,3,num_dat_imu],dtype='single')
    mag = np.zeros([dim,3,num_dat_imu],dtype='single')
    gyr = np.zeros([dim,3,num_dat_imu],dtype='single')

    pos = 0
    for ind in ids_swp: # sweep indeces
        next_sentinel = bytes[ind+(num_swp_bytes+2)*8:ind+(num_swp_bytes+2+2)*8]
        if next_sentinel in sentinels:
            swp_bytes = bytes[ind+2*8:ind+(num_swp_bytes+2)*8]
            pip0_bytes = swp_bytes[5*8:(5+2*num_samples)*8]
            pip1_bytes = swp_bytes[(5+2*num_samples)*8:]
            swp_time_tmp = swp_bytes[0:4*8].uintle*t_scale
            payload_id_tmp = swp_bytes[4*8:5*8].uintle
            for sample in range(0,2*num_samples,2): # allocate all sweep samples to arrays
                swp_time[0,pos] = swp_time_tmp # copy static data for each sample
                payload_id[0,pos] = payload_id_tmp
                volts[0,0,pos] = pip0_bytes[sample*8:(sample+2)*8].uintle*p_scale
                volts[0,1,pos] = pip1_bytes[sample*8:(sample+2)*8].uintle*p_scale
                pos += 1

    pos = 0
    for ind in ids_imu: # imu indices
        next_sentinel = bytes[ind+(num_imu_bytes+2)*8:ind+(num_imu_bytes+2+2)*8]
        if next_sentinel in sentinels:
            imu_bytes = bytes[ind+2*8:ind+(num_imu_bytes+2)*8]
            imu_time[0,pos] = imu_bytes[0:4*8].uintle*t_scale
            acc[0,0,pos] = imu_bytes[4  *8:6  *8].intle*a_scale
            acc[0,1,pos] = imu_bytes[6  *8:8  *8].intle*a_scale
            acc[0,2,pos] = imu_bytes[8  *8:10 *8].intle*a_scale
            mag[0,0,pos] = imu_bytes[10 *8:12 *8].intle*m_scale
            mag[0,1,pos] = imu_bytes[12 *8:14 *8].intle*m_scale
            mag[0,2,pos] = imu_bytes[14 *8:16 *8].intle*m_scale
            gyr[0,0,pos] = imu_bytes[16 *8:18 *8].intle*g_scale
            gyr[0,1,pos] = imu_bytes[18 *8:20 *8].intle*g_scale
            gyr[0,2,pos] = imu_bytes[20 *8:22 *8].intle*g_scale
            pos += 1

    if buffered:
        pos = 0
        for ind in ids_swp_buf: # buffered sweep indeces
            next_sentinel = bytes[ind+(num_swp_bytes+2)*8:ind+(num_swp_bytes+2+2)*8]
            if next_sentinel in sentinels:
                swp_bytes = bytes[ind+2*8:ind+(num_swp_bytes+2)*8]
                pip0_bytes = swp_bytes[5*8:(5+2*num_samples)*8]
                pip1_bytes = swp_bytes[(5+2*num_samples)*8:]
                swp_time_tmp = swp_bytes[0:4*8].uintle*t_scale
                payload_id_tmp = swp_bytes[4*8:5*8].uintle
                for sample in range(0,2*num_samples,2): # allocate all sweep samples to arrays
                    swp_time[1,pos] = swp_time_tmp # copy static data for each sample
                    payload_id[1,pos] = payload_id_tmp
                    volts[1,0,pos] = pip0_bytes[sample*8:(sample+2)*8].uintle*p_scale
                    volts[1,1,pos] = pip1_bytes[sample*8:(sample+2)*8].uintle*p_scale
                    pos += 1

        pos = 0
        for ind in ids_imu_buf: # buffered imu indeces
            next_sentinel = bytes[ind+(num_imu_bytes+2)*8:ind+(num_imu_bytes+2+2)*8]
            if next_sentinel in sentinels:
                imu_bytes = bytes[ind+2*8:ind+(num_imu_bytes+2)*8]
                imu_time[1,pos] = imu_bytes[0:4*8].uintle*t_scale
                acc[1,0,pos] = imu_bytes[4  *8:6  *8].intle*a_scale
                acc[1,1,pos] = imu_bytes[6  *8:8  *8].intle*a_scale
                acc[1,2,pos] = imu_bytes[8  *8:10 *8].intle*a_scale
                mag[1,0,pos] = imu_bytes[10 *8:12 *8].intle*m_scale
                mag[1,1,pos] = imu_bytes[12 *8:14 *8].intle*m_scale
                mag[1,2,pos] = imu_bytes[14 *8:16 *8].intle*m_scale
                gyr[1,0,pos] = imu_bytes[16 *8:18 *8].intle*g_scale
                gyr[1,1,pos] = imu_bytes[18 *8:20 *8].intle*g_scale
                gyr[1,2,pos] = imu_bytes[20 *8:22 *8].intle*g_scale
                pos += 1

    swp_time[(swp_time==0) | (swp_time>max_time)] = np.nan
    imu_time[(imu_time==0) | (imu_time>max_time)] = np.nan

    imu_cad = np.diff(imu_time,append=np.nan)*1e3

    # Plotting
    fig.canvas.mpl_connect('close_event', on_close) # exit loop when closing figure
    fig.subplots_adjust(hspace=0)
    lw = 1

    ax0.clear() # accelerometer
    ax0.plot(imu_time[0],acc[0,0],linewidth=lw)
    ax0.plot(imu_time[0],acc[0,1],linewidth=lw)
    ax0.plot(imu_time[0],acc[0,2],linewidth=lw)
    ax0.set_ylabel('ACC [g]')
    ax0.grid()
    ax0.ticklabel_format(useOffset=False)
    ax0.set_xlabel('IMU TIME SINCE SHIELD POWER [s]')
    ax0.xaxis.tick_top()
    ax0.xaxis.set_label_position('top')
    ax0.text(0.9, 1.5, 'SHIELD ID: ' + str(payload_id[0,0]), transform=ax0.transAxes, fontsize=15)
    # if monitoring_only:
    #     if flash:
    #         ax0.text(-0.1, 1.5, 'MONITORING ONLY', transform=ax0.transAxes, color='red',fontsize=20,weight="bold")
    #         flash = False
    #     else:
    #         flash = True

    ax1.clear() # magnetometer
    ax1.plot(imu_time[0],mag[0,0],linewidth=lw)
    ax1.plot(imu_time[0],mag[0,1],linewidth=lw)
    ax1.plot(imu_time[0],mag[0,2],linewidth=lw)
    ax1.set_ylabel('MAG [G]')
    ax1.grid()
    ax1.ticklabel_format(useOffset=False)
    ax1.xaxis.set_ticklabels([])

    ax2.clear() # gyrometer
    ax2.plot(imu_time[0],gyr[0,0],linewidth=lw)
    ax2.plot(imu_time[0],gyr[0,1],linewidth=lw)
    ax2.plot(imu_time[0],gyr[0,2],linewidth=lw)
    ax2.set_ylabel('GYR [Hz]')
    ax2.grid()
    ax2.ticklabel_format(useOffset=False)
    ax2.xaxis.set_ticklabels([])

    ax3.clear() # Cadance
    ax3.plot(imu_time[0],imu_cad[0],linewidth=lw)
    ax3.set_ylabel('CAD [ms]')
    ax3.grid()
    ax3.ticklabel_format(useOffset=False)
    ax3.xaxis.set_ticklabels([])

    ax4.clear() # pip0 voltage
    ax4.plot(swp_time[0],volts[0,0],linewidth=lw/2)
    ax4.set_ylabel('P0 [V]')
    ax4.grid()
    ax4.ticklabel_format(useOffset=False)
    ax4.xaxis.set_ticklabels([])

    ax5.clear() # pip1 voltage
    ax5.plot(swp_time[0],volts[0,1],linewidth=lw/2)
    ax5.set_ylabel('P1 [V]')
    ax5.grid()
    ax5.ticklabel_format(useOffset=False)
    ax5.set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]')
    # # ax5.text(-0.1, -0.6, 'P0 RMS: ' + "{0:.1f}".format(p0_rms) + ' mV', transform=ax5.transAxes)
    # # ax5.text(-0.1, -0.8, 'P1 RMS: ' + "{0:.1f}".format(p1_rms) + ' mV', transform=ax5.transAxes)
    # # ax5.text( 0.2, -0.6, 'P0 STD: ' + "{0:.1f}".format(p0_std) + ' mV', transform=ax5.transAxes)
    # # ax5.text( 0.2, -0.8, 'P1 STD: ' + "{0:.1f}".format(p1_std) + ' mV', transform=ax5.transAxes)
    # # ax5.text( 0.5, -0.8, 'CAD: ' + "{0:.1f}".format(imu_cad_med) + ' ms', transform=ax5.transAxes)

    if buffered:
        ax0b.clear() # accelerometer
        ax0b.plot(imu_time[1],acc[1,0],linewidth=lw)
        ax0b.plot(imu_time[1],acc[1,1],linewidth=lw)
        ax0b.plot(imu_time[1],acc[1,2],linewidth=lw)
        ax0b.grid()
        ax0b.ticklabel_format(useOffset=False)
        ax0b.set_xlabel('IMU TIME SINCE SHIELD POWER [s]')
        ax0b.xaxis.tick_top()
        ax0b.xaxis.set_label_position('top')

        ax1b.clear() # magnetometer
        ax1b.plot(imu_time[1],mag[1,0],linewidth=lw)
        ax1b.plot(imu_time[1],mag[1,1],linewidth=lw)
        ax1b.plot(imu_time[1],mag[1,2],linewidth=lw)
        ax1b.grid()
        ax1b.ticklabel_format(useOffset=False)
        ax1b.xaxis.set_ticklabels([])

        ax2b.clear() # gyrometer
        ax2b.plot(imu_time[1],gyr[1,0],linewidth=lw)
        ax2b.plot(imu_time[1],gyr[1,1],linewidth=lw)
        ax2b.plot(imu_time[1],gyr[1,2],linewidth=lw)
        ax2b.grid()
        ax2b.ticklabel_format(useOffset=False)
        ax2b.xaxis.set_ticklabels([])
        
        ax3b.clear() # Cadance
        ax3b.plot(imu_time[1],imu_cad[1],linewidth=lw)
        ax3b.grid()
        ax3b.ticklabel_format(useOffset=False)
        ax3b.xaxis.set_ticklabels([])
        
        ax4b.clear() # pip0 voltage
        ax4b.plot(swp_time[1],volts[1,0],linewidth=lw/2)
        ax4b.grid()
        ax4b.ticklabel_format(useOffset=False)
        ax4b.xaxis.set_ticklabels([])

        ax5b.clear() # pip1 voltage
        ax5b.plot(swp_time[1],volts[1,1],linewidth=lw/2)
        ax5b.grid()
        ax5b.ticklabel_format(useOffset=False)
        ax5b.set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]')

    plt.pause(read_time) # needed for pyplot realtime plotting.