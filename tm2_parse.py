
from datetime import datetime
# equiv of matlab strfind
def find_all(data: bytes, pattern: bytes):
    indices = []
    start = 0
    while True:
        idx = data.find(pattern, start)
        if idx == -1:
            break
        indices.append(idx)
        start = idx + 1
    return indices

def write_stream(channel, cols_arr):
    file_name = channel +'_' + datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") +".bin"
    stream = []
    # adjust columns to byte position (and zero indexing)
    cols = list(map(lambda x: (x-1)*2,cols_arr))
    for idx in packet_ind:
        packet = rawdata[idx:idx+packetlength]
        for i in cols:
            word = packet[i:i+2]
            if len(word) == 2 and word[0] == 0x80:  # keep only words starting with 0x80
                stream.append(bytes([word[1]]))

    stream = b''.join(stream)
    with open(file_name,'wb') as f:
        f.write(stream)

filename = "398_swarm_deploy_11042025.bin"
with open(filename,'rb') as f:
	rawdata = f.read()
# sync word
packet_ind = find_all(rawdata, b'\x40\x28\x6B\xFE')
packetlength = 240 # 120 columns * 2 bytes per column (UDP bytes before packet)

R1_cols = [5,11,18,23,30,34,42,46,52,58,61,70,73,80,85,92,98,104,107,116]
R2_cols = [8,14,17,26,29,35,41,48,53,60,64,72,76,82,88,91,100,103,110,115]
R3_cols = [10,13,20,25,32,38,44,47,56,59,65,71,78,83,90,94,102,106,112,118]
R4_cols = [12,16,22,28,31,40,43,50,55,62,68,74,77,86,89,95,101,108,113,120]
write_stream('R1',R1_cols)
write_stream('R2',R2_cols)
write_stream('R3', R3_cols)
write_stream('R4', R4_cols)