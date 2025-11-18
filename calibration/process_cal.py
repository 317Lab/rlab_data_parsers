import parse_binary as pb
import numpy as np
def save_data(binary, output):
    swp_time, payload_id, volts, imu_time, acc, mag, gyr = pb.parse_all(binary)
    np.savez(output, swp_time=swp_time, payload_id=payload_id, volts=volts, imu_time=imu_time, acc=acc, mag=mag, gyr=gyr)

def load_data(filename):
    data = np.load(filename)
    swp_time = data["swp_time"]
    payload_id = data["payload_id"]
    volts = data["volts"]
    imu_time = data["imu_time"]
    acc = data["acc"]
    mag = data["mag"]
    gyr = data["gyr"]
    return swp_time, payload_id, volts, imu_time, acc, mag, gyr

save_data("36.397_MAG_CAL_D1_GL_D1_R4.bin","397_D1_magcal")
save_data("36.397_MAG_CAL_D4_GL_D4_R4.bin","397_D4_magcal")
save_data("36.398_MAG_CAL_D1_GL_D1_R4.bin","398_D1_magcal")
save_data("36.398_MAG_CAL_D4_GL_D4_R4.bin","398_D4_magcal")
save_data("397_Swarm_deploy_d1.bin", "397_D1_deploy")
save_data("397_Swarm_deploy_d4.bin", "397_D4_deploy")
save_data("398_swarm_deploy_11042025_d1.bin", "398_D1_deploy")
save_data("398_swarm_deploy_11042025_d4.bin", "398_D4_deploy")