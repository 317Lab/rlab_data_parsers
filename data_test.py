from bitstring import BitArray
import sys
import numpy as np
import matplotlib.pyplot as plt

file_name = sys.argv[1]
bytes = BitArray(filename=file_name)

ids = list(bytes.findall('0x232353', bytealigned=False))
msg_sizes = np.diff(ids)/8
sizes,counts = np.unique(msg_sizes,return_counts=True)
max_count = max(counts)
total_count = np.sum(counts)

print()
print('size (bytes)\tinstances')
for size,count in zip(sizes,counts):
    print(str(int(size)),'\t\t',str(count))
print()
print('Data drop rate: 100 % x (1 -',str(max_count),'/',str(total_count),') =','{:.1f} %'.format(100*(1-max_count/total_count)))

plt.plot(msg_sizes)
plt.show()
