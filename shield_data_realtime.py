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

# user settings
baud = 230400
freq = 45 # set data frequency in Hz
read_time = 1 # time to read data for in seconds
read_multiplier = 4 # multiples of read_time seconds to plot
initial_timeout = 4*3600*0+10
plotting_timeout = 3600*0+5
buffered = True
debugging = False
tuner = 1.2

# parameters
num_samples = 28 # how many samples per message
num_swp_bytes = 4 + 1 + num_samples * 2 * 2 # 4 times bytes, 1 id byte, 2 bytes per sample per 2 pips
num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2 # 4 time bytes, xyz for agm each 2 bytes, 2 temp bytes
num_msg_bytes = 2 + num_swp_bytes + 2 + num_imu_bytes
t_scale = 1.e-6; a_scale = 4*9.8/2**15; m_scale = 1./2**15; g_scale = 2000./360/2**15; p_scale = 5/2**14 # data scales
num_bytes_target = round(read_time*freq*num_msg_bytes*tuner) # N seconds worth of bytes

# opening data port/file
suffix = ''
monitoring_only = False
port = sys.argv[1]
print('Reading from port',port,'at baud rate',baud,flush=True)
if len(sys.argv) == 3: # optional argument
    if sys.argv[2] == '-m':
        monitoring_only = True
        print(''.center(64,'*'))
        print(' MONITORING ONLY '.center(64,'*'))
        print(''.center(64,'*'))
    else:
        suffix = '_' + sys.argv[2]
try:
    ser = serial.Serial(port, baud, timeout=initial_timeout) # wait until all bytes are read or x seconds pass
    ser.reset_input_buffer() # flush serial port
    print('Initial serial port timeout =',ser.timeout,'seconds',flush=True)
except:
    print('Serial port not found.')
    exit()

file_name = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + '_data_' + port.split('.')[-1] + '_' + str(baud) + suffix + '.bin'
if not(monitoring_only):
    file = open(file_name,'ab')
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

num_bytes_target = dim*num_bytes_target # twice as much data

# initialize global parameters
plotting = True
raw_bytes = b'\x00' # needs non-zero length
raw_bytes_old = b''
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
            raw_bytes_tmp = ser.read(num_bytes_target)
            if not(monitoring_only):
                file.write(raw_bytes_tmp)
            raw_bytes_old = raw_bytes_tmp[-num_msg_bytes:] # stitch on one full message
            raw_bytes = raw_bytes_tmp + raw_bytes_old
            if debugging:
                print('File size = ',os.path.getsize(file_name),' bytes')
        except:
            print('Background thread read on closed port.')
            plotting = False

# start main loop
def main():
    global plotting, raw_bytes

    flash = True
    initial_print = True

    # thread reading and writing raw bytes
    # "daemon = False" ensures read_write_thread continues writing if main thread is killed
    rw_thread = th.Thread(target=read_write_thread, args=(), name='read_write_thread', daemon=False) ## CHANGE BACK TO FALSE
    rw_thread.start()
    
    # data lengths
    num_dat_swp = round(read_time*freq*num_samples*2) # add 50% for safety
    num_dat_imu = round(read_time*freq*2)
    len_plt_swp = num_dat_swp # lengths to plot, grow while plotting
    len_plt_imu = num_dat_imu

    # initialize history arrays
    # history stitches poorly due to messages getting cut between frames
    swp_time_old = np.zeros([dim,0],dtype='uint32') # unsigned 4 bytes
    p0_volts_old = np.zeros([dim,0],dtype='int16') # signed 2 bytes
    p1_volts_old = np.zeros([dim,0],dtype='int16')
    imu_time_old = np.zeros([dim,0],dtype='uint32')
    ax_old = np.zeros([dim,0],dtype='int16'); ay_old = np.zeros([dim,0],dtype='int16'); az_old = np.zeros([dim,0],dtype='int16') 
    mx_old = np.zeros([dim,0],dtype='int16'); my_old = np.zeros([dim,0],dtype='int16'); mz_old = np.zeros([dim,0],dtype='int16')
    gx_old = np.zeros([dim,0],dtype='int16'); gy_old = np.zeros([dim,0],dtype='int16'); gz_old = np.zeros([dim,0],dtype='int16')

    while plotting:
        num_bytes = len(raw_bytes)
        if num_bytes == 0: # end recording if no bytes after timeout
            print('No data after serial timeout',flush=True)
            print('Terminating at',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
            plotting = False
        elif num_bytes == num_bytes_target+num_msg_bytes:
            # pre-allocate arrays of maximum possible sizes
            swp_time = np.zeros([dim,num_dat_swp],dtype='uint32') # unsigned 4 bytes
            payload_id = np.zeros([dim,num_dat_swp],dtype='uint8') # unsigned 1 byte
            p0_volts = np.zeros([dim,num_dat_swp],dtype='int16') # signed 2 bytes
            p1_volts = np.zeros([dim,num_dat_swp],dtype='int16')
            imu_time = np.zeros([dim,num_dat_imu],dtype='uint32')
            ax = np.zeros([dim,num_dat_imu],dtype='int16')
            ay = np.zeros([dim,num_dat_imu],dtype='int16')
            az = np.zeros([dim,num_dat_imu],dtype='int16') 
            mx = np.zeros([dim,num_dat_imu],dtype='int16')
            my = np.zeros([dim,num_dat_imu],dtype='int16')
            mz = np.zeros([dim,num_dat_imu],dtype='int16')
            gx = np.zeros([dim,num_dat_imu],dtype='int16')
            gy = np.zeros([dim,num_dat_imu],dtype='int16')
            gz = np.zeros([dim,num_dat_imu],dtype='int16')
            # imu_temp = np.zeros([dim,num_dat_imu],dtype='int16')

            pos_swp = 0 # position in respective arrays
            pos_imu = 0
            pos_bswp = 0 # buffered positions
            pos_bimu = 0
            for i in range(num_bytes-num_swp_bytes-2): # scan through raw_bytes
                # if raw_bytes[i] == 35: # byte is "#": start of data message NOT NEEDED, BELOW CONDITIONS ARE ENOUGH
                if raw_bytes[i+1] == 83: # byte is "S": start of sweep data
                    if i+num_swp_bytes+2 <= num_bytes: # full message is available
                        if raw_bytes[i+num_swp_bytes+2] == 35: # next "#" indicates correct number of sweep bytes
                            swp_bytes = raw_bytes[i+2:i+num_swp_bytes+2] # collect appropriate bytes
                            p0_bytes = swp_bytes[5:5+2*num_samples]
                            p1_bytes = swp_bytes[5+2*num_samples:]
                            for sample in range(0,2*num_samples,2): # allocate all sweep samples to arrays
                                swp_time[0,pos_swp] = conc(swp_bytes[0:4]) # copy static data for each sample
                                payload_id[0,pos_swp] = swp_bytes[4]
                                p0_volts[0,pos_swp] = conc(p0_bytes[sample:sample+2])
                                p1_volts[0,pos_swp] = conc(p1_bytes[sample:sample+2])
                                pos_swp += 1
                elif raw_bytes[i+1] == 73: # byte is "I": start of IMU data
                    if i+num_imu_bytes+2 <= num_bytes: # full message is available
                        if raw_bytes[i+num_imu_bytes+2] == 35: # next "#" indicates correct number of IMU bytes
                            imu_bytes = raw_bytes[i+2:i+num_imu_bytes+2] # collect appropriate bytes
                            imu_time[0,pos_imu] = conc(imu_bytes[0:4])
                            ax[0,pos_imu] = conc(imu_bytes[4:6])
                            ay[0,pos_imu] = conc(imu_bytes[6:8])
                            az[0,pos_imu] = conc(imu_bytes[8:10])
                            mx[0,pos_imu] = conc(imu_bytes[10:12])
                            my[0,pos_imu] = conc(imu_bytes[12:14])
                            mz[0,pos_imu] = conc(imu_bytes[14:16])
                            gx[0,pos_imu] = conc(imu_bytes[16:18])
                            gy[0,pos_imu] = conc(imu_bytes[18:20])
                            gz[0,pos_imu] = conc(imu_bytes[20:22])
                            # imu_temp[0,pos_imu] = conc(imu_bytes[22:24])
                            pos_imu += 1
                elif buffered and (raw_bytes[i+1] == 84): # byte is "T": start of buffered sweep data
                    if i+num_swp_bytes+2 <= num_bytes: # full message is available
                        if raw_bytes[i+num_swp_bytes+2] == 35: # next "#" indicates correct number of sweep bytes
                            swp_bytes = raw_bytes[i+2:i+num_swp_bytes+2] # collect appropriate bytes
                            p0_bytes = swp_bytes[5:5+2*num_samples]
                            p1_bytes = swp_bytes[5+2*num_samples:]
                            for sample in range(0,2*num_samples,2): # allocate all sweep samples to arrays
                                swp_time[1,pos_bswp] = conc(swp_bytes[0:4]) # copy static data for each sample
                                payload_id[1,pos_bswp] = swp_bytes[4]
                                p0_volts[1,pos_bswp] = conc(p0_bytes[sample:sample+2])
                                p1_volts[1,pos_bswp] = conc(p1_bytes[sample:sample+2])
                                pos_bswp += 1
                elif buffered and (raw_bytes[i+1] == 74): # byte is "J": start of buffer IMU data
                    if i+num_imu_bytes+2 <= num_bytes: # full message is available
                        if raw_bytes[i+num_imu_bytes+2] == 35: # next "#" indicates correct number of IMU bytes
                            imu_bytes = raw_bytes[i+2:i+num_imu_bytes+2] # collect appropriate bytes
                            imu_time[1,pos_bimu] = conc(imu_bytes[0:4])
                            ax[1,pos_bimu] = conc(imu_bytes[4:6])
                            ay[1,pos_bimu] = conc(imu_bytes[6:8])
                            az[1,pos_bimu] = conc(imu_bytes[8:10])
                            mx[1,pos_bimu] = conc(imu_bytes[10:12])
                            my[1,pos_bimu] = conc(imu_bytes[12:14])
                            mz[1,pos_bimu] = conc(imu_bytes[14:16])
                            gx[1,pos_bimu] = conc(imu_bytes[16:18])
                            gy[1,pos_bimu] = conc(imu_bytes[18:20])
                            gz[1,pos_bimu] = conc(imu_bytes[20:22])
                            # imu_temp[0,pos_imu] = conc(imu_bytes[22:24])
                            pos_bimu += 1

            if (pos_swp==0) or (pos_imu==0): # no full messages found indicating scrambled bytes
                print('DATA DROPOUT AT',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"),flush=True)
                time.sleep(1) # print in 1 second intervals until end of data drop=
            else:
                if initial_print:
                    start_time = time.time()
                    ser.timeout = plotting_timeout # shorten timeout after initial message capture
                    initial_print = False
                    print('Initial message capture at',datetime.now().strftime("%Y/%m/%d, %H:%M:%S LT"))
                    print('Serial port timeout =',ser.timeout,'seconds')
                
                # Converting bytes and scaling data
                swp_ids = swp_time[0] != 0 # chop off zeros in non-buffered times only (easier for now)
                imu_ids = imu_time[0] != 0

                swp_time = swp_time[:,swp_ids]*t_scale
                payload_id = payload_id[0,0]
                p0_volts = p0_volts[:,swp_ids]*p_scale
                p1_volts = p1_volts[:,swp_ids]*p_scale
                imu_time = imu_time[:,imu_ids]*t_scale
                ax = ax[:,imu_ids]*a_scale; ay = ay[:,imu_ids]*a_scale; az = az[:,imu_ids]*a_scale
                mx = mx[:,imu_ids]*m_scale; my = my[:,imu_ids]*m_scale; mz = mz[:,imu_ids]*m_scale
                gx = gx[:,imu_ids]*g_scale; gy = gy[:,imu_ids]*g_scale; gz = gz[:,imu_ids]*g_scale

                # stitch on history
                swp_time_plt = np.concatenate((swp_time_old,swp_time),axis=1)[:,-len_plt_swp:]
                p0_volts_plt = np.concatenate((p0_volts_old,p0_volts),axis=1)[:,-len_plt_swp:]
                p1_volts_plt = np.concatenate((p1_volts_old,p1_volts),axis=1)[:,-len_plt_swp:]
                imu_time_plt = np.concatenate((imu_time_old,imu_time),axis=1)[:,-len_plt_imu:]
                ax_plt = np.concatenate((ax_old,ax),axis=1)[:,-len_plt_imu:]
                ay_plt = np.concatenate((ay_old,ay),axis=1)[:,-len_plt_imu:]
                az_plt = np.concatenate((az_old,az),axis=1)[:,-len_plt_imu:]
                mx_plt = np.concatenate((mx_old,mx),axis=1)[:,-len_plt_imu:]
                my_plt = np.concatenate((my_old,my),axis=1)[:,-len_plt_imu:]
                mz_plt = np.concatenate((mz_old,mz),axis=1)[:,-len_plt_imu:]
                gx_plt = np.concatenate((gx_old,gx),axis=1)[:,-len_plt_imu:]
                gy_plt = np.concatenate((gy_old,gy),axis=1)[:,-len_plt_imu:]
                gz_plt = np.concatenate((gz_old,gz),axis=1)[:,-len_plt_imu:]

                len_plt_swp = min(read_multiplier*num_dat_swp,len_plt_swp+len(swp_time_plt[0]))
                len_plt_imu = min(read_multiplier*num_dat_imu,len_plt_imu+len(imu_time_plt[0]))

                # data calculations
                imu_cad_plt = np.diff(imu_time_plt,prepend=np.nan)*1e3
                imu_cad_med = np.median(np.diff(imu_time_plt))*1e3
                p0_rms = np.sqrt(np.mean(np.square(p0_volts_plt[0]-np.mean(p0_volts_plt[0]))))*1e3 # calculate rms
                p1_rms = np.sqrt(np.mean(np.square(p1_volts_plt[0]-np.mean(p1_volts_plt[0]))))*1e3
                p0_std = np.std(p0_volts_plt[0])*1e3 # calculate standard deviation
                p1_std = np.std(p1_volts_plt[0])*1e3

                # Plotting
                fig.canvas.mpl_connect('close_event', on_close) # exit loop when closing figure
                fig.subplots_adjust(hspace=0)
                lw = 1

                ax0.clear() # accelerometer
                ax0.plot(imu_time_plt[0],ax_plt[0],linewidth=lw)
                ax0.plot(imu_time_plt[0],ay_plt[0],linewidth=lw)
                ax0.plot(imu_time_plt[0],az_plt[0],linewidth=lw)
                ax0.set_ylabel('ACC [g]')
                ax0.grid()
                ax0.ticklabel_format(useOffset=False)
                ax0.set_xlabel('IMU TIME SINCE SHIELD POWER [s]')
                ax0.xaxis.tick_top()
                ax0.xaxis.set_label_position('top')
                ax0.text(0.9, 1.5, 'SHIELD ID: ' + str(payload_id), transform=ax0.transAxes, fontsize=15)
                if monitoring_only:
                    if flash:
                        ax0.text(-0.1, 1.5, 'MONITORING ONLY', transform=ax0.transAxes, color='red',fontsize=20,weight="bold")
                        flash = False
                    else:
                        flash = True

                ax1.clear() # magnetometer
                ax1.plot(imu_time_plt[0],mx_plt[0],linewidth=lw)
                ax1.plot(imu_time_plt[0],my_plt[0],linewidth=lw)
                ax1.plot(imu_time_plt[0],mz_plt[0],linewidth=lw)
                ax1.set_ylabel('MAG [G]')
                ax1.grid()
                ax1.ticklabel_format(useOffset=False)
                ax1.xaxis.set_ticklabels([])

                ax2.clear() # gyrometer
                ax2.plot(imu_time_plt[0],gx_plt[0],linewidth=lw)
                ax2.plot(imu_time_plt[0],gy_plt[0],linewidth=lw)
                ax2.plot(imu_time_plt[0],gz_plt[0],linewidth=lw)
                ax2.set_ylabel('GYR [Hz]')
                ax2.grid()
                ax2.ticklabel_format(useOffset=False)
                ax2.xaxis.set_ticklabels([])
                
                ax3.clear() # Cadance
                ax3.plot(imu_time_plt[0],imu_cad_plt[0],linewidth=lw)
                ax3.set_ylabel('CAD [ms]')
                ax3.grid()
                ax3.ticklabel_format(useOffset=False)
                ax3.xaxis.set_ticklabels([])
                
                ax4.clear() # pip0 voltage
                ax4.plot(swp_time_plt[0],p0_volts_plt[0],linewidth=lw/2)
                ax4.set_ylabel('P0 [V]')
                ax4.grid()
                ax4.ticklabel_format(useOffset=False)
                ax4.xaxis.set_ticklabels([])

                ax5.clear() # pip1 voltage
                ax5.plot(swp_time_plt[0],p1_volts_plt[0],linewidth=lw/2)
                ax5.set_ylabel('P1 [V]')
                ax5.grid()
                ax5.ticklabel_format(useOffset=False)
                ax5.set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]')
                ax5.text(-0.1, -0.6, 'P0 RMS: ' + "{0:.1f}".format(p0_rms) + ' mV', transform=ax5.transAxes)
                ax5.text(-0.1, -0.8, 'P1 RMS: ' + "{0:.1f}".format(p1_rms) + ' mV', transform=ax5.transAxes)
                ax5.text( 0.1, -0.6, 'P0 STD: ' + "{0:.1f}".format(p0_std) + ' mV', transform=ax5.transAxes)
                ax5.text( 0.1, -0.8, 'P1 STD: ' + "{0:.1f}".format(p1_std) + ' mV', transform=ax5.transAxes)
                ax5.text( 0.3, -0.8, 'CAD: ' + "{0:.1f}".format(imu_cad_med) + ' ms', transform=ax5.transAxes)

                if buffered:
                    ax0b.clear() # accelerometer
                    ax0b.plot(imu_time_plt[1],ax_plt[1],linewidth=lw)
                    ax0b.plot(imu_time_plt[1],ay_plt[1],linewidth=lw)
                    ax0b.plot(imu_time_plt[1],az_plt[1],linewidth=lw)
                    ax0b.grid()
                    ax0b.ticklabel_format(useOffset=False)
                    ax0b.set_xlabel('IMU TIME SINCE SHIELD POWER [s]')
                    ax0b.xaxis.tick_top()
                    ax0b.xaxis.set_label_position('top')

                    ax1b.clear() # magnetometer
                    ax1b.plot(imu_time_plt[1],mx_plt[1],linewidth=lw)
                    ax1b.plot(imu_time_plt[1],my_plt[1],linewidth=lw)
                    ax1b.plot(imu_time_plt[1],mz_plt[1],linewidth=lw)
                    ax1b.grid()
                    ax1b.ticklabel_format(useOffset=False)
                    ax1b.xaxis.set_ticklabels([])

                    ax2b.clear() # gyrometer
                    ax2b.plot(imu_time_plt[1],gx_plt[1],linewidth=lw)
                    ax2b.plot(imu_time_plt[1],gy_plt[1],linewidth=lw)
                    ax2b.plot(imu_time_plt[1],gz_plt[1],linewidth=lw)
                    ax2b.grid()
                    ax2b.ticklabel_format(useOffset=False)
                    ax2b.xaxis.set_ticklabels([])
                    
                    ax3b.clear() # Cadance
                    ax3b.plot(imu_time_plt[1],imu_cad_plt[1],linewidth=lw)
                    ax3b.grid()
                    ax3b.ticklabel_format(useOffset=False)
                    ax3b.xaxis.set_ticklabels([])
                    
                    ax4b.clear() # pip0 voltage
                    ax4b.plot(swp_time_plt[1],p0_volts_plt[1],linewidth=lw/2)
                    ax4b.grid()
                    ax4b.ticklabel_format(useOffset=False)
                    ax4b.xaxis.set_ticklabels([])

                    ax5b.clear() # pip1 voltage
                    ax5b.plot(swp_time_plt[1],p1_volts_plt[1],linewidth=lw/2)
                    ax5b.grid()
                    ax5b.ticklabel_format(useOffset=False)
                    ax5b.set_xlabel('SWEEP TIME SINCE SHIELD POWER [s]')

                swp_time_old = swp_time_plt
                p0_volts_old = p0_volts_plt
                p1_volts_old = p1_volts_plt
                imu_time_old = imu_time_plt
                ax_old = ax_plt; ay_old = ay_plt; az_old = az_plt
                mx_old = mx_plt; my_old = my_plt; mz_old = mz_plt
                gx_old = gx_plt; gy_old = gy_plt; gz_old = gz_plt

                plt.pause(read_time) # needed for pyplot realtime plotting.
    
    ser.close()
    
    if not ser.is_open:
        print('Serial port',port,'closed')
    if not(monitoring_only):
        file.close()
        file_size = os.path.getsize(file_name)
        try:
            os.rename(file_name,file_name[:-4]+'_'+str(payload_id)+'.bin') # add payload ID to file_name
            print('File name =',file_name[:-4]+'_'+str(payload_id)+'.bin')
        except:
            print('No payload ID determined.')
        try:
            file_size_target = round((time.time()-start_time)*freq*num_msg_bytes)
            print('File size =',file_size,'bytes')
            print('File size target =',dim*file_size_target,'bytes')
        except:
            print('File size =',file_size,'bytes')
main()
