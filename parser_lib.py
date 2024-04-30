## Shield data parsers 
## Magda Moses adapted from Jules van Irsel Codes 

import numpy as np 

def parse_swp(bytes_data, byte_ids, is_buffer_data, sentinels, num_swp_bytes, num_dat_swp, num_samples=28, freq=45, \
        scale_dct={'time': 1e-6, 'acc': 4./2**15, 'mag': 1./2**15, 'gyr': 2000./360/2**15, 'pip': 5./2**14}):
    if 1<len(np.unique([len(bytes.fromhex(sentinalStr.split('x')[-1])) for sentinalStr in sentinels])): print('Warning: sentinel_size inconsistent')
    sentinel_size = np.unique([len(bytes.fromhex(sentinalStr.split('x')[-1])) for sentinalStr in sentinels])[0]
    pos = 0
    ID=0; dim=1
    #ID = int(is_buffer_data)
    #if dim==1 and is_buffer_data: dim = 2
    swp_time = np.zeros([dim,num_dat_swp],dtype='single')
    payload_id = np.zeros([dim,num_dat_swp],dtype='uint8')
    volts = np.zeros([dim,2,num_dat_swp],dtype='single')

    for ind in byte_ids: # sweep indeces
        next_sentinel = bytes_data[ind+(num_swp_bytes+sentinel_size)*8:ind+(num_swp_bytes+2*sentinel_size)*8]
        if next_sentinel in sentinels: # double sentinel match insures full message available
            swp_bytes = bytes_data[ind+sentinel_size*8:ind+(num_swp_bytes+sentinel_size)*8]
            pip0_bytes = swp_bytes[5*8:(5+2*num_samples)*8]
            pip1_bytes = swp_bytes[(5+2*num_samples)*8:]
            swp_time_tmp = swp_bytes[0:4*8].uintle*scale_dct['time']
            payload_id_tmp = swp_bytes[4*8:5*8].uintle
            for sample in range(0,2*num_samples,2): # allocate all sweep samples to arrays
                swp_time[ID,pos] = swp_time_tmp + sample/num_samples/freq/2# copy static data for each sample
                payload_id[ID,pos] = payload_id_tmp
                volts[ID,0,pos] = pip0_bytes[sample*8:(sample+2)*8].uintle*scale_dct['pip']
                volts[ID,1,pos] = pip1_bytes[sample*8:(sample+2)*8].uintle*scale_dct['pip']
                pos += 1
                
    return swp_time, payload_id, volts

def parse_imu(byte_ids, bytes_data, is_buffer_data, sentinels, num_imu_bytes, num_dat_imu, freq=45, \
        scale_dct={'time': 1e-6, 'acc': 4./2**15, 'mag': 1./2**15, 'gyr': 2000./360/2**15, 'pip': 5./2**14}):
    if 1<len(np.unique([len(bytes.fromhex(sentinalStr.split('x')[-1])) for sentinalStr in sentinels])): print('Warning: sentinel_size inconsistent')
    sentinel_size = np.unique([len(bytes.fromhex(sentinalStr.split('x')[-1])) for sentinalStr in sentinels])[0]
    pos = 0
    ID=0; dim=1
    imu_time = np.zeros([dim,num_dat_imu],dtype='single')
    acc = np.zeros([dim,3,num_dat_imu],dtype='single')
    mag = np.zeros([dim,3,num_dat_imu],dtype='single')
    gyr = np.zeros([dim,3,num_dat_imu],dtype='single')

    #ID = int(is_buffer_data)
    #if dim==1 and is_buffer_data: dim = 2
    for ind in byte_ids: # imu indices
        next_sentinel = bytes_data[ind+(num_imu_bytes+sentinel_size)*8:ind+(num_imu_bytes+2*sentinel_size)*8]
        if next_sentinel in sentinels:
            imu_bytes = bytes_data[ind+sentinel_size*8:ind+(num_imu_bytes+sentinel_size)*8]
            imu_time[ID,pos] = imu_bytes[0:4*8].uintle*scale_dct['time']
            acc[ID,0,pos] = imu_bytes[4  *8:6  *8].intle*scale_dct['acc']
            acc[ID,1,pos] = imu_bytes[6  *8:8  *8].intle*scale_dct['acc']
            acc[ID,2,pos] = imu_bytes[8  *8:10 *8].intle*scale_dct['acc']
            mag[ID,0,pos] = imu_bytes[10 *8:12 *8].intle*scale_dct['mag']
            mag[ID,1,pos] = imu_bytes[12 *8:14 *8].intle*scale_dct['mag']
            mag[ID,2,pos] = imu_bytes[14 *8:16 *8].intle*scale_dct['mag']
            gyr[ID,0,pos] = imu_bytes[16 *8:18 *8].intle*scale_dct['gyr']
            gyr[ID,1,pos] = imu_bytes[18 *8:20 *8].intle*scale_dct['gyr']
            gyr[ID,2,pos] = imu_bytes[20 *8:22 *8].intle*scale_dct['gyr']
            pos += 1
    return imu_time, acc, mag, gyr
