# coding: utf-8

# In[173]:

from __future__ import division

import sys
import os
import matplotlib
matplotlib.use("Agg")
#if 'matplotlib.pyplot' not in sys.modules.keys():
#    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import numpy as np

#shieldnum = 16 
#get_ipython().magic(u'matplotlib notebook')

if len(sys.argv)>1: test=sys.argv[1]
else: test='baseline'
if len(sys.argv)>2: pltype=sys.argv[2]
else: pltype='orig'

if test == 'all': tlst = ['baseline', 'horiz_cw', 'horiz_ccw', 'pitch_cw', 'pitch_ccw']
else: tlst = [test]

fig_path = os.path.join('FiguresPy','Delamere_Bob_Vacuum', 'Interrupt_Plots')

detail_compare = True
#path = "./Delamere_Vacuum_Tests/Bob_Vacuum/Shield%s/" % (shieldnum)
path = "./Delamere_Vacuum_Tests/Bob_Vacuum/"
if not os.path.exists(fig_path): os.makedirs(fig_path)

for test in tlst:
    if test == 'baseline': 
        title_str = 'Interrupts for Baseline Measurements of All Shields'
        file_lst = ['Shield17/data_file_230k-Shield17_Plasma_Baseline_Roll45_Pitch0-11_25_20.txt', \
                    'Shield14/data_file_230k-Shield14_First_Plasma-12_02_20.txt', \
                    'Shield16/data_file_230k-Shield16_Plasma_Start_Baseline_Roll45_Pitch0-12_04_20.txt']
        rel_etimes = [4*60, 7*60+38.99, 3*60+28.23] 

    elif test == 'horiz_cw': 
        title_str = 'Interrupts for Horizontal CW Rotations of All Shields'
        file_lst = ['Shield17/data_file_230k-Shield17_Plasma_RollCWsweep15_Pitch0-11_25_20.txt', \
                    'Shield14/data_file_230k-Shield14_Plasma_RollCWsweep15_Pitch0-12_01_20.txt', \
                    'Shield16/data_file_230k-Shield16_Plasma_RollCWsweep15_Pitch0-12_04_20.txt']
        rel_etimes = [9*60+10.30, 7*60+25.78,11*60]

    elif test == 'horiz_ccw': 
        title_str = 'Interrupts for Horizontal CCW Rotations of All Shields'
        file_lst = ['Shield17/data_file_230k-Shield17_Plasma_RollCCWsweep15_Pitch0-11_25_20.txt', \
                    'Shield14/data_file_230k-Shield14_Plasma_RollCCWsweep15_Pitch0-12_01_20.txt', \
                    'Shield16/data_file_230k-Shield16_Plasma_RollCCWsweep15_Pitch0-12_04_20.txt']
        rel_etimes = [11.5*60,9*60, 10*60]

    elif test == 'pitch_cw':
        title_str = 'Interrupts for Pitched CW Rotations of All Shields'
        file_lst = ['Shield17/data_file_230k-Shield17_Plasma_RollCWsweep15_PitchDown10-11_25_20.txt', \
                    'Shield14/data_file_230k-Shield14_Plasma_RollCWsweep15_PitchUp10-12_02_20.txt', \
                    'Shield16/data_file_230k-Shield16_Plasma_RollCWsweep15_PitchDown10-12_04_20.txt']
        rel_etimes = [9*60+18.33, 12*60, 11*60]

    elif test == 'pitch_ccw':
        title_str = 'Interrupts for Pitched CCW Rotations of All Shields'
        file_lst = ['Shield17/data_file_230k-Shield17_Plasma_RollCCWsweep15_PitchDown10-11_25_20.txt', \
                    'Shield14/data_file_230k-Shield14_Plasma_RollCCWsweep15_PitchUp10-12_02_20.txt', \
                    'Shield16/data_file_230k-Shield16_Plasma_RollCCWsweep15_PitchDown10-12_04_20.txt']
        rel_etimes = [9*60.,11*60,11.5*60]

    ### Following are Nov. 25, 2020 chamber tests ###
    #if shieldnum == 17: 
    #    file_lst = ['data_file_230k-Shield17_First_Plasma_Roll45_Pitch0-11_25_20.txt', \
    #            'data_file_230k-Shield17_First_Plasma_Roll45_Pitch0_B-11_25_20.txt', \
    #            'data_file_230k-Shield17_Plasma_Baseline_Roll45_Pitch0-11_25_20.txt', \
    #            'data_file_230k-Shield17_Plasma_RollCWsweep15_Pitch0-11_25_20.txt', \
    #            'data_file_230k-Shield17_Plasma_RollCCWsweep15_Pitch0-11_25_20.txt', \
    #            'data_file_230k-Shield17_Plasma_DurationTest_Roll45_Pitch0-11_25_20.txt', \
    #            'data_file_230k-Shield17_Plasma_RollCWsweep15_PitchDown10-11_25_20.txt', \
    #            'data_file_230k-Shield17_Plasma_RollCCWsweep15_PitchDown10-11_25_20.txt']
    #
    #### Following are Dec. 1, 2020 and Dec. 2, 2020 chamber tests ###
    #if shieldnum == 14: 
    #    file_lst = ['data_file_230k-Shield14_First_Plasma-12_01_20.txt', \
    #            'data_file_230k-Shield14_Plasma_RollCWsweep15_Pitch0-12_01_20.txt', \
    #            'data_file_230k-Shield14_Plasma_RollCCWsweep15_Pitch0-12_01_20.txt', \
    #            'data_file_230k-Shield14_Plasma_TestEVTgnd_Roll45_Pitch0-12_01_20.txt', \
    #            'data_file_230k-Shield14_Plasma_TestEVT5V_Roll45_Pitch0-12_01_20.txt', \
    #            'data_file_230k-Shield14_First_Plasma-12_02_20.txt', \
    #            'data_file_230k-Shield14_Plasma_RollCWsweep15_PitchUp10-12_02_20.txt', \
    #            'data_file_230k-Shield14_Plasma_RollCCWsweep15_PitchUp10-12_02_20.txt', \
    #            'data_file_230k-Shield14_Plasma_PostSweepsRun-12_02_20.txt', \
    #            'data_file_230k-Shield14_Plasma_FinalEVTtest_Roll45_Pitch0-12_02_20.txt', \
    #            'data_file_230k-Shield14_Plasma_TestEVTgndToPartner_Roll45_Pitch0-12_02_20.txt']
    #
    #
    #### Following are Dec 4, 2020 chamber tests ###
    #if shieldnum == 16: 
    #    file_lst = ['data_file_230k-Shield16_First_Plasma_TableCheck1_Roll45_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_First_Plasma_TableFix1_RollMove15_PitchMove10-12_04_20.txt', \
    #            'data_file_230k-Shield16_First_Plasma_GasAdjust_Roll45_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_First_Plasma_PlasmaAdjust_Roll45_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_First_Plasma_PlasmaAdjust2_Roll45_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_First_Plasma_PlasmaAdjust3_Roll45_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_First_Plasma_PlasmaAdjust4_Roll45_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_Plasma_Start_Baseline_Roll45_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_Plasma_RollCWsweep15_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_Plasma_RollCCWsweep15_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_Plasma_RollCWsweep15_PitchDown10-12_04_20.txt', \
    #            'data_file_230k-Shield16_Plasma_RollCCWsweep15_PitchDown10-12_04_20.txt', \
    #            'data_file_230k-Shield16_Plasma_End_Baseline_Roll45_Pitch0-12_04_20.txt', \
    #            'data_file_230k-Shield16_Plasma_TableBox_Test_Roll45_Pitch0-12_04_20.txt']

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
                # if more than delta_t gap, fill in
                elif t - l[l.index(t) - 1] >= 2 * dt:
                    new.append(l.index(t))
                    l.insert(l.index(t), l[l.index(t) - 1] + dt)

    # running through timewords and cleaning all mistakes from timefix
    def clean(l, dt):    # l = same l data from timefix, dt = delta t
        i = 2
        while i < len(l):
            if l[i] - l[i - 1] < 0 or l[i] - l[i - 1] > 1:
                l[i] = l[i - 1] + dt
            else:
                i += 1

    # padding pip data as arrays
    def pad_data(original, new):  # original = non-time data array, new = same "new" list (now filled) from timefix
        NaN = np.nan
        if original is pip0 or original is pip1 or original is pip0Rpt or original is pip1Rpt:
            filler = np.full([1,28], NaN)
        else:
            filler = np.full([1,1], NaN)
        for data in new:
            one = np.split(original, [data])[0]
            two = np.split(original, [data])[1]
            original = np.vstack((one, filler, two))
        return original


    # In[174]:
    test_chrono = 1 
    lines_dct = dict()
    time_rng = [0, 0]
    flag=True
    errflag=False
    plt_lst = []
    stime_lst = []
    for file_name in file_lst: 
    #    print "\n**************\nAnalyzing Data from Test #%s of %s\n*************" % (test_chrono, len(file_lst)) #, file_name)
        dataFile=path + file_name 
    #    print "Located at "+dataFile+"\n" 
        lines_dct[file_name.split('/')[0].lower()]=dict()

        ########### Load the data file ###########
        f = open(dataFile, 'r')
        rawData = f.read()

        # Create payload objects and store parsed data
        mainPIPData = PayloadData()
        mainPIPData.rawData = rawData
        payloads = [mainPIPData]

        ########### Parse by data type for each payload ###########
        strict_parse = True # Require a pound symbol at the end of the data
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
    #        print("Num IMU Messages: %s" %len(imu))
    #        print("Num Sweep Messages: %s" %len(sweeps))
    #        print("Num IMU Messages (buffer): %s" %len(imuRpt))
    #        print("Num Sweep Messages (buffer): %s" %len(sweepsRpt))
    #        print("Num interrupt messages: %s" %len(interrupt))

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
    #        if payloadMatch:
    #            print("Payload ID's match. This was payload #%s." %payloadID[0])
    #        else:
    #            print("Payload ID's don't match. Something went wrong...")
            if not payloadMatch: print("Payload ID's don't match. Something went wrong...")
                
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

        if np.min(np.array(payload.imu.time)/1.E6) < 60: stime_lst.append(0)
        else: stime_lst.append(np.floor(np.min(np.array(payload.imu.time)/1.E6)))

        # In[175]:
        if detail_compare: 
            """%%%% Event Interrupt Details %%%%"""
            #set(interruptArray)
    #        print "File name %s" % dataFile
            print "**************************************************************************************" 
    #        print "File name: %s\n*******************************************" % dataFile
            print "File name: %s" % dataFile
            print"Num interrupt messages for payload %s: %s" %(payloadID[0], len(interrupt))
            print "Num unique interrupt times: ", len(np.unique(np.array(interruptTime)/10.**6))
            print '***************************************'
            EventTimes = []
            EventNum = []
            if not len(interrupt)==0:
                prev=np.unique(np.array(interruptTime)/10.**6)[0]
                for event in np.unique(np.array(interruptTime)/10.**6): 
                    if int(np.floor(event-prev)) >= 30: print "-----------------------------------------"
                    print "Number of recordings for %ss:" % (event), len(np.where(np.array(interruptTime)/10.**6 == event)[0]) 
                    EventNum.append(len(np.where(np.array(interruptTime)/10.**6 == event)[0]))
                    EventTimes.append(event)
                    prev=event
            else: 
                print "No Event Interrupts Recieved"
            print "**************************************************************************************\n" 
            lines_dct['shield'+str(payloadID[0])]={'times': EventTimes, 'cnt': EventNum} 
            if 1<=len(EventTimes): 
                if np.min(EventTimes) < time_rng[0]: time_rng[0]=np.min(EventTimes) 
                if np.max(EventTimes) > time_rng[1]: time_rng[1]=np.max(EventTimes)
                if flag: 
                    time_rng[0]=np.min(EventTimes) 
                    flag = False
                if np.any(np.min(EventTimes)+60<EventTimes): errflag = True


        # In[176]:
        else: 
            """%%%% Noisy Event Interrupt Cleaning %%%%"""
            max_dt = 10
            newEventTimes=[]
            newEventNum=[]
            newEvent=[]
            tmp = []
            cnt = 0
            print "\n**************\nFile name %s\n*************" % dataFile
            print"Num interrupt messages for payload %s: %s" %(payloadID[0], len(interrupt))
            print "Num unique interrupt times: ", len(np.unique(np.array(interruptTime)/10.**6))
            if not len(interrupt)==0:
                #prev=np.unique(np.array(interruptTime)/10.**6)[0]
                gprev = np.unique(np.array(interruptTime)/10.**6)[0]
                for event in np.unique(np.array(interruptTime)/10.**6):
                    if np.round(event, decimals=0)-np.round(gprev, decimals=0) < max_dt: 
                        tmp.append(event)
                        cnt = cnt+len(np.where(np.array(interruptTime)/10.**6 == event)[0])
                    else: 
                        #Reset temporary variables
                        newEventTimes.append(tmp); tmp = []
                        newEventNum.append(cnt); cnt = 0
                        newEvent.append(np.round(gprev, decimals = 0)); gprev = event
                        #Save this event information
                        tmp.append(event)
                        cnt = cnt+len(np.where(np.array(interruptTime)/10.**6 == event)[0])
                #Save Final Event Information
                newEventTimes.append(tmp)
                newEventNum.append(cnt)
                newEvent.append(np.round(gprev, decimals = 0))
                del tmp, cnt, gprev
            #    print "\n**************\nAnalyzing Data from Test #%s of %s\n*************" % (test_chrono, len(file_lst)) #, file_name)
                print "\nTimes are grouped together if they are within %ss of eachother" % (max_dt)
                print "Num unique grouped interrupt times: ", len(np.unique(np.array(interruptTime)/10.**6))
                print '***************************************'
                prev = newEvent[0]
                for event, count, sublst in zip(np.array(newEvent), np.array(newEventNum), newEventTimes):         
                    if int(np.floor(event-prev)) >= 30: print "-----------------------------------------"
                    print "Number of recordings for ~%ss:" % (event), count, "\tNumber of unique times in %ss group:" %(event), len(sublst)
                    prev=event
            else: 
                print "No Event Interrupts Recieved"
            lines_dct['shield'+str(payloadID[0])]={'times': newEvent, 'cnt': newEventNum} 
            if 1<=len(newEvent): 
                if np.min(newEvent) < time_rng[0]: time_rng[0]=np.min(newEvent)
                if np.max(newEvent) > time_rng[1]: time_rng[1]=np.max(newEvent)
                if flag: 
                    time_rng[0]=np.min(newEvent) 
                    flag = False
    #            if np.any(np.min(newEvent)+60<np.array(newEvent)): errflag = True
        plt_lst.append('shield'+str(payloadID[0]))
        
        
    # In[177]:
    #    from prettytable import PrettyTable
    if pltype=='orig': 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        prefix = 'Original'
        marker_size =12 
        for shieldstr in plt_lst: 
            # If no interrupt values for this shield, make line with value 0 go from 0s to 60s 
            if len(lines_dct[shieldstr]['times'])<1: 
                xval = np.arange(time_rng[0],time_rng[0]+70,10)
                yval = np.zeros(xval.shape)
                mark = 'x'
            # If interrupt values for shield, plot them 
            else: 
                xval = lines_dct[shieldstr]['times']
                yval = lines_dct[shieldstr]['cnt']
                mark = 'o'
            ax.plot(xval, yval, marker=mark, markersize=marker_size, linestyle='-', label=shieldstr[0:-2].capitalize()+' '+shieldstr[-2:])
            marker_size -= 2
        ax.set_xlabel('Interrupt Time relative to Shield Start Time (s)')
        ax.set_ylabel('Number of Interrupts Recorded')
        plt.title(title_str)
        ax.legend()
        if detail_compare: suffix='All_Times' 
        else: suffix = 'Grouped_Times'
        figname = '-'.join([prefix, title_str.replace(' ', '_'), suffix])+'.png'
        fig.savefig(os.path.join(fig_path, figname))

    # In[178]:
    #    from prettytable import PrettyTable
    elif pltype == 'rel': 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        prefix = 'Relative_Times'
        marker_size =12 
        for shieldstr,stime in zip(plt_lst, stime_lst): 
            # If no interrupt values for this shield, make line with value 0 go from 0s to 60s 
            if len(lines_dct[shieldstr]['times'])<1: 
                xval = [10]
                yval = [0]
                mark = 'x'
            elif stime != 0: 
                tmp = stime-10
                xval = np.array(lines_dct[shieldstr]['times'])-tmp 
                yval = lines_dct[shieldstr]['cnt']
                mark = '^'
            # If interrupt values for shield, plot them 
            else: 
                xval = lines_dct[shieldstr]['times']
                yval = lines_dct[shieldstr]['cnt']
                mark = 'o'
            ax.plot(xval, yval, marker=mark, markersize=marker_size, linestyle='-', label=shieldstr[0:-2].capitalize()+' '+shieldstr[-2:]+' (start time = %ss)'%(stime))
            marker_size -= 2
        ax.set_xlabel('Interrupt Time Relative to Test Start Time (s)')
        ax.set_ylabel('Number of Interrupts Recorded')
        plt.title(title_str)
        ax.legend()
        if detail_compare: suffix='All_Times' 
        else: suffix = 'Grouped_Times'
        figname = '-'.join([prefix, title_str.replace(' ', '_'), suffix])+'.png'
        fig.savefig(os.path.join(fig_path, figname))

    elif pltype == 'rel_vlmax': 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        prefix = 'Relative_Times_Annote'
        marker_size =12 
        vval_lst, vcolors = [], []
        for shieldstr,stime, etime in zip(plt_lst, stime_lst, rel_etimes): 
            if stime !=0: 
                tmp = stime-10
            else: tmp = None
            # If no interrupt values for this shield, make line with value 0 go from 0s to 60s 
            if len(lines_dct[shieldstr]['times'])<1: 
                xval = [10]
                yval = [0]
                mark = 'x'
#                if tmp is not None: vval_lst.append(etime-tmp)
                vval_lst.append(etime)
            elif stime != 0: 
                tmp = stime-10
                xval = np.array(lines_dct[shieldstr]['times'])-tmp 
                yval = lines_dct[shieldstr]['cnt']
#                vval_lst.append(etime-tmp)
                vval_lst.append(etime)
                mark = '^'
            # If interrupt values for shield, plot them 
            else: 
                xval = lines_dct[shieldstr]['times']
                yval = lines_dct[shieldstr]['cnt']
                vval_lst.append(etime)
                mark = 'o'
            line = ax.plot(xval, yval, marker=mark, markersize=marker_size, linestyle='-', label=shieldstr[0:-2].capitalize()+' '+shieldstr[-2:]+' (start time = %ss)'%(stime))
            vcolors.append(line[-1].properties()['color'])
            marker_size -= 2

        ax.vlines(vval_lst, ax.get_ylim()[0], ax.get_ylim()[1], color=vcolors, linestyle='--')
        ax.set_xlabel('Interrupt Time Relative to Test Start Time (s)')
        ax.set_ylabel('Number of Interrupts Recorded')
        plt.title(title_str)
        ax.legend()
        if detail_compare: suffix='All_Times' 
        else: suffix = 'Grouped_Times'
        figname = '-'.join([prefix, title_str.replace(' ', '_'), suffix])+'.png'
        fig.savefig(os.path.join(fig_path, figname))
