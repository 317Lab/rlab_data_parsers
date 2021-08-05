
import numpy as np 
 
def volt2nA_pipRng(pip1=None, pip2=None, shieldnum=16):
#    if np.any([shieldnum]*3 == [14, 16, 17]): 
    pip1V2nA = 1.0/320.e-3
    pip2V2nA = 1.0/40.e-3
    if pip1 is not None: 
        print 'PIP 1 Voltage=', pip1[0], '-', pip1[1]
        print 'PIP 1 Current (nA) =', (pip1[0]-1.)*pip1V2nA, '-', (pip1[1]-1.)*pip1V2nA, '\n'
    if pip2 is not None: 
        print 'PIP 2 Voltage=', pip2[0], '-', pip2[1]
        print 'PIP 2 Current (nA) =', (pip2[0]-1.)*pip2V2nA, '-', (pip2[1]-1.)*pip2V2nA, '\n'
    return None

def test_times2seconds(time_lst, laps=True):
    """
    Convert times from mm:ss to seconds. 

    Params
    ----------
    time_lst    : list 
        List of times (in list format), where the format of each time (mm:ss) in the array is [mm, ss]. 
    laps        : bool
        Whether or not the times in time_lst are stopwatch lap times (True) or times measured from time zero (False). 

    Returns
    --------
    tsec_lst    : list
        List of times in seconds from time zero.

    """
    minu, sec = time_lst[0]

    tsec_lst = []
    for minu, sec in time_lst: 
         if laps and 0<len(tsec_lst):
             tsec_lst.append(minu*60+sec+tsec_lst[-1])
         else: 
             tsec_lst.append(minu*60+sec)
    return tsec_lst


def rectimes2seconds(time_lst, laps=True, unit='s'):
    """
    Convert recorded test times to seconds. 

    Params
    ----------
    time_lst    : list/array
        List of times. Each time in the list can be in list format and/or number format. The format of a time in the list/array depends on that time's type(). 
        If the time in the list/array time_lst is a(n)
            --> list/array: its format is either [hh, mm, ss], [mm, ss] or [ss] 
            --> float/int: its units are specified by the optional input variable "unit"
    laps        : bool
        (Optional) Whether or not the times in time_lst are stopwatch lap times (True) or times measured from time zero (False). 
        [Default: laps=True]
    units       : str
        (Optional) A character only used if one or more entries in time_lst are of type float/int (i.e. not a sub-list/array), to indicate the units of such entries.
        Possible values: 
            --> 's': [Default] Seconds
            --> 'm': Minutes
            --> 'h': Hours

    Returns
    --------
    tsec_lst    : list
        List of times in seconds from time zero.

    """
#    minu, sec = time_lst[0]

    tsec_lst = []
    for rec in time_lst: 
        if hasattr(rec, '__iter__'): 
            if len(rec)==3: rec = rec[0]*60**2 +rec[1]*60+rec[2]
            elif len(rec)==2: rec = rec[0]*60+rec[1]
            elif len(rec)==1: rec = rec[0]
            else: print 'ERROR: Unrecognized Time Format!'
        elif not unit=='s': 
            if unit=='m': rec = rec*60
            elif unit=='h': rec = rec*60**2
            else: print 'ERROR: Unrecognized Time Unit!'

        if laps and 0<len(tsec_lst):
            tsec_lst.append(rec+tsec_lst[-1])
        else: 
            tsec_lst.append(rec)
    return tsec_lst

# def lap2totalElapsed_time(time_lst, input_units='s'): 
#     if hasattr(time_lst[0], '__iter__'): 
#         ##If of format [mm:ss], then 
#         if len(time_lst[0])==2: tsec_lst = test_times2seconds(time_lst, laps=True)
#         ## If format [[val0], [val1], ...]
#         elif len(time_lst[0] == 1): 
#             time_lst = [val[0] for val in time_lst]
#             flag = True
#    else: flag = True
#    
#    if flag == True: 
#
#
#
#     return tsec_lst
#     if not hastrr(time_lst[0], '__iter__'): 
#         print "List of seconds input"
#
#
## def convert_time(time 
