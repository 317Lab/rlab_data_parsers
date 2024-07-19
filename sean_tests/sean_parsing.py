import bitstring
from bitstring import BitArray
import math
import os

def read_file():
	script_dir = os.path.dirname(__file__)
	file_path = os.path.join("20240709T150326Z_data_COM13_230400.bin")
	with open(file_path, "rb") as file:
		data = file.read()
	return data

def find_sentinel(bitarr, bytestr):
    # Convert the 3-byte string to an integer
    target = int.from_bytes(bytestr.encode(), 'big')
    n = len(bitarr)
    indices = []

    # We need to make sure we have at least 24 bits (3 bytes) to compare
    if n < 24:
        return indices

    # Iterate through the bitarray in chunks of 24 bits (3 bytes)
    for i in range(0, n - 23, 8):  # 8-bit steps, 24 bits is 3 bytes
        # Extract the 24-bit segment
        segment = bitarr[i:i+24]
        # Convert the segment to an integer
        segment_int = segment.uint
        # Compare to the target
        if segment_int == target:
            indices.append(i//8)  # Return the starting byte index of the match

    return indices  # Return -1 if no match is found

data = read_file()
data = BitArray(data)
sweep_sent = '0x230x230x53'
ldata = list(data.findall(sweep_sent, bytealigned=False)) 
print(ldata)
print(data)

