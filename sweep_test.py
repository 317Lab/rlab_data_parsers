import sys
import numpy as np
import matplotlib.pyplot as plt
import time

file = sys.argv[1]
do_plot = True
show_plot = False
mov_avg_win = 100
pos_slope_lim = 5000 # mV/ms
neg_slope_lim = -5000 # mV/ms

def moving_average(x, w):
    return np.convolve(x, np.ones(w+1), 'valid') / (w+1)

def slope_ids(x,y,lim):
    slopes = np.diff(y,append=np.nan)/np.diff(x,append=np.nan)
    if lim >= 0:
        slope_ids = np.asarray(slopes>lim).nonzero()[0]
    else:
        slope_ids = np.asarray(slopes<lim).nonzero()[0]
    splits = np.asarray(np.diff(slope_ids)>100).nonzero()[0]+1
    slopes_split = np.split(slope_ids,splits)
    l = len(slopes_split)
    times = np.zeros(l)
    volts = np.zeros(l)
    for i in range(l):
        times[i] = np.median(x[slopes_split[i]])
        volts[i] = np.median(y[slopes_split[i]])
    return times, volts

raw = np.genfromtxt(file, delimiter=',',skip_header=16,usecols=(0,1))
times = raw[:-mov_avg_win,0]*1e3 # s to ms
volts = moving_average(raw[:,1],mov_avg_win)*1e3 # V to mV
cad = np.median(np.diff(times))

rise_times, rise_volts =  slope_ids(times,volts,pos_slope_lim)
fall_times, fall_volts =  slope_ids(times,volts,neg_slope_lim)

time0 = rise_times[0]
time1 = rise_times[1]

step_bounds = fall_times[(fall_times>time0) & (fall_times<time1)]
num_steps = len(step_bounds)+1
steps = np.zeros([num_steps,2])
for i in range(1,num_steps-1):
    t0 = step_bounds[i-1]
    t1 = step_bounds[i]
    ids = (times>t0) & (times<t1)
    t = np.median(times[ids])
    v = np.median(volts[ids])
    steps[i,:] = [t,v]

ids_max = (times>time0) & (times<step_bounds[0])
ids_min = (times<time1) & (times>step_bounds[-1])
steps[0,:] = [np.median(times[ids_max]),np.median(volts[ids_max])]
steps[-1,:] = [np.median(times[ids_min]),np.median(volts[ids_min])]

period = time1-time0
frequency = 1e3/period
min_voltage = steps[-1,1]
max_voltage = steps[0,1]
amplitude = max_voltage - min_voltage
step_duration = np.median(np.diff(steps[1:,0]))*1e3 # skip first step
step_dur_sig = np.std(np.diff(steps[1:,0]))*1e3
step_amplitude = -np.median(np.diff(steps[:,1]))
step_amp_sig = np.std(np.diff(steps[:,1]))
print('Period = {:.2f} ms'.format(period))
print('Frequency = {:.2f} Hz'.format(frequency))
print('Min voltage = {:.0f} mV'.format(min_voltage))
print('Max voltage = {:.0f} mV'.format(max_voltage))
print('Amplitude = {:.0f} mV'.format(amplitude))
print('Number of steps = {}'.format(num_steps))
print('Step duration = {:.1f} +/- {:.1f} us'.format(step_duration,2*step_dur_sig))
print('Step amplitude = {:.0f} +/- {:.0f} mV'.format(step_amplitude,2*step_amp_sig))

if do_plot:
    plt.figure(figsize=(15,15/1.618))
    plt.plot(times,volts,label='data')
    plt.plot(rise_times,rise_volts,'o',label='rise times')
    plt.plot(fall_times,fall_volts,'o',label='fall times')
    plt.plot(steps[:,0],steps[:,1],'o',label='steps')
    plt.xlabel('time (ms)')
    plt.ylabel('signal (mV)')
    plt.legend()
    plt.title('Path = ' + file + ' , Period = {:.2f} ms , V_min = {:.2f} V , V_max = {:.2f} V'.format(period,min_voltage/1e3,max_voltage/1e3))
    plt.grid()
    plt.savefig(file[:-4]+'.png',dpi=300)
    if show_plot:
        plt.show()
    
