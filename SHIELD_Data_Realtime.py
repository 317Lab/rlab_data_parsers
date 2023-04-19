# Data collection + realtime parsing & plotting of SHIELD housekeeping and PIP data
# Updated version for python 3
# Arguments:
#   1) Portname
#   2) (Optional) Data file_name suffix
# Writes all captured bytes to binary file in separate thread
# x minute initial timeout to allow for early code execution
# Loop terminates after a y minute timeout with no data after initial full frame capture
# To stop recording, close figure
# Contact: jules.van.irsel.gr@dartmouth.edu

import sys
import os
import serial
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time
import threading as th

# parameters
num_samples = 28 # how many samples per message
num_swp_bytes = 4 + 1 + num_samples * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
num_msg_bytes = num_swp_bytes + 2 + num_imu_bytes + 2
t_scale = 1.e-6; a_scale = 4*9.8/2**15; m_scale = 1./2**15; g_scale = 2000./360/2**15; p_scale = 5/2**14 # data scales
freq = 45 # set data frequency in Hz
plot_time = 2 # time to plot for in seconds
num_bytes_target = plot_time*freq*num_msg_bytes # N seconds worth of bytes

# opening data port/file
port = sys.argv[1]
baud = 230400
initial_timeout = 4*3600*0+30
plotting_timeout = 3600*0+10
monitoring_only = False
suffix = ''
print('Reading from port',port,'at baud rate',baud,flush=True)
if len(sys.argv) == 3: # optional argument
    if sys.argv[2] == '-m':
        monitoring_only = True
        print(''.center(64,'*'))
        print(' MONITORING ONLY '.center(64,'*'))
        print(''.center(64,'*'))
    else:
        suffix = '_' + sys.argv[2]
ser = serial.Serial(port, baud, timeout=initial_timeout) # wait until all bytes are read or x seconds pass
print('Initial serial port timeout =',ser.timeout,'seconds',flush=True)
ser.reset_input_buffer() # flush serial port
file_name = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + '_data_' + port.split('.')[-1] + '_' + str(baud) + suffix + '.bin'
if not(monitoring_only):
    file = open(file_name,'ab')
fig, axs = plt.subplots(6, 1, figsize=(8,6))

# initialize global parameters
plotting = True
raw_bytes = b'\x00'
payload_id = 0

# for closing on figure exit
def on_close(event):
    global plotting
    print('Close event captured at',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
    plotting = False

# concatenate multiple bytes
def conc(word):
    if len(word) == 2:
        return (word[1]<<8) | word[0]
    if len(word) == 4:
        return (word[3]<<24) | (word[2]<<16) | (word[1]<<8) | word[0]

# background read + write thread
def read_write_thread():
    global plotting, raw_bytes
    while plotting:
        try:
            raw_bytes = ser.read(num_bytes_target)
            if not(monitoring_only):
                file.write(raw_bytes)
        except:
            print('Background thread read on closed port.')
            plotting = False

# start main loop
def main():
    global plotting, raw_bytes
    flash = True
    rw_thread = th.Thread(target=read_write_thread, args=(), name='read_write_thread', daemon=False) # thread reading and writing raw bytes
    rw_thread.start()
    
    # initialize history arrays
    # history stitches poorly due to messages getting cut between frames
    swp_time_old = np.zeros(0,dtype='uint32') # unsigned 4 bytes
    p0_volts_old = np.zeros(0,dtype='int16') # signed 2 bytes
    p1_volts_old = np.zeros(0,dtype='int16')
    imu_time_old = np.zeros(0,dtype='uint32')
    ax_old = np.zeros(0,dtype='int16'); ay_old = np.zeros(0,dtype='int16'); az_old = np.zeros(0,dtype='int16') 
    mx_old = np.zeros(0,dtype='int16'); my_old = np.zeros(0,dtype='int16'); mz_old = np.zeros(0,dtype='int16')
    gx_old = np.zeros(0,dtype='int16'); gy_old = np.zeros(0,dtype='int16'); gz_old = np.zeros(0,dtype='int16')
    imu_cad_old = np.zeros(0,dtype='uint32')

    initial_print = True

    while plotting:
        num_bytes = len(raw_bytes)
        if num_bytes == 0: # end recording if no bytes after timeout
            print('No data after serial timeout',flush=True)
            print('Terminating at',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
            plotting = False
        elif num_bytes == num_bytes_target:
            ser.timeout = plotting_timeout # shorten timeout after initial message capture
            num_dat_swp = round(plot_time*freq*num_samples*1.5) # add 50% for safety
            num_dat_imu = round(plot_time*freq*1.5)

            # pre-allocate arrays of maximum possible sizes
            swp_time = np.zeros(num_dat_swp,dtype='uint32') # unsigned 4 bytes
            payload_id = np.zeros(num_dat_swp,dtype='uint8') # unsigned 1 byte
            p0_volts = np.zeros(num_dat_swp,dtype='int16') # signed 2 bytes
            p1_volts = np.zeros(num_dat_swp,dtype='int16')
            imu_time = np.zeros(num_dat_imu,dtype='uint32')
            ax = np.zeros(num_dat_imu,dtype='int16'); ay = np.zeros(num_dat_imu,dtype='int16'); az = np.zeros(num_dat_imu,dtype='int16') 
            mx = np.zeros(num_dat_imu,dtype='int16'); my = np.zeros(num_dat_imu,dtype='int16'); mz = np.zeros(num_dat_imu,dtype='int16')
            gx = np.zeros(num_dat_imu,dtype='int16'); gy = np.zeros(num_dat_imu,dtype='int16'); gz = np.zeros(num_dat_imu,dtype='int16')
            imu_temp = np.zeros(num_dat_imu,dtype='int16')

            pos_swp = 0 # position in respective arrays
            pos_imu = 0
            for i in range(num_bytes-num_swp_bytes-2): # scan through raw_bytes
                if raw_bytes[i] == 35: # byte is "#": start of data message
                    if raw_bytes[i+1] == 83: # byte is "S": start of sweep data
                        if i+num_swp_bytes+2 <= num_bytes: # full message is available
                            if raw_bytes[i+num_swp_bytes+2] == 35: # next "#" indicates correct number of sweep bytes
                                swp_bytes = raw_bytes[i+2:i+num_swp_bytes+2] # collect appropriate bytes
                                p0_bytes = swp_bytes[5:5+2*num_samples]
                                p1_bytes = swp_bytes[5+2*num_samples:]
                                for sample in range(0,2*num_samples,2): # allocate all sweep samples to arrays
                                    swp_time[pos_swp] = conc(swp_bytes[0:4]) # copy static data for each sample
                                    payload_id[pos_swp] = swp_bytes[4]
                                    p0_volts[pos_swp] = conc(p0_bytes[sample:sample+2])
                                    p1_volts[pos_swp] = conc(p1_bytes[sample:sample+2])
                                    pos_swp += 1
                    elif raw_bytes[i+1] == 73: # byte is "I": start of IMU data
                        if i+num_imu_bytes+2 <= num_bytes: # full message is available
                            if raw_bytes[i+num_imu_bytes+2] == 35: # next "#" indicates correct number of IMU bytes
                                imu_bytes = raw_bytes[i+2:i+num_imu_bytes+2] # collect appropriate bytes
                                imu_time[pos_imu] = conc(imu_bytes[0:4])
                                ax[pos_imu] = conc(imu_bytes[4:6])
                                ay[pos_imu] = conc(imu_bytes[6:8])
                                az[pos_imu] = conc(imu_bytes[8:10])
                                mx[pos_imu] = conc(imu_bytes[10:12])
                                my[pos_imu] = conc(imu_bytes[12:14])
                                mz[pos_imu] = conc(imu_bytes[14:16])
                                gx[pos_imu] = conc(imu_bytes[16:18])
                                gy[pos_imu] = conc(imu_bytes[18:20])
                                gz[pos_imu] = conc(imu_bytes[20:22])
                                imu_temp[pos_imu] = conc(imu_bytes[22:24])
                                pos_imu += 1

            if pos_swp==0 or pos_imu==0: # no full messages found indicating scrambled bytes
                print('DATA DROPOUT AT',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
                time.sleep(1) # print in 1 second intervals until end of data drop
            else:
                if initial_print:
                    start_time = time.time()
                    print('Initial message capture at',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"))
                    print('Serial port timeout =',ser.timeout,'seconds')
                    initial_print = False
                
                # Converting bytes and scaling data
                swp_time = swp_time[0:pos_swp]*t_scale # chop off unused zeros
                payload_id = payload_id[0]
                p0_volts = p0_volts[0:pos_swp]*p_scale
                p1_volts = p1_volts[0:pos_swp]*p_scale
                imu_time = imu_time[0:pos_imu]*t_scale
                ax = ax[0:pos_imu]*a_scale; ay = ay[0:pos_imu]*a_scale; az = az[0:pos_imu]*a_scale
                mx = mx[0:pos_imu]*m_scale; my = my[0:pos_imu]*m_scale; mz = mz[0:pos_imu]*m_scale
                gx = gx[0:pos_imu]*g_scale; gy = gy[0:pos_imu]*g_scale; gz = gz[0:pos_imu]*g_scale
                imu_temp = imu_temp[0:pos_imu]

                # data calculations
                imu_cad = np.diff(imu_time)*1e3
                imu_cad = np.append(imu_cad,imu_cad[-1]) # make array same length
                p0_rms = np.sqrt(np.mean(np.square(p0_volts-np.mean(p0_volts))))*1e3 # calculate rms
                p1_rms = np.sqrt(np.mean(np.square(p1_volts-np.mean(p1_volts))))*1e3
                p0_std = np.std(p0_volts)*1e3 # calculate standard deviation
                p1_std = np.std(p1_volts)*1e3

                # Plotting
                fig.canvas.mpl_connect('close_event', on_close) # exit loop when closing figure
                fig.subplots_adjust(hspace=0)
                lw = 1
            
                axs[0].clear() # accelerometer
                axs[0].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((ax_old,ax)),linewidth=lw)
                axs[0].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((ay_old,ay)),linewidth=lw)
                axs[0].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((az_old,az)),linewidth=lw)
                axs[0].set_ylabel('ACC [g]')
                axs[0].grid()
                axs[0].ticklabel_format(useOffset=False)
                axs[0].set_xlabel('IMU TIME SINCE SHIELD POWER [s]')
                axs[0].xaxis.tick_top()
                axs[0].xaxis.set_label_position('top')
                axs[0].text(0.9, 1.5, 'SHIELD ID: ' + str(payload_id), transform=axs[0].transAxes, fontsize=15)
                if monitoring_only:
                    if flash:
                        axs[0].text(-0.1, 1.5, 'MONITORING ONLY', transform=axs[0].transAxes, color='red',fontsize=20,weight="bold")
                        flash = False
                    else:
                        flash = True

                axs[1].clear() # magnetometer
                axs[1].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((mx_old,mx)),linewidth=lw)
                axs[1].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((my_old,my)),linewidth=lw)
                axs[1].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((mz_old,mz)),linewidth=lw)
                axs[1].set_ylabel('MAG [G]')
                axs[1].grid()
                axs[1].ticklabel_format(useOffset=False)
                axs[1].xaxis.set_ticklabels([])

                axs[2].clear() # gyrometer
                axs[2].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((gx_old,gx)),linewidth=lw)
                axs[2].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((gy_old,gy)),linewidth=lw)
                axs[2].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((gz_old,gz)),linewidth=lw)
                axs[2].set_ylabel('GYR [Hz]')
                axs[2].grid()
                axs[2].ticklabel_format(useOffset=False)
                axs[2].xaxis.set_ticklabels([])
                
                axs[3].clear() # Cadance
                axs[3].plot(np.concatenate((imu_time_old,imu_time)),np.concatenate((imu_cad_old,imu_cad)),linewidth=lw)
                axs[3].set_ylabel('CAD [ms]')
                axs[3].grid()
                axs[3].ticklabel_format(useOffset=False)
                axs[3].xaxis.set_ticklabels([])
                
                axs[4].clear() # pip0 voltage
                axs[4].plot(np.concatenate((swp_time_old,swp_time)),np.concatenate((p0_volts_old,p0_volts)),linewidth=lw/2)
                axs[4].set_ylabel('P0 [V]')
                axs[4].grid()
                axs[4].ticklabel_format(useOffset=False)
                axs[4].xaxis.set_ticklabels([])

                axs[5].clear() # pip1 voltage
                axs[5].plot(np.concatenate((swp_time_old,swp_time)),np.concatenate((p1_volts_old,p1_volts)),linewidth=lw/2)
                axs[5].set_ylabel('P1 [V]')
                axs[5].grid()
                axs[5].ticklabel_format(useOffset=False)
                axs[5].set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]')
                axs[5].text(-0.1, -0.6, 'P0 RMS: ' + "{0:.1f}".format(p0_rms) + ' mV', transform=axs[5].transAxes)
                axs[5].text(-0.1, -0.8, 'P1 RMS: ' + "{0:.1f}".format(p1_rms) + ' mV', transform=axs[5].transAxes)
                axs[5].text( 0.1, -0.6, 'P0 STD: ' + "{0:.1f}".format(p0_std) + ' mV', transform=axs[5].transAxes)
                axs[5].text( 0.1, -0.8, 'P1 STD: ' + "{0:.1f}".format(p1_std) + ' mV', transform=axs[5].transAxes)

                swp_time_old = swp_time
                p0_volts_old = p0_volts
                p1_volts_old =p1_volts
                imu_time_old = imu_time
                ax_old = ax; ay_old = ay; az_old = az
                mx_old = mx; my_old = my; mz_old = mz
                gx_old = gx; gy_old = gy; gz_old = gz
                imu_cad_old = imu_cad

                plt.pause(plot_time) # needed for pyplot realtime plotting.
    
    ser.close()
    
    if not ser.is_open:
        print('Serial port',port,'closed')
    if not(monitoring_only):
        file.close()
        file_size = os.path.getsize(file_name)
        os.rename(file_name,file_name[:-4]+'_'+str(payload_id)+'.bin') # add payload ID to file_name
        print('File name =',file_name[:-4]+'_'+str(payload_id)+'.bin')
        try:
            file_size_target = round((time.time()-start_time)*freq*num_msg_bytes)
            print('File size =',file_size,'bytes')
            print('File size target =',file_size_target,'bytes')
        except:
            print('File size =',file_size,'bytes')
main()
