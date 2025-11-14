import parse_binary as pb
import numpy as np
import json


acc_zero_times = {"397_D1":(149.2,149.8), "397_D4":(147.91,148.45),"398_D1":(449.8,450.35),"398_D4":(447.4,448.05)}
gyr_zero_times = {"397_D1":(450,550), "397_D4":(400,500),"398_D1":(430,525),"398_D4":(425,515)}
mag_zero_times = {"397_D1":(510,565), "397_D4":(460,520),"398_D1":(490,540),"398_D4":(470,520)}

filenames = {"397_D1_mag":"36.397_MAG_CAL_D1_GL_D1_R4.bin", "397_D4_mag":"36.397_MAG_CAL_D4_GL_D4_R4.bin","398_D1_mag":"36.398_MAG_CAL_D1_GL_D1_R4.bin",
             "398_D4_mag":"36.398_MAG_CAL_D4_GL_D4_R4.bin", "397_D1_deploy":"397_Swarm_deploy_d1.bin", "397_D4_deploy":"397_Swarm_deploy_d4.bin",
             "398_D1_deploy":"398_swarm_deploy_11042025_d1.bin", "398_D4_deploy":"398_swarm_deploy_11042025_d4.bin"}

# bob_num is string of form "rocketnum_bobnum" ie "397_D1"
def get_cal(bob_num, type):
    if type == "mag":
        filename = filenames[bob_num+"_mag"]
        _, _, _, imu_time, _, mag, _ = pb.parse_all(filename)
        return get_avg(imu_time, mag, mag_zero_times[bob_num])
        
    elif type == "acc":
        filename = filenames[bob_num+"_deploy"]
        _, _, _, imu_time, acc, _, _ = pb.parse_all(filename)
        return get_avg(imu_time, acc, acc_zero_times[bob_num])
    elif type == "gyr":
        filename = filenames[bob_num+"_mag"]
        _, _, _, imu_time, _, _, gyr = pb.parse_all(filename)
        return get_avg(imu_time, gyr, gyr_zero_times[bob_num])
    else:
        raise Exception("Invalid measurement type")
    
def get_avg(imu_time, data,time_tuple):
    idxs = np.where(((imu_time[0,:]>=time_tuple[0])&(imu_time[0,:]<=time_tuple[1])))
    return (np.mean(data[0,0,idxs]).item(),np.mean(data[0,1,idxs]).item(), np.mean(data[0,2,idxs]).item())

offsets = {"397_D1":{"mag":get_cal("397_D1","mag"),"acc":get_cal("397_D1","acc"),"gyr":get_cal("397_D1","gyr")},
          "397_D4":{"mag":get_cal("397_D4","mag"),"acc":get_cal("397_D4","acc"),"gyr":get_cal("397_D4","gyr")},
          "398_D1":{"mag":get_cal("398_D1","mag"),"acc":get_cal("398_D1","acc"),"gyr":get_cal("398_D1","gyr")},
          "398_D4":{"mag":get_cal("398_D4","mag"),"acc":get_cal("398_D4","acc"),"gyr":get_cal("398_D4","gyr")}}    
with open("offsets.json", "w") as f:
    json.dump(offsets,f,indent=2)




