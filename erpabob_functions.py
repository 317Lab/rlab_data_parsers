#!/usr/bin/env python

import numpy as np
import pickle 

def load_pickle(path, mid_fname=None, params='all', version='Original', DeltInx=[100,300], unpickled_fname=None, prefix="FlightTimeParsedData"):
    """
    Load Pickle File with Flight Data 

    Params
    --------
    path        : str
        Path the Pickle File
    mid_fname   : str
        Middle of the filename. It is the same as the unpickled, original data file's name (without the .txt extension).
    params      : list or str
        List of strings
    version     : str
        Specify if Original (unbuffered) data or Repeat (buffered) data
    DeltInx     : lst
        Start and end index of section used to calculate some interval (from original code)
    unpickled_fname : str
        [Optional] The file name of the origiinal data file. 

    Returns
    ---------
    """
    if mid_fname is None: mid_fname = unpickled_fname.partition(".")[0]
    if params == "all" or params == ["all"]: params=["shieldID", "interruptArray", " imuPlot", "axPlot", "ayPlot", "azPlot", "gxPlot", "gyPlot", "gzPlot", "mxPlot", "myPlot", " mzPlot", "magfullPlot", "tempPlot", "sweepPlot", "pip0Plot", "pip1Plot", "sweepTimeLPlot", "pip0LPlot", " pip1LPlot"]
    ############ Load Pickle File ##############
    pklfname = path+"%s_wDInx%sto%s-%s-%s.pkl" % (prefix, DeltInx[0], DeltInx[1], mid_fname, version)
    pklf = open(pklfname, "rb")
    dct = pickle.load(pklf)
#    shieldID=dct['shieldID']; interruptArray=dct['interruptArray']; imuPlot=dct['imuPlot']
#    axPlot=dct['axPlot']; ayPlot=dct['ayPlot']; azPlot=dct['azPlot']
#    gxPlot=dct['gxPlot']; gyPlot=dct['gyPlot']; gzPlot=dct['gzPlot']
#    mxPlot=dct['mxPlot']; myPlot=dct['myPlot']; mzPlot=dct['mzPlot']
#    tempPlot=dct['tempPlot']; sweepPlot=dct['sweepPlot']; pip0Plot=dct['pip0Plot']; pip1Plot=dct['pip1Plot']
#    sweepTimeLPlot=dct['sweepTimeLPlot']; pip0LPlot=dct['pip0LPlot']; pip1LPlot=dct['pip1LPlot']
    pklf.close()
#    del dct
    if np.any("magfullPlot" == np.array(params)): dct['magfullPlot'] = mxPlot**2+myPlot**2+mzPlot**2
    return [dct[key] for key in params]

#def get_intTime():
