import sys
import serial
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# parameters
numSampleBytes = 28 # How many samples per message
numSweepBytes = 4 + 1 + numSampleBytes * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
numIMUBytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
tScale = 1.e-6; aScale = 4*9.8/2**15; mScale = 1./2**15; gScale = 2000./360/2**15; pScale = 5/2**14 # data scales
freq = 45 # Set data frequency in Hz
plotTime = 3 # Time to plot for in seconds

# opening data port/file
port = sys.argv[1]
baud = 230400
if len(sys.argv)==3: # optional suffix argument
    suffix = '_' + sys.argv[2]
else:
    suffix = ''
ser = serial.Serial(port, baud, timeout=None) # timeout off, wait until all bytes are read
ser.reset_input_buffer() # flush serial port
fn = datetime.now().strftime("%Y%m%dT%H%M%S") + '_data_' + port.split('.')[-1] + '_' + str(baud) + suffix + '.bin'
f = open(fn,'ab')
fig, axs = plt.subplots(6, 1, figsize=(16,9))

# for closing on figure exit
plotting = True
def on_close(event):
    global plotting 
    plotting = False

def conc(word):
    if len(word) == 2:
        return (word[1]<<8) | word[0]
    if len(word) == 4:
        return (word[3]<<24) | (word[2]<<16) | (word[1]<<8) | word[0]

while plotting:
    rawBytes = ser.read(plotTime*freq*(numSweepBytes+numIMUBytes+2)) # N seconds worth of bytes
    f.write(rawBytes)
    numBytes = len(rawBytes)

    sweepTime = [] # need to change this to preallocated arrays numpy concatenate start to nparray
    payloadID = []
    pip0Voltages = []
    pip1Voltages = []
    IMUTime = []
    ax = []; ay = []; az = [] 
    mx = []; my = []; mz = []
    gx = []; gy = []; gz = []
    IMUTemp = []

    for i in range(numBytes-numSweepBytes-2):
        if rawBytes[i] == 35: # byte is #: start of data
            if rawBytes[i+1] == 83: # byte is "S": start of sweep data
                if i+numSweepBytes+2 <= numBytes:
                    if rawBytes[i+numSweepBytes+2] == 35: # next "#" correct number of sweep bytes
                        sweepBytes = rawBytes[i+2:i+numSweepBytes+2]
                        pip0Bytes = sweepBytes[5:5+2*numSampleBytes]
                        pip1Bytes = sweepBytes[5+2*numSampleBytes:]
                        for sample in range(0,2*numSampleBytes,2):
                            sweepTime.append(conc(sweepBytes[0:4])) # copy for each sample
                            payloadID.append(sweepBytes[4])
                            pip0Voltages.append(conc(pip0Bytes[sample:sample+2]))
                            pip1Voltages.append(conc(pip1Bytes[sample:sample+2]))
            elif rawBytes[i+1] == 73: # byte is "I": start of IMU data
                if i+numIMUBytes+2 <= numBytes:
                    if rawBytes[i+numIMUBytes+2] == 35: # next "#" correct number of IMU bytes
                        IMUBytes = rawBytes[i+2:i+numIMUBytes+2]
                        IMUTime.append(conc(IMUBytes[0:4]))
                        ax.append(conc(IMUBytes[4:6]))
                        ay.append(conc(IMUBytes[6:8]))
                        az.append(conc(IMUBytes[8:10]))
                        mx.append(conc(IMUBytes[10:12]))
                        my.append(conc(IMUBytes[12:14]))
                        mz.append(conc(IMUBytes[14:16]))
                        gx.append(conc(IMUBytes[16:18]))
                        gy.append(conc(IMUBytes[18:20]))
                        gz.append(conc(IMUBytes[20:22]))
                        IMUTemp.append(conc(IMUBytes[22:24]))

    # Converting bytes and scaling data
    sweepTime = np.array(sweepTime, dtype='uint32')*tScale
    payloadID = np.array(payloadID, dtype='uint8')
    pip0Voltages = np.array(pip0Voltages, dtype='int16')*pScale
    pip1Voltages = np.array(pip1Voltages, dtype='int16')*pScale
    IMUTime = np.array(IMUTime, dtype='uint32')*tScale
    ax = np.array(ax, dtype='int16')*aScale; ay = np.array(ay, dtype='int16')*aScale; az = np.array(az, dtype='int16')*aScale
    mx = np.array(mx, dtype='int16')*mScale; my = np.array(my, dtype='int16')*mScale; mz = np.array(mz, dtype='int16')*mScale
    gx = np.array(gx, dtype='int16')*mScale; gy = np.array(gy, dtype='int16')*mScale; gz = np.array(gz, dtype='int16')*mScale
    IMUTemp = np.array(IMUTemp, dtype='int16')

    IMUCad = np.diff(IMUTime)*1e3
    IMUCad = np.append(IMUCad,IMUCad[-1]) # make array same length
    pip0rms = np.sqrt(np.mean(np.square(pip0Voltages)))*1e3
    pip1rms = np.sqrt(np.mean(np.square(pip1Voltages)))*1e3

    # Plotting
    fig.canvas.mpl_connect('close_event', on_close) # exit loop when closing figure
    fig.subplots_adjust(hspace=0)
    
    axs[0].clear()
    axs[0].plot(IMUTime,ax)
    axs[0].plot(IMUTime,ay)
    axs[0].plot(IMUTime,az)
    axs[0].set_ylabel('ACC [g]')
    axs[0].grid()
    axs[0].set_xlabel('IMU TIME SINCE SHIELD POWER [s]')
    axs[0].xaxis.tick_top()
    axs[0].xaxis.set_label_position('top')
    axs[0].text(0.9, 1.5, 'SHIELD ID: ' + str(payloadID[1]), transform=axs[0].transAxes)

    axs[1].clear()
    axs[1].plot(IMUTime,mx)
    axs[1].plot(IMUTime,my)
    axs[1].plot(IMUTime,mz)
    axs[1].set_ylabel('MAG [G]')
    axs[1].grid()
    axs[1].xaxis.set_ticklabels([])

    axs[2].clear()
    axs[2].plot(IMUTime,gx)
    axs[2].plot(IMUTime,gy)
    axs[2].plot(IMUTime,gz)
    axs[2].set_ylabel('GYR [Hz]')
    axs[2].grid()
    axs[2].xaxis.set_ticklabels([])

    axs[3].clear()
    axs[3].plot(IMUTime,IMUCad)
    axs[3].set_ylabel('CAD [ms]')
    axs[3].grid()
    axs[3].ticklabel_format(useOffset=False)
    axs[3].xaxis.set_ticklabels([])

    axs[4].clear()
    axs[4].plot(sweepTime[1:],pip0Voltages[1:])
    axs[4].set_ylabel('P0 [V]')
    axs[4].grid()
    axs[4].xaxis.set_ticklabels([])

    axs[5].clear()
    axs[5].plot(sweepTime[1:],pip1Voltages[1:])
    axs[5].set_ylabel('P1 [V]')
    axs[5].grid()
    axs[5].set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]')
    axs[5].text(-0.1, -0.5, 'P0 RMS: ' + "{0:.1f}".format(pip0rms) + ' mV', transform=axs[5].transAxes)
    axs[5].text(-0.1, -0.7, 'P1 RMS: ' + "{0:.1f}".format(pip1rms) + ' mV', transform=axs[5].transAxes)

    plt.pause(0.1)

plt.show()
f.close()