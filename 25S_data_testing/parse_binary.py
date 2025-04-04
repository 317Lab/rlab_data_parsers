def parse_all(filename):
    import numpy as np
    from bitstring import BitArray

    buffered = True
    freq = 45
    dim = 2 if buffered else 1

    # constants...
    t_scale = 1.e-6; a_scale = 4./2**15; m_scale = 1./2**15
    g_scale = 2000./360/2**15; p_scale = 5./2**14
    sentinels = ['0x232353','0x232349','0x232354','0x23234A']
    sentinel_size = 3

    num_samples = 28
    num_swp_bytes = 4 + 1 + num_samples * 2 * 2
    num_imu_bytes = 4 + (3 + 3 + 3 + 1) * 2

    with open(filename, 'rb') as f:
        bytes = BitArray(f.read())

    ids_swp = list(bytes.findall(sentinels[0], bytealigned=False))
    ids_imu = list(bytes.findall(sentinels[1], bytealigned=False))
    ids_swp_buf = list(bytes.findall(sentinels[2], bytealigned=False)) if buffered else ids_swp
    ids_imu_buf = list(bytes.findall(sentinels[3], bytealigned=False)) if buffered else ids_imu

    num_dat_swp = max(len(ids_swp), len(ids_swp_buf)) * num_samples
    num_dat_imu = max(len(ids_imu), len(ids_imu_buf))

    swp_time = np.zeros([dim,num_dat_swp],dtype='single')
    payload_id = np.zeros([dim,num_dat_swp],dtype='uint8')
    volts = np.zeros([dim,2,num_dat_swp],dtype='single')
    imu_time = np.zeros([dim,num_dat_imu],dtype='single')
    acc = np.zeros([dim,3,num_dat_imu],dtype='single')
    mag = np.zeros([dim,3,num_dat_imu],dtype='single')
    gyr = np.zeros([dim,3,num_dat_imu],dtype='single')

    def parse_swp(byte_ids, id):
        pos = 0
        for ind in byte_ids:
            next_sentinel = bytes[ind+(num_swp_bytes+sentinel_size)*8:ind+(num_swp_bytes+2*sentinel_size)*8]
            if next_sentinel in sentinels:
                swp_bytes = bytes[ind+sentinel_size*8:ind+(num_swp_bytes+sentinel_size)*8]
                pip0_bytes = swp_bytes[5*8:(5+2*num_samples)*8]
                pip1_bytes = swp_bytes[(5+2*num_samples)*8:]
                swp_time_tmp = swp_bytes[0:4*8].uintle*t_scale
                payload_id_tmp = swp_bytes[4*8:5*8].uintle
                for sample in range(0,2*num_samples,2):
                    swp_time[id,pos] = swp_time_tmp + sample/num_samples/freq/2
                    payload_id[id,pos] = payload_id_tmp
                    volts[id,0,pos] = pip0_bytes[sample*8:(sample+2)*8].uintle*p_scale
                    volts[id,1,pos] = pip1_bytes[sample*8:(sample+2)*8].uintle*p_scale
                    pos += 1

    def parse_imu(byte_ids, id):
        pos = 0
        for ind in byte_ids:
            next_sentinel = bytes[ind+(num_imu_bytes+sentinel_size)*8:ind+(num_imu_bytes+2*sentinel_size)*8]
            if next_sentinel in sentinels:
                imu_bytes = bytes[ind+sentinel_size*8:ind+(num_imu_bytes+sentinel_size)*8]
                imu_time[id,pos] = imu_bytes[0:4*8].uintle*t_scale
                acc[id,0,pos] = imu_bytes[4*8:6*8].intle*a_scale
                acc[id,1,pos] = imu_bytes[6*8:8*8].intle*a_scale
                acc[id,2,pos] = imu_bytes[8*8:10*8].intle*a_scale
                mag[id,0,pos] = imu_bytes[10*8:12*8].intle*m_scale
                mag[id,1,pos] = imu_bytes[12*8:14*8].intle*m_scale
                mag[id,2,pos] = imu_bytes[14*8:16*8].intle*m_scale
                gyr[id,0,pos] = imu_bytes[16*8:18*8].intle*g_scale
                gyr[id,1,pos] = imu_bytes[18*8:20*8].intle*g_scale
                gyr[id,2,pos] = imu_bytes[20*8:22*8].intle*g_scale
                pos += 1

    parse_swp(ids_swp, 0)
    parse_imu(ids_imu, 0)
    if buffered:
        parse_swp(ids_swp_buf, 1)
        parse_imu(ids_imu_buf, 1)

    return swp_time, payload_id, volts, imu_time, acc, mag, gyr
