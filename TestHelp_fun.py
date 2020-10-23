
import numpy as np 
 
def test_times2seconds(time_lst, laps=True):
     minu, sec = time_lst[0]

     tsec_lst = []
     for minu, sec in time_lst: 
         if laps and 0<len(tsec_lst):
             tsec_lst.append(minu*60+sec+tsec_lst[-1])
         else: 
             tsec_lst.append(minu*60+sec)
     return tsec_lst
