# Shield data file plotter.
# Example usages:
#   cat YYYYMMDDThhmmssZ_data_<port>_<baud>_<suffix>_<id>.bin | python shield_plot.py
# Known issues:
#   - possible false postive sentinel matches when higher order bytes for steady data are 0x23.
#       - E.g. when pip voltage 2.7 - 2.8 V or timestamp is ~ 9 or 20 minutes.
#       - 3-byte sentinels are needed.
# Contact: jules.van.irsel.gr@dartmouth.edu

import sys
from bitstring import BitArray
import numpy as np
import matplotlib.pyplot as plt

# user settings
buffered = True # whether to plot RAM buffered data
lock_axes = True # whether to lock all x axes
freq = 45 # approximate message frequency in Hz
max_time = 10*50*60 # sweep time word errors have t > 3000 s which are removed. MIGHT BE FIXED TBD

# initialize figure + axes
if buffered: # buffered data shown on second column of plots
    fig, axs = plt.subplots(6, 2, figsize=(8,6), sharex=lock_axes)
    ax0 = axs[0,0]; ax1 = axs[1,0]; ax2 = axs[2,0]
    ax3 = axs[3,0]; ax4 = axs[4,0]; ax5 = axs[5,0]
    ax0b = axs[0,1]; ax1b = axs[1,1]; ax2b = axs[2,1]
    ax3b = axs[3,1]; ax4b = axs[4,1]; ax5b = axs[5,1]
    dim = 2
else:
    fig, axs = plt.subplots(6, 1, figsize=(8,6), sharex=lock_axes)
    ax0 = axs[0]; ax1 = axs[1]; ax2 = axs[2]
    ax3 = axs[3]; ax4 = axs[4]; ax5 = axs[5]
    dim = 1

# parameters
num_samples = 28 # how many samples per pip per sweep message
num_swp_bytes = 4 + 1 + num_samples * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
num_msg_bytes = (2 + num_swp_bytes + 2 + num_imu_bytes)*dim

t_scale = 1.e-6; a_scale = 4./2**15; m_scale = 1./2**15; g_scale = 2000./360/2**15; p_scale = 5./2**14 # data scales
sentinels = ['0x2353','0x2349','0x2354','0x234A'] # ['#S','#I','#T','#J']

bytes = BitArray(sys.stdin.buffer.read(-1)) # read bytes from standard input
ids_swp = list(bytes.findall(sentinels[0], bytealigned=False))
ids_imu = list(bytes.findall(sentinels[1], bytealigned=False))
if buffered:
    ids_swp_buf = list(bytes.findall(sentinels[2], bytealigned=False))
    ids_imu_buf = list(bytes.findall(sentinels[3], bytealigned=False))
else:
    ids_swp_buf = ids_swp
    ids_imu_buf = ids_imu
num_dat_swp = max(len(ids_swp),len(ids_swp_buf))*num_samples # sweep data is repeated per sweep sample
num_dat_imu = max(len(ids_imu),len(ids_imu_buf))

# initialize data arrays
swp_time = np.zeros([dim,num_dat_swp],dtype='single')
payload_id = np.zeros([dim,num_dat_swp],dtype='uint8')
volts = np.zeros([dim,2,num_dat_swp],dtype='single')
imu_time = np.zeros([dim,num_dat_imu],dtype='single')
acc = np.zeros([dim,3,num_dat_imu],dtype='single')
mag = np.zeros([dim,3,num_dat_imu],dtype='single')
gyr = np.zeros([dim,3,num_dat_imu],dtype='single')

# parse data
pos = 0
for ind in ids_swp: # sweep indeces
    next_sentinel = bytes[ind+(num_swp_bytes+2)*8:ind+(num_swp_bytes+2+2)*8]
    ### TEMP FIX UNTIL 3-BYTE SENTINELS ARE USED
    next_next_sentinel = bytes[ind+(num_swp_bytes+num_imu_bytes+4)*8:ind+(num_swp_bytes+num_imu_bytes+4+2)*8] # TEMP FIX
    # if next_sentinel in sentinels: # double sentinel match insures full message available
    if (next_sentinel in sentinels) and (next_next_sentinel in sentinels): # triple sentinel match insures full message available TEMP FIX
        swp_bytes = bytes[ind+2*8:ind+(num_swp_bytes+2)*8]
        pip0_bytes = swp_bytes[5*8:(5+2*num_samples)*8]
        pip1_bytes = swp_bytes[(5+2*num_samples)*8:]
        swp_time_tmp = swp_bytes[0:4*8].uintle*t_scale
        payload_id_tmp = swp_bytes[4*8:5*8].uintle
        for sample in range(0,2*num_samples,2): # allocate all sweep samples to arrays
            swp_time[0,pos] = swp_time_tmp + sample/num_samples/freq/2# copy static data for each sample
            payload_id[0,pos] = payload_id_tmp
            volts[0,0,pos] = pip0_bytes[sample*8:(sample+2)*8].uintle*p_scale
            volts[0,1,pos] = pip1_bytes[sample*8:(sample+2)*8].uintle*p_scale
            pos += 1

pos = 0
for ind in ids_imu: # imu indices
    next_sentinel = bytes[ind+(num_imu_bytes+2)*8:ind+(num_imu_bytes+2+2)*8]
    next_next_sentinel = bytes[ind+(2*num_imu_bytes+4)*8:ind+(2*num_imu_bytes+4+2)*8] # TEMP FIX
    # if next_sentinel in sentinels:
    if (next_sentinel in sentinels) and (next_next_sentinel in sentinels): # TEMP FIX
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
        next_next_sentinel = bytes[ind+(2*num_swp_bytes+4)*8:ind+(2*num_swp_bytes+4+2)*8] # TEMP FIX
        # if next_sentinel in sentinels:
        if (next_sentinel in sentinels) and (next_next_sentinel in sentinels): # TEMP FIX
            swp_bytes = bytes[ind+2*8:ind+(num_swp_bytes+2)*8]
            pip0_bytes = swp_bytes[5*8:(5+2*num_samples)*8]
            pip1_bytes = swp_bytes[(5+2*num_samples)*8:]
            swp_time_tmp = swp_bytes[0:4*8].uintle*t_scale
            payload_id_tmp = swp_bytes[4*8:5*8].uintle
            for sample in range(0,2*num_samples,2):
                swp_time[1,pos] = swp_time_tmp + sample/num_samples/freq/2
                payload_id[1,pos] = payload_id_tmp
                volts[1,0,pos] = pip0_bytes[sample*8:(sample+2)*8].uintle*p_scale
                volts[1,1,pos] = pip1_bytes[sample*8:(sample+2)*8].uintle*p_scale
                pos += 1

    pos = 0
    for ind in ids_imu_buf: # buffered imu indeces
        next_sentinel = bytes[ind+(num_imu_bytes+2)*8:ind+(num_imu_bytes+2+2)*8]
        next_next_sentinel = bytes[ind+(num_imu_bytes+num_swp_bytes+4)*8:ind+(num_imu_bytes+num_swp_bytes+4+2)*8] # TEMP FIX
        # if next_sentinel in sentinels:
        if (next_sentinel in sentinels) and (next_next_sentinel in sentinels): # TEMP FIX
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

# measured values
imu_cad = np.diff(imu_time,append=np.nan)*1e3 # imu cadence in ms
imu_cad_avg = np.nanmean(imu_cad)
imu_freq = 1e3/imu_cad_avg # imu frequency in Hz
pip0_std = np.nanstd(volts[0,0])*1e3 # pip 0 standard deviation
pip1_std = np.nanstd(volts[0,1])*1e3 # pip 1 standard deviation

fig.subplots_adjust(hspace=0)
lw = 1 # line width
fs = 8 # font size
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
middle = np.nanmean(volts[0,0])

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

plt.show()