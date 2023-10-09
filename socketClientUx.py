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
import NeuralNetwork
import dill  
import oscWriter       

class GetData:
    
    def __init__(self, *, host="192.168.1.75", port=80, packetSize=1, numSensors=4, pathPreface='data/data', labelPath="Test", label=0, getTraining=True):
        self.host = host
        self.port = port
        self.packetSize = packetSize
        self.numSensors = numSensors
        self.packetData = np.zeros([1, self.packetSize * self.numSensors * 3]) #one packet of data corresponding to a gesture - 3 axis * number of sensors times the number of samples per gesture
        #self.packetArr = np.zeros([1, self.packetSize * self.numSensors * 3]) #An array of packets (gestures) used while collecting data for training
        self.packetCount = 0
        self.packetDone = 0
        self.pathPreface = pathPreface 
        self.labelPath = labelPath
        self.label = label
        self.getTraining = getTraining
        #self.packetLimit = packetLimit
        self.predictions = []
        self.plotTimer = int(time.time() * 1000)   #Used to make timed plots of input data for plots
        self.plotCounter = 0 #counts how many plots have been made
        self.dataTx = struct.pack("=B", 255)     #Used to determine what data packet to get from the ESP32 (ie. time of flight data or no) (255 [OxFF] is no ToF, 15 [0x0F] is yes ToF)
        self.extraRxByte = 0   #Use to add to the socket RX index to collect the ToF byte when it exists
        self.ToFByte = -1 #Holds the ToF sensor data value
        self.y = []
        self.dataGot = 0   #data received flag

    def processData(self, binaryData):
        print()
        print(f'processData()')
        print(f'binaryData: {binaryData}')

        #packetStartMS = int(time() * 1000)
        #global processCount

        def formatData(binaryData, sensorIndex):
            print(f'sensor: {sensorIndex}')
            #print()
            #print(f'binaryData: {binaryData}')
            #Parse binary data and recombine into ints
            #X Axis

            # print(f'sensor: {sensorIndex}')
            # print(f'XIndex: {0 + (sensorIndex * 3 * self.numSensors)}')

            XAccTuple = struct.unpack("=b", binaryData[0 + (sensorIndex * 3)])  ##MSB is second byte in axis RX; Just a nibble
            XAcc = XAccTuple[0]
            #XAcc = float(int(binaryData[0 + (sensorIndex * 3 * self.numSensors)]),0)
            print(f'XAcc Raw: {XAcc}')
            if self.getTraining is False:
                self.packetData[0, (3 * sensorIndex)] = XAcc / 127
            else:
                self.packetData[0, (3 * sensorIndex)] = XAcc

            #Y Axis
            YAccTuple = struct.unpack("=b", binaryData[1 + (sensorIndex * 3)])
            YAcc = YAccTuple[0]
            print(f'YAcc Raw: {YAcc}')
            if self.getTraining is False:
                self.packetData[0, 1 + (3 * sensorIndex)] = YAcc / 127
            else:       
                self.packetData[0, 1 + (3 * sensorIndex)] = YAcc

            #Z Axis
            ZAccTuple = struct.unpack("=b", binaryData[2 + (sensorIndex * 3)])
            ZAcc = ZAccTuple[0]
            print(f'ZAcc Raw: {ZAcc}')
            if self.getTraining is False:
                self.packetData[0, 2 + (3 * sensorIndex)] = ZAcc / 127
            else:
                self.packetData[0, 2 + (3 * sensorIndex)] = ZAcc

            #print(f"self.dataTx: {self.dataTx}")
            # TOF sensor
            if self.dataTx[0] == 0x0F and sensorIndex == self.numSensors - 1:  #If ToF is enabled and we are on the last sensor - get the ToF byte
                ToFTuple = struct.unpack("=b", binaryData[(self.numSensors * 3)])   #ToF data is the last byte
                self.ToFByte = ToFTuple[0]
                print(f"self.ToFByte: {self.ToFByte}")
            else:
                #reset ToFByte
                self.ToFByte = -1
        
        for i in range(self.numSensors):
            formatData(binaryData, i)
    
    def receiveBytes(self):
        print()
        print(f'receiveBytes(self)')
        #Signals the server then receives a byte from the sample
        
        sock = socket.socket()
        sock.connect((self.host, self.port))
        print()
        print("Connected to server")
        try:
            sock.send(self.dataTx)
            #print("Sent Data")
        except:
           sock.connect((self.host, self.port))
           #print("Socket Reconnected")
           sock.send(self.dataTx)
        # print(f'sockname: {sock.getsockname()}')
        # print(f'sockpeer: {sock.getpeername()}')
        #y = []
        #time.sleep(0.01)
        #y = sock.recv(18)
        a = 0
        errorCount = 0
        sampleRxStartMS = int(time.time() * 1000)
        while a < ((self.numSensors * 3) + self.extraRxByte):                #iterate through the number of sensors * the number of bytes per sample
            #print(f'while loop a')
            try:
                self.y.append(sock.recv(1))
                #print(f'Received 1')
            except ConnectionError:
                print(f"Unable to reach client with socket: Retrying")
                #Close and reopen the connection
                if errorCount < 10:      #If you get ten connection errors in a row close and reopen the socket
                    #Close and reopen the connection
                    sock.close()
                    sock = socket.socket()
                    sock.connect((self.host, self.port))
                    a -= 1     #Ask for a resend (decrement data index)
                    errorCount += 1
                    sock.send(self.dataTx)
                else:
                    print(f'Fatal Error: SocketBroken')
                    return -1
            a += 1 
        sock.close()
        self.dataGot = 1
        #print(f"self.y: {self.y}")
        return self.y
    
    #print(f'Sample Received - One byte')

    def getSample(self): #recvCount counts samples in a packet in training mode; in prediction mode it is the index for the circular buffer
        print()
        print('getSample()')
        packetStartMS = 0 

            #Sends one byte from dataPacket and asks for more
            #while recvCount < self.packetSize:
        sampleRxStartMS = int(time.time() * 1000)
        dataThread = Thread(target=self.receiveBytes)
        dataThread.start()
                #y = self.receiveBytes()
                #print(f'Receive Bytes')

        while threading.active_count() > 1:
            #print(f'threading.active_count(): {threading.active_count()}')
            dataThread.join()

        sampleRxStopMS = int(time.time() * 1000)
        sampleRxTimeMS = sampleRxStopMS - sampleRxStartMS
        print(f'Sample receive time in ms: {sampleRxTimeMS}')

        #print(f'self.y loop: {self.y}')
                
        #print(f'Start preocessData() thread for sample: {recvCount}' )
                
        self.processData(self.y)
        self.y = []  #Reset y so that it doesn't get too full...

        #Prediction mode      
    def predictSample(self):

        NNINput = np.roll(self.packetData, (3 * self.numSensors)*(self.packetSize - 1))  #roll the packetData circular array to put them in the right order

        #print(f'Input to NN (rolled): {NNINput}')
        print(f'Making Prediction...') 
        prediction = NeuralNetwork.realTimePrediction(NNINput, self.pathPreface)
                    #print(f'prediction: {prediction}')

        return prediction            

        # print(f'Converting gesture to OSC...') 
        # writer = oscWriter.OSCWriter()   #writer is passed during GetData.__init__()
        # writer.getPredictions(prediction[0])
        # if writer.ToFEnable:
        #     print(f'Enable Time of Flight Sensor...') 
        #     self.dataTx = 0 #Reset dataTx
        #     self.dataTx = struct.pack("=B", 15)   #Enable ToF sensor
        #     self.extraRxByte = 1
        # else:
        #     print(f'Disable Time of Flight Sensor...') 
        #     self.dataTx = 0 #Reset dataTx
        #     self.dataTx = struct.pack("=B", 255)   #Disable ToF sensor 
        #     self.extraRxByte = 0
        # self.dataGot = 0   #Reset the dataGot flag for the next sample

    def prepTraining(self):    #Prep the packet for training
        print()
        print('prepTraining')
        print(f'self.label: {self.label}')
        #print(f'self.packetData: {self.packetData}') 

        #scale the data to +-1
        for i in range(self.packetData.shape[1]):
            self.packetData[0,i] = self.packetData[0,i] / 127
        print(f'self.packetData.shape: {self.packetData.shape}')
        #Get ground truth labels
        packetTruth = np.zeros([1,], dtype=int)
        #print(f'packetTruth.shape: {packetTruth.shape}')
        packetTruth[0] = self.label
        #print(f'packetTruth: {packetTruth}')

        #Write to files
        self.writetoBinary(self.packetData, packetTruth)
        self.writetoCSV(self.packetData, packetTruth)

    def writetoBinary(self,trainingData, packetTruth):
        print()
        print('writetoBinary()')
        print(f'trainingData for write: {trainingData}')
        #Write data to .npy file (binary) -- faster
        dataPath = self.pathPreface + self.labelPath + '.npy'
        truthPath = self.pathPreface + self.labelPath + '_truth.npy'

        #Data
        if os.path.exists(dataPath):
            tmpArr = np.load(dataPath,allow_pickle=False)
            #print(f'tmpArr from file: {tmpArr}')
            tmpArr = np.append(tmpArr,trainingData, axis=0)
            np.save(dataPath, tmpArr, allow_pickle=False)
            # print(f'dataPacket shape (Binary): {tmpArr.shape}')
            # print(f'dataPacket saved (Binary): {tmpArr}')
            
        else: 
            np.save(dataPath, trainingData, allow_pickle=False)
            # print(f'dataPacket shape (Binary): {trainingData.shape}')
            # print(f'dataPacket saved (Binary): {trainingData}')

        #Truth
        print(f'truth path: {truthPath}')
        if os.path.exists(truthPath):
            tmpArr = np.load(truthPath,allow_pickle=False)
            print(f'Binary truths from file: {tmpArr}')
            tmpArr = np.append(tmpArr,packetTruth)
            np.save(truthPath, tmpArr, allow_pickle=False)
            print(f'packetTruth appended and saved (Binary): {tmpArr}')
        else: 
            np.save(truthPath, packetTruth, allow_pickle=False)
            print(f'packetTruth saved (Binary): {packetTruth}')

    def writetoCSV(self, trainingData, packetTruth):
        print()
        print('writetoCSV()')
        print(f'trainingData for write: {trainingData}')
        #Write data to .csv file (text) - human readable
        #print(f'CSV write training data')
        dataPath = self.pathPreface + self.labelPath + '.csv'
        truthPath = self.pathPreface + self.labelPath + '_truth.csv'
        
        #Data - 2D array axis 0 (rows) are gestures, axis 1 (cols) are features within a gesture
        if os.path.exists(dataPath):
            tmpArr = np.loadtxt(dataPath,dtype=float, delimiter=',', ndmin=2)       
            #print(f'tmpArr.shape 1: {tmpArr.shape}')
            #print(f'tmpArr: {tmpArr}')          
            
            tmpArr = np.append(tmpArr,trainingData, axis=0)                  #Append trainingData to tmpArr
            #print(f'tmpArr.shape 2 (CSV): {tmpArr.shape}')
            #print(f'tmpArr (CSV): {tmpArr}')

            np.savetxt(dataPath, tmpArr, fmt="%f", delimiter=",") 
            # print(f'dataPacket appended and saved (CSV): {tmpArr}')
        else: 
            #tmpArr = np.reshape(trainingData, (trainingData.shape[0] * 4, 4))   #Reshape to a 2-D array
            np.savetxt(dataPath, trainingData, fmt="%f", delimiter=",")
            # print(f'dataPacket appended and saved (CSV): {trainingData}')
            # print(f'dataPacket shape: {trainingData.shape}')
        
        #Truth - 1D Array of same length as data
        if os.path.exists(truthPath):
            tmpArr = np.loadtxt(truthPath,dtype=int, delimiter=',')
            tmpArr = np.append(tmpArr,packetTruth) 
            np.savetxt(truthPath, tmpArr, fmt="%d", delimiter=",")
            #print(f'packetTruth appended and saved (CSV): {tmpArr}')
            #print(f'packetTruth shape: {tmpArr.shape}')
        else: 
             np.savetxt(truthPath, packetTruth, fmt="%d", delimiter=",")
             #print(f'packetTruth appended and saved (CSV): {packetTruth}')
             #print(f'dataPacket shape: {packetTruth.shape}')

    def plotAcc(self):

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
                #print(f'XList{j}: {XList}')
            axs[i][0].plot(XList[1], XList[0])

            YList = [[],[]]
            for j in range(self.packetSize):
                YList[0].append(self.packetData[0, 1 + (i * 3) + (j * self.numSensors * 3)])
                YList[1].append(j)
                #print(f'YList{j}: {YList}')
            axs[i][1].plot(YList[1], YList[0])

            ZList = [[],[]]
            for j in range(self.packetSize):
                ZList[0].append(self.packetData[0, 2 + (i * 3) + (j * self.numSensors * 3)])
                ZList[1].append(j)
                #print(f'ZList{j}: {ZList}')
            axs[i][2].plot(ZList[1], ZList[0])

        if self.getTraining:    
            figPath = self.pathPreface + self.labelPath + str(self.packetCount) + '_' + str(self.label) + '.png'
            plt.savefig(figPath)
        else:
            figPath = self.pathPreface + "PredPlots/" + str(self.plotCounter) + '.png'
            
            plt.savefig(figPath)

        #plt.show()   
        plt.close         

# def createTrainingData(*, pathPreface='data/data', labelPath="test", label=0, packetLimit=1, packetSize=1, numSensors=4):
#     trgData = GetData(packetSize=packetSize, pathPreface=pathPreface, labelPath=labelPath, label=label, getTraining=True, packetLimit=packetLimit, numSensors=numSensors)
#     trgData.socketLoop(0)

# def main():
    
#     #Get Data for training
#     # createTrainingData(pathPreface="data/packet5Avg20/training00_noMove", packetLimit=20, label=0, packetSize=5, numSensors=2)
#     # createTrainingData(pathPreface="data/packet5Avg20/training00_noMove_Test", packetLimit=2, label=0, packetSize=5, numSensors=2)

#     # createTrainingData(pathPreface="data/packet5Avg20/training01_upandDown", packetLimit=20, label=1, packetSize=5, numSensors=2)
#     # createTrainingData(pathPreface="data/packet5Avg20/training01_upandDown_Test", packetLimit=2, label=1, packetSize=5, numSensors=2)

#     # createTrainingData(pathPreface="data/packet5Avg20/training02_inandOut", packetLimit=20, label=2, packetSize=5, numSensors=2)
#     # createTrainingData(pathPreface="data/packet5Avg20/training02_inandOut_Test", packetLimit=2, label=2, packetSize=5, numSensors=2)
    
#     #Testing
#     #createTrainingData(pathPreface="data/test/test", packetLimit=10, label=0, packetSize=5, numSensors=2)

#     # model = NeuralNetwork.Model.load("data/AccModel01Dill")
#     # parameters = model.get_parameters()
#     # print(f'Model: {parameters}')
    

# if __name__ == "__main__": main()