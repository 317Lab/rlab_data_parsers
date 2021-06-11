#!/usr/bin/env python
# coding: utf-8

# In[1]:

from __future__ import division

import sys
import matplotlib
if 'matplotlib.pyplot' not in sys.modules.keys():
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import numpy as np

import os

matplotlib.use('nbagg')
import matplotlib.cm as cm
import scipy.signal as sig
from scipy.interpolate import interp1d
from scipy.io import savemat, loadmat
import pickle


#get_ipython().magic(u'matplotlib notebook')
cplt_kwargs = None

bad_tmwrd_files = ['./wallops_intDel/Dallas_Vibration_20210329/Dallas1_X-Axis_RandomVibe_3-29-2021.txt', 
                  './wallops_intDel/20210429_Tests-Dallas/data_file_230k_1-Test8-04_29_21.txt', 
                  './wallops_intDel/RailOn-Dallas/data_file_230k_1-RailOn-05_05_21.txt',
                  './wallops_intDel/RailOn_Playback-Dallas/data_file_230k_1-RailOn_Playback-05_06_21.txt'] #, 
#                   './wallops_intDel/LaunchDay1_20210508-Main/VertCheck-data_file_230k_1-05_08_21.txt']
DeltInx=[100, 300, 200]

#path = "./wallops_intDel/LaunchDay7_20210516-Dallas/"
# file_name = "PreLaunchAndFlight-data_file_230k_1-05_16_21.txt"
#file_name = "PreLaunchAndFlight-data_file_230k_2-05_16_21.txt"
# path = "./wallops_intDel/LaunchDay7_20210516-Main/" 
# file_name = "VertAndBoxCheck-data_file_230k_1-05_16_21.txt"
# file_name = "VertAndBoxCheck-data_file_230k_2-05_16_21.txt"
# file_name = "VertAndBoxCheck-data_file_230k_3-05_16_21.txt"
# file_name = "VertAndBoxCheck-data_file_230k_4-05_16_21.txt"
# file_name = "PreLaunch-data_file_230k_1-05_16_21.txt"
# file_name = "PreLaunch-data_file_230k_2-05_16_21.txt"
# file_name = "PreLaunch-data_file_230k_3-05_16_21.txt"
# file_name = "PreLaunch-data_file_230k_4-05_16_21.txt"
# file_name = "Flight-data_file_230k_1-05_16_21.txt"
# file_name = "Flight-data_file_230k_2-05_16_21.txt"
# file_name = "Flight-data_file_230k_3-05_16_21.txt"
# file_name = "Flight-data_file_230k_4-05_16_21.txt"

###################################################################################
### Set Inputs/Options
######################
##** All Day of Launch Flight Files **##
#path_lst = ["./wallops_intDel/LaunchDay7_20210516-Dallas/", "./wallops_intDel/LaunchDay7_20210516-Main/"] 
#file_lst = [["PreLaunchAndFlight-data_file_230k_1-05_16_21.txt", "PreLaunchAndFlight-data_file_230k_2-05_16_21.txt", \
#        "Playback-data_file_230k_1-05_16_21.txt", "Playback-data_file_230k_2-05_16_21.txt", \
#        "Dallas1_FlightData_5-16-2021.txt", "Dallas4_FlightData_5-16-2021.txt"], \
#        ["Flight-data_file_230k_1-05_16_21.txt", "Flight-data_file_230k_2-05_16_21.txt", "Flight-data_file_230k_3-05_16_21.txt", "Flight-data_file_230k_4-05_16_21.txt", \
#        "Playback-data_file_230k_1-05_16_21.txt", "Playback-data_file_230k_2-05_16_21.txt", "Playback-data_file_230k_3-05_16_21.txt", "Playback-data_file_230k_4-05_16_21.txt"]]
##** All Dallas Day of Launch Flight Files  **##
#path_lst = ["./wallops_intDel/LaunchDay7_20210516-Dallas/"]
#file_lst = [["PreLaunchAndFlight-data_file_230k_1-05_16_21.txt", "PreLaunchAndFlight-data_file_230k_2-05_16_21.txt", \
#        "Playback-data_file_230k_1-05_16_21.txt", "Playback-data_file_230k_2-05_16_21.txt", \
#        "Dallas1_FlightData_5-16-2021.txt", "Dallas4_FlightData_5-16-2021.txt"]]
##** All Main Day of Launch Flight Files  **##
path_lst = ["./wallops_intDel/LaunchDay7_20210516-Main/"] 
file_lst = [["Flight-data_file_230k_1-05_16_21.txt", "Flight-data_file_230k_2-05_16_21.txt", "Flight-data_file_230k_3-05_16_21.txt", "Flight-data_file_230k_4-05_16_21.txt"]] #, \
#        "Playback-data_file_230k_1-05_16_21.txt", "Playback-data_file_230k_2-05_16_21.txt", "Playback-data_file_230k_3-05_16_21.txt", "Playback-data_file_230k_4-05_16_21.txt"]]

##** Day of Launch Realtime Flight Files **## 
#path_lst = ["./wallops_intDel/LaunchDay7_20210516-Dallas/", "./wallops_intDel/LaunchDay7_20210516-Main/"] 
#file_lst = [["PreLaunchAndFlight-data_file_230k_1-05_16_21.txt", "PreLaunchAndFlight-data_file_230k_2-05_16_21.txt"], \
#        ["Flight-data_file_230k_1-05_16_21.txt", "Flight-data_file_230k_2-05_16_21.txt", "Flight-data_file_230k_3-05_16_21.txt", "Flight-data_file_230k_4-05_16_21.txt"]]
##** Day of Launch Playback Flight Files **## 
#path_lst = ["./wallops_intDel/LaunchDay7_20210516-Dallas/", "./wallops_intDel/LaunchDay7_20210516-Main/"] 
#file_lst = [["Playback-data_file_230k_1-05_16_21.txt", "Playback-data_file_230k_2-05_16_21.txt"], \
#        ["Playback-data_file_230k_1-05_16_21.txt", "Playback-data_file_230k_2-05_16_21.txt", "Playback-data_file_230k_3-05_16_21.txt", "Playback-data_file_230k_4-05_16_21.txt"]]

##** Select Day of Launch Flight Files **## 
#path_lst = ["./wallops_intDel/LaunchDay7_20210516-Dallas/", "./wallops_intDel/LaunchDay7_20210516-Main/"] 
#file_lst = [["PreLaunchAndFlight-data_file_230k_1-05_16_21.txt", "PreLaunchAndFlight-data_file_230k_2-05_16_21.txt", \
#        "Playback-data_file_230k_1-05_16_21.txt", "Playback-data_file_230k_2-05_16_21.txt"], \
#        ["Flight-data_file_230k_1-05_16_21.txt", "Flight-data_file_230k_2-05_16_21.txt", "Flight-data_file_230k_3-05_16_21.txt", "Flight-data_file_230k_4-05_16_21.txt"]]

#path_lst = ["./wallops_intDel/LaunchDay7_20210516-Dallas/"]
#file_lst = [["Dallas1_FlightData_5-16-2021.txt", "Dallas4_FlightData_5-16-2021.txt"]]

notify_every = False #Option: Whether or not to give a audio notification when done with parsing each file
notify = True

fig_subpath = 'Script_Plots/'
plottype = 1
yLnZooms = dict()
xLnZooms = dict()

figsuffix = None
Xlims = "default" #None 
cplt_kwargs={'pip0': {}, 'pip1':{}}

#figsuffix = "ZoomSweep_1203" #_Cbar0-20"
#path_lst, file_lst = ["./wallops_intDel/LaunchDay7_20210516-Main/"], [["Flight-data_file_230k_1-05_16_21.txt", "Flight-data_file_230k_2-05_16_21.txt", "Flight-data_file_230k_3-05_16_21.txt", "Flight-data_file_230k_4-05_16_21.txt"]] #, \
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[1203-0.22, 1203+.22],[1203-.22, 1203+.22]] 
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':8}, 'pip1':{'vmin':0, 'vmax':8}}

#figsuffix = "ZoomDt_1180-1120"
#path_lst, file_lst= ["./wallops_intDel/LaunchDay7_20210516-Main/"], [["Flight-data_file_230k_1-05_16_21.txt", "Flight-data_file_230k_2-05_16_21.txt", "Flight-data_file_230k_3-05_16_21.txt", "Flight-data_file_230k_4-05_16_21.txt"]] #, \
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[1180, 1220],[1180, 1220]] 
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':8}, 'pip1':{'vmin':0, 'vmax':8}}
#
#figsuffix = "ZoomDt_1190-1230" 
#path_lst, file_lst = ["./wallops_intDel/LaunchDay7_20210516-Dallas/"], [["PreLaunchAndFlight-data_file_230k_1-05_16_21.txt", "PreLaunchAndFlight-data_file_230k_2-05_16_21.txt"]] #, \
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[1190, 1230],[1190, 1230]] 
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':8}, 'pip1':{'vmin':0, 'vmax':8}}
#
#figsuffix = "ZoomA_Cbar0-20"
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = "default" #None 
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':20}, 'pip1':{'vmin':0, 'vmax':20}}
#
#figsuffix = "ZoomA2_Cbar0-20"
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[550, 1345], [550, 1345]] 
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':20}, 'pip1':{'vmin':0, 'vmax':20}}

figsuffix = "ZoomA3_Cbar0-20"
yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
Xlims = [[550, 1345], [550, 1345]] 
cplt_kwargs={'pip0': {'vmin':0, 'vmax':20}, 'pip1':{'vmin':0, 'vmax':20}}

#figsuffix = "ZoomB2_Cbar0-8"
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[1100,1250], [1100, 1250]]
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':8}, 'pip1':{'vmin':0, 'vmax':8}}
#
#figsuffix = "ZoomB2b_Cbar0-4"
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[1100,1250], [1100, 1250]]
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':4}, 'pip1':{'vmin':0, 'vmax':4}}

#figsuffix = "Zoom_Cbar0-20"
#yLnZooms['cad'] = [15, 55]
#yLnZooms['mag'] = [-0.5, 0.5]
#yLnZooms['pip0']=[1, 5]
#yLnZooms['pip1']=[1, 5]
#Xlims = "default" #None 
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':20}, 'pip1':{'vmin':0, 'vmax':20}}

#figsuffix = "ZoomT0" #_Cbar0-20"
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[1050, 1050.22],[1050, 1050.22]] 
##cplt_kwargs={'pip0': {}, 'pip1':{}}
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':20}, 'pip1':{'vmin':0, 'vmax':20}}

#figsuffix = "ZoomT1"
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[1170, 1170.22],[1170, 1170.22]] 
#cplt_kwargs={'pip0': {}, 'pip1':{}}
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':20}, 'pip1':{'vmin':0, 'vmax':20}}
#
#figsuffix = "ZoomT1b_Cbar20"
#yLnZooms['cad'] = [15, 55]; yLnZooms['mag'] = [-0.5, 0.5]; yLnZooms['pip0']=[0, 5]; yLnZooms['pip1']=[0, 5]
#Xlims = [[1180, 1180.22],[1180, 1180.22]] 
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':20}, 'pip1':{'vmin':0, 'vmax':20}}

#figsuffix = "ZoomB"
#yLnZooms['cad'] = [15, 55]
### # # # # del yLnZooms['accel']
### # yLnZooms['accel'] = [-2.5, 10.75]
#yLnZooms['mag'] = [-0.5, 0.5]
## # yLnZooms['gyro'] = [-0.041, 0.025]
##yLnZooms['pip0']=[0, 10]
#yLnZooms['pip0']=[1, 5]
#yLnZooms['pip1']=[1, 5]
## yLnZooms['pip0'] = [np.mean(pip0LPlot)-.005, np.mean(pip0LPlot)+.005]
## yLnZooms['pip1'] = [np.mean(pip1LPlot)-.005, np.mean(pip1LPlot)+.005]
## xLnZooms['xCzoom'] = 1000
#figsuffix = "ZoomB2"
#xlims = [800, sweepPlot[-1]]
#xlims2 = [800, sweepPlot[-1]]
#figsuffix = "ZoomB_cbar0-20and0-5"
#xlims = [1150, 1250]
#xlims2 = [1150, 1250]
#cplt_kwargs={'pip0': {'vmin':0, 'vmax':8}, 'pip1':{'vmin':0, 'vmax':20}}

if figsuffix is not None: fig_subpath = fig_subpath + figsuffix+"/"

#if cplt_kwargs is not None: cplt_lst = [cplt_kwargs]*len(path_lst)
###################################################################################

###################################################################################
### Definition of Classes 
#########################
class IMUData():
    def __init__(self):

        self.time = []; self.temp = []
        self.ax = []; self.ay = []; self.az = []
        self.mx = []; self.my = []; self.mz = []
        self.gx = []; self.gy = []; self.gz = []
        
        self.timeRpt = []; self.tempRpt = []
        self.axRpt = []; self.ayRpt = []; self.azRpt = []
        self.mxRpt = []; self.myRpt = []; self.mzRpt = []
        self.gxRpt = []; self.gyRpt = []; self.gzRpt = []
        
class SweepData():
    def __init__(self):
        self.time = []
        self.pip0 = []; self.pip1 = [];
        
        self.timeRpt = []
        self.pip0Rpt = []; self.pip1Rpt = [];
        
class PayloadData():
    def __init__(self):
        self.rawData = ''
        self.imu = IMUData()
        self.sweeps = SweepData()
        self.macAddress = ''
        self.rssiData = []
        self.shieldID = 0
        
# Functions for merging bytes
def combine2(a, b):
    return (a << 8) | b
def combine4(a, b, c, d):
    return (a << 24) | (b << 16) | (c << 8) | d

# Functions for saving data
def convertDataToLists(dataSet):
    dataSet.imu.ax = dataSet.imu.ax.tolist()
    dataSet.imu.ay = dataSet.imu.ay.tolist()
    dataSet.imu.az = dataSet.imu.az.tolist()
    dataSet.imu.mx = dataSet.imu.mx.tolist()
    dataSet.imu.my = dataSet.imu.my.tolist()
    dataSet.imu.mz = dataSet.imu.mz.tolist()
    dataSet.imu.gx = dataSet.imu.gx.tolist()
    dataSet.imu.gy = dataSet.imu.gy.tolist()
    dataSet.imu.gz = dataSet.imu.gz.tolist()
    dataSet.imu.temp = dataSet.imu.temp.tolist()
    dataSet.imu.time = dataSet.imu.time.tolist()
    dataSet.sweeps.time = dataSet.sweeps.time.tolist()
    dataSet.sweeps.pip0 = dataSet.sweeps.pip0.tolist()
    dataSet.sweeps.pip1 = dataSet.sweeps.pip1.tolist()
    
    dataSet.imu.axRpt = dataSet.imu.axRpt.tolist()
    dataSet.imu.ayRpt = dataSet.imu.ayRpt.tolist()
    dataSet.imu.azRpt = dataSet.imu.azRpt.tolist()
    dataSet.imu.mxRpt = dataSet.imu.mxRpt.tolist()
    dataSet.imu.myRpt = dataSet.imu.myRpt.tolist()
    dataSet.imu.mzRpt = dataSet.imu.mzRpt.tolist()
    dataSet.imu.gxRpt = dataSet.imu.gxRpt.tolist()
    dataSet.imu.gyRpt = dataSet.imu.gyRpt.tolist()
    dataSet.imu.gzRpt = dataSet.imu.gzRpt.tolist()
    dataSet.imu.tempRpt = dataSet.imu.tempRpt.tolist()
    dataSet.imu.timeRpt = dataSet.imu.timeRpt.tolist()
    dataSet.sweeps.timeRpt = dataSet.sweeps.timeRpt.tolist()
    dataSet.sweeps.pip0Rpt = dataSet.sweeps.pip0Rpt.tolist()
    dataSet.sweeps.pip1Rpt = dataSet.sweeps.pip1Rpt.tolist()
    return dataSet

def makeJSONFile (fname, payloadData):
    f = open(fname, 'w')
    # Convert into lists and dictionaries for JSON storage
    payloadData = convertDataToLists(payloadData)
    JSONDict = {}
    # First the IMU data
    imu = payloadData.imu
    imuData = {"time":imu.time, "temp":imu.temp,
               "ax":imu.ax, "ay":imu.ay, "az":imu.az,
               "mx":imu.mx, "my":imu.my, "mz":imu.mz,
               "gx":imu.gx, "gy":imu.gy, "gz":imu.gz}
    JSONDict["imu"] = imuData
    # Then the sweep data
    sweeps = payloadData.sweeps
    sweepData = {"id":sweeps.payloadID, "time":sweeps.time, "pip0":sweeps.pip0, "pip1":sweeps.pip1}
    JSONDict["sweeps"] = sweepData

    json.dump(JSONDict, f)
    f.close()
    
# Functions for padding data

# padding time data as lists
def timefix(l, new, dt):   # l = time data as list, new = empty list, dt = delta t
    for t in l:
        if l.index(t) >= 2:
            # replace bad timewords
            if t - l[l.index(t) - 1] < 0 or t - l[l.index(t) - 1] > 1:
                l[l.index(t) - 1] = l[l.index(t) - 2] + dt
                t = l[l.index(t) - 1] + dt
###################################################################################

###################################################################################
### Main Loop 
##################
# In[2]:
#for path, flist, cplt_kwargs in zip(path_lst, file_lst, cplt_lst): 
for path, flist in zip(path_lst, file_lst): 
    for file_name in flist: 
        dataFile = path + file_name


        ########### Load the data file ###########
        f = open(dataFile, 'r')
        rawData = f.read()
        print "Opened file:", dataFile

        # Create payload objects and store parsed data
        mainPIPData = PayloadData()
        mainPIPData.rawData = rawData
        payloads = [mainPIPData]

        ########### Parse by data type for each payload ###########
        strict_parse = False # Require a pound symbol at the end of the data
        for payload in payloads:
            payloadrawData = payload.rawData
            imu = []
            sweeps = []
            imuRpt = []
            sweepsRpt = []
            interrupt = []
            # 2 PIPs with 28 2-byte samples + 4-byte timestamp + ID
            sweepSamples = 28
            numSweepBytes = sweepSamples * 2 * 2 + 4 + 1
            # 9 2-byte data points + 2-byte temp + 4-byte timestamp
            numIMUBytes = 24
            # Barium interrupt
            numInterruptBytes = 4
            
            pntr = 0
            while pntr < len(payloadrawData):
                # Check message start sentinels and not at end
                if payloadrawData[pntr] == '#' and (len(payloadrawData)-pntr) >= numIMUBytes:
                    if payloadrawData[pntr+1] == 'I':
                        # If not the last, check message end sentinel
                        if pntr+2+numIMUBytes < len(payloadrawData):
                            if not strict_parse or payloadrawData[pntr+2+numIMUBytes] == '#':
                                imu.append(payloadrawData[pntr+2:pntr+2+numIMUBytes])
                        # Or just add the last message
                        else:
                            imu.append(payloadrawData[pntr+2:pntr+2+numIMUBytes])
                        pntr += 1
                    elif payloadrawData[pntr+1] == 'S':
                        if  pntr+2+numSweepBytes < len(payloadrawData):
                            if not strict_parse or payloadrawData[pntr+2+numSweepBytes] == '#':
                                sweeps.append(payloadrawData[pntr+2:pntr+2+numSweepBytes])
                        else:
                            sweeps.append(payloadrawData[pntr+2:pntr+2+numSweepBytes])
                        pntr += 1
                    elif payloadrawData[pntr+1] == 'J':
                        if pntr+2+numIMUBytes < len(payloadrawData):
                            if not strict_parse or payloadrawData[pntr+2+numIMUBytes] == '#':
                                imuRpt.append(payloadrawData[pntr+2:pntr+2+numIMUBytes])
                        else:
                            imuRpt.append(payloadrawData[pntr+2:pntr+2+numIMUBytes])
                        pntr += 1
                    elif payloadrawData[pntr+1] == 'T':
                        if  pntr+2+numSweepBytes < len(payloadrawData):
                            if not strict_parse or payloadrawData[pntr+2+numSweepBytes] == '#':
                                sweepsRpt.append(payloadrawData[pntr+2:pntr+2+numSweepBytes])
                        else:
                            sweepsRpt.append(payloadrawData[pntr+2:pntr+2+numSweepBytes])
                        pntr += 1
                    elif payloadrawData[pntr+1] == 'B':
                        if  pntr+2+numInterruptBytes < len(payloadrawData):
                            if not strict_parse or payloadrawData[pntr+2+numInterruptBytes] == '#':
                                interrupt.append(payloadrawData[pntr+2:pntr+2+numInterruptBytes])
                        else:
                            interrupt.append(payloadrawData[pntr+2:pntr+2+numInterruptBytes])
                        pntr += 1
                    else:
                        pntr += 1
                else:
                    pntr += 1
            print("Num IMU Messages: %s" %len(imu))
            print("Num Sweep Messages: %s" %len(sweeps))
            print("Num IMU Messages (buffer): %s" %len(imuRpt))
            print("Num Sweep Messages (buffer): %s" %len(sweepsRpt))
            print("Num interrupt messages: %s" %len(interrupt))

            ########### Build data structures ###########
            # First the IMU/IMU Buffer
            imuTime = [];
            ax = []; ay = []; az = []
            mx = []; my = []; mz = []
            gx = []; gy = []; gz = []
            temp = [];
            
            imuTimeRpt = [];
            axRpt = []; ayRpt = []; azRpt = []
            mxRpt = []; myRpt = []; mzRpt = []
            gxRpt = []; gyRpt = []; gzRpt = []
            tempRpt = [];
            
            for i in imu:
                if len(i) == numIMUBytes:
                    imuTime.append(combine4(ord(i[3]), ord(i[2]), ord(i[1]), ord(i[0])))
                    # The byte order is reversed, but the data sets are not
                    ax.append(combine2(ord(i[5]), ord(i[4])))
                    ay.append(combine2(ord(i[7]), ord(i[6])))
                    az.append(combine2(ord(i[9]), ord(i[8])))
                    mx.append(combine2(ord(i[11]), ord(i[10])))
                    my.append(combine2(ord(i[13]), ord(i[12])))
                    mz.append(combine2(ord(i[15]), ord(i[14])))
                    gx.append(combine2(ord(i[17]), ord(i[16])))
                    gy.append(combine2(ord(i[19]), ord(i[18])))
                    gz.append(combine2(ord(i[21]), ord(i[20])))
                    temp.append(combine2(ord(i[23]), ord(i[22])))
            
            for i in imuRpt:
                if len(i) == numIMUBytes:
                    imuTimeRpt.append(combine4(ord(i[3]), ord(i[2]), ord(i[1]), ord(i[0])))
                    axRpt.append(combine2(ord(i[5]), ord(i[4])))
                    ayRpt.append(combine2(ord(i[7]), ord(i[6])))
                    azRpt.append(combine2(ord(i[9]), ord(i[8])))
                    mxRpt.append(combine2(ord(i[11]), ord(i[10])))
                    myRpt.append(combine2(ord(i[13]), ord(i[12])))
                    mzRpt.append(combine2(ord(i[15]), ord(i[14])))
                    gxRpt.append(combine2(ord(i[17]), ord(i[16])))
                    gyRpt.append(combine2(ord(i[19]), ord(i[18])))
                    gzRpt.append(combine2(ord(i[21]), ord(i[20])))
                    tempRpt.append(combine2(ord(i[23]), ord(i[22])))

            imuTime = np.array(imuTime, dtype='uint32')
            ax = np.array(ax, dtype='int16')
            ay = np.array(ay, dtype='int16')
            az = np.array(az, dtype='int16')
            mx = np.array(mx, dtype='int16')
            my = np.array(my, dtype='int16')
            mz = np.array(mz, dtype='int16')
            gx = np.array(gx, dtype='int16')
            gy = np.array(gy, dtype='int16')
            gz = np.array(gz, dtype='int16')
            temp = np.array(temp, dtype='int16')
            
            imuTimeRpt = np.array(imuTimeRpt, dtype='uint32')
            axRpt = np.array(axRpt, dtype='int16')
            ayRpt = np.array(ayRpt, dtype='int16')
            azRpt = np.array(azRpt, dtype='int16')
            mxRpt = np.array(mxRpt, dtype='int16')
            myRpt = np.array(myRpt, dtype='int16')
            mzRpt = np.array(mzRpt, dtype='int16')
            gxRpt = np.array(gxRpt, dtype='int16')
            gyRpt = np.array(gyRpt, dtype='int16')
            gzRpt = np.array(gzRpt, dtype='int16')
            tempRpt = np.array(tempRpt, dtype='int16')

            payload.imu.time = imuTime
            payload.imu.ax = ax
            payload.imu.ay = ay
            payload.imu.az = az
            payload.imu.mx = mx
            payload.imu.my = my
            payload.imu.mz = mz
            payload.imu.gx = gx
            payload.imu.gy = gy
            payload.imu.gz = gz
            payload.imu.temp = temp
            
            payload.imu.timeRpt = imuTimeRpt
            payload.imu.axRpt = axRpt
            payload.imu.ayRpt = ayRpt
            payload.imu.azRpt = azRpt
            payload.imu.mxRpt = mxRpt
            payload.imu.myRpt = myRpt
            payload.imu.mzRpt = mzRpt
            payload.imu.gxRpt = gxRpt
            payload.imu.gyRpt = gyRpt
            payload.imu.gzRpt = gzRpt
            payload.imu.tempRpt = tempRpt

            # Then the sweeps
            payloadID = [];
            sweepTime = []
            allSweepsPIP0 = []
            individualSweepsPIP0 = []
            allSweepsPIP1 = []
            individualSweepsPIP1 = []
            PIP0StartByte = 4 + 1                             # Four for time, one payload ID  
            PIP0StopByte = PIP0StartByte + sweepSamples*2   # Number of samples, two bytes each
            PIP1StopByte = PIP0StopByte + sweepSamples*2      # Number of samples, two bytes each
            
            sweepTimeRpt = []
            allSweepsPIP0Rpt = []
            individualSweepsPIP0Rpt = []
            allSweepsPIP1Rpt = []
            individualSweepsPIP1Rpt = []
            PIP0StartByteRpt = 4 + 1                             # Four for time, one payload ID  
            PIP0StopByteRpt = PIP0StartByteRpt + sweepSamples*2   # Number of samples, two bytes each
            PIP1StopByteRpt = PIP0StopByteRpt + sweepSamples*2      # Number of samples, two bytes each
            
            for i in sweeps:
                if len(i) == numSweepBytes:
                    sweepTime.append(combine4(ord(i[3]), ord(i[2]), ord(i[1]), ord(i[0])))
                    payloadID.append(ord(i[4]))
                    tempSweep = []
                    for byte in xrange(PIP0StartByte,PIP0StopByte,2):
                        allSweepsPIP0.append(combine2(ord(i[byte+1]), ord(i[byte])))
                        tempSweep.append(combine2(ord(i[byte+1]), ord(i[byte])))
                    individualSweepsPIP0.append(tempSweep)
                    tempSweep = []
                    for byte in xrange(PIP0StopByte,PIP1StopByte,2):
                        allSweepsPIP1.append(combine2(ord(i[byte+1]), ord(i[byte])))
                        tempSweep.append(combine2(ord(i[byte+1]), ord(i[byte])))
                    individualSweepsPIP1.append(tempSweep)
                    
            for i in sweepsRpt:
                if len(i) == numSweepBytes:
                    sweepTimeRpt.append(combine4(ord(i[3]), ord(i[2]), ord(i[1]), ord(i[0])))
                    tempSweepRpt = []
                    for byte in xrange(PIP0StartByteRpt,PIP0StopByteRpt,2):
                        allSweepsPIP0Rpt.append(combine2(ord(i[byte+1]), ord(i[byte])))
                        tempSweepRpt.append(combine2(ord(i[byte+1]), ord(i[byte])))
                    individualSweepsPIP0Rpt.append(tempSweepRpt)
                    tempSweepRpt = []
                    for byte in xrange(PIP0StopByteRpt,PIP1StopByteRpt,2):
                        allSweepsPIP1Rpt.append(combine2(ord(i[byte+1]), ord(i[byte])))
                        tempSweepRpt.append(combine2(ord(i[byte+1]), ord(i[byte])))
                    individualSweepsPIP1Rpt.append(tempSweepRpt)
                    
            interruptTime = []        
            for i in interrupt:
                if len(i) == numInterruptBytes:
                    interruptTime.append(combine4(ord(i[3]), ord(i[2]), ord(i[1]), ord(i[0])))
                               
            payloadMatch = (len(set(payloadID)) == 1)
            if payloadMatch:
                print("Payload ID's match. This was payload #%s." %payloadID[0])
            else:
                print("Payload ID's don't match. Something went wrong...")
                
            sweepTime = np.array(sweepTime, dtype='uint32')
            individualSweepsPIP0 = np.array(individualSweepsPIP0, dtype='int16')
            individualSweepsPIP1 = np.array(individualSweepsPIP1, dtype='int16')
            payload.shieldID = payloadID[0]
            payload.sweeps.time = sweepTime
            payload.sweeps.pip0 = individualSweepsPIP0
            payload.sweeps.pip1 = individualSweepsPIP1
            
            sweepTimeRpt = np.array(sweepTimeRpt, dtype='uint32')
            individualSweepsPIP0Rpt = np.array(individualSweepsPIP0Rpt, dtype='int16')
            individualSweepsPIP1Rpt = np.array(individualSweepsPIP1Rpt, dtype='int16')
            payload.sweeps.timeRpt = sweepTimeRpt
            payload.sweeps.pip0Rpt = individualSweepsPIP0Rpt
            payload.sweeps.pip1Rpt = individualSweepsPIP1Rpt


        # In[3]:


        ################################## Forming and Scaling Data ##################################### 

        sweepSize = 28
        sweepStepDt = 0.02 / sweepSize

        # Define as None for no limits
        timeMin = None # 485 produces better plots than 480
        timeMax = None

        # Set by the time limits automatically
        timesToSkip = 30 # To impove the quality of sample numbering selection
        IMUSampleMin = None
        IMUSampleMax = None
        SweepSampleMin = None
        SweepSampleMax = None

        for payload in payloads:
            # Extract data from each set, cast into arrays
            aScale = 4*9.8; mScale = 1.; gScale = 2000./360
            
            imuTime = np.array(payload.imu.time)/1.E6;
            sweepTime = np.array(payload.sweeps.time)/1.E6
            
            imuTimeRpt = np.array(payload.imu.timeRpt)/1.E6;
            sweepTimeRpt = np.array(payload.sweeps.timeRpt)/1.E6
            
            # Figure out what the sample bounds should be
            if timeMin:
                IMUSampleMin = np.where(imuTime>=timeMin)[0][timesToSkip]
                IMUSampleMax = np.where(imuTime<=timeMax)[0][-1 * timesToSkip]
                SweepSampleMin = np.where(sweepTime>=timeMin)[0][timesToSkip]
                SweepSampleMax = np.where(sweepTime<=timeMax)[0][-1 * timesToSkip]
            imuTime = imuTime[IMUSampleMin:IMUSampleMax]
            sweepTime = sweepTime[SweepSampleMin:SweepSampleMax]
            
            ############################################################
            ##Bringing in from parse_erpabob-2 to use for lineplots
            # Flatten out sweepSampleTime 
            sweepSampleTime = []
            for t in sweepTime:
                for n in range(0, sweepSize):
                    sweepSampleTime.append(t+sweepStepDt*n)
            sweepSampleTime = np.array(sweepSampleTime)
            
            pip0 = np.array(payload.sweeps.pip0)*5./2**14
            pip1 = np.array(payload.sweeps.pip1)*5./2**14
            pip1L = pip1.flatten();
            pip0L = pip0.flatten();
            
            sweepSampleTimeRpt = []
            for t in sweepTimeRpt: 
                for n in range(0, sweepSize):
                    sweepSampleTimeRpt.append(t+sweepStepDt*n)
            sweepSampleTimeRpt = np.array(sweepSampleTimeRpt)
            
            pip0Rpt = np.array(payload.sweeps.pip0Rpt)*5./2**14
            pip1Rpt = np.array(payload.sweeps.pip1Rpt)*5./2**14
            pip0RptL = pip0Rpt.flatten();
            pip1RptL = pip1Rpt.flatten();
            #SweepSampleMin = SweepSampleMin * sweepSize # Scale up sizing
            #SweepSampleMax = SweepSampleMax * sweepSize
            ############################################################
             
            # Make everything an array
            interruptArray = np.array(interruptTime)/10**6
            
            temp = payload.imu.temp[IMUSampleMin:IMUSampleMax];
            ax = np.array(payload.imu.ax[IMUSampleMin:IMUSampleMax])*aScale/2**15
            ay = np.array(payload.imu.ay[IMUSampleMin:IMUSampleMax])*aScale/2**15
            az = np.array(payload.imu.az[IMUSampleMin:IMUSampleMax])*aScale/2**15
            mx = np.array(payload.imu.mx[IMUSampleMin:IMUSampleMax])*mScale/2**15
            my = np.array(payload.imu.my[IMUSampleMin:IMUSampleMax])*mScale/2**15
            mz = np.array(payload.imu.mz[IMUSampleMin:IMUSampleMax])*mScale/2**15
            gx = np.array(payload.imu.gx[IMUSampleMin:IMUSampleMax])*gScale/2**15
            gy = np.array(payload.imu.gy[IMUSampleMin:IMUSampleMax])*gScale/2**15
            gz = np.array(payload.imu.gz[IMUSampleMin:IMUSampleMax])*gScale/2**15
            shieldID = payload.shieldID
            pip0 = np.array(payload.sweeps.pip0)*5./2**14
            pip1 = np.array(payload.sweeps.pip1)*5./2**14
            
            tempRpt = payload.imu.tempRpt[IMUSampleMin:IMUSampleMax];
            axRpt = np.array(payload.imu.axRpt[IMUSampleMin:IMUSampleMax])*aScale/2**15
            ayRpt = np.array(payload.imu.ayRpt[IMUSampleMin:IMUSampleMax])*aScale/2**15
            azRpt = np.array(payload.imu.azRpt[IMUSampleMin:IMUSampleMax])*aScale/2**15
            mxRpt = np.array(payload.imu.mxRpt[IMUSampleMin:IMUSampleMax])*mScale/2**15
            myRpt = np.array(payload.imu.myRpt[IMUSampleMin:IMUSampleMax])*mScale/2**15
            mzRpt = np.array(payload.imu.mzRpt[IMUSampleMin:IMUSampleMax])*mScale/2**15
            gxRpt = np.array(payload.imu.gxRpt[IMUSampleMin:IMUSampleMax])*gScale/2**15
            gyRpt = np.array(payload.imu.gyRpt[IMUSampleMin:IMUSampleMax])*gScale/2**15
            gzRpt = np.array(payload.imu.gzRpt[IMUSampleMin:IMUSampleMax])*gScale/2**15
            pip0Rpt = np.array(payload.sweeps.pip0Rpt)*5./2**14
            pip1Rpt = np.array(payload.sweeps.pip1Rpt)*5./2**14
            
            print("Data Scaled")
        ############################ Padding Data #######################################

            # Change time data to list form for padding
            imuList = imuTime.tolist()
            sweepList = sweepTime.tolist()
            
            imuListRpt = imuTimeRpt.tolist()
            sweepListRpt = sweepTimeRpt.tolist()
            
            # Find correct delta t
            imuDelt = round(((imuList[DeltInx[1]] - imuList[DeltInx[0]]) / DeltInx[2]), 4)
            sweepDelt = round(((sweepList[DeltInx[1]] - sweepList[DeltInx[0]]) / DeltInx[2]), 4)
            
            imuDeltRpt = round(((imuListRpt[DeltInx[1]] - imuListRpt[DeltInx[0]]) / DeltInx[2]), 4)
            sweepDeltRpt = round(((sweepListRpt[DeltInx[1]] - sweepListRpt[DeltInx[0]]) / DeltInx[2]), 4)
            print("Deltas found")
            newImuTime =  []
            newSweepTime = []
            
            newImuTimeRpt =  []
            newSweepTimeRpt = []
            
            # iterate through IMU twice to better fill gaps
            timefix(imuList, newImuTime, imuDelt)
            timefix(imuList, newImuTime, imuDelt)
            print("IMU Original")
            
            timefix(imuListRpt, newImuTimeRpt, imuDeltRpt)
            timefix(imuListRpt, newImuTimeRpt, imuDeltRpt)
            print("IMU Time Done")
            
            # iterate through sweep
            timefix(sweepList, newSweepTime, sweepDelt)
            timefix(sweepList, newSweepTime, sweepDelt)
            print("Sweep Original")
            
            timefix(sweepListRpt, newSweepTimeRpt, sweepDeltRpt)
            timefix(sweepListRpt, newSweepTimeRpt, sweepDeltRpt)
            
            print("Sweep Time Done")
            
            # change back to array
            imuList = np.array(imuList)
            sweepList = np.array(sweepList)
            
            imuListRpt = np.array(imuListRpt)
            sweepListRpt = np.array(sweepListRpt)
            
            # reshape all data
            ax = np.reshape(ax, (len(ax), 1))
            ay = np.reshape(ay, (len(ay), 1))
            az = np.reshape(az, (len(az), 1))
            gx = np.reshape(gx, (len(gx), 1))
            gy = np.reshape(gy, (len(gy), 1))
            gz = np.reshape(gz, (len(gz), 1))
            mx = np.reshape(mx, (len(mx), 1))
            my = np.reshape(my, (len(my), 1))
            mz = np.reshape(mz, (len(mz), 1))
            temp = np.reshape(temp, (len(temp), 1))
            
            axRpt = np.reshape(axRpt, (len(axRpt), 1))
            ayRpt = np.reshape(ayRpt, (len(ayRpt), 1))
            azRpt = np.reshape(azRpt, (len(azRpt), 1))
            gxRpt = np.reshape(gxRpt, (len(gxRpt), 1))
            gyRpt = np.reshape(gyRpt, (len(gyRpt), 1))
            gzRpt = np.reshape(gzRpt, (len(gzRpt), 1))
            mxRpt = np.reshape(mxRpt, (len(mxRpt), 1))
            myRpt = np.reshape(myRpt, (len(myRpt), 1))
            mzRpt = np.reshape(mzRpt, (len(mzRpt), 1))
            tempRpt = np.reshape(tempRpt, (len(tempRpt), 1))
            
            
            print("Rest Done")
        #     print("Length of IMUList is " + str(len(imuList)))
        #     print("Length of sweepList is " + str(len(sweepList)))
        #     print("Length of IMUList (buffer) is " + str(len(imuListRpt)))
        #     print("Length of sweepList (buffer) is " + str(len(sweepListRpt)))
            
            interruptValue = (len(set(interruptArray[100:200])) == 1)
            if interruptValue and len(interruptArray) > 100:
                 print("Time of interrupt is at " + str(interruptArray[100]) + " seconds.")
            else:
                 print("Something wrong. Interrupt time doesn't make sense.")


        # In[ ]:





        # In[4]:


        if notify_every: os.system('say "Done parsing data."')
        print ""


        # In[5]:


        # Changes screen voltage to nA

        highV2I = 1.0/(320.0E-3)
        lowV2I = 1.0/(40.0E-3)

        #pip0nA = (pip0-1)*highV2I
        #pip1nA = (pip1-1)*highV2I
        #pip0RptnA = (pip0Rpt-1)*highV2I
        #pip1RptnA = (pip1Rpt-1)*highV2I

        if np.any(shieldID == np.array([14, 16, 17, 22])):
            pip0V2I = highV2I
            pip1V2I = lowV2I
        elif np.any(shieldID == np.array([18, 21])): 
            pip0V2I = lowV2I
            pip1V2I = lowV2I
        else: #Shield 19 and 20 
            pip0V2I = highV2I
            pip1V2I = highV2I
            
        pip0nA = (pip0-1)*pip0V2I
        pip1nA = (pip1-1)*pip1V2I

        pip0RptnA = (pip0Rpt-1)*pip0V2I
        pip1RptnA = (pip1Rpt-1)*pip1V2I


        # In[6]:
        #### Save Pickle File ####
        dct = dict()
        version="Original"
        dct['shieldID']=shieldID; dct['interruptArray']=interruptArray
        dct['imuPlot']=imuList; dct['axPlot']=axPlot=ax; dct['ayPlot']=ay; dct['azPlot']=az
        dct['gxPlot']=gx; dct['gyPlot']=gy; dct['gzPlot']=gz; dct['mxPlot']=mx; dct['myPlot']=my; dct['mzPlot']=mz
        dct['tempPlot']=temp; dct['sweepPlot']=sweepList; dct['sweepTimeLPlot']=sweepSampleTime
        dct['pip0Plot']=pip0nA; dct['pip1Plot']=pip1nA; dct['pip0LPlot']=pip0L; dct['pip1LPlot']=pip1L
        pklfname = path+"ParsedData_wDInx%sto%s-%s-%s.pkl" % (DeltInx[0], DeltInx[1], file_name.partition(".")[0], version)
        pklf = open(pklfname, "wb"); pickle.dump(dct, pklf); pklf.close()
        print pklfname
        del pklf, pklfname, dct

        dct=dict()
        version = "Repeat"
        dct['shieldID']=shieldID; dct['interruptArray']=interruptArray
        dct['imuPlot']=imuListRpt; dct['axPlot']=axRpt; dct['ayPlot']=ayRpt; dct['azPlot']=azRpt
        dct['gxPlot']=gxRpt; dct['gyPlot']=gyRpt; dct['gzPlot']=gzRpt; dct['mxPlot']=mxRpt; dct['myPlot']=myRpt; dct['mzPlot']=mzRpt
        dct['tempPlot']=tempRpt; dct['sweepPlot']=sweepListRpt; dct['sweepTimeLPlot']=sweepSampleTimeRpt
        dct['pip0Plot']=pip0RptnA; dct['pip1Plot']=pip1RptnA; dct['pip0LPlot']=pip0RptL; dct['pip1LPlot']=pip1RptL
        pklfname = path+"ParsedData_wDInx%sto%s-%s-%s.pkl" % (DeltInx[0], DeltInx[1], file_name.partition(".")[0], version)
        pklf = open(pklfname, "wb"); pickle.dump(dct, pklf); pklf.close()
        print pklfname


        # choose original or repeat
#        plottype = 1

        if plottype == 1:
            version = 'Original'
            imuPlot = imuList
            axPlot = ax
            ayPlot = ay
            azPlot = az
            gxPlot = gx
            gyPlot = gy
            gzPlot = gz
            mxPlot = mx
            myPlot = my
            mzPlot = mz
            tempPlot = temp
            sweepPlot = sweepList
            pip0Plot = pip0nA
            pip1Plot = pip1nA 
            
            pip0LPlot = pip0L
            pip1LPlot = pip1L
            sweepTimeLPlot = sweepSampleTime
            
        elif plottype == 2:
            version = 'Repeat'
            imuPlot = imuListRpt
            axPlot = axRpt
            ayPlot = ayRpt
            azPlot = azRpt
            gxPlot = gxRpt
            gyPlot = gyRpt
            gzPlot = gzRpt
            mxPlot = mxRpt
            myPlot = myRpt
            mzPlot = mzRpt
            tempPlot = tempRpt
            sweepPlot = sweepListRpt
            pip0Plot = pip0RptnA
            pip1Plot = pip1RptnA
            
            pip0LPlot = pip0RptL
            pip1LPlot = pip1RptL
            sweepTimeLPlot = sweepSampleTimeRpt


        # In[7]:


        magfullPlot = mxPlot**2+myPlot**2+mzPlot**2


        # In[8]:


        # print sweepPlot[-2688]; print sweepPlot[-2687]; print sweepPlot[0]
        # print imuPlot[-2690]; print imuPlot[-2689]
        # print np.where(sweepPlot==sweepPlot[-2688])
        # np.where(np.round(sweepPlot, decimals=0)==618)[0][-1]


        # In[9]:


        # # sweepPlot[0:11] = 0
        # sweepPlot[-2] = sweepPlot[-3]+sweepDelt
        # sweepPlot[-1] = sweepPlot[-2]+sweepDelt

        upbnd=None
        # upbnd = 1589.
        if np.any(dataFile == np.array(bad_tmwrd_files)): 
            if upbnd is None: error_locs = np.where(np.array(sweepPlot)<sweepPlot[0])[0]
            else: error_locs = np.where(np.logical_or(np.array(sweepPlot)<sweepPlot[0], upbnd<np.array(sweepPlot)))[0]
            # print sweepPlot[error_locs]; print error_locs
            for inx in error_locs: sweepPlot[inx]=sweepPlot[inx-1]+sweepDelt
        #     sweepLDelt = np.mean(np.diff(sweepTimeLPlot)[0:1000])
            print "Replaced %s bad timewords" % (len(error_locs))
            error_bk = np.array([loc for loc in error_locs])
        # elif np.any(dataFile == np.array(pwr_cycle_files[0][:])):
        #     loc = np.where(dataFile == np.array(pwr_cycle_files[0]))[0]
        #     np.where(np.round(sweepPlot, decimals=0)==final_val[[0][-1]
        # print np.where(np.array(imuPlot)<imuPlot[0])[0]
        # print np.where(np.logical_or(np.array(sweepTimeLPlot)<sweepTimeLPlot[0], np.array(sweepTimeLPlot)>(sweepPlot[-1]+5)))[0]
        # print np.where(np.array(sweepTimeLPlot)>(sweepPlot[-1]+5))[0]
        # print imuPlot[np.where(np.array(imuPlot)<imuPlot[0])[0][0]-1]
        # print sweepTimeLPlot[np.where(np.array(sweepTimeLPlot)<sweepTimeLPlot[0])[0]]
        # print np.unique(np.diff(np.where(np.array(imuPlot)<imuPlot[0])[0]))
        # print np.mean(np.diff(imuPlot)[0:1000])
        # print imuDelt
        # print sweepDelt
        # print np.unique(np.diff(sweepTimeLPlot)[0:101])
        # print np.mean(np.diff(sweepTimeLPlot)[0:1000])
        # print np.diff(sweepTimeLPlot)[0]


        # In[50]:

        #Modify PIP Lineplots' and colorplots' x-axis limits and set PIP colorplots' colorbar limits
        # xlims = [200, 200.5]
        # xlims2 = [400, 400.5]
        if Xlims == 'default': 
            xlims = [sweepPlot[0]-5, sweepPlot[-1]+5]
            xlims2 = [sweepPlot[0]-5, sweepPlot[-1]+5]
        elif Xlims is None: 
            xlims, xlims2 = None, None
        else: 
            xlims, xlims2 = Xlims

        # xlims = [sweepPlot[0]-5, 625]
        # xlims2 = [sweepPlot[0]-5, 625]

### Delete? ***
        # cplt_kwargs={'pip0': {'vmin':0, 'vmax':50}, 'pip1':{'vmin':0, 'vmax':50}}
#        cplt_kwargs={'pip0': {}, 'pip1':{}}
#
#        figsuffix = None
#        yLnZooms = dict()
#        xLnZooms = dict()
#
#        figsuffix = "ZoomB"
#        yLnZooms['cad'] = [15, 55]
#        # # # # # del yLnZooms['accel']
#        # # yLnZooms['accel'] = [-2.5, 10.75]
#        # # yLnZooms['mag'] = [-0.125, 0.035]
#        # # yLnZooms['gyro'] = [-0.041, 0.025]
#        yLnZooms['pip0']=[0, 10]
#        yLnZooms['pip1']=[0, 5]
#        # yLnZooms['pip0'] = [np.mean(pip0LPlot)-.005, np.mean(pip0LPlot)+.005]
#        # yLnZooms['pip1'] = [np.mean(pip1LPlot)-.005, np.mean(pip1LPlot)+.005]
#        # # # # # # # # # # # # # xLnZooms={'axis1':[1320,1400], 'xCzoom': 1000}
#        # # # # # # # # xLnZooms={'axis1':[2123, 3180]}
#        # xLnZooms['xCzoom'] = 1000
##        figsuffix = "ZoomB2"
##        xlims = [800, sweepPlot[-1]]
##        xlims2 = [800, sweepPlot[-1]]
##        figsuffix = "ZoomB_cbar0-20and0-5"
##        xlims = [1150, 1250]
##        xlims2 = [1150, 1250]
##        cplt_kwargs={'pip0': {'vmin':0, 'vmax':8}, 'pip1':{'vmin':0, 'vmax':20}}
###  *********

        #Modify PIP Lineplots' ylims and Cadance plot ylims
        ## Zoom in PIP Noise and x-axis of Cadance
        # figsuffix = "Zoom"
        # # ylims, ylims2 = None, None
        # # ylims, ylims2 = ([1.015, 1.035], [1.015, 1.035])
        # ylims = [np.mean(pip0LPlot)-.005, np.mean(pip0LPlot)+.0075]
        # ylims2 = [np.mean(pip1LPlot)-.005, np.mean(pip1LPlot)+.005]
        # # # ylims = [np.mean(pip0LPlot)-0.005, np.mean(pip0LPlot)+07.0025]
        # # # ylims2 = [np.mean(pip1LPlot)-0.0025, np.mean(pip1LPlot)+0.0025]
        # ylimsC = [-1, 50]
        # xCzoom = 1000
        ## Zoom in on Cadance y-axis and Zoom in a little on PIPs 
        # figsuffix = "Zoom2"
        # ylims, ylims2 = None, None
        # xLnlims= [1475, 1590] #[2650, 2680]
        # # ylims, ylims2 = [-5,5], [-5,5]
        # ylims = [np.mean(pip0LPlot)-0.0025, np.mean(pip0LPlot)+0.0025]
        # ylims2 = [np.mean(pip1LPlot)-0.0025, np.mean(pip1LPlot)+0.0025]
        # ylimsC = [15,50]

        # figsuffix = "ZoomA"
        # yLnZooms['cad'] = [0, 50]
        # EVT = 1493-8
        # yLnZooms['accel']=[-11, 5]
        # yLnZooms['mag']= [-0.15, 0.25]
        # yLnZooms['gyro'] = [-0.0975, 0.09975]
        # # # yLnZooms['pip0']=[1.005, 1.02]
        # # # yLnZooms['pip1']=[1.005, 1.02]
        # yLnZooms['pip0'] = [np.mean(pip0LPlot)-.005, np.mean(pip0LPlot)+.005]
        # yLnZooms['pip1'] = [np.mean(pip1LPlot)-.005, np.mean(pip1LPlot)+.005]
        # xLnZooms={'xCzoom': 1000}
        # # xLnZooms['axis1']=[sweepPlot[0]-5, 1408]
        # For Deploy ONLY: 
        # xLnZooms['axis1'] = [EVT-5, EVT+10]
#
#        figsuffix = "ZoomB"
#        yLnZooms['cad'] = [15, 55]
#        # # # # # del yLnZooms['accel']
#        # # yLnZooms['accel'] = [-2.5, 10.75]
#        # # yLnZooms['mag'] = [-0.125, 0.035]
#        # # yLnZooms['gyro'] = [-0.041, 0.025]
#        yLnZooms['pip0']=[0, 10]
#        yLnZooms['pip1']=[0, 5]
#        # yLnZooms['pip0'] = [np.mean(pip0LPlot)-.005, np.mean(pip0LPlot)+.005]
#        # yLnZooms['pip1'] = [np.mean(pip1LPlot)-.005, np.mean(pip1LPlot)+.005]
#        # # # # # # # # # # # # # xLnZooms={'axis1':[1320,1400], 'xCzoom': 1000}
#        # # # # # # # # xLnZooms={'axis1':[2123, 3180]}
#        # xLnZooms['xCzoom'] = 1000
##        figsuffix = "ZoomB2"
##        xlims = [800, sweepPlot[-1]]
##        xlims2 = [800, sweepPlot[-1]]
##        figsuffix = "ZoomB_cbar0-20and0-5"
##        xlims = [1150, 1250]
##        xlims2 = [1150, 1250]
##        cplt_kwargs={'pip0': {'vmin':0, 'vmax':8}, 'pip1':{'vmin':0, 'vmax':20}}

        # figsuffix = "ZoomB2"
        # xLnZooms['xCzoom'] = 1000
        # # figsuffix = 'Zoom1B'
        # yLnZooms['pip0']=[0.9, 1.2]
        # yLnZooms['pip1']=[0.9, 1.2]

        # # figsuffix = 'ZoomA'; xLnZooms={'xCzoom': 1000}; yLnZooms={'gyro': [-0.0975, 0.09975], 'mag': [-0.15, 0.25], 'cad': [0, 50]}
        # figsuffix = 'ZoomB'; xLnZooms={'xCzoom': 1000, 'axis1': [490, 580]}; yLnZooms={'pip1': [0.9375, 1.055], 'pip0': [0.955, 1.055], 'gyro': [-0.15, 0.075], 'accel': [-11.8, 36.9], 'mag': [-0.21, 0.15], 'cad': [15, 55]}


        # In[51]:


        print yLnZooms
        # print np.mean(pip0LPlot)
        # print np.mean(pip1LPlot)
        print 'Final IMU Time:', imuPlot[-1]


        # In[52]:


#        matplotlib.use('nbagg')
#        import matplotlib.cm as cm
#        import scipy.signal as sig
#        from scipy.interpolate import interp1d
#        from scipy.io import savemat, loadmat
#        from __future__ import division

        dots = True

        gs_left = plt.GridSpec(6, 2,  hspace=0.7)

        # Set up dots or not more cleanly
        line_style = '-'
        if dots:
            line_style = '.'

        markersize = 1

        fig = plt.figure(figsize=(10, 7.5))

        # Accel
        axis1 = fig.add_subplot(gs_left[0,0])
        plt.plot(imuPlot, axPlot, line_style, markersize=markersize, label='ax') 
        plt.plot(imuPlot, ayPlot, line_style, markersize=markersize, label='ay')  
        plt.plot(imuPlot, azPlot, line_style, markersize=markersize, label='az') 
        plt.ylabel("Accel (m/s$^2$)")
        #plt.ylim([-2, 2])
        #plt.xlim([75, 100])
        if figsuffix is not None: 
            if np.any('accel'==np.array(yLnZooms.keys())): plt.ylim(yLnZooms['accel'])
        if figsuffix=="Zoom2": plt.xlim(xLnlims)
        plt.xticks(visible=True)
        plt.xlabel("Time (s)")
        print ("1 Done")

        # Mag
        fig.add_subplot(gs_left[1,0], sharex=axis1)
        plt.plot(imuPlot, mxPlot, line_style, markersize=markersize, label='mx') 
        plt.plot(imuPlot, myPlot, line_style, markersize=markersize, label='my')  
        plt.plot(imuPlot, mzPlot, line_style, markersize=markersize, label='mz') 
        plt.plot(imuPlot, magfullPlot, line_style, markersize=markersize, color='black', label='magfull')
        #plt.ylim([-0.2, 0.25])
        plt.ylabel("Mag (Gauss)")
        if figsuffix is not None: 
            if np.any('mag'==np.array(yLnZooms.keys())): plt.ylim(yLnZooms['mag'])
        if figsuffix=="Zoom2": plt.xlim(xLnlims)
        plt.xticks(visible=True)
        plt.xlabel("Time (s)")
        print ("2 Done")

        # Gyro
        fig.add_subplot(gs_left[2,0], sharex=axis1)
        plt.plot(imuPlot, gxPlot, line_style, markersize=markersize, label='gx') 
        plt.plot(imuPlot, gyPlot, line_style, markersize=markersize, label='gy')  
        plt.plot(imuPlot, gzPlot, line_style, markersize=markersize, label='gz') 
        plt.ylabel("Gyro (Hz)")
        #plt.ylim([-0.5, 0.5])  
        #plt.xlim([75, 100])
        if figsuffix is not None: 
            if np.any('gyro'==np.array(yLnZooms.keys())): plt.ylim(yLnZooms['gyro'])
        if figsuffix=="Zoom2": plt.xlim(xLnlims)
        plt.xticks(visible=True)
        plt.xlabel("Time (s)")
        print ("3 Done")

        # First PIP (line)
        fig.add_subplot(gs_left[3,0], sharex=axis1)
        plt.plot(sweepTimeLPlot, pip0LPlot, line_style, markersize=markersize)
        plt.ylabel("PIP0 (V)")
        #plt.ylim([1.01, 1.03])
        #plt.ylim([1.0075, 1.0125])
        if figsuffix is not None: 
            if np.any('pip0'==np.array(yLnZooms.keys())): plt.ylim(yLnZooms['pip0'])
            if figsuffix=='Zoom': plt.ylim(ylims)
        plt.xlim(xlims)
        if figsuffix=="Zoom2": plt.xlim(xLnlims)
        print("4 Done")

        # Second PIP (line)
        fig.add_subplot(gs_left[4,0], sharex=axis1)
        plt.plot(sweepTimeLPlot, pip1LPlot, line_style, markersize=markersize)
        #plt.ylim([1.027, 1.033])
        #plt.ylim([1.011, 1.013])
        if figsuffix is not None: 
            if np.any('pip1'==np.array(yLnZooms.keys())): plt.ylim(yLnZooms['pip1'])
            if figsuffix=='Zoom': plt.ylim(ylims2)
        plt.xlim(xlims2)
        if figsuffix=="Zoom2": plt.xlim(xLnlims)
        plt.ylabel("PIP1 (V)")
        print("5 Done")

        # Make any last changes to axis1's x-axis limits
        if figsuffix is not None and np.any('axis1'==np.array(xLnZooms.keys())): axis1.set_xlim(xLnZooms['axis1'])

        # Cadence (sweep on top)
        axis2 = fig.add_subplot(gs_left[5,0])
        plt.plot(np.diff(imuPlot*1E3), line_style, color='blue', markersize=markersize)
        plt.plot(np.diff(sweepPlot)*1E3, line_style, color='red', markersize=markersize)
        if figsuffix is not None: 
            if figsuffix == "Zoom": 
                plt.xlim([np.round(plt.axis()[1]/2-xCzoom, decimals=-3), np.round(plt.axis()[1]/2, decimals=-3)+xCzoom])
                axis2.set_xticks(axis2.get_xticks()[::2])
                plt.ylim(ylimsC)
            if np.any('cad'==np.array(yLnZooms.keys())): plt.ylim(yLnZooms['cad'])
        #plt.ylim([22,25])
        #plt.xlim([200,400])
        if figsuffix=="Zoom2": plt.xlim(xLnlims)
        plt.ylabel("Cadences (ms)\n IMU-Blue\n Sweep-Red")
        plt.xlabel("Index")
        print ("6 Done")

        # Cadence (imu on top)
        fig.add_subplot(gs_left[5,1], sharex=axis2, sharey=axis2)
        plt.plot(np.diff(sweepPlot)*1E3, line_style, color='red', markersize=markersize)
        plt.plot(np.diff(imuPlot*1E3), line_style, color='blue', markersize=markersize)
        #plt.ylim([22,25])
        if figsuffix is not None: 
            if figsuffix == "Zoom": 
                plt.xlim([np.round(plt.axis()[1]/2-xCzoom, decimals=-3), np.round(plt.axis()[1]/2, decimals=-3)+xCzoom])
                axis2.set_xticks(axis2.get_xticks()[::2])
                plt.ylim(ylimsC)
            if np.any('cad'==np.array(yLnZooms.keys())): plt.ylim(yLnZooms['cad'])
        #plt.xlim([200,400])
        if figsuffix=="Zoom2": plt.xlim(xLnlims)
        plt.xlabel("Index")
        print ("7 Done")

        # Make any last changes to axis2's x-axis limits
        if figsuffix is not None: #and not np.all('axis1'==np.array(xLnZooms.keys())):
            # Zoom into the center of the x-axis
            if np.any('xCzoom'==np.array(xLnZooms.keys())):
                axis2.set_xlim([np.round(plt.axis()[1]/2-xLnZooms['xCzoom'], decimals=-3), np.round(plt.axis()[1]/2, decimals=-3)+xLnZooms['xCzoom']])
                axis2.set_xticks(axis2.get_xticks()[::2])
            # Zoom into the specified x-axis limits
            elif np.any('axis2'==np.array(xLnZooms.keys())):
                axis2.set_xlim(xLnZooms['axis2'])
            
        # **Plot sweep time vs sweep data (Color plots)**

        # commands to reorient pip array to match with other axes
        pip0_rot = np.rot90(pip0Plot, k=1, axes=(0, 1))
        pip1_rot = np.rot90(pip1Plot, k=1, axes=(0, 1))

        sweep_voltage = np.linspace(0,5,28)

        line_style = '-'

        ax1 = plt.subplot2grid((5,2),(0,1),rowspan = 2)
        plt.pcolormesh(sweepPlot, sweep_voltage, pip0_rot, cmap='plasma', **cplt_kwargs['pip0'])
        plt.xlim(xlims)
        ax1.set_xlabel("Flight Time (s)")
        ax1.set_ylabel("Screen Bias (V)")
        cb = plt.colorbar(pad = 0.2)
        cb.set_label("PIP0 (nA)")
        print ("8 Done")

        ax1 = plt.subplot2grid((5,2),(2,1),rowspan = 2)
        plt.pcolormesh(sweepPlot, sweep_voltage, pip1_rot, cmap='plasma', **cplt_kwargs['pip1'])
        plt.xlim(xlims2)
        ax1.set_xlabel("Flight Time (s)")
        ax1.set_ylabel("Screen Bias (V)")
        cb = plt.colorbar(pad = 0.2)
        cb.set_label("PIP1 (nA)")
        print ("9 Done")
                
        # Adjust figure
        fig.subplots_adjust(right=.90)
        fig.subplots_adjust(left=0.10)
        fig.subplots_adjust(top=0.90)
        fig.subplots_adjust(bottom=0.10)
        fig.subplots_adjust(hspace=0.75)

        # if interruptValue and len(interruptArray) > 100:
        #     interruptNum = str(interruptArray[100]) + " seconds"

        # elif len(interruptArray) > 100:
        if len(interruptArray) > 100:
            numRec=0
            for event in np.unique(np.array(interruptArray)): 
        #         print "Number of recordings for %ss:" % (event), len(np.where(np.array(interruptArray) == event)[0]) 
                if len(np.where(np.array(interruptArray) == event)[0]) > numRec:
                    numRec = len(np.where(np.array(interruptArray) == event)[0])
                    if numRec>100: interruptNum = str(event) + " seconds"
#                    if numRec>100: interruptNum = str(event-8.00622) + " s (Corrected)"
                    else: interruptNum = "None"
        else:
            interruptNum = "None"
            
        plt.suptitle(file_name+"\n"+"Data from Shield %s (Version: %s)\n Interrupt Time: %s" 
                     %(shieldID, version, interruptNum), fontweight='bold')
            
#        plt.show()


        # In[46]:


        # yLnZooms['accel'] = [-4.5, 10.75]
        # yLnZooms['mag'] = [-0.125, 0.0525]
        # yLnZooms['gyro'] = [-0.0625, 0.025]
        # yLnZooms['pip0']=[1.0025, 1.0125]
        # yLnZooms['pip1']=[0.9975, 1.0075]
        # figsuffix = "Zoom_Ejection" # figsuffix = 'ZoomB'
        # figsuffix = "NoZooms"
        if not os.path.exists(path+fig_subpath): os.makedirs(path+fig_subpath)
        if figsuffix is None: figfname = path+fig_subpath+"Fig_%s_%sPlot.png" % (file_name.partition(".")[0], version)
        else: figfname = path+fig_subpath+"Fig_%s_%sPlot%s.png" % (file_name.partition(".")[0], version, figsuffix) 

        fig.savefig(figfname)
        # fig.axes[3].properties()['ylim']
        print("Saved Figure to "+figfname)

        plt.close()
        del fig, figfname
        del imuList, ax, ay, az, gx, gy, gz, mx, my, mz, temp, sweepList, pip0, pip1  
        del imuListRpt, axRpt, ayRpt, azRpt, gxRpt, gyRpt, gzRpt, mxRpt, myRpt, mzRpt, tempRpt, sweepListRpt, pip0Rpt, pip1Rpt 
        del imuPlot, axPlot, ayPlot, azPlot, gxPlot, gyPlot, gzPlot, mxPlot, myPlot, mzPlot , tempPlot, sweepPlot, pip0Plot, pip1Plot
        del dataFile, payload, payloads
        print "***********************\n"
    if notify: os.system('say "Done Parsing Files in Folder"') 
### End of Main Loop ###
###################################################################################


#        # In[18]:
#
#
#        arr = [axPlot, ayPlot, azPlot]; narr = ['x', 'y', 'z']
#        # arr = [mxPlot, myPlot, mzPlot, magfullPlot]; narr = ['x', 'y', 'z', 'full']
#        # arr = [gxPlot, gyPlot, gzPlot]; narr = ['x', 'y', 'z']
#        # arr = [pip0LPlot, pip1LPlot]; narr = ['pip0', 'pip1']
#        for val, name in zip(arr, narr): 
#            print name.upper(), 'Mean:', np.mean(np.round(val, decimals=3))
#            bnds= [int(len(val)/2-25), int(len(val)/2+25)]
#            print np.round(val, decimals=3)[bnds[0]: bnds[1]].transpose()
#        #     print 'Slice Mean:', np.mean(np.round(val[bnds[0]-100, bnds[1]+100], decimals=3))
#        # int(len(val)/2)
#        # len(val)
#
#
#
##        # In[18]:
##
##
##        # # print np.unique(np.diff(sweepTimeLPlot[np.where(np.logical_and(0<=np.diff(sweepTimeLPlot), sweepTimeLPlot[1:]>sweepTimeLPlot[0]))[0]+1]))
##        # print pip0LPlot
##        # print sweepTimeLPlot
##        # print sweepPlot[0] == sweepTimeLPlot[0]
##        # print np.diff(sweepTimeLPlot)[0]==0.0007142857143662695
##        # print np.where(np.diff(sweepTimeLPlot)<0)[0]
##        # print np.where(sweepTimeLPlot<sweepTimeLPlot[0])[0]
##        # print sweepTimeLPlot[227051], sweepTimeLPlot[227052]
##        # # print sweepTimeLPlot[np.where(np.logical_and(0<=np.diff(sweepTimeLPlot), sweepTimeLPlot[1:]>sweepTimeLPlot[0]))[0]+1]
##
##
##        # In[19]:
##
##
##        color_check=['#1f77b4', '#ff7f0e', '#2ca02c']
##        for ax_tmp in  fig.axes:
##            ln_lst = ax_tmp.lines[0:3]
##            ln.properties()['color']
##
##
##        # In[28]:
##
##
##        """%%%% Event Interrupt Details %%%%"""
##        #set(interruptArray)
##        print "File name %s" % dataFile
##        print"Num interrupt messages for payload %s: %s" %(payloadID[0], len(interrupt))
##        print "Num unique interrupt times: ", len(np.unique(np.array(interruptTime)/10.**6))
##        print '***************************************'
##        numRec = 0 
##        evtTime = None
##        if not len(interrupt)==0:
##            prev=np.unique(np.array(interruptTime)/10.**6)[0]
##            for event in np.unique(np.array(interruptTime)/10.**6): 
##                if int(np.floor(event-prev)) >= 30: print "-----------------------------------------"
##                print "Number of recordings for %ss:" % (event), len(np.where(np.array(interruptTime)/10.**6 == event)[0]) 
##                prev=event
##                if len(np.where(np.array(interruptTime)/10.**6 == event)[0]) > numRec:
##                    numRec = len(np.where(np.array(interruptTime)/10.**6 == event)[0])
##                    evtTime = event
##        else: 
##            print "No Event Interrupts Recieved"
##        print '\n***************************************'
##        print 'Offset from IMU/Sweep Times Used = %ss' % (8.00622)
##        print 'Reported Interrupt Time  = %ss' % (evtTime)
##        print 'Corrected Interrupt Time = %ss' % (np.round(evtTime-8.00622, decimals=6))
##
##
##        # In[12]:
##
##
##        print 'Final Time in imuPlot:        %ss' % (imuPlot[-1])
##        print 'Final Time in sweepTimeLPlot: %ss' % (sweepTimeLPlot[-1])
##        print 'Final Time in sweepPlot:      %ss' % (sweepPlot[-1])
##
##
##        # In[ ]:
##
##
##
##
##
##        # In[38]:
##
##
##        from prettytable import PrettyTable
##        ## PIP Voltage and Noise Analysis ##
##        print "%%%%%%%%%%%%%%%%%%%%%% Shield "+str(shieldID)+" PIP Voltage Levels %%%%%%%%%%%%%%%%%%%%%" 
##        # print "------------------------------------------------------------------------------------------------"
##        print "(%s)" % (file_name)
##        print "[Noise (in a PIP Measurement) = PIP Measured Voltage - PIP Mean Voltage]"
##        print "[Note: Nrel = PIP Measured Voltage - Max{ABS{Mean{V>=0}-Mean Voltage, Mean{V<0}-Mean Voltage}}"
##        t = PrettyTable(); t.right_padding_width=0; t.left_padding_width=0
##        t.field_names = ['Source', '|', 'Mean{Voltage}', 'Mean{V>=0}', 'Mean{V<0}', '', 'Mean{Noise}', 'Mean{|Noise|}', 'Mean{|N_rel|}']
##        sp_arr = [11, 1, 15, 12, 12, 0, 14, 15, 15]
##        # t.field_names = ['Source', '|', 'Mean{Voltage}', '', 'Mean{Noise}', 'Mean{|Noise|}']
##        # sp_arr = [11, 1, 15, 0, 14, 15]
##        charArr=['-']*len(t.field_names); charArr[t.field_names.index(u'|')] = '|'
##        for pipV_arr, name in zip([pip0L, pip0RptL, sp_arr, pip1L, pip1RptL], ['PIP 1', 'PIP 1 Rpt', 'split', 'PIP 2', 'PIP 2 Rpt']): 
##            if name is not 'split':
##                row_arr = [name, '|']
##                row_arr.append('~ %s V' %(np.format_float_positional(np.nanmean(pipV_arr), precision=3)))
##                row_arr.append('~ %s V' %(np.format_float_positional(np.nanmean(pipV_arr[np.where(0<=pipV_arr)[0]]), precision=3)))
##                row_arr.append('~ %s V' %(np.format_float_positional(np.nanmean(pipV_arr[np.where(pipV_arr<0)[0]]), precision=3)))
##                Vavg_arr = np.array([np.nanmean(pipV_arr[np.where(0<=pipV_arr)[0]]), np.nanmean(pipV_arr[np.where(pipV_arr<0)[0]])])
##                row_arr.append('')
##                noise_arr = pipV_arr-np.nanmean(pipV_arr)
##                nrel_arr = pipV_arr-Vavg_arr[np.where(np.abs(Vavg_arr - np.nanmean(pipV_arr))==np.nanmin(np.abs(Vavg_arr - np.nanmean(pipV_arr))))[0]]
##                row_arr.append('~ %s V' %(np.format_float_scientific(np.nanmean(noise_arr), precision=1)))
##                row_arr.append('~ %s mV' % (np.round(np.nanmean(np.abs(noise_arr))*1e3, decimals=1)))
##                row_arr.append('~ %s mV' % (np.round(np.nanmean(np.abs(nrel_arr))*1e3, decimals=1)))
##        ## Create section split between pip1&pip2 data
##            else: row_arr=[char*ln for char, ln in zip(charArr, pipV_arr)] #row_arr=['-'*ln for ln in pipV_arr]
##            t.add_row(row_arr); del row_arr
##        t.align = "c"
##        print t
##        del t  
#
#
#        # In[12]:
#
#
#        #Save Normal Figure 
#        #fig.savefig(path+"Fig_%s_%sPlot.png" % (file_name.partition(".")[0], version))
#
#
#        # In[35]:
#
#
#        #Save Zoomed Figure 
#        #fig.savefig(path+"Fig_%s_%sPlotZoom.png" % (file_name.partition(".")[0], version))
#
#
#        # In[11]:
#
#
#        # fig.savefig(path+"%s.png" % (file_name.partition(".")[0]))
#
#
#        # In[ ]:
#
#
#
#
#
#        # In[ ]:
#
#
#
#
