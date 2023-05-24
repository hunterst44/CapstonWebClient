#   Python Socket client
#   Sends query to esp32 to request data
#   Accepts streaming data from esp32
#   Performs data analysis on data received
#   
#  Basic functionality
#  Connect to server and send test byte
#  Receive six bytes data and decode into 3x1 vector


import socket  
import numpy as np
import struct
import time
import threading
from threading import Thread
import matplotlib.pyplot as plt 
import os.path          

class GetData:
    
    def __init__(self, *, host="192.168.1.75", port=80, packetSize=5, numSensors=4, pathPreface='data/data', label=0, getTraining=True, packetLimit=100):
        self.host = host
        self.port = port
        self.packetSize = packetSize
        self.numSensors = numSensors
        self.AccData = np.zeros([self.packetSize, self.numSensors, 3])
        self.packetCount = 0
        self.packetDone = 0
        self.packetStartMS = int(time.time() * 1000)
        self.pathPreface = pathPreface 
        self.label = label
        self.getTraining = getTraining
        self.packetLimit = packetLimit


# sock = socket.socket()
# host = "192.168.1.75"
# port = 80    
# packetStartMS = int(time.time() * 1000)   
# self.packetDone = 0 
# PACKETSIZE = 5   #Size of a packet - corresponds to a gesture -- aim to cover about 1 - 2 seconds of sampling time (~10 samples) Use less for testing
# NUMSENSORS = 4   #Number of sensors
# self.packetCount = 0  #number of packets through the machine
# AccData = np.zeros([PACKETSIZE,NUMSENSORS,3])    ##3 dimensional array to hold sensor data [Samples: Sensors : Features]


    def processData(self, binaryData, recvCount):
        print(f'processData recvCount(): {recvCount}')
        print(f'binaryData: {binaryData}')

        #packetStartMS = int(time() * 1000)
        #global processCount

        def formatData(binaryData, sensorIndex):
            print(f'recvCount: {recvCount}')
            #Parse binary data and recombine into ints
            #X Axis
            XAcc = struct.unpack("=b", binaryData[1 + (sensorIndex * 6)])  ##MSB is second byte in axis RX; Just a nibble
            #print(f'XAcc Raw: {XAcc}')
            XAcc = XAcc[0] << 8
            #print(f'XAcc Shift: {XAcc}')
            XAcc1 = struct.unpack("=b", binaryData[0 + (sensorIndex * 6)])  ##LSB is first byte in axis RX; full byte
            XAcc = XAcc + XAcc1[0]
            print(f'XAcc Final: {XAcc}')

            #Y Axis
            YAcc = struct.unpack("=b", binaryData[3 + (sensorIndex * 6)])
            #print(f'XAcc Raw: {XAcc}')
            YAcc = YAcc[0] << 8
            #print(f'YAcc Shift: {YAcc}')
            YAcc1 = struct.unpack("=b", binaryData[2 + (sensorIndex * 6)])
            YAcc = YAcc + YAcc1[0]
            print(f'YAcc Final: {YAcc}')

            #Z Axis
            ZAcc = struct.unpack("=b", binaryData[5 + (sensorIndex * 6)])
            #print(f'XAcc Raw: {XAcc}')
            ZAcc = ZAcc[0] << 8
            #print(f'ZAcc Shift: {ZAcc}')
            ZAcc1 = struct.unpack("=b", binaryData[4 + (sensorIndex * 6)])
            ZAcc = ZAcc + ZAcc1[0]
            print(f'ZAcc Final: {ZAcc}')
            return XAcc, YAcc, ZAcc
        
        if recvCount < self.packetSize:
        
            X1Acc, Y1Acc, Z1Acc = formatData(binaryData, 0)
            self.AccData[recvCount,0,0] = X1Acc
            self.AccData[recvCount,0,1] = Y1Acc
            self.AccData[recvCount,0,2] = Z1Acc

            X2Acc, Y2Acc, Z2Acc = formatData(binaryData, 1)
            self.AccData[recvCount,1,0] = X2Acc
            self.AccData[recvCount,1,1] = Y2Acc
            self.AccData[recvCount,1,2] = Z2Acc

            X3Acc, Y3Acc, Z3Acc = formatData(binaryData, 2)
            self.AccData[recvCount,2,0] = X3Acc
            self.AccData[recvCount,2,1] = Y3Acc
            self.AccData[recvCount,2,2] = Z3Acc

            X4Acc, Y4Acc, Z4Acc = formatData(binaryData, 3)
            self.AccData[recvCount,3,0] = X4Acc
            self.AccData[recvCount,3,1] = Y4Acc
            self.AccData[recvCount,3,2] = Z4Acc

        #print(f'self.AccData: {self.AccData}')
        #print()
        print(f'self.AccData:')
        for i in range(self.numSensors):
            for j in range(3):
                print(f'Sample: {recvCount}, Sensor: {i}, Axis: {j}: {self.AccData[recvCount,i,j]}')
        #     print()

    def prepTraining(self):    #Prep the packet for training

        #self.AccData is a three dimensional array (self.packetSize, self.numSensors, Axi[XYZ])
        #Scale Axes to +-1

        trainingData = self.AccData.copy()
        trainingData = np.resize(trainingData, (self.packetSize,self.numSensors,4))   #Add another spot for the ground truth label

        print(f'self.AccData Original: {self.AccData}')  
        for i in range(self.packetSize):
            for j in range(self.numSensors):
                if self.AccData[i, j, 0]:                   #X axis not zero
                    trainingData[i, j, 0] = trainingData[i, j, 0] / 2048

                if trainingData[i, j, 1]:                   #Y axis not zero
                    trainingData[i, j, 1] = trainingData[i, j, 1] / 2048
            
                if trainingData[i, j, 2]:                   #Z axis not zero
                    trainingData[i, j, 2] = trainingData[i, j, 2] / 2048 

                #print(f'trainingData scaled: {trainingData}')    

                trainingData[i,j,3] = self.label          #Add ground truth label

        #print(f'trainingData scaled: {trainingData}') 

        pathToBinary = self.pathPreface + '.npy'
        pathToCSV = self.pathPreface + '.csv'

        #Write to files
        self.writetoBinary(trainingData, pathToBinary)
        self.writetoCSV(trainingData, pathToCSV)

    def writetoBinary(self,trainingData, pathTo):
        print(f'trainingData for write: {trainingData}')
        #Write data to .npy file (binary)
        if os.path.exists(pathTo):
            tmpArr = np.load(pathTo,allow_pickle=False)
            print(f'tmpArr from file: {tmpArr}')
            tmpArr = np.append(tmpArr,trainingData, axis=0)
            print(f'tmpArr appended and saved (Binary): {tmpArr}')
            np.save(pathTo, tmpArr, allow_pickle=False)
        else: 
            np.save(pathTo, trainingData, allow_pickle=False)
            print(f'trainingData saved: {trainingData}')

    def writetoCSV(self, trainingData, pathTo):
        #Write data to .csv file (text)
        #TODO: Flatten to 2D before write; expand to 3D after read numpy.reshape()
        if os.path.exists(pathTo):
            tmpArr = np.loadtxt(pathTo,dtype=float, delimiter=',')
            print(f'tmpArr.shape 1: {tmpArr.shape}')
            
            TwoDtrainingData = np.reshape(trainingData, (trainingData.shape[0] * 4, 4))  #Shape trainingData to 2-D array for CSV
            print(f'TwoDtrainingData Shape: {TwoDtrainingData.shape}')              
            
            tmpArr = np.append(tmpArr,TwoDtrainingData, axis=0)                  #Append trainingData to tmpArr
            print(f'tmpArr.shape 2: {tmpArr.shape}')

            np.savetxt(pathTo, tmpArr, fmt="%f", delimiter=",") 
            print(f'tmpArr appended and saved (TXT): {tmpArr}')

        else: 
            tmpArr = np.reshape(trainingData, (trainingData.shape[0] * 4, 4))   #Reshape to a 2-D array
            np.savetxt(pathTo, tmpArr, fmt="%f", delimiter=",")
            print(f'tmpArr appended and saved (TXT): {tmpArr}')

    def plotAcc(self):
        #Arrange the data
        #time.sleep(2)

        XList1 = [[],[]]
        for i in range(self.packetSize):
            XList1[0].append(self.AccData[i,0,0])
            XList1[1].append(i)
        #print(f'XList1: {XList1}')

        XList2 = [[],[]]
        for i in range(self.packetSize):
            XList2[0].append(self.AccData[i,1,0])
            XList2[1].append(i)
        #print(f'XList: {XList}')

        XList3 = [[],[]]
        for i in range(self.packetSize):
            XList3[0].append(self.AccData[i,2,0])
            XList3[1].append(i)
        #print(f'XList1: {XList1}')

        XList4 = [[],[]]
        for i in range(self.packetSize):
            XList4[0].append(self.AccData[i,3,0])
            XList4[1].append(i)
        #print(f'XList: {XList}')

        YList1 = [[],[]]
        for i in range(self.packetSize):
            YList1[0].append(self.AccData[i,0,1])
            YList1[1].append(i)
        #print(f'YList: {YList}')

        YList2 = [[],[]]
        for i in range(self.packetSize):
            YList2[0].append(self.AccData[i,1,1])
            YList2[1].append(i)
        #print(f'YList: {YList}')

        YList3 = [[],[]]
        for i in range(self.packetSize):
            YList3[0].append(self.AccData[i,2,1])
            YList3[1].append(i)
        #print(f'XList1: {XList1}')

        YList4 = [[],[]]
        for i in range(self.packetSize):
            YList4[0].append(self.AccData[i,3,1])
            YList4[1].append(i)

        ZList1 = [[],[]]
        for i in range(self.packetSize):
            ZList1[0].append(self.AccData[i,0,2])
            ZList1[1].append(i)
        #print(f'ZList: {ZList}')

        ZList2 = [[],[]]
        for i in range(self.packetSize):
            ZList2[0].append(self.AccData[i,1,2])
            ZList2[1].append(i)
        #print(f'ZList2: {ZList2}')

        ZList3 = [[],[]]
        for i in range(self.packetSize):
            ZList3[0].append(self.AccData[i,2,2])
            ZList3[1].append(i)
        #print(f'XList1: {XList1}')

        ZList4 = [[],[]]
        for i in range(self.packetSize):
            ZList4[0].append(self.AccData[i,3,2])
            ZList4[1].append(i)

        _,axs = plt.subplots(4,3, figsize=(6,4))
        #axs[0][0].plot(self.AccData[:,1,1])
        axs[0][0].plot(XList1[1],XList1[0])
        axs[0][0].set_title('X Axis')
        axs[0][1].plot(YList1[1],YList1[0])
        axs[0][1].set_title('Y Axis')
        axs[0][2].plot(ZList1[1],ZList1[0])
        axs[0][2].set_title('Z Axis')
        axs[1][0].plot(XList2[1],XList2[0])
        #axs[1][0].set_title('Sensor 2, X Axis')
        axs[1][1].plot(YList2[1],YList2[0])
        #axs[1][1].set_title('Sensor 2, Y Axis')
        axs[1][2].plot(ZList2[1],ZList2[0])
        #axs[1][2].set_title('Sensor 2, Z Axis')
        axs[2][0].plot(XList3[1],XList3[0])
        #axs[1][0].set_title('Sensor 3, X Axis')
        axs[2][1].plot(YList3[1],YList3[0])
        #axs[2][1].set_title('Sensor 3, Y Axis')
        axs[2][2].plot(ZList3[1],ZList3[0])
        #axs[2][2].set_title('Sensor 3, Z Axis')
        axs[3][0].plot(XList4[1],XList4[0])
        #axs[3][0].set_title('Sensor 4, X Axis')
        axs[3][1].plot(YList4[1],YList4[0])
        #axs[3][1].set_title('Sensor 4, Y Axis')
        axs[3][2].plot(ZList4[1],ZList4[0])
        #axs[3][2].set_title('Sensor 4, Z Axis')
    
        figPath = self.pathPreface + str(self.packetCount) + '_' + str(self.label) + '.png'
        plt.savefig(figPath)
        plt.show()


    def socketLoop(self, recvCount): 
        #recvCount counts how many packets have been received
        #print()
        #print("socketLoop")
        #global processCount
        #print(f'processCount: {processCount}' )
        #print(f'Start socketLoop recvCount: {recvCount}' )
        #global packetDone
        #global packetStartMS
        #global packetCount
        if recvCount == 0:
            self.packetStartMS = int(time.time() * 1000)

            if self.getTraining:
                #Prompt user to get ready to create training data
                print('********************************************')  
                print('********************************************') 
                print('********************************************') 
                print('Creating training data.')

                if self.label == 0:
                    print('Get ready to perform gesture: 0 No movement')
                elif self.label == 1:
                    print('Get ready to perform gesture: 1 Alternate up and down')
                elif self.label == 2:
                    print('Get ready to perform gesture: 2 Out and in together')
                
                print('In 3...')
                time.sleep(1)
                print('2...')
                time.sleep(1)
                print('1...')
                time.sleep(1)
                print('Go!')
                time.sleep(0.1)

        while recvCount <= self.packetSize:             #Only needed for testing - production code will run continiously
            sock = socket.socket()
            sock.connect((self.host, self.port))
            #print("Connected to server")
            dataTx = struct.pack("=i", 255)
            #try:
            sock.send(dataTx);
            #except:
            #    sock.connect((host, port))
            #    print("Socket Reconnected")
            #    sock.send(255);
            #print(f'sockname: {sock.getsockname()}')
            #print(f'sockpeer: {sock.getpeername()}')
            y = []
            #time.sleep(0.01)
            #y = sock.recv(18)
            a = 0
            errorCount = 0
            while a < 24:
                #print(f'while loop a')
                try:
                    y.append(sock.recv(1))
                    #print(f'Received 1')
                except ConnectionError:
                    print(f"Unable to reach client with socket: Retrying")
                    print(f'Connection error recvCount: {recvCount}' )
                    #Close and reopen the connection
                    if errorCount < 10:
                        #Close and reopen the connection
                        sock.close()
                        sock = socket.socket()
                        sock.connect((self.host, self.port))
                        a -= 1     #Ask for a resend
                        errorCount += 1
                        sock.send(dataTx);
                    else:
                        print(f'Fatal Error: SocketBroken')
                        return -1

                a += 1 
            sock.close()
            print(f'Start preocessData() thread for sample: {recvCount}' )
            dataThread = Thread(target=self.processData, args=(y, recvCount,))
            dataThread.start()
            recvCount += 1
            print(f'Completed Rx of sample: {recvCount}' )
            #socketLoop(recvCount)

            if recvCount == self.packetSize:                      # Once we've received 5 packets
                while threading.active_count() > 1:    #wait for the last threads to finish processing
                    #print(f'threading.active_count(): {threading.active_count()}')
                    pass
                
                print(f'Packet Done')
                packetStopMS = int(time.time() * 1000)
                packetTimeMS = packetStopMS - self.packetStartMS
                #print(f'packetStart: {self.packetStartMS}')
                print(f'processing time in ms: {packetTimeMS}')
                # for thread in threading.enumerate(): 
                #     print(thread.name)
                #print()
                #print(f'data: {self.AccData}')
                #print()
                #self.plotAcc()
                
                if self.getTraining:
                    #Save data for training
                    #Training Label codes
                    # 0 Not movinng - Environmental movements
                    # 1 Alternate up and down
                    # 2 Out and in alternately
                    self.prepTraining()
                
                #self.packetDone = 1
                print(f'Completed packet: {self.packetCount} of {self.packetLimit} packets')
                #time.sleep(1)
                self.packetCount += 1
                if self.packetCount > self.packetLimit:  # We have all the packets we need 
                    #Jobs done
                    return 0
                recvCount = 0    #Reset recvCount to get the next packet

def createTrainingData(*, pathPreface='data/data', label=0, packetLimit=5, packetSize=5):
    trgData = GetData(packetSize=packetSize, pathPreface=pathPreface, label=label, getTraining=True, packetLimit=packetLimit)
    trgData.socketLoop(0)

def main():
    
    createTrainingData(pathPreface="data/training00_noMove", label=0)
    createTrainingData(pathPreface="data/training01_upandDown", label=1)
    createTrainingData(pathPreface="data/training01_inandOut", label=2)

    

if __name__ == "__main__": main()