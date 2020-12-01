import numpy as np
import TestHelp_fun as funct

def gen_subdct(ID): 
    dct = dict()
    if ID == 'Shield17': 
        ## Initial Turn on Data  
        dct['Shield17_First_Plasma_Roll45_Pitch0-11_25_20']=dict()
        stime=[[0, 4.36],  [6, 46.31]]
        times = funct.test_times2seconds(stime)
        roll_locs = np.array([45]*len(times))
        pitch_locs = np.array([0]*len(times))
        if not len(roll_locs)==len(pitch_locs) or not len(roll_locs)==len(times) or not len(pitch_locs)==len(times): print 'Warning: Array Sizes Inconsistent!!!'
        dct['Shield17_First_Plasma_Roll45_Pitch0-11_25_20']={'roll': roll_locs, 'pitch': pitch_locs, 'time': np.array(times)}
        del roll_locs, pitch_locs, stime, times


#        ##Environment Modification Test
#        times = funct.test_times2seconds(stime)
#        roll_locs = np.array([45]*len(times))
#        pitch_locs = np.array([0]*len(times))
#        if not len(roll_locs)==len(pitch_locs) or not len(roll_locs)==len(times) or not len(pitch_locs)==len(times): print 'Warning: Array Sizes Inconsistent!!!'
#
#        ##Environment Baseline and/or Duration Tests
#
#        #dct['']=dict()
#        #times = funct.test_times2seconds(stime)
#        #if not len(roll_locs)==len(pitch_locs) or not len(roll_locs)==len(times) or not len(pitch_locs)==len(times): print 'Warning: Array Sizes Inconsistent!!!'
#        #dct['']={'roll': roll_locs, 'pitch': pitch_locs, 'time': np.array(times)}
#        #del roll_locs, pitch_locs, stime, times


        ## Rotational Motion Tests
        dct['Shield17_Plasma_RollCWsweep15_Pitch0-11_25_20']=dict()
        roll_locs = np.array([45, 30, 15, 0, -15, 0, 15, 30, 45])
        pitch_locs = np.array([0]*len(roll_locs))
        stime = [[0, 14.15], [1, 10.13], [0, 47.34], [0, 49.22], [1, 2.05], [0, 56.49], [0, 54.19], [1, 4.09], [0,48.17]]
        times = funct.test_times2seconds(stime)
        if not len(roll_locs)==len(pitch_locs) or not len(roll_locs)==len(times) or not len(pitch_locs)==len(times): print 'Warning: Array Sizes Inconsistent!!!'
        dct['Shield17_Plasma_RollCWsweep15_Pitch0-11_25_20']={'roll': roll_locs, 'pitch': pitch_locs, 'time': np.array(times)}
        del roll_locs, pitch_locs, stime, times

        dct['Shield17_Plasma_RollCCWsweep15_Pitch0-11_25_20']=dict()
        roll_locs = np.array([45, 60, 75, 90, 105, 90, 75, 60, 45])
        pitch_locs = np.array([0]*len(roll_locs))
        stime = [[0, 11.85+40.4], [0, 59.1], [0, 59.25], [0, 59.09], [1, 0.047], [0, 56.66], [1, 7.85], [0, 58.09], [0, 56.45]]
        times = funct.test_times2seconds(stime)
        if not len(roll_locs)==len(pitch_locs) or not len(roll_locs)==len(times) or not len(pitch_locs)==len(times): print 'Warning: Array Sizes Inconsistent!!!'
        dct['Shield17_Plasma_RollCCWsweep15_Pitch0-11_25_20']={'roll': roll_locs, 'pitch': pitch_locs, 'time': np.array(times)}
        del roll_locs, pitch_locs, stime, times

        dct['Shield17_Plasma_RollCWsweep15_PitchDown10-11_25_20']=dict()
        pitch_locs= np.array([0, 10, 10, 10, 10, 10, 10, 10, 10, 10])
        roll_locs = np.array([45, 45, 30, 15, 0, -15, 0, 15, 30, 45])
        stime =  [[0,10.33], [1, 20.81], [0, 48.30], [0, 46.96], [0, 42.5], [0, 48.05], [0, 47.27], [0, 42.19], [0, 46.79], [0, 52.58]]
        times = funct.test_times2seconds(stime)
        if not len(roll_locs)==len(pitch_locs) or not len(roll_locs)==len(times) or not len(pitch_locs)==len(times): print 'Warning: Array Sizes Inconsistent!!!'
        dct['Shield17_Plasma_RollCWsweep15_PitchDown10-11_25_20']={'roll': roll_locs, 'pitch': pitch_locs, 'time': np.array(times)}
        del roll_locs, pitch_locs, stime, times

        dct['Shield17_Plasma_RollCCWsweep15_PitchDown10-11_25_20']=dict()
        pitch_locs = np.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 0])
        roll_locs = np.array([45, 60, 75, 90, 105, 90, 75, 60, 45, 45])  
        stime = [[0, 11.11], [0, 56.71], [0, 55.28], [0, 51.56], [0, 49.57], [0, 49.68], [0, 49.34], [0, 49.86], [0, 49.71], [0, 51.16]]
        times = funct.test_times2seconds(stime)
        if not len(roll_locs)==len(pitch_locs) or not len(roll_locs)==len(times) or not len(pitch_locs)==len(times): print 'Warning: Array Sizes Inconsistent!!!'
        dct['Shield17_Plasma_RollCCWsweep15_PitchDown10-11_25_20']={'roll': roll_locs, 'pitch': pitch_locs, 'time': np.array(times)}
        del roll_locs, pitch_locs, stime, times

        #dct['']=dict()
        #times = funct.test_times2seconds(stime)
        #if not len(roll_locs)==len(pitch_locs) or not len(roll_locs)==len(times) or not len(pitch_locs)==len(times): print 'Warning: Array Sizes Inconsistent!!!'
        #dct['']={'roll': roll_locs, 'pitch': pitch_locs, 'time': np.array(times)}
        #del roll_locs, pitch_locs, stime, times
    return dct 

def get_dct(fsuffix, ID=None): 
    if ID is None: ID = fsuffix.partition('_')[0]
    dct = gen_subdct(ID)
    return dct[fsuffix].copy()


def num_valid(dct, sweepPlot, pip0_rot, pip1_rot, sweep_voltage): 
    """
    dct is output of get_dct function
    """
    tmp = []
    for roll in np.arange(0, len(dct['roll'])):
        if roll == len(dct['roll'])-1:
            roll_locs = np.where(dct['time'][roll]<=sweepPlot)[0]
        elif roll == 0:
            roll_locs = np.where(sweepPlot<dct['time'][roll+1])[0]
        else: 
            roll_locs = np.where(np.logical_and(dct['time'][roll]<=sweepPlot, sweepPlot<dct['time'][roll+1]))[0]
        print '\n-------------\nRoll: %s degrees\n------------' % (dct['roll'][roll])
        tmp0 = []
        tmp1 = []
        for volt in np.arange(0, len(sweep_voltage)): 
            tmp0.append(len(np.where(np.isnan(pip0_rot[volt][roll_locs])==False)[0]))
            tmp1.append(len(np.where(np.isnan(pip1_rot[volt][roll_locs])==False)[0]))
        print 'Unique Counts for PIP0: %s' % (np.unique(tmp0))
        print 'Unique Counts for PIP1: %s' % (np.unique(tmp1))
        tmp0.extend(tmp1)
        tmp.append(np.unique(tmp0))
        del tmp0, tmp1
    return tmp 

