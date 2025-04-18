# TODO: automate this - prompt user to set voltage, then automatically collect files, then when files are all collected, run the test.
######## INSTRUCTIONS FOR DC TEST ANALYSIS ########
# Store the binary files in the binary_files folder.
# Binary files must be titled "DC_test_1.bin", "DC_test_2.bin", etc.
# There must be one file per voltage level.

# Store test data in the following structure:
# test1 = util.DCTest(
# 	test_id = 1,
# 	voltages = volts_list[0][0,1,:],
# 	resistor_reading = 2.1,
# 	supply_voltage = 1.4
# )

####### Test Code #######
import utilities as util
import numpy as np
import parse_binary as pb

volts_list = []
numtests = 5
for i in range(1,numtests+1):
	binary_file = f"binary_files/DC_test_{i}.bin"
	_, _, volts, _, _, _, _ = pb.parse_all(binary_file)
	volts_list.append(volts)

### DEFINE TEST OBJECTS HERE ###

### PUT IN LIST eg test = [test1, test2, test3, test4] ###
tests = []
util.show_dc_noise(tests=tests)