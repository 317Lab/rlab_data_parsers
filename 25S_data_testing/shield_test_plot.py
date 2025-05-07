"""
Stripped down version of Jules' shield_plot.py for shield testing.
Author: Sean Wallace
Date: April 2025
"""
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

def plot_data(ax,x,y,lw,xlabel,ylabel,xticks_off, fs):
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

def save_plots(swp_time, volts, imu_time, acc, mag, gyr, save_path):
# initialize figure + axes
    num_samples = 28
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

    plot_data(ax0,imu_time[0],acc[0],lw,lbl_imu,'ACC [g]',0, fs=fs)
    ax0.xaxis.tick_top()
    ax0.xaxis.set_label_position('top')
    plot_data(ax1,imu_time[0],mag[0],lw,'','MAG [G]',1, fs=fs)
    plot_data(ax2,imu_time[0],gyr[0],lw,'','GYR [Hz]',1, fs=fs)
    plot_data(ax3,imu_time[0,:-2],imu_cad[0,:-2],lw,'','CAD [ms]',1, fs=fs)
    plot_data(ax4,swp_time[0],volts[0,0],lw/2,'','P0 [V]',1, fs=fs)
    plot_data(ax5,swp_time[0],volts[0,1],lw/2,lbl_swp,'P1 [V]',0, fs=fs)
    #ax5.text(0.0*dim,-0.8, 'ID: ' + str(payload_id[0,0]), transform=ax5.transAxes)
    ax5.text(0.1*dim,-0.8, '$2\sigma_0$: {0:.1f} mV'.format(2*pip0_std), transform=ax5.transAxes)
    ax5.text(0.3*dim,-0.8, '$2\sigma_1$: {0:.1f} mV'.format(2*pip1_std), transform=ax5.transAxes)
    ax5.text(0.5*dim,-0.8, 'CAD: {0:.1f} ms'.format(imu_cad_avg), transform=ax5.transAxes)

    if buffered:
        plot_data(ax0b,imu_time[1],acc[0],lw,lbl_imu,'',0, fs=fs)
        ax0b.xaxis.tick_top()
        ax0b.xaxis.set_label_position('top')
        plot_data(ax1b,imu_time[1],mag[1],lw,'','',1, fs=fs)
        plot_data(ax2b,imu_time[1],gyr[1],lw,'','',1, fs=fs)
        plot_data(ax3b,imu_time[1,:-2],imu_cad[0,:-2],lw,'','',1, fs=fs)
        plot_data(ax4b,swp_time[1],volts[1,0],lw/2,'','',1, fs=fs)
        plot_data(ax5b,swp_time[1],volts[1,1],lw/2,lbl_swp,'',0, fs=fs)
    plt.savefig(save_path)
    plt.close()