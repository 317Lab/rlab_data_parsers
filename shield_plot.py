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
lock_axes = True # whether to lock all horizontal axes
index_plot = False # plot against index instead of time
scatter_plot = True # whether to do a scatter or line plot
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
t_scale = 1.e-6; a_scale = 4./2**15; m_scale = 1./2**15; g_scale = 2000./360/2**15; p_scale = 5./2**14 # data scales
sentinels = ['0x232353','0x232349','0x232354','0x23234A'] # ['##S','##I','##T','##J']
sentinel_size = 3

num_samples = 28 # how many samples per pip per sweep message
num_swp_bytes = 4 + 1 + num_samples * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
num_msg_bytes = (2*sentinel_size + num_swp_bytes + num_imu_bytes)*dim

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
def parse_swp(byte_ids,is_buffer_data):
    pos = 0
    id = int(is_buffer_data)
    for ind in byte_ids: # sweep indeces
        next_sentinel = bytes[ind+(num_swp_bytes+sentinel_size)*8:ind+(num_swp_bytes+2*sentinel_size)*8]
        #print(next_sentinel)
        if next_sentinel in sentinels: # double sentinel match insures full message available
       #print("found sentinel")
            swp_bytes = bytes[ind+sentinel_size*8:ind+(num_swp_bytes+sentinel_size)*8]
            #print(swp_bytes)
            pip0_bytes = swp_bytes[5*8:(5+2*num_samples)*8]
            pip1_bytes = swp_bytes[(5+2*num_samples)*8:]
            #print(pip0_bytes)
            #print(pip1_bytes)
            swp_time_tmp = swp_bytes[0:4*8].uintle*t_scale
            payload_id_tmp = swp_bytes[4*8:5*8].uintle
            for sample in range(0,2*num_samples,2): # allocate all sweep samples to arrays
                swp_time[id,pos] = swp_time_tmp + sample/num_samples/freq/2# copy static data for each sample
                payload_id[id,pos] = payload_id_tmp
                volts[id,0,pos] = pip0_bytes[sample*8:(sample+2)*8].uintle*p_scale
                volts[id,1,pos] = pip1_bytes[sample*8:(sample+2)*8].uintle*p_scale
                pos += 1

def parse_imu(byte_ids,is_buffer_data):
    pos = 0
    id = int(is_buffer_data)
    for ind in byte_ids: # imu indices
        next_sentinel = bytes[ind+(num_imu_bytes+sentinel_size)*8:ind+(num_imu_bytes+2*sentinel_size)*8]
        if next_sentinel in sentinels:
            imu_bytes = bytes[ind+sentinel_size*8:ind+(num_imu_bytes+sentinel_size)*8]
            imu_time[id,pos] = imu_bytes[0:4*8].uintle*t_scale
            acc[id,0,pos] = imu_bytes[4  *8:6  *8].intle*a_scale
            acc[id,1,pos] = imu_bytes[6  *8:8  *8].intle*a_scale
            acc[id,2,pos] = imu_bytes[8  *8:10 *8].intle*a_scale
            mag[id,0,pos] = imu_bytes[10 *8:12 *8].intle*m_scale
            mag[id,1,pos] = imu_bytes[12 *8:14 *8].intle*m_scale
            mag[id,2,pos] = imu_bytes[14 *8:16 *8].intle*m_scale
            gyr[id,0,pos] = imu_bytes[16 *8:18 *8].intle*g_scale
            gyr[id,1,pos] = imu_bytes[18 *8:20 *8].intle*g_scale
            gyr[id,2,pos] = imu_bytes[20 *8:22 *8].intle*g_scale
            pos += 1
swp_difs = []
for i in range(0,len(ids_swp)-1):
    swp_difs.append(ids_swp[i+1]-ids_swp[i])
swp_difs_vals = []
for i in range(0,len(swp_difs)):
    if not swp_difs[i] in swp_difs_vals:
        swp_difs_vals.append(swp_difs[i])
dif_dict = {}
for val in swp_difs_vals:
    dif_dict[val] = swp_difs.count(val)
print(dif_dict)
parse_swp(ids_swp,False)
parse_imu(ids_imu,False)
if buffered:
    parse_swp(ids_swp_buf,True)
    parse_imu(ids_imu_buf,True)
            
# find invalid timestamps
inv_ids_swp = (swp_time==0) | (swp_time>max_time)
inv_ids_imu = (imu_time==0) | (imu_time>max_time)

# measured values
imu_cad = np.diff(imu_time,append=np.nan)*1e3 # imu cadence in ms
imu_cad_avg = np.nanmedian(imu_cad)
imu_freq = 1e3/imu_cad_avg # imu frequency in Hz
pip0_std = np.nanstd(volts[0,0,:-100])*1e3 # pip 0 standard deviation
pip1_std = np.nanstd(volts[0,1,:-100])*1e3 # pip 1 standard deviation

fig.subplots_adjust(hspace=0)
lw = 1 # line width
fs = 8 # font size
plt.rcParams.update({'font.size': fs})
lbl_swp = 'SWEEP TIME SINCE SHIELD POWER [s]'
lbl_imu = 'IMU TIME SINCE SHIELD POWER [s]'

if index_plot:
    lbl_swp = 'SWEEP INDEX'
    lbl_imu = 'IMU INDEX'
    swp_time[0] = np.arange(len(swp_time[0]))
    imu_time[0] = np.arange(len(imu_time[0]))
    if buffered:
        swp_time[1] = np.arange(len(swp_time[1]))
        imu_time[1] = np.arange(len(imu_time[1]))
    if lock_axes:
        lbl_imu = 'IMU INDEX x NUM_SAMPLES'
        imu_time = imu_time*num_samples
else:
    lbl_swp = 'SWEEP TIME SINCE SHIELD POWER [s]'
    lbl_imu = 'IMU TIME SINCE SHIELD POWER [s]'

# remove invalid timestamps
swp_time[inv_ids_swp] = np.nan
imu_time[inv_ids_imu] = np.nan

# plot
def plot_data(ax,x,y,lw,xlabel,ylabel,xticks_off):
    ylim0 = np.nanquantile(y.flatten(),0.1)
    ylim1 = np.nanquantile(y.flatten(),0.9)
    ylim_offset = 2*(ylim1-ylim0)
    # ylim_avg = np.nanmedian(y.flatten())
    # ylim_rng = 0.5*np.nanstd(y.flatten())
    ax.clear()
    if np.shape(y)[0] != 3:
        if scatter_plot:
            ax.scatter(x,y,s=lw)
        else:
            ax.plot(x,y,linewidth=lw)
    else:
        for yy in y:
            if scatter_plot:
                ax.scatter(x,yy,s=lw)
            else:
                ax.plot(x,yy,linewidth=lw)
    ax.set_xlabel(xlabel,fontsize=fs)
    ax.set_ylabel(ylabel,fontsize=fs)
    ax.grid()
    ax.ticklabel_format(useOffset=False)
    ax.set_ylim(ylim0-ylim_offset,ylim1+ylim_offset)
    if xticks_off:
        ax.xaxis.set_ticklabels([])

plot_data(ax0,imu_time[0],acc[0],lw,lbl_imu,'ACC [g]',0)
ax0.xaxis.tick_top()
ax0.xaxis.set_label_position('top')
plot_data(ax1,imu_time[0],mag[0],lw,'','MAG [G]',1)
plot_data(ax2,imu_time[0],gyr[0],lw,'','GYR [Hz]',1)
plot_data(ax3,imu_time[0,:-2],imu_cad[0,:-2],lw,'','CAD [ms]',1)
plot_data(ax4,swp_time[0],volts[0,0],lw/2,'','P0 [V]',1)
plot_data(ax5,swp_time[0],volts[0,1],lw/2,lbl_swp,'P1 [V]',0)
ax5.text(0.0*dim,-0.8, 'ID: ' + str(payload_id[0,0]), transform=ax5.transAxes)
ax5.text(0.1*dim,-0.8, '$2\sigma_0$: {0:.1f} mV'.format(2*pip0_std), transform=ax5.transAxes)
ax5.text(0.3*dim,-0.8, '$2\sigma_1$: {0:.1f} mV'.format(2*pip1_std), transform=ax5.transAxes)
ax5.text(0.5*dim,-0.8, 'CAD: {0:.1f} ms'.format(imu_cad_avg), transform=ax5.transAxes)

if buffered:
    plot_data(ax0b,imu_time[1],acc[0],lw,lbl_imu,'',0)
    ax0b.xaxis.tick_top()
    ax0b.xaxis.set_label_position('top')
    plot_data(ax1b,imu_time[1],mag[1],lw,'','',1)
    plot_data(ax2b,imu_time[1],gyr[1],lw,'','',1)
    plot_data(ax3b,imu_time[1,:-2],imu_cad[0,:-2],lw,'','',1)
    plot_data(ax4b,swp_time[1],volts[1,0],lw/2,'','',1)
    plot_data(ax5b,swp_time[1],volts[1,1],lw/2,lbl_swp,'',0)
plt.show()