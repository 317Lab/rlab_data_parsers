# plots time-corresponding buffered and non buffered data.
# Should see one line for pip, three for IMU
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from recordclass import recordclass, RecordClass


############################### Checking Buffered Data ###############################
def find_consecutive_block(indices, length):
    for i in range(len(indices) - length + 1):
        window = indices[i:i+length]
        if window[-1] - window[0] == length - 1:
            return window
    return None  

def good_slices(time, is_sweep=True):
    if is_sweep:
        num_steps = 28
    else:
        num_steps = 1
    for i in range(10,1,-1):
        time_buf = time[1, :]
        time_nonbuf = time[0, :]
        #nonzeros = time_nonbuf[np.where(time_nonbuf != 0)[0]]
        time_step = np.median(np.diff(time[0,:]))

        mask = (np.abs(np.diff(time[0,:])) <= 2*time_step) & (np.abs(np.diff(time[1,:])) <= 2*time_step)
        good_idx = np.where(mask)[0]
        nonbuf_slice = find_consecutive_block(good_idx, i*num_steps)
        start_time = time[0, nonbuf_slice[0]]
        end_time = time[0, nonbuf_slice[-1]]
        buf_slice = np.intersect1d(np.where(start_time <= time_buf)[0], np.where(time_buf <= end_time)[0])
        if len(buf_slice)==len(nonbuf_slice):
            return nonbuf_slice, buf_slice, start_time, end_time
    return None, None

def check_buffers(swp_time, volts, imu_time, acc, mag, gyr, save=False, save_path=None):
    fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
    buf_slice, nonbuf_slice, start_time, end_time = good_slices(swp_time)
    time_slice = swp_time[0,nonbuf_slice]
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
    nonbuf_slice = np.where((imu_time[0,:]>=start_time)&(imu_time[0,:]<=end_time))[0]
    buf_slice = np.where((imu_time[1,:]>=start_time)&(imu_time[1,:]<=end_time))[0]
    if len(nonbuf_slice)!=len(buf_slice):
        min_len = min(len(nonbuf_slice), len(buf_slice))
        nonbuf_slice = nonbuf_slice[:min_len]
        buf_slice = buf_slice[:min_len]
    time_slice=imu_time[0,nonbuf_slice]
    time_slice=imu_time[0,buf_slice]
    # Accelerometer plot
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
    if save:
        plt.savefig(save_path)
    else:
        plt.show()

    
############################### Checking Noise ###############################

# gets every nth element of a length x chunk of arr
def get_nth(arr, n, x):
    arr = arr[:len(arr) - len(arr) % x]  # Trim to full chunks
    reshaped = arr.reshape(-1, x)
    return reshaped[:, n]

# put each nth sweep step from every sweep into a column of a 2D array
def get_sweep_steps(volts):
	first_max = np.where(volts[0,0,:]==np.max(volts[0,0,:]))[0][0]
	first_min = np.where(volts[0,0,:]==np.min(volts[0,0,:]))[0][0]
	length = first_max - first_min + 1
	# ceiling to account for padding
	new_height = int(np.ceil(len(volts[0, 0, :]) / length))
	steps = np.zeros((new_height, length))

	# fill each column with every nth sample
	for i in range(length):
		steps[:, i] = get_nth(volts[0, 0, :], i, length)

	# drop trailing zero row
	if steps[-1, -1] == 0.0:
		steps = np.delete(steps, -1, axis=0)
	return steps

# return an array of the standard deviation at every step
def get_step_std(steps):
	stds = np.zeros(steps.shape[1])
	for i in range(steps.shape[1]):
		stds[i] = np.std(steps[:, i])
	return stds

# generate scatter plot of adc readings at every sweep step. includes average std and index of max std
def show_step_noise(volts):
	first_max = np.where(volts[0,0,:]==np.max(volts[0,0,:]))[0][0]
	first_min = np.where(volts[0,0,:]==np.min(volts[0,0,:]))[0][0]
	length = first_max - first_min + 1
	print(length)
	fig, ax = plt.subplots()
	steps = get_sweep_steps(volts)
	stds = get_step_std(steps=steps)
	ax.text(0.15, 0.9, f"Avg Std: {np.round(np.mean(stds),5)}", fontsize=10, ha='center', va='center', transform=ax.transAxes)
	ax.text(0.15, 0.8, f"Max Std: Step {np.where(np.max(stds)==stds)[0][0]+1}", fontsize=10, ha='center', va='center', transform=ax.transAxes)
	for i in range(length):
		plt.scatter([i+1] * steps.shape[0], steps[:, i], alpha=0.5, s=5, label=f"Step {i+1}" if i < 10 else None)
	ax.set_xlim(ax.get_xlim())
	ax.autoscale(enable=True, axis='y')
	ticks = np.unique(np.concatenate(([1], np.arange(4, length + 1, 4))))
	ax.set_xticks(ticks)
	plt.xlabel("Sweep step")
	plt.ylabel("Volts (V)")
	plt.title("ADC reading distribution at each step of sweep")
	plt.show()

    
# Mutable struct for storing data from DC voltage noise tests on the ADC
class DCTest(RecordClass):
    test_id: int
    voltages: np.ndarray
    resistor_reading: float
    supply_voltage: float
    start: float = 0.0
    end: float = 5
    counts : np.ndarray = None
    bins : np.ndarray = None
    std : float = None
      
# takes a list of DCTest objects and shows the histogram of voltages for each test
def show_dc_noise(tests):
    if not all(isinstance(i, DCTest) for i in tests):
        raise TypeError("All elements in tests must be of type DCTest")
    for i in tests:
        i.std = np.std(i.voltages)
        i.start = np.mean(i.voltages)-0.015
        i.end = np.mean(i.voltages)+0.015
        i.counts, i.bins = np.histogram(i.voltages, range=(i.start,i.end), bins=100)
    fig, axs = plt.subplots(len(tests))
    fig.suptitle("DC Noise Tests")
    for i, test in enumerate(tests):
        axs[i].stairs(test.counts, test.bins)
        axs[i].set_title(f"Supply Voltage {test.supply_voltage} V, Resistor Voltage {test.resistor_reading} V")
        axs[i].set_xlim(test.start, test.end)
        axs[i].set_xlabel("ADC Reading (V)")
        axs[i].set_ylabel("# of Samples")
        axs[i].set_xticks(np.arange(test.start, test.end, 0.002))
        axs[i].xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        axs[i].text(0.02,0.8, f"Std: {test.std:.3f}", fontsize=10, transform=axs[i].transAxes)
    plt.subplots_adjust(hspace=0.7)
    plt.show()