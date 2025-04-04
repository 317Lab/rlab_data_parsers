# plots time-corresponding buffered and non buffered data.
# Should see one line for pip, three for IMU
import matplotlib.pyplot as plt
import numpy as np

############################### Checking Buffered Data ###############################
def check_buffers(start_time, end_time, swp_time, volts, imu_time, acc, mag, gyr):
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
def get_adc_std(steps):
	stds = np.zeros(steps.shape[1])
	for i in range(steps.shape[1]):
		stds[i] = np.std(steps[:, i])
	return stds

# generate scatter plot of adc readings at every sweep step. includes average std and index of max std
def plot_adc_noise(volts):
	first_max = np.where(volts[0,0,:]==np.max(volts[0,0,:]))[0][0]
	first_min = np.where(volts[0,0,:]==np.min(volts[0,0,:]))[0][0]
	length = first_max - first_min + 1
	print(length)
	fig, ax = plt.subplots()
	steps = get_sweep_steps(volts)
	stds = get_adc_std(steps=steps)
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

        