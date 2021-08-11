#!/usr/bin/env python2

"""
This code plots data from Main PIP in real time.
Max Roberts, 08/05/2016

Edited for 230k 
Ruthie Nordhoff, 12/05/2018

"""

import sys
import time 
import serial
import threading
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

# Define a few constants, classes and functions
aScale = 4 * 9.8 / 2**15
mScale = 1. / 2**15
gScale = 2000. / 360 / 2**15
pipScale = 5. / 2**14

# 2 PIPs with 28 2-byte samples + 4-byte timestamp + ID
sweepSamples = 28
numSweepBytes = sweepSamples * 2 * 2 + 4 + 1

# 9 2-byte data points + 2-byte temp + 4-byte timestamp
numIMUBytes = 24

if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    print("Need to specify port for Main PIP, like:")
    print("python erpabob_realtime_plot_summer2021_delamere.py '/dev/tty.KeySerial1'")
    sys.exit()

class IMUData():
    def __init__(self):
        self.time = []; self.temp = []
        self.ax = []; self.ay = []; self.az = []
        self.mx = []; self.my = []; self.mz = []
        self.gx = []; self.gy = []; self.gz = []
        
class SweepData():
    def __init__(self):
        self.time = []
        self.pip0 = []
        self.pip1 = []
        
class PayloadData():
    def __init__(self):
        self.rawData = ''
        self.imu = IMUData()
        self.sweeps = SweepData()
        self.shieldID = 0
        
# A class for the thread to communicate with the main thread.
class Communication(QtCore.QObject):
    signal = QtCore.pyqtSignal()
        
# Functions for merging bytes
def combine2(a, b):
    return (a << 8) | b
def combine4(a, b, c, d):
    return (a << 24) | (b << 16) | (c << 8) | d

# plot class
class PayloadPlot(QtGui.QMainWindow):
    # constr
    def __init__(self, port):
        super(PayloadPlot, self).__init__()
        # open serial port, choose 115k or 230k
#        self.ser = serial.Serial(port, 230400, timeout=None)
        self.ser = serial.Serial(port, 115200, timeout=None)
        
        # Split out the port name to save with:
        port_name = port.split(".")[-1]
        
        # Open file to write to
#        self.dataFile = open('data_file_230k_%s.txt' %port_name, 'w')
        self.dataFile = open('data_file_115k_%s.txt' %port_name, 'w')
        self.closed = False
        time.sleep(10)
        self.rawData = ''

        self.t = []
        self.temp = []
        self.humid = []
        self.buf = ''
        
        self.imuLim = 80 * 5
        self.sweepLim = 16 * 5
        
        # These are a signals for comm between the data parsing and main thread 
        self.updatePlotSignal = Communication()
        self.updatePlotSignal.signal.connect(self.updatePlot)
        
        print("Initializing payload...")
        self.initializePayload()
        
        print("Intitializing plots...")
        self.initializePlotting()
        
        ###################################################
        ############### General Setup #####################
        ###################################################
        
        self.setGeometry(100, 100, 800, 1000)

        self.show()
        self.activateWindow()
        self.raise_()  # Brings window to front   
        
    # This one listens at start up to determine the payload MAC addresses
    def initializePayload(self):
        ########### Record initial data ###########
        # Collect 5 seconds of sample data
        # First, flush any initial junk by reading for 1 sec
        flushTime = 1
        start = time.clock()
        while time.clock()-start < flushTime:
            self.ser.read()
        # Collect 5 seconds of sample data
        readTime = 5
        rawData = ''
        start = time.clock() 
        while time.clock()-start < readTime:
            rawData += self.ser.read()
        end = time.clock()

        # Create payload objects and store parsed data
        self.payload = PayloadData()
        self.payload.rawData = rawData
            
        self.parse_raw_data(self.payload, init=True)
        
        # Start the update thread
        self.getDataWithThread()
            
    def initializePlotting(self):
        # set up animation
        #self.app = QtGui.QApplication([])
        red = (255,0,0)
        green = (0,255,0)
        blue = (0,0,255)

        # Generates grids with multiple items
        self.win = pg.GraphicsWindow()  
        self.p00 = self.win.addPlot(row=0, col=0)
        self.p00.setLabels(left=('Accel'))
#        self.p00.setLabels(left=('Accel'+str(self.payload.shieldID)))
        self.p01 = self.win.addPlot(row=1, col=0)
        self.p01.setLabels(left=('Mag'))
        self.p02 = self.win.addPlot(row=2, col=0)
        self.p02.setLabels(left=('Gyro'))
        #self.p03 = self.win.addPlot(row=3, col=0)
        #self.p03.setLabels(left=('Temp'))
        self.p03 = self.win.addPlot(row=3, col=0)
        self.p03.setLabels(left=('Cadence'))
#        self.p03.setLabels(left=('Cad. '+str(self.payload.shieldID)))
        self.p04 = self.win.addPlot(row=4, col=0)
        self.p04.setLabels(left=('PIP 1'))
        self.p05 = self.win.addPlot(row=5, col=0)
        self.p05.setLabels(left=('PIP 2'))
        
        # Plots for first payload 
        self.ax_0 = self.p00.plot([], [], pen=blue)
        self.ay_0 = self.p00.plot([], [], pen=green)
        self.az_0 = self.p00.plot([], [], pen=red)
        self.mx_0 = self.p01.plot([], [], pen=blue)
        self.my_0 = self.p01.plot([], [], pen=green)
        self.mz_0 = self.p01.plot([], [], pen=red)
        self.gx_0 = self.p02.plot([], [], pen=blue)
        self.gy_0 = self.p02.plot([], [], pen=green)
        self.gz_0 = self.p02.plot([], [], pen=red)
        #self.temp_0 = self.p03.plot([], [], pen=blue)
        self.cadence_0 = self.p03.plot([], [], pen=blue)
        self.pip0_0 = self.p04.plot([], [], pen=red)
        self.pip1_0 = self.p05.plot([], [], pen=green)
        
        grid = QtGui.QGridLayout()
        self.main_widget = QtGui.QWidget(self)
        self.main_widget.setLayout(grid)
        self.setCentralWidget(self.main_widget)
        grid.addWidget(self.win, 0,0)
        
    def parse_raw_data(self, payload, init=False):
        # Now parse the messages into measurements!
        data = payload.rawData
        imu = []
        sweeps = []
        pntr = 0
        while pntr < len(data):
            # Check message start sentinels and not at end
            if data[pntr] == '#' and (len(data)-pntr) >= numIMUBytes:
                if data[pntr+1] == 'I':
                    # If not the last, check message end sentinel
                    if pntr+2+numIMUBytes < len(data):
                        if data[pntr+2+numIMUBytes] == '#':
                            imu.append(data[pntr+2:pntr+2+numIMUBytes])
                    # Or just add the last message
                    else:
                        imu.append(data[pntr+2:pntr+2+numIMUBytes])
                    pntr += 1
                elif data[pntr+1] == 'S':
                    if pntr+2+numSweepBytes < len(data):
                        if data[pntr+2+numSweepBytes] == '#':
                            sweeps.append(data[pntr+2:pntr+2+numSweepBytes])
                    else:
                        sweeps.append(data[pntr+2:pntr+2+numSweepBytes])
                    pntr += 1
                else:
                    pntr += 1
            else:
                pntr += 1

        ########### Build data structures ###########
        
        # First the IMU
        imuTime = [];
        ax = []; ay = []; az = []
        mx = []; my = []; mz = []
        gx = []; gy = []; gz = []
        temp = [];
        
        for i in imu:
            if len(i) == numIMUBytes:
                imuTime.append(combine4(ord(i[3]), ord(i[2]), ord(i[1]), ord(i[0])))
                # The byte order is reversed, but the data sets are not
                ax.append(combine2(ord(i[5]), ord(i[4])))
                ay.append(combine2(ord(i[7]), ord(i[6])))
                az.append(combine2(ord(i[9]), ord(i[8])))
                mx.append(combine2(ord(i[11]), ord(i[10])))
                my.append(combine2(ord(i[13]), ord(i[12])))
                mz.append(combine2(ord(i[15]), ord(i[14])))
                gx.append(combine2(ord(i[17]), ord(i[16])))
                gy.append(combine2(ord(i[19]), ord(i[18])))
                gz.append(combine2(ord(i[21]), ord(i[20])))
                temp.append(combine2(ord(i[23]), ord(i[22])))
        if init:
            payload.imu.time = np.array(imuTime, dtype='uint32')/1.E6
            payload.imu.ax = np.array(ax, dtype='int16')*aScale
            payload.imu.ay = np.array(ay, dtype='int16')*aScale
            payload.imu.az = np.array(az, dtype='int16')*aScale
            payload.imu.mx = np.array(mx, dtype='int16')*mScale
            payload.imu.my = np.array(my, dtype='int16')*mScale
            payload.imu.mz = np.array(mz, dtype='int16')*mScale
            payload.imu.gx = np.array(gx, dtype='int16')*gScale
            payload.imu.gy = np.array(gy, dtype='int16')*gScale
            payload.imu.gz = np.array(gz, dtype='int16')*gScale
            payload.imu.temp = np.array(temp, dtype='int16')
            
        else:
            imuTime = np.array(imuTime, dtype='uint32')/1.E6
            ax = np.array(ax, dtype='int16')*aScale
            ay = np.array(ay, dtype='int16')*aScale
            az = np.array(az, dtype='int16')*aScale
            mx = np.array(mx, dtype='int16')*mScale
            my = np.array(my, dtype='int16')*mScale
            mz = np.array(mz, dtype='int16')*mScale
            gx = np.array(gx, dtype='int16')*gScale
            gy = np.array(gy, dtype='int16')*gScale
            gz = np.array(gz, dtype='int16')*gScale
            temp = np.array(temp, dtype='int16')

            # Add measurements and trim
            payload.imu.time = np.concatenate([ payload.imu.time, imuTime])[-self.imuLim:]
            payload.imu.ax = np.concatenate([ payload.imu.ax, ax])[-self.imuLim:]
            payload.imu.ay = np.concatenate([ payload.imu.ay, ay])[-self.imuLim:]
            payload.imu.az = np.concatenate([ payload.imu.az, az])[-self.imuLim:]
            payload.imu.mx = np.concatenate([ payload.imu.mx, mx])[-self.imuLim:]
            payload.imu.my = np.concatenate([ payload.imu.my, my])[-self.imuLim:]
            payload.imu.mz = np.concatenate([ payload.imu.mz, mz])[-self.imuLim:]
            payload.imu.gx = np.concatenate([ payload.imu.gx, gx])[-self.imuLim:]
            payload.imu.gy = np.concatenate([ payload.imu.gy, gy])[-self.imuLim:]
            payload.imu.gz = np.concatenate([ payload.imu.gz, gz])[-self.imuLim:]
            payload.imu.temp = np.concatenate([ payload.imu.temp, temp])[-self.imuLim:]

        # Then the sweeps
        payloadID = [];
        sweepTime = []
        allSweepsPIP0 = []
        individualSweepsPIP0 = []
        allSweepsPIP1 = []
        individualSweepsPIP1 = []
        
        PIP0StartByte = 4 + 1                             # Four for time, one payload ID  
        PIP0StopByte = PIP0StartByte + sweepSamples * 2   # Number of samples, two bytes each
        PIP1StopByte = PIP0StopByte + sweepSamples * 2      # Number of samples, two bytes each
    
        for i in sweeps:
            if len(i) == numSweepBytes:
                sweepTime.append(combine4(ord(i[3]), ord(i[2]), ord(i[1]), ord(i[0])))
                payloadID.append(ord(i[4]))
                tempSweep = []
                for byte in xrange(PIP0StartByte,PIP0StopByte,2):
                    allSweepsPIP0.append(combine2(ord(i[byte+1]), ord(i[byte])))
                    tempSweep.append(combine2(ord(i[byte+1]), ord(i[byte])))
                individualSweepsPIP0.append(tempSweep)
                tempSweep = []
                for byte in xrange(PIP0StopByte,PIP1StopByte,2):
                    allSweepsPIP1.append(combine2(ord(i[byte+1]), ord(i[byte])))
                    tempSweep.append(combine2(ord(i[byte+1]), ord(i[byte])))
                individualSweepsPIP1.append(tempSweep)
        payloadMatch = (len(set(payloadID)) == 1)
        if not payloadMatch:
            print("Payload IDs don't match. Something went wrong...")
            
        sweepTime = np.array(sweepTime, dtype='uint32')
        individualSweepsPIP0 = np.array(individualSweepsPIP0, dtype='int16')*pipScale
        individualSweepsPIP1 = np.array(individualSweepsPIP1, dtype='int16')*pipScale
        
        if init:
#            payload.shieldID = 1 # payloadID[0]
            payload.shieldID = payloadID[0]
            payload.sweeps.time = sweepTime/1.E6
            payload.sweeps.pip0 = individualSweepsPIP0
            payload.sweeps.pip1 = individualSweepsPIP1
            
        else:
            # Add measurements and trim
            payload.sweeps.time = np.concatenate([payload.sweeps.time, sweepTime])[-self.sweepLim:]
            payload.sweeps.pip0 = np.append(payload.sweeps.pip0, individualSweepsPIP0, axis=0)[-self.sweepLim:]
            payload.sweeps.pip1 = np.append(payload.sweeps.pip1, individualSweepsPIP1, axis=0)[-self.sweepLim:]
            
        # Clear the raw data for each payload
        payload.rawData = ''
            
    def updatePayloads(self):
        while not self.closed:
            ########### Collect 25000 bytes ###########
            rawData = ''
            for i in range(25000):
                data = self.ser.read()
                rawData += data
                self.dataFile.write(data)
                
            self.payload.rawData = rawData
        
            self.parse_raw_data(self.payload)
            
            # Send signal to update the plot
            self.updatePlotSignal.signal.emit()
       
    # update data set
    def getDataWithThread(self):
        # Start put the data retrieval on a new thread to not block the UI
        self.dataThread = threading.Thread(target=self.updatePayloads)
        self.dataThread.start()

    # update plot
    def updatePlot(self):
        self.ax_0.setData(self.payload.imu.time, self.payload.imu.ax)
        self.ay_0.setData(self.payload.imu.time, self.payload.imu.ay)
        self.az_0.setData(self.payload.imu.time, self.payload.imu.az)
        self.mx_0.setData(self.payload.imu.time, self.payload.imu.mx)
        self.my_0.setData(self.payload.imu.time, self.payload.imu.my)
        self.mz_0.setData(self.payload.imu.time, self.payload.imu.mz)
        self.gx_0.setData(self.payload.imu.time, self.payload.imu.gx)
        self.gy_0.setData(self.payload.imu.time, self.payload.imu.gy)
        self.gz_0.setData(self.payload.imu.time, self.payload.imu.gz)
        #self.temp_0.setData(self.payload.imu.time, self.payload.imu.temp)
        self.cadence_0.setData(np.diff(self.payload.imu.time))
        self.pip0_0.setData(self.payload.sweeps.pip0.flatten())
        self.pip1_0.setData(self.payload.sweeps.pip1.flatten())
        
        app.processEvents()
       
    """  Make sure to close the serial connection before exit """
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Really quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            # close serial
            self.closed = True
            time.sleep(.25)
            self.ser.flush()
            self.ser.close()
            time.sleep(.25)
            # close write file
            self.dataFile.close()
            event.accept()
        else:
            event.ignore()

# call main
if __name__ == '__main__':
    
  print('Using serial port %s...' % port)
  app = QtGui.QApplication(sys.argv)
  ex = PayloadPlot(port)
  sys.exit(app.exec_())
