from bitstring import BitArray
import numpy as np
import matplotlib.pyplot as plt

buffered = True # whether to plot RAM buffered data
lock_axes = True # whether to lock all horizontal axes
index_plot = False # plot against index instead of time
scatter_plot = True # whether to do a scatter or line plot
freq = 45 # approximate message frequency in Hz
max_time = 10*50*60 # sweep time word errors have t > 3000 s which are removed. MIGHT BE FIXED TBD
binary_file = "25S_data_testing/20250402T191624Z_data_COM13_230400_60.bin"

if buffered: # buffered data shown on second column of plots
    dim = 2
else:
    dim = 1

t_scale = 1.e-6; a_scale = 4./2**15; m_scale = 1./2**15; g_scale = 2000./360/2**15; p_scale = 5./2**14 # data scales
sentinels = ['0x232353','0x232349','0x232354','0x23234A'] # ['##S','##I','##T','##J']
sentinel_size = 3

num_samples = 28 # how many samples per pip per sweep message
num_swp_bytes = 4 + 1 + num_samples * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
num_msg_bytes = (2*sentinel_size + num_swp_bytes + num_imu_bytes)*dim

with open(binary_file, 'rb') as f:
    bytes = BitArray(f.read())

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
        if next_sentinel in sentinels: # double sentinel match insures full message available
            swp_bytes = bytes[ind+sentinel_size*8:ind+(num_swp_bytes+sentinel_size)*8]
            pip0_bytes = swp_bytes[5*8:(5+2*num_samples)*8]
            pip1_bytes = swp_bytes[(5+2*num_samples)*8:]
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

# remove invalid timestamps
swp_time[inv_ids_swp] = np.nan
imu_time[inv_ids_imu] = np.nan
    
# plots time-corresponding buffered and non buffered data.
# Should see one line for pip, three for IMU
def check_buffers(start_time, end_time):
    fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)

    # Pip 0 plot
    time_nonbuf = swp_time[0, :]
    time_buf = swp_time[1, :]
    nonbuf_slice = np.intersect1d(np.where(start_time <= time_nonbuf)[0], np.where(time_nonbuf <= end_time)[0])
    buf_slice = np.intersect1d(np.where(start_time <= time_buf)[0], np.where(time_buf <= end_time)[0])
    time_slice = swp_time[0, nonbuf_slice]
    axs[0].plot(time_slice, volts[0, 0, nonbuf_slice], label="not buffered")
    axs[0].plot(time_slice, volts[1, 0, buf_slice], label="buffered")
    axs[0].legend()
    axs[0].set_title(f"Sweep Data, Pip 0")
    axs[0].set_ylabel("Volts (V)")

    # pip 1 plot 
    axs[1].plot(time_slice, volts[0, 1, nonbuf_slice], label="not buffered")
    axs[1].plot(time_slice, volts[1, 1, buf_slice], label="buffered")
    axs[1].legend()
    axs[1].set_title(f"Sweep Data, Pip 1")
    axs[1].set_ylabel("Volts (V)")


    # Accelerometer plot
    time_nonbuf = imu_time[0, :]
    time_buf = imu_time[1, :]
    nonbuf_slice = np.intersect1d(np.where(start_time <= time_nonbuf)[0], np.where(time_nonbuf <= end_time)[0])
    buf_slice = np.intersect1d(np.where(start_time <= time_buf)[0], np.where(time_buf <= end_time)[0])
    time_slice = imu_time[0, nonbuf_slice]
    for axis in range(3):
        axs[4].plot(time_slice, acc[0, axis, nonbuf_slice], label=f"{['x','y','z'][axis]}, non-buf")
        axs[4].plot(time_slice, acc[1, axis, buf_slice], label=f"{['x','y','z'][axis]}, buf")
    axs[4].legend()
    axs[4].set_title("Acceleration")
    axs[4].set_ylabel("g")
    axs[4].set_xlabel("Time (s)")

    # Magnetometer plot
    for axis in range(3):
        axs[2].plot(time_slice, mag[0, axis, nonbuf_slice], label=f"{['x','y','z'][axis]}, non-buf")
        axs[2].plot(time_slice, mag[1, axis, buf_slice], label=f"{['x','y','z'][axis]}, buf")
    axs[2].legend()
    axs[2].set_title("Magnetic Field")
    axs[2].set_ylabel("MAG (G)")

    # Gyroscope plot
    for axis in range(3):
        axs[3].plot(time_slice, gyr[0, axis, nonbuf_slice], label=f"{['x','y','z'][axis]}, non-buf")
        axs[3].plot(time_slice, gyr[1, axis, buf_slice], label=f"{['x','y','z'][axis]}, buf")
    axs[3].legend()
    axs[3].set_title("Gyroscope")
    axs[3].set_ylabel("GYR (Hz)")

    plt.tight_layout()
    plt.show()

    

start_time = 40
end_time = 40 + (5/freq)

# check_mag_buf(start_time=start_time,end_time=end_time)
check_buffers(start_time=start_time,end_time=end_time)

