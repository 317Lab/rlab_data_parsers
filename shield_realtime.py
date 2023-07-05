import sys
from bitstring import BitArray
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import time

# user settings
buffered = True # whether to plot RAM buffered data
debug = True
read_time = 1 # approximate read time in seconds
read_multiplier = 4 # multiplier length of history
max_time = 10*50*60 # sweep time word errors have t > 3000 s which are removed. MIGHT BE FIXED TBD
freq = 45 # approximate message frequency in Hz
sync_max_offset = 0.1 # max absolute allowed parser-shield sync offset in seconds
sync_tuner = 0.03 # tune sync aggressiveness, 0 = no sync

# initialize figure + axes
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

# parameters
num_samples = 28 # how many samples per message
num_swp_bytes = 4 + 1 + num_samples * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
num_msg_bytes = (2 + num_swp_bytes + 2 + num_imu_bytes)*dim
num_bytes_target_set = round(read_time*freq*num_msg_bytes) # N seconds worth of bytes

t_scale = 1.e-6; a_scale = 4*9.8/2**15; m_scale = 1./2**15; g_scale = 2000./360/2**15; p_scale = 5/2**14 # data scales
sentinels = ['0x2353','0x2349','0x2354','0x234A'] # [#S,#I,#T,#J]
plotting = True
first_capture = True
num_bytes_target = num_bytes_target_set

# for closing on figure exit
def on_close(event):
    global plotting
    print('Close event captured at',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
    plotting = False

# history data arrays, required for initial stitch
swp_time_old = np.zeros([dim,0],dtype='single')
volts_old = np.zeros([dim,2,0],dtype='single')
imu_time_old = np.zeros([dim,0],dtype='single')
acc_old = np.zeros([dim,3,0],dtype='single')
mag_old = np.zeros([dim,3,0],dtype='single')
gyr_old = np.zeros([dim,3,0],dtype='single')
imu_cad_old = np.zeros([dim,0],dtype='single')

while plotting:
    bytes = BitArray(sys.stdin.buffer.read(num_bytes_target))
    if b'TIMEOUT\n' in bytes:
        print('SERIAL TIMEOUT AT',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
        break

    ids_swp = list(bytes.findall(sentinels[0], bytealigned=False))
    ids_imu = list(bytes.findall(sentinels[1], bytealigned=False))
    if buffered:
        ids_swp_buf = list(bytes.findall(sentinels[2], bytealigned=False))
        ids_imu_buf = list(bytes.findall(sentinels[3], bytealigned=False))
    else:
        ids_swp_buf = ids_swp
        ids_imu_buf = ids_imu
    num_dat_swp = max(len(ids_swp),len(ids_swp_buf))*num_samples
    num_dat_imu = max(len(ids_imu),len(ids_imu_buf))

    if (num_dat_swp<=num_samples) | (num_dat_imu<=1):
        try:
            print('DATA DROPOUT AT',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
            time.sleep(1) # print in 1 second intervals until end of data drop
        except KeyboardInterrupt:
            print('Close event captured at',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
            plotting = False
        continue

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
        if next_sentinel in sentinels: # double sentinel match insures full message available
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
                for sample in range(0,2*num_samples,2):
                    swp_time[1,pos] = swp_time_tmp
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
                
    # remove invalid timestamps
    swp_time[(swp_time==0) | (swp_time>max_time)] = np.nan
    imu_time[(imu_time==0) | (imu_time>max_time)] = np.nan

    # keep track of parser vs. shield timing
    if first_capture:
        t0_parser = time.time()
        t0_shield = imu_time[0,0]
        first_capture = False
    t_parser = time.time() - t0_parser
    t_shield = np.nanmax(imu_time) - t0_shield
    sync_offset = t_parser - t_shield
    sync_factor = 1 + np.tanh(sync_offset*sync_tuner) # unitless factor between 0 and 2, linear when close to 1
    sync_drift = num_bytes_target/num_bytes_target_set
    if sync_offset < -sync_max_offset: # parser too slow, grab fewer bytes per read_time
        num_bytes_target = round(num_bytes_target*sync_factor)
    elif sync_offset > sync_max_offset: # parser too fast, grab more bytes per read_time
        num_bytes_target = round(num_bytes_target*sync_factor)
    if abs(sync_drift) > 5:
        num_bytes_target = num_bytes_target_set

    # measured values
    imu_cad = np.diff(imu_time,append=np.nan)*1e3 # imu cadence
    imu_cad_avg = np.nanmean(imu_cad)
    imu_freq = 1e3/imu_cad_avg # hz
    # pip0_rms = np.sqrt(np.mean(np.square(volts[0,0]-np.mean(volts[0,0]))))*1e3 # pip 0 rms noise
    # pip1_rms = np.sqrt(np.mean(np.square(volts[0,1]-np.mean(volts[0,1]))))*1e3 # pip 1 rms noise
    pip0_std = np.nanstd(volts[0,0])*1e3 # pip 0 standard deviation
    pip1_std = np.nanstd(volts[0,1])*1e3 # pip 1 standard deviation

    # stitch history
    swp_time = np.concatenate((swp_time_old,swp_time),axis=1)
    volts = np.concatenate((volts_old,volts),axis=2)
    imu_time = np.concatenate((imu_time_old,imu_time),axis=1)
    acc = np.concatenate((acc_old,acc),axis=2)
    mag = np.concatenate((mag_old,mag),axis=2)
    gyr = np.concatenate((gyr_old,gyr),axis=2)
    imu_cad = np.concatenate((imu_cad_old,imu_cad),axis=1)

    # plotting
    fig.canvas.mpl_connect('close_event', on_close) # exit loop when closing figure
    fig.subplots_adjust(hspace=0)
    lw = 1
    fs = 8
    plt.rcParams.update({'font.size': fs})

    ax0.clear() # accelerometer
    ax0.plot(imu_time[0],acc[0,0],linewidth=lw)
    ax0.plot(imu_time[0],acc[0,1],linewidth=lw)
    ax0.plot(imu_time[0],acc[0,2],linewidth=lw)
    ax0.set_ylabel('ACC [g]',fontsize=fs)
    ax0.grid()
    ax0.ticklabel_format(useOffset=False)
    ax0.set_xlabel('IMU TIME SINCE SHIELD POWER [s]',fontsize=fs)
    ax0.xaxis.tick_top()
    ax0.xaxis.set_label_position('top')
    if debug:
        ax0.text(0.0*dim,1.7, 'FRQ: {0:.1f} Hz'.format(imu_freq), transform=ax0.transAxes)
        ax0.text(0.3*dim,1.7, 'SYNC OFFSET: {0:.1f} s'.format(sync_offset), transform=ax0.transAxes)
        ax0.text(0.6*dim,1.7,' SYNC FACTOR: {0:.2f}'.format(sync_factor), transform=ax0.transAxes)
        ax0.text(0.9*dim,1.7,' SYNC DRIFT: {0:.2f}'.format(sync_drift), transform=ax0.transAxes)
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
    ax1.set_ylabel('MAG [G]',fontsize=fs)
    ax1.grid()
    ax1.ticklabel_format(useOffset=False)
    ax1.xaxis.set_ticklabels([])

    ax2.clear() # gyrometer
    ax2.plot(imu_time[0],gyr[0,0],linewidth=lw)
    ax2.plot(imu_time[0],gyr[0,1],linewidth=lw)
    ax2.plot(imu_time[0],gyr[0,2],linewidth=lw)
    ax2.set_ylabel('GYR [Hz]',fontsize=fs)
    ax2.grid()
    ax2.ticklabel_format(useOffset=False)
    ax2.xaxis.set_ticklabels([])

    ax3.clear() # Cadance
    ax3.plot(imu_time[0],imu_cad[0],linewidth=lw)
    ax3.set_ylabel('CAD [ms]',fontsize=fs)
    ax3.grid()
    ax3.ticklabel_format(useOffset=False)
    ax3.xaxis.set_ticklabels([])

    ax4.clear() # pip0 voltage
    ax4.plot(swp_time[0],volts[0,0],linewidth=lw/2)
    ax4.set_ylabel('P0 [V]',fontsize=fs)
    ax4.grid()
    ax4.ticklabel_format(useOffset=False)
    ax4.xaxis.set_ticklabels([])

    ax5.clear() # pip1 voltage
    ax5.plot(swp_time[0],volts[0,1],linewidth=lw/2)
    ax5.set_ylabel('P1 [V]',fontsize=fs)
    ax5.grid()
    ax5.ticklabel_format(useOffset=False)
    ax5.set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]',fontsize=fs)
    ax5.text(0.0*dim,-0.8, 'ID: ' + str(payload_id[0,0]), transform=ax5.transAxes)
    ax5.text(0.1*dim,-0.8, 'STD0: {0:.1f} mV'.format(pip0_std), transform=ax5.transAxes)
    ax5.text(0.3*dim,-0.8, 'STD1: {0:.1f} mV'.format(pip1_std), transform=ax5.transAxes)
    ax5.text(0.5*dim,-0.8, 'CAD: {0:.1f} ms'.format(imu_cad_avg), transform=ax5.transAxes)

    if buffered:
        ax0b.clear() # accelerometer
        ax0b.plot(imu_time[1],acc[1,0],linewidth=lw)
        ax0b.plot(imu_time[1],acc[1,1],linewidth=lw)
        ax0b.plot(imu_time[1],acc[1,2],linewidth=lw)
        ax0b.grid()
        ax0b.ticklabel_format(useOffset=False)
        ax0b.set_xlabel('IMU TIME SINCE SHIELD POWER [s]',fontsize=fs)
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
        
        ax3b.clear() # cadance
        ax3b.plot(imu_time[1],imu_cad[1],linewidth=lw)
        ax3b.grid()
        ax3b.ticklabel_format(useOffset=False)
        ax3b.xaxis.set_ticklabels([])
        
        ax4b.clear() # pip 0 voltage
        ax4b.plot(swp_time[1],volts[1,0],linewidth=lw/2)
        ax4b.grid()
        ax4b.ticklabel_format(useOffset=False)
        ax4b.xaxis.set_ticklabels([])

        ax5b.clear() # pip 1 voltage
        ax5b.plot(swp_time[1],volts[1,1],linewidth=lw/2)
        ax5b.grid()
        ax5b.ticklabel_format(useOffset=False)
        ax5b.set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]',fontsize=fs)
    
    # history of read_multiplier x number of data per read time
    swp_time_old = swp_time[:,-num_dat_swp*read_multiplier:]
    volts_old = volts[:,:,-num_dat_swp*read_multiplier:]
    imu_time_old = imu_time[:,-num_dat_imu*read_multiplier:]
    acc_old = acc[:,:,-num_dat_imu*read_multiplier:]
    mag_old = mag[:,:,-num_dat_imu*read_multiplier:]
    gyr_old = gyr[:,:,-num_dat_imu*read_multiplier:]
    imu_cad_old = imu_cad[:,-num_dat_imu*read_multiplier:]

    plt.pause(read_time) # needed for pyplot realtime plotting
