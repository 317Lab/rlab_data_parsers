# Data collection + realtime parsing & plotting of SHIELD housekeeping and PIP data
# Updated version for python 3 or higher
# Arguments: 1) Portname, 2) Data filename suffix (Optional)
# To exit, simply close the plotting window
# Contact: jules.van.irsel.gr@dartmouth.edu

import sys
import os
import serial
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time

# parameters
numSamples = 28 # how many samples per message
numSWPBytes = 4 + 1 + numSamples * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
numIMUBytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
tScale = 1.e-6; aScale = 4*9.8/2**15; mScale = 1./2**15; gScale = 2000./360/2**15; pScale = 5/2**14 # data scales
freq = 45 # set data frequency in Hz
plotTime = 3 # time to plot for in seconds
numBytesTarget = plotTime*freq*(numSWPBytes+numIMUBytes+2) # N seconds worth of bytes

# opening data port/file
port = sys.argv[1]
baud = 230400
if len(sys.argv)==3: # optional suffix argument
    suffix = '_' + sys.argv[2]
else:
    suffix = ''
ser = serial.Serial(port, baud, timeout=600) # wait until all bytes are read or x seconds pass
ser.reset_input_buffer() # flush serial port
fn = datetime.now().strftime("%Y%m%dT%H%M%S") + '_data_' + port.split('.')[-1] + '_' + str(baud) + suffix + '.bin'
f = open(fn,'ab')
fig, axs = plt.subplots(6, 1, figsize=(16,9))

# for closing on figure exit
plotting = True
def on_close(event):
    global plotting 
    plotting = False

# concatenate multiple bytes
def conc(word):
    if len(word) == 2:
        return (word[1]<<8) | word[0]
    if len(word) == 4:
        return (word[3]<<24) | (word[2]<<16) | (word[1]<<8) | word[0]

while plotting:
    rawBytes = ser.read(numBytesTarget)
    f.write(rawBytes)
    numBytes = len(rawBytes)
    if numBytes == 0: # end recording if no bytes after timeout
        print('No data after serial timeout',flush=True)
        break
    elif numBytes == numBytesTarget:
        ser.timeout = plotTime*10 # shorten timeout after initial message capture
        numDataSWP = round(plotTime*freq*numSamples*2.5) # add 250% for safety
        numDataIMU = round(plotTime*freq*2.5)

        # pre-allocate arrays of maximum possible sizes
        SWPTime = np.zeros(numDataSWP,dtype='uint32') # unsigned 4 bytes
        payloadID = np.zeros(numDataSWP,dtype='uint8') # unsigned 1 byte
        pip0Voltages = np.zeros(numDataSWP,dtype='int16') # signed 2 bytes
        pip1Voltages = np.zeros(numDataSWP,dtype='int16')
        IMUTime = np.zeros(numDataIMU,dtype='uint32')
        ax = np.zeros(numDataIMU,dtype='int16'); ay = np.zeros(numDataIMU,dtype='int16'); az = np.zeros(numDataIMU,dtype='int16') 
        mx = np.zeros(numDataIMU,dtype='int16'); my = np.zeros(numDataIMU,dtype='int16'); mz = np.zeros(numDataIMU,dtype='int16')
        gx = np.zeros(numDataIMU,dtype='int16'); gy = np.zeros(numDataIMU,dtype='int16'); gz = np.zeros(numDataIMU,dtype='int16')
        IMUTemp = np.zeros(numDataIMU,dtype='int16')

        posSWP = 0 # position in respective arrays
        posIMU = 0
        for i in range(numBytes-numSWPBytes-2): # scan through rawBytes
            if rawBytes[i] == 35: # byte is "#": start of data message
                if rawBytes[i+1] == 83: # byte is "S": start of sweep data
                    if i+numSWPBytes+2 <= numBytes: # full message is available
                        if rawBytes[i+numSWPBytes+2] == 35: # next "#" indicates correct number of sweep bytes
                            SWPBytes = rawBytes[i+2:i+numSWPBytes+2] # collect appropriate bytes
                            pip0Bytes = SWPBytes[5:5+2*numSamples]
                            pip1Bytes = SWPBytes[5+2*numSamples:]
                            for sample in range(0,2*numSamples,2): # allocate all sweep samples to arrays
                                SWPTime[posSWP] = conc(SWPBytes[0:4]) # copy static data for each sample
                                payloadID[posSWP] = SWPBytes[4]
                                pip0Voltages[posSWP] = conc(pip0Bytes[sample:sample+2])
                                pip1Voltages[posSWP] = conc(pip1Bytes[sample:sample+2])
                                posSWP += 1
                elif rawBytes[i+1] == 73: # byte is "I": start of IMU data
                    if i+numIMUBytes+2 <= numBytes: # full message is available
                        if rawBytes[i+numIMUBytes+2] == 35: # next "#" indicates correct number of IMU bytes
                            IMUBytes = rawBytes[i+2:i+numIMUBytes+2] # collect appropriate bytes
                            IMUTime[posIMU] = conc(IMUBytes[0:4])
                            ax[posIMU] = conc(IMUBytes[4:6])
                            ay[posIMU] = conc(IMUBytes[6:8])
                            az[posIMU] = conc(IMUBytes[8:10])
                            mx[posIMU] = conc(IMUBytes[10:12])
                            my[posIMU] = conc(IMUBytes[12:14])
                            mz[posIMU] = conc(IMUBytes[14:16])
                            gx[posIMU] = conc(IMUBytes[16:18])
                            gy[posIMU] = conc(IMUBytes[18:20])
                            gz[posIMU] = conc(IMUBytes[20:22])
                            IMUTemp[posIMU] = conc(IMUBytes[22:24])
                            posIMU += 1

        print('# of sweep data: ',posSWP,flush=True)
        print('# of IMU data: ',posIMU,flush=True)
        # Converting bytes and scaling data
        SWPTime = SWPTime[0:posSWP]*tScale # chop off unused zeros
        payloadID = payloadID[0:posSWP]
        pip0Voltages = pip0Voltages[0:posSWP]*pScale
        pip1Voltages = pip1Voltages[0:posSWP]*pScale
        IMUTime = IMUTime[0:posIMU]*tScale
        ax = ax[0:posIMU]*aScale; ay = ay[0:posIMU]*aScale; az = az[0:posIMU]*aScale
        mx = mx[0:posIMU]*mScale; my = my[0:posIMU]*mScale; mz = mz[0:posIMU]*mScale
        gx = gx[0:posIMU]*mScale; gy = gy[0:posIMU]*mScale; gz = gz[0:posIMU]*mScale
        IMUTemp = IMUTemp[0:posIMU]

        IMUCad = np.diff(IMUTime)*1e3
        IMUCad = np.append(IMUCad,IMUCad[-1]) # make array same length
        pip0rms = np.sqrt(np.mean(np.square(pip0Voltages-np.mean(pip0Voltages))))*1e3 # determine rms
        pip1rms = np.sqrt(np.mean(np.square(pip1Voltages-np.mean(pip1Voltages))))*1e3
        pip0std = np.std(pip0Voltages)*1e3 # determine standard deviation
        pip1std = np.std(pip1Voltages)*1e3

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
        axs[4].plot(SWPTime[1:],pip0Voltages[1:])
        axs[4].set_ylabel('P0 [V]')
        axs[4].grid()
        axs[4].xaxis.set_ticklabels([])

        axs[5].clear()
        axs[5].plot(SWPTime[1:],pip1Voltages[1:])
        axs[5].set_ylabel('P1 [V]')
        axs[5].grid()
        axs[5].set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]')
        axs[5].text(-0.1, -0.6, 'P0 RMS: ' + "{0:.1f}".format(pip0rms) + ' mV', transform=axs[5].transAxes)
        axs[5].text(-0.1, -0.8, 'P1 RMS: ' + "{0:.1f}".format(pip1rms) + ' mV', transform=axs[5].transAxes)
        axs[5].text( 0.1, -0.6, 'P0 STD: ' + "{0:.1f}".format(pip0std) + ' mV', transform=axs[5].transAxes)
        axs[5].text( 0.1, -0.8, 'P1 STD: ' + "{0:.1f}".format(pip1std) + ' mV', transform=axs[5].transAxes)

        plt.pause(0.1) # needed for pyplot realtime plotting. might switch back to pyqtgraph for speed

plt.show()
f.close()
time.sleep(1)
os.rename(fn,fn[:-4]+'_'+str(payloadID[-1])+'.bin')
