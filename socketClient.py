#   Python Socket client
#   Created May 1 2023 by Joel Legassie
#   
#  Functionality
#  Connect to server and send test byte
#  Receive 24 bytes data and decode into 3x1 vector
#  Decodes binary code in 12 bit twos complement into 16 bit signed integers
#  Organizes samples into packets of packetSize corresponding to a gesture
#  Writes packets to files cumulatively - binary and human readable (CSV)
#  Generates plot images of each packet


import socket  
import numpy as np
import struct
import time
import threading
from threading import Thread
import matplotlib.pyplot as plt 
import os.path          

class GetData:
    
    def __init__(self, *, host="192.168.1.65", port=80, packetSize=5, numSensors=4, pathPreface='data/data', label=0, getTraining=True, packetLimit=100):
        self.host = host
        self.port = port
        self.packetSize = packetSize
        self.numSensors = numSensors
        self.packetData = np.zeros([1, self.packetSize * self.numSensors * 3]) #one packet of data corresponding to a gesture - 3 axis * number of sensors times the number of samples per gesture
        self.packetArr = np.zeros([1, self.packetSize * self.numSensors * 3]) #An array of packets (gestures) used while collecting data for training
        self.packetCount = 0
        self.packetDone = 0
        self.pathPreface = pathPreface 
        self.label = label
        self.getTraining = getTraining
        self.packetLimit = packetLimit

    def processData(self, binaryData, recvCount):
      
        #print(f'processData recvCount(): {recvCount}')
        #print(f'binaryData: {binaryData}')

        #packetStartMS = int(time() * 1000)
        #global processCount

        def formatData(binaryData, sensorIndex):
            #print(f'recvCount: {recvCount}')
            #Parse binary data and recombine into ints
            #X Axis
            XAcc = struct.unpack("=b", binaryData[1 + (sensorIndex * 6)])  ##MSB is second byte in axis RX; Just a nibble
            #print(f'XAcc Raw: {XAcc}')
            XAcc = XAcc[0] << 8
            #print(f'XAcc Shift: {XAcc}')
            XAcc1 = struct.unpack("=b", binaryData[0 + (sensorIndex * 6)])  ##LSB is first byte in axis RX; full byte
            self.packetData[0,(self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = XAcc + XAcc1[0]
            #print(f'XAcc Final: {XAcc}')

            #Y Axis
            YAcc = struct.unpack("=b", binaryData[3 + (sensorIndex * 6)])
            #print(f'XAcc Raw: {XAcc}')
            YAcc = YAcc[0] << 8
            #print(f'YAcc Shift: {YAcc}')
            YAcc1 = struct.unpack("=b", binaryData[2 + (sensorIndex * 6)])
            self.packetData[0, 1 + (self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = YAcc + YAcc1[0]
            #print(f'YAcc Final: {YAcc}')

            #Z Axis
            ZAcc = struct.unpack("=b", binaryData[5 + (sensorIndex * 6)])
            #print(f'XAcc Raw: {XAcc}')
            ZAcc = ZAcc[0] << 8
            #print(f'ZAcc Shift: {ZAcc}')
            ZAcc1 = struct.unpack("=b", binaryData[4 + (sensorIndex * 6)])
            self.packetData[0, 2 + (self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = ZAcc + ZAcc1[0]
            #print(f'ZAcc Final: {ZAcc}')
        
        if recvCount < self.packetSize:
            for i in range(self.numSensors):
                formatData(binaryData, i)
            
            # X1Acc, Y1Acc, Z1Acc = formatData(binaryData, 0)
            # self.packetData[0,0 + (recvCount * 3)] = X1Acc
            # self.packetData[0,1 + (recvCount * 3)] = Y1Acc
            # self.packetData[0,2 + (recvCount * 3)] = Z1Acc

            # X2Acc, Y2Acc, Z2Acc = formatData(binaryData, 1)
            # self.packetData[0,0 + (recvCount * 3)] = X2Acc
            # self.packetData[recvCount,1,1] = Y2Acc
            # self.packetData[recvCount,1,2] = Z2Acc

            # X3Acc, Y3Acc, Z3Acc = formatData(binaryData, 2)
            # self.packetData[recvCount,2,0] = X3Acc
            # self.packetData[recvCount,2,1] = Y3Acc
            # self.packetData[recvCount,2,2] = Z3Acc

            # X4Acc, Y4Acc, Z4Acc = formatData(binaryData, 3)
            # self.packetData[recvCount,3,0] = X4Acc
            # self.packetData[recvCount,3,1] = Y4Acc
            # self.packetData[recvCount,3,2] = Z4Acc

        #print(f'self.packetArr: {self.packetArr}')
        #print()
        # print(f'self.packetArr:')
        # for i in range(self.numSensors):
        #     for j in range(3):
        #         print(f'Sample: {recvCount}, Sensor: {i}, Axis: {j}: {self.packetArr[recvCount,i,j]}')
        # #     print()


    def socketLoop(self, recvCount): 

        packetStartMS = 0

        while self.packetCount < self.packetLimit:                   #keep getting packets until the packetLimit is reaches   
            if recvCount == 0:

                if self.getTraining:
                    #Prompt user to get ready to create training data
                    time.sleep(0.5)
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
                
                packetStartMS = int(time.time() * 1000)
                print(f'Start packet time: {packetStartMS}')

            while recvCount < self.packetSize:             

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
                sampleRxStartMS = int(time.time() * 1000)
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
                
                print(f'Sample Received')
                sampleRxStopMS = int(time.time() * 1000)
                sampleRxTimeMS = sampleRxStopMS - sampleRxStartMS
                print(f'Sample receive time in ms: {sampleRxTimeMS}')
                
                #print(f'Start preocessData() thread for sample: {recvCount}' )
                dataThread = Thread(target=self.processData, args=(y, recvCount,))
                dataThread.start()
                recvCount += 1
                #print(f'Completed Rx of sample: {recvCount}' )
                #socketLoop(recvCount)

            if recvCount == self.packetSize:                      # Once we've received 5 packets
                while threading.active_count() > 1:    #wait for the last threads to finish processing
                    #print(f'threading.active_count(): {threading.active_count()}')
                    pass
                
                print(f'Packet Done')
                packetStopMS = int(time.time() * 1000)
                packetTimeMS = packetStopMS - packetStartMS
                print(f'packetStart: {packetStartMS}')
                print(f'packetStopMS: {packetStopMS}')
                print(f'packet processing time in ms: {packetTimeMS}')
                # for thread in threading.enumerate(): 
                #     print(thread.name)
                #print()
                #print(f'data: {self.packetArr}')
                #print()
                
                if self.getTraining:
                    #Save data for training
                    #Training Label codes
                    # 0 Not movinng - Environmental movements
                    # 1 Alternate up and down
                    # 2 Out and in alternately
                    metaDataTimeStartMs = int(time.time() * 1000)
                    #Append the data to the packet array
                    np.append(self.packetArr,self.packetData, axis=1) 
                    self.prepTraining()
                    self.plotAcc()
                    metaDataTimeStopMs = int(time.time() * 1000)
                    print(f'metaData Time Save to files and image [ms]: {metaDataTimeStopMs - metaDataTimeStartMs}')   
                
                print(f'Completed packet: {self.packetCount + 1} of {self.packetLimit} packets')
                self.packetCount += 1
                recvCount = 0    #Reset recvCount to get the next packet
        
        self.packetCount = 0            
        return 0

    def prepTraining(self):    #Prep the packet for training

        #TODO add ground treuth labels data
        #self.packetArr is a three dimensional array (self.packetSize, self.numSensors, Axi[XYZ])
        #Scale Axes to +-1

        #trainingData = np.zeros_like(self.packetArr)
        #trainingData = np.resize(trainingData, (self.packetSize,self.numSensors,4))   #Add another spot for the ground truth label
        print(self.packetData) 

        #scale the data to +-1
        for feature in self.packetData:
            feature = feature / 2048

        #Get ground truth labels
        packetTruth = np.array([1,1])
        packetTruth[0,0] = self.label

        # #print(f'self.packetArr Original: {self.packetArr}')  
        # #print(f'trainingData Original: {trainingData}') 
        # for i in range(self.packetSize):
        #     #print()
        #     #print(f'i: {i}')
        #     for j in range(self.numSensors):
        #         #print(f'j: {j}')
        #         #print(f'packetArr pre-scaled (X): {self.packetArr[i, j, 0]}')
        #         if self.packetArr[i, j, 0]:                   #X axis not zero
        #             trainingData[i, j, 0] = self.packetArr[i, j, 0] / 2048
        #             #print(f'trainingData post-scaled (X): {trainingData[i, j, 0]}')
        #         else:
        #           trainingData[i, j, 0] = 0.  
                
        #         #print(f'packetArr pre-scaled (Y): {self.packetArr[i, j, 1]}')
        #         if self.packetArr[i, j, 1]:                   #Y axis not zero
        #             trainingData[i, j, 1] = self.packetArr[i, j, 1] / 2048
        #             #print(f'trainingData post-scaled (Y): {trainingData[i, j, 1]}')
        #         else:
        #           trainingData[i, j, 1] = 0.
                
        #         #print(f'packetArr pre-scaled (Z): {self.packetArr[i, j, 2]}')
        #         if self.packetArr[i, j, 2]:                   #Z axis not zero
        #             trainingData[i, j, 2] = self.packetArr[i, j, 2] / 2048 
        #             #print(f'trainingData post-scaled (Z): {trainingData[i, j, 2]}')
        #         else:
        #           trainingData[i, j, 2] = 0.

        #         #print(f'trainingData scaled: {trainingData}')    

        #         trainingData[i,j,3] = self.label          #Add ground truth label

        #print(f'trainingData scaled Complete: {trainingData}') 

        #print(f'trainingData [0,2,0]: {trainingData[0,2,0]}')
        #print(f'packetArr [0,2,0]: {self.packetArr[0,2,0]}')
        #print(f'packetArr [0,2,2]: {self.packetArr[0,2,2]}')

        #pathToBinary = self.pathPreface + '.npy'
        #pathToCSV = self.pathPreface + '.csv'

        #Write to files
        self.writetoBinary(self.packetData, packetTruth)
        self.writetoCSV(self.packetData, packetTruth)

    def writetoBinary(self,trainingData, packetTruth):
        #print(f'trainingData for write: {trainingData}')
        #Write data to .npy file (binary)
        dataPath = self.pathPreface + '.npy'
        truthPath = self.pathPreface + '_truth.npy'

        if os.path.exists(dataPath):
            tmpArr = np.load(dataPath,allow_pickle=False)
            #print(f'tmpArr from file: {tmpArr}')
            tmpArr = np.append(tmpArr,trainingData, axis=1)
            np.save(dataPath, tmpArr, allow_pickle=False)
            print(f'dataPacket saved (Binary): {tmpArr}')
        else: 
            np.save(dataPath, trainingData, allow_pickle=False)
            print(f'dataPacket saved (Binary): {trainingData}')

        if os.path.exists(truthPath):
            tmpArr = np.load(truthPath,allow_pickle=False)
            #print(f'tmpArr from file: {tmpArr}')
            tmpArr = np.append(tmpArr,packetTruth, axis=1)
            np.save(truthPath, tmpArr, allow_pickle=False)
            print(f'packetTruth appended and saved (Binary): {tmpArr}')
        else: 
            np.save(truthPath, packetTruth, allow_pickle=False)
            print(f'packetTruth saved (Binary): {packetTruth}')

    def writetoCSV(self, trainingData, packetTruth):
        #Write data to .csv file (text)
        dataPath = self.pathPreface + '.csv'
        truthPath = self.pathPreface + '_truth.csv'
        if os.path.exists(dataPath):
            tmpArr = np.loadtxt(dataPath,dtype=float, delimiter=',')
            #print(f'tmpArr.shape 1: {tmpArr.shape}')
            #print(f'tmpArr: {tmpArr}')
            
            #TwoDtrainingData = np.reshape(trainingData, (trainingData.shape[0] * 4, 4))  #Shape trainingData to 2-D array for CSV
            #print(f'TwoDtrainingData Shape: {TwoDtrainingData.shape}')   
            #print(f'TwoDtrainingData: {TwoDtrainingData}')            
            
            tmpArr = np.append(tmpArr,trainingData, axis=1)                  #Append trainingData to tmpArr
            #print(f'tmpArr.shape 2: {tmpArr.shape}')
            #print(f'tmpArr: {tmpArr}')

            np.savetxt(dataPath, tmpArr, fmt="%f", delimiter=",") 
            print(f'dataPacket appended and saved (CSV): {tmpArr}')
        else: 
            #tmpArr = np.reshape(trainingData, (trainingData.shape[0] * 4, 4))   #Reshape to a 2-D array
            np.savetxt(dataPath, trainingData, fmt="%f", delimiter=",")
            print(f'dataPacket appended and saved (CSV): {trainingData}')
        
        if os.path.exists(truthPath):
            tmpArr = np.loadtxt(truthPath,dtype=float, delimiter=',')
            tmpArr = np.append(tmpArr,packetTruth, axis=1) 
            np.savetxt(truthPath, tmpArr, fmt="%f", delimiter=",")
            print(f'packetTruth appended and saved (CSV): {tmpArr}')
        else: 
             np.savetxt(truthPath, packetTruth, fmt="%f", delimiter=",")
             print(f'packetTruth appended and saved (CSV): {packetTruth}')

    def plotAcc(self):
        #Arrange the data
        #time.sleep(2)

        # XList = [[],[]]
        # for i in range(self.packetSize):
        #     XList[0].append(self.packetData[0,0 + (i * self.numSensors * 3)])
        #     XList[1].append(i)
        # #print(f'XList1: {XList1}')

        # XList2 = [[],[]]
        # for i in range(self.packetSize):
        #     XList2[0].append(self.packetArr[i,1,0])
        #     XList2[1].append(i)
        # #print(f'XList: {XList}')

        # XList3 = [[],[]]
        # for i in range(self.packetSize):
        #     XList3[0].append(self.packetArr[i,2,0])
        #     XList3[1].append(i)
        # #print(f'XList1: {XList1}')

        # XList4 = [[],[]]
        # for i in range(self.packetSize):
        #     XList4[0].append(self.packetArr[i,3,0])
        #     XList4[1].append(i)
        # #print(f'XList: {XList}')

        # YList1 = [[],[]]
        # for i in range(self.packetSize):
        #     YList1[0].append(self.packetArr[i,0,1])
        #     YList1[1].append(i)
        # #print(f'YList: {YList}')

        # YList2 = [[],[]]
        # for i in range(self.packetSize):
        #     YList2[0].append(self.packetArr[i,1,1])
        #     YList2[1].append(i)
        # #print(f'YList: {YList}')

        # YList3 = [[],[]]
        # for i in range(self.packetSize):
        #     YList3[0].append(self.packetArr[i,2,1])
        #     YList3[1].append(i)
        # #print(f'XList1: {XList1}')

        # YList4 = [[],[]]
        # for i in range(self.packetSize):
        #     YList4[0].append(self.packetArr[i,3,1])
        #     YList4[1].append(i)

        # ZList1 = [[],[]]
        # for i in range(self.packetSize):
        #     ZList1[0].append(self.packetArr[i,0,2])
        #     ZList1[1].append(i)
        # #print(f'ZList: {ZList}')

        # ZList2 = [[],[]]
        # for i in range(self.packetSize):
        #     ZList2[0].append(self.packetArr[i,1,2])
        #     ZList2[1].append(i)
        # #print(f'ZList2: {ZList2}')

        # ZList3 = [[],[]]
        # for i in range(self.packetSize):
        #     ZList3[0].append(self.packetArr[i,2,2])
        #     ZList3[1].append(i)
        # #print(f'XList1: {XList1}')

        # ZList4 = [[],[]]
        # for i in range(self.packetSize):
        #     ZList4[0].append(self.packetArr[i,3,2])
        #     ZList4[1].append(i)

        _,axs = plt.subplots(self.numSensors,3, figsize=(12,8))
        
        #Axis labels
        axs[0][0].set_title('X Axis')
        axs[0][1].set_title('Y Axis')
        axs[0][2].set_title('Z Axis')
        
        for i in range(self.numSensors):
            # Sensor labels
            axs[i][0].set_ylabel(f'Sensor {i}')

            #Data
            XList = [[],[]]
            for j in range(self.packetSize):
                XList[0].append(self.packetData[0, 0 + (i * 3) + (j * self.numSensors * 3)])
                XList[1].append(j)
                print(f'XList{j}: {XList}')
            axs[i][0].plot(XList[0], YList[1])

            YList = [[],[]]
            for j in range(self.packetSize):
                YList[0].append(self.packetData[0, 1 + (i * 3) + (j * self.numSensors * 3)])
                YList[1].append(j)
                print(f'YList{j}: {ZList}')
            axs[i][1].plot(YList[0], YList[1])

            ZList = [[],[]]
            for j in range(self.packetSize):
                ZList[0].append(self.packetData[0, 2 + (i * 3) + (j * self.numSensors * 3)])
                ZList[1].append(j)
                print(f'ZList{j}: {ZList}')
            axs[i][2].plot(ZList[0], ZList[1])
            

            # axs[1][0].plot(XList2[1],XList2[0])
            # axs[1][1].plot(YList2[1],YList2[0])
            # axs[1][2].plot(ZList2[1],ZList2[0])
            # axs[2][0].plot(XList3[1],XList3[0])
            # axs[2][0].set_ylabel('Sensor 3')
            # axs[2][1].plot(YList3[1],YList3[0])
            # axs[2][2].plot(ZList3[1],ZList3[0])
            # axs[3][0].plot(XList4[1],XList4[0])
            # axs[3][0].set_ylabel('Sensor 4')
            # axs[3][1].plot(YList4[1],YList4[0])
            # axs[3][2].plot(ZList4[1],ZList4[0])
    
        figPath = self.pathPreface + str(self.packetCount) + '_' + str(self.label) + '.png'
        plt.savefig(figPath)
        #plt.show()            

def createTrainingData(*, pathPreface='data/data', label=0, packetLimit=1, packetSize=10):
    trgData = GetData(packetSize=packetSize, pathPreface=pathPreface, label=label, getTraining=True, packetLimit=packetLimit)
    trgData.socketLoop(0)

def main():
    
    #createTrainingData(pathPreface="data/packet5Avg20/training00_noMove", packetLimit=5, label=0, packetSize=5)
    #createTrainingData(pathPreface="data/packet5Avg20/training01_upandDown", packetLimit=5, label=1, packetSize=5)
    #createTrainingData(pathPreface="data/packet5Avg20/training02_inandOut", packetLimit=5, label=2, packetSize=5)

    createTrainingData(pathPreface="data/test/test", packetLimit=5, label=0, packetSize=5)

    

if __name__ == "__main__": main()