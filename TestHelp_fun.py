
import numpy as np 
 
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


 def lap2totalElapsed_time(time_lst, input_units='s'): 
     if hasattr(time_lst[0], '__itter__'): 
         ##If of format [mm:ss], then 
         if len(time_lst[0])==2: tsec_lst = test_times2seconds(time_lst, laps=True)
         ## If format [[val0], [val1], ...]
         elif len(time_lst[0] == 1): 
             time_lst = [val[0] for val in time_lst]
             flag = True
    else: flag = True
    
    if flag == True: 



     return tsec_lst
     if not hastrr(time_lst[0], '__itter__'): 
         print "List of seconds input"


# def convert_time(time 
