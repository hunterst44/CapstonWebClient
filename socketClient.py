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

class GetData:
    
    def __init__(self, *, host="192.168.1.67", port=80, packetSize=5, numSensors=4, pathPreface='data/data', labelPath="Test", label=0, getTraining=True, packetLimit=100):
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
        self.packetLimit = packetLimit
        self.predictions = []
        self.plotTimer = int(time.time() * 1000)   #Used to make timed plots of input data for plots
        self.plotCounter = 0 #counts how many plots have been made

    def processData(self, binaryData, recvCount):
      
        # print(f'processData recvCount(): {recvCount}')
        # print(f'binaryData: {binaryData}')

        #packetStartMS = int(time() * 1000)
        #global processCount

        def formatData(binaryData, sensorIndex):
            #print(f'recvCount: {recvCount}')
            #Parse binary data and recombine into ints
            #X Axis
            XAcc = struct.unpack("=b", binaryData[1 + (sensorIndex * 3 * self.numSensors)])  ##MSB is second byte in axis RX; Just a nibble
            #print(f'XAcc Raw: {XAcc}')
            XAcc = XAcc[0] << 8
            #print(f'XAcc Shift: {XAcc}')
            XAcc1 = struct.unpack("=B", binaryData[0 + (sensorIndex * 3 * self.numSensors)])  ##LSB is first byte in axis RX; full byte
            if self.getTraining is False:
                self.packetData[0,(self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = (XAcc + XAcc1[0]) / 2048
            else:
                self.packetData[0,(self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = XAcc + XAcc1[0]
            #print(f'XAcc Final: {XAcc + XAcc1[0]}')

            #Y Axis
            YAcc = struct.unpack("=b", binaryData[3 + (sensorIndex * 3 * self.numSensors)])
            #print(f'XAcc Raw: {XAcc}')
            YAcc = YAcc[0] << 8
            #print(f'YAcc Shift: {YAcc}')
            YAcc1 = struct.unpack("=B", binaryData[2 + (sensorIndex * 3 * self.numSensors)])
            if self.getTraining is False:
                self.packetData[0, 1 + (self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = (YAcc + YAcc1[0])/2048
            else:       
                self.packetData[0, 1 + (self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = YAcc + YAcc1[0]
            #print(f'YAcc Final: {YAcc + YAcc1[0]}')

            #Z Axis
            ZAcc = struct.unpack("=b", binaryData[5 + (sensorIndex * 3 * self.numSensors)])
            #print(f'sensor: {sensorIndex}')
            #print(f'ZAcc Raw: {ZAcc}')
            ZAcc = ZAcc[0] << 8
            #print(f'ZAcc Shift: {ZAcc}')
            ZAcc1 = struct.unpack("=B", binaryData[4 + (sensorIndex * 3 * self.numSensors)])
            ZAcc2 = struct.unpack("=B", binaryData[4])
            #print(f'ZAcc1 Raw: {ZAcc1}')
            #print(f'ZAcc1[0]: {ZAcc1[0]}')
            #print(f'ZAcc2[0]: {ZAcc2[0]}')
            if self.getTraining is False:
                self.packetData[0, 2 + (self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = (ZAcc + ZAcc1[0]) /2048
            else:
                self.packetData[0, 2 + (self.numSensors * 3 * recvCount) + (3 * sensorIndex)] = ZAcc + ZAcc1[0]
            #print(f'ZAcc final: {ZAcc + ZAcc1[0]}')
            #print(f'ZAcc Final: {ZAcc}')
        
        if recvCount < self.packetSize:
            for i in range(self.numSensors):
                formatData(binaryData, i)

        #print(f'packet after fresh data insertion: {self.packetData}')

        # if self.getTraining is False:
        #     #scale the data to +-1
        #     for i in range(self.packetData.shape[1]):
        #         print(f'packetData[0, {i}] (before): {self.packetData[0,i]}') 
        #         self.packetData[0,i] = self.packetData[0,i] / 2048
        #         print(f'packetData[0, {i}] (scaled): {self.packetData[0,i]}')

    def socketLoop(self, recvCount): #recvCount counts samples in a packet in training mode; in prediction mode it is the index for the circular buffer

        packetStartMS = 0
        firstFive = 0 #flip to one after first five sample are in to start predictions

        while self.packetCount < self.packetLimit:                   #keep getting packets until the packetLimit is reaches   
            if recvCount == 0:

                if self.getTraining:
                    #Prompt user to get ready to create training data
                    time.sleep(0.5)
                    print('********************************************')  
                    print('********************************************') 
                    print('********************************************') 
                    print('Creating training data.')
                    print(f'packetNumber: {self.packetCount} of {self.packetLimit}')
                    print('') 
                    print('') 
                    print(f'packetNumber: {self.packetCount} of {self.packetLimit}')
                    print('') 
                    print('') 
                    print(f'Get ready to perform gesture: {self.label}, {self.labelPath}')
                    print(f'packetNumber: {self.packetCount} of {self.packetLimit}')
                    # if self.label == 0:
                    #     print('Get ready to perform gesture: 0 No movement')
                    # elif self.label == 1:
                    #     print('Get ready to perform gesture: 1 Alternate up and down')
                    # elif self.label == 2:
                    #     print('Get ready to perform gesture: 2 Out and in together')
                    
                    print('In 3...')
                    time.sleep(1)
                    print('2...')
                    time.sleep(1)
                    print('1...')
                    time.sleep(1)
                    print('Go!')
                    time.sleep(0.1)

                    
                    #print(f'Start packet time: {packetStartMS}')
            
            packetStartMS = int(time.time() * 1000)    
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
                while a < (self.numSensors * 6):
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
                
                #print(f'Sample Received')
                
                print()
                print(f'Start preocessData() thread for sample: {recvCount}' )
                # if self.getTraining is False:  #while predicting make sure all threads are done before starting another
                #     while threading.active_count() > 1:    #wait for the last threads to finish processing
                #         print(f'threading.active_count(): {threading.active_count()}')
                #         pass
                
                dataThread = Thread(target=self.processData, args=(y, recvCount,))
                dataThread.start()

                if self.getTraining:
                    sampleRxStopMS = int(time.time() * 1000)
                    sampleRxTimeMS = sampleRxStopMS - sampleRxStartMS
                    print(f'Sample receive time in ms: {sampleRxTimeMS}')
                    recvCount += 1

                #Sample is received make a prediction    
                else:       
                    if firstFive:   #wait for full packet before doing prediction

                        dataThread.join()    #wait for the data to be proccessed in the other thread
                        
                        #predictionStartMs = int(time.time() * 1000)
                        
                        #scale the data to +-1
                        # for i in range(self.packetData.shape[1]):
                        #     print(f'packetData[0, {i}] (before): {self.packetData[0,i]}') 
                        #     self.packetData[0,i] = self.packetData[0,i] / 2048
                        #     print(f'packetData[0, {i}] (scaled): {self.packetData[0,i]}')


                        NNINput = np.roll(self.packetData, (3 * self.numSensors)*(self.packetSize - recvCount - 1))  #roll the packetData circular array to put them in the right order
                        try:
                            predictThread.join()   #Ensure last prediction is done before proceeding
                        except:
                            print("predictThread doesn't exist yet")

                        #Make a plot every 5 seconds
                        plotTimerCheck = int(time.time() * 1000)
                        if (plotTimerCheck - self.plotTimer) > 5000 and self.plotCounter < 20:  
                            self.plotCounter += 1     
                            self.plotAcc()   #take the packet now hot off the press
                            self.plotTimer = int(time.time() * 1000)   #reset plotTimer

                        #print(f'Input to NN (rolled): {NNINput}')
                        print(f'Making Prediction...{recvCount}') 
                        predictThread = Thread(target=NeuralNetwork.realTimePrediction, args=(NNINput, self.predictions, self.pathPreface))
                        predictThread.start()
                        #self.predictions = NeuralNetwork.realTimePrediction(NnInput) 

                        # predictionStopMS = int(time.time() * 1000)
                        # predictionTimeMS = predictionStopMS - predictionStartMs
                        # print(f'It\'s {self.predictions}') 
                        # print(f'Time to predict: {predictionTimeMS}')
                        
                    if recvCount == self.packetSize - 1:    #reset recvCount to 0 if a full packet is received
                        firstFive = 1                       #Enable first five so a prediction will be made on next pass
                        recvCount = 0                       
                    else: 
                        recvCount += 1                      #Advance recvCount
                    
                    sampleRxStopMS = int(time.time() * 1000)
                    sampleRxTimeMS = sampleRxStopMS - sampleRxStartMS
                    print(f'Sample receive time in ms: {sampleRxTimeMS}')
    
                #print(f'Completed Rx of sample: {recvCount}' )
                #socketLoop(recvCount)

            #training data packet is ready
            if recvCount == self.packetSize and self.getTraining:                      # Once we've received 5 packets
                dataThread.join()
                while threading.active_count() > 1:    #wait for the last threads to finish processing
                    #print(f'threading.active_count(): {threading.active_count()}')
                    pass
                
                print(f'Packet Done')
                packetStopMS = int(time.time() * 1000)
                packetTimeMS = packetStopMS - packetStartMS
                #print(f'packetStart: {packetStartMS}')
                #print(f'packetStopMS: {packetStopMS}')
                print(f'packet processing time in ms: {packetTimeMS}')
                # for thread in threading.enumerate(): 
                #     print(thread.name)
                #print()
                #print(f'data: {self.packetArr}')
                #print()
                #np.append(self.packetArr,self.packetData, axis=1) 
                #Save data for training
                #Training Label codes
                # 0 Not movinng - Environmental movements
                # 1 Alternate up and down
                # 2 Out and in alternately
                metaDataTimeStartMs = int(time.time() * 1000)
                #Append the data to the packet array
                self.prepTraining()
                self.plotAcc()
                self.packetCount += 1
                recvCount = 0    #Reset recvCount to get the next packet
                metaDataTimeStopMs = int(time.time() * 1000)
                print(f'metaData Time Save to files and image [ms]: {metaDataTimeStopMs - metaDataTimeStartMs}')

        self.packetCount = 0            
        return 0

    def prepTraining(self):    #Prep the packet for training

        #print(f'self.packetData: {self.packetData}') 

        #scale the data to +-1
        for i in range(self.packetData.shape[1]):
            self.packetData[0,i] = self.packetData[0,i] / 2048
        #print(f'self.packetData.shape: {self.packetData.shape}')
        #Get ground truth labels
        packetTruth = np.zeros([1,], dtype=int)
        #print(f'packetTruth.shape: {packetTruth.shape}')
        packetTruth[0] = self.label
        #print(f'packetTruth: {packetTruth}')

        #Write to files
        self.writetoBinary(self.packetData, packetTruth)
        self.writetoCSV(self.packetData, packetTruth)

    def writetoBinary(self,trainingData, packetTruth):
        #print(f'trainingData for write: {trainingData}')
        #Write data to .npy file (binary) -- faster
        dataPath = self.pathPreface + self.labelPath + '.npy'
        truthPath = self.pathPreface + self.labelPath + '_truth.npy'

        #Data
        if os.path.exists(dataPath):
            tmpArr = np.load(dataPath,allow_pickle=False)
            #print(f'tmpArr from file: {tmpArr}')
            tmpArr = np.append(tmpArr,trainingData, axis=0)
            np.save(dataPath, tmpArr, allow_pickle=False)
            #print(f'dataPacket shape (Binary): {tmpArr.shape}')
            #print(f'dataPacket saved (Binary): {tmpArr}')
            
        else: 
            np.save(dataPath, trainingData, allow_pickle=False)
            #print(f'dataPacket shape (Binary): {trainingData.shape}')
            #print(f'dataPacket saved (Binary): {trainingData}')

        #Truth
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
            #print(f'dataPacket appended and saved (CSV): {tmpArr}')
        else: 
            #tmpArr = np.reshape(trainingData, (trainingData.shape[0] * 4, 4))   #Reshape to a 2-D array
            np.savetxt(dataPath, trainingData, fmt="%f", delimiter=",")
            #print(f'dataPacket appended and saved (CSV): {trainingData}')
            #print(f'dataPacket shape: {trainingData.shape}')
        
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

def createTrainingData(*, pathPreface='data/data', labelPath="test", label=0, packetLimit=1, packetSize=10, numSensors=4):
    trgData = GetData(packetSize=packetSize, pathPreface=pathPreface, labelPath=labelPath, label=label, getTraining=True, packetLimit=packetLimit, numSensors=numSensors)
    trgData.socketLoop(0)

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