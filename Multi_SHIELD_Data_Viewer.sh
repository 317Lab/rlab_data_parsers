if [[ $1 == "-m" ]]; then
    echo "MONITORING ONLY MODE"
    python SHIELD_Data_Monitor.py COM4 &
    python SHIELD_Data_Monitor.py COM5 &
    python SHIELD_Data_Monitor.py COM6 &
    python SHIELD_Data_Monitor.py COM7 &
else
    echo "Writing data files"
    python SHIELD_Data_Realtime.py COM4 $1 &
    python SHIELD_Data_Realtime.py COM5 $1 &
    python SHIELD_Data_Realtime.py COM6 $1 &
    python SHIELD_Data_Realtime.py COM7 $1 &
fi