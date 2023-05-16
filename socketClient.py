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
from threading import Thread
import matplotlib.pyplot as plt           
 
# sock = socket.socket()
host = "192.168.1.75"
port = 80    
sampleCount = 0        

Acc1Data = []
AccData = np.zeros([50,2,6])    ##3 dimensional array to hold sensor data [Samples: Sensors : Features]


# def getHost():
#     host = "192.168.1.65"
#     #host = input("Enter Server IP: ")
#     print("Host IP: {host}")

def processData(binaryData):
    print("processData(binaryData)")
    print(f'binaryData: {binaryData}')
    print()
    global sampleCount

    def formatData(binaryData, sensorIndex):

        #Parse binary data and recombine into ints
        #X Axis
        XAcc = struct.unpack("=b", binaryData[0 + (sensorIndex * 18)])
        #print(f'XAcc Raw: {XAcc}')
        XAcc = XAcc[0] << 4
        #print(f'XAcc Shift: {XAcc}')
        XAcc1 = struct.unpack("=b", binaryData[1 + (sensorIndex * 18)])
        XAcc = XAcc + XAcc1[0]
        #print(f'XAcc Final: {XAcc}')

        #Y Axis
        YAcc = struct.unpack("=b", binaryData[3 + (sensorIndex * 18)])
        #print(f'XAcc Raw: {XAcc}')
        YAcc = YAcc[0] << 4
        #print(f'YAcc Shift: {YAcc}')
        YAcc1 = struct.unpack("=b", binaryData[2 + (sensorIndex * 18)])
        YAcc = YAcc + YAcc1[0]
        #print(f'YAcc Final: {YAcc}')

        #Z Axis
        ZAcc = struct.unpack("=b", binaryData[5 + (sensorIndex * 18)])
        #print(f'XAcc Raw: {XAcc}')
        ZAcc = ZAcc[0] << 4
        #print(f'ZAcc Shift: {ZAcc}')
        ZAcc1 = struct.unpack("=b", binaryData[4 + (sensorIndex * 18)])
        ZAcc = ZAcc + ZAcc1[0]
        #print(f'ZAcc Final: {ZAcc}')

        #X Time
        XT = struct.unpack("=B", binaryData[9 + (sensorIndex * 18)])
        if XT != 0:
            XT = XT[0] << 24
        XT2 = struct.unpack("=B", binaryData[8 + (sensorIndex * 18)])
        if XT2 != 0:
            XT = XT + (XT2[0] << 16)
        XT3 = struct.unpack("=B", binaryData[7 + (sensorIndex * 18)])
        if XT3 != 0:
            XT = XT + (XT3[0] << 8)
        XT4 = struct.unpack("=B", binaryData[6 + (sensorIndex * 18)])
        XT = (XT + XT4[0]) / 8000
        print(f'XT: {XT}')

        #Y Time
        YT = struct.unpack("=B", binaryData[13 + (sensorIndex * 18)])
        if YT != 0:
            YT = YT[0] << 24
        YT2 = struct.unpack("=B", binaryData[12 + (sensorIndex * 18)])
        if YT2 != 0:
            YT = YT + (YT2[0] << 16)
        YT3 = struct.unpack("=B", binaryData[11 + (sensorIndex * 18)])
        if YT3 != 0:
            YT = YT + (YT3[0] << 8)
        YT4 = struct.unpack("=B", binaryData[10 + (sensorIndex * 18)])
        YT = (YT + YT4[0]) / 8000
        #print(f'YT: {YT}')

        #Z Time
        ZT = struct.unpack("=B", binaryData[17 + (sensorIndex * 18)])
        if ZT != 0:
            ZT = ZT[0] << 24
        ZT2 = struct.unpack("=B", binaryData[16 + (sensorIndex * 18)])
        if ZT2 != 0:
            ZT = ZT + (ZT2[0] << 16)
        ZT3 = struct.unpack("=B", binaryData[15 + (sensorIndex * 18)])
        if ZT3 != 0:
            ZT = ZT + (ZT3[0] << 8)
        ZT4 = struct.unpack("=B", binaryData[14 + (sensorIndex * 18)])
        ZT = (ZT + ZT4[0]) / 8000
        #print(f'ZT: {ZT}')

        return XAcc, YAcc, ZAcc, XT, YT, ZT
    
    X1Acc, Y1Acc, Z1Acc, X1T, Y1T, Z1T = formatData(binaryData, 0)
    X2Acc, Y2Acc, Z2Acc, X2T, Y2T, Z2T = formatData(binaryData, 1)

    AccData[sampleCount,0,0] = X1Acc
    AccData[sampleCount,0,1] = Y1Acc
    AccData[sampleCount,0,2] = Z1Acc
    AccData[sampleCount,0,3] = X1T
    AccData[sampleCount,0,4] = Y1T
    AccData[sampleCount,0,5] = Z1T
    AccData[sampleCount,1,0] = X2Acc
    AccData[sampleCount,1,1] = Y2Acc
    AccData[sampleCount,1,2] = Z2Acc
    AccData[sampleCount,1,3] = X2T
    AccData[sampleCount,1,4] = Y2T
    AccData[sampleCount,1,5] = Z2T

    sampleCount += 1

    # Acc1Data.append([])

    # Acc1Data[len(Acc1Data) -1].append(XAcc)    #XAcc
    # Acc1Data[len(Acc1Data) -1].append(YAcc)    #YAcc
    # Acc1Data[len(Acc1Data) -1].append(ZAcc)    #ZAcc
    # Acc1Data[len(Acc1Data)-1].append(XT)       #XT
    # Acc1Data[len(Acc1Data)-1].append(YT)       #YT
    # Acc1Data[len(Acc1Data)-1].append(ZT)       #ZT
    
    #print(f'AccData: {AccData}')
    #print()
    # for i in range(len(Acc1Data)):
    #     for j in range(len(Acc1Data[i])):
    #         print(f'Acc1Data {i},{j}: {Acc1Data[i][j]}')
    #     print()
    
def plotAcc():
    #Arrange the data
    time.sleep(2)
    XList1 = [[],[]]
    for i in range(50):
        XList1[0].append(AccData[i,0,0])
        XList1[1].append(AccData[i,0,3])
    print(f'XList1: {XList1}')

    XList2 = [[],[]]
    for i in range(50):
        XList2[0].append(AccData[i,1,0])
        XList2[1].append(AccData[i,1,3])
    #print(f'XList: {XList}')

    YList1 = [[],[]]
    for i in range(50):
        YList1[0].append(AccData[i,0,1])
        YList1[1].append(AccData[i,0,4])
    #print(f'YList: {YList}')

    YList2 = [[],[]]
    for i in range(50):
        YList2[0].append(AccData[i,1,1])
        YList2[1].append(AccData[i,1,4])
    #print(f'YList: {YList}')

    ZList1 = [[],[]]
    for i in range(50):
        ZList1[0].append(AccData[i,0,2])
        ZList1[1].append(AccData[i,0,5])
    #print(f'ZList: {ZList}')

    ZList2 = [[],[]]
    for i in range(50):
        ZList2[0].append(AccData[i,1,2])
        ZList2[1].append(AccData[i,1,5])
    #print(f'ZList: {ZList}')

    _,axs = plt.subplots(2,3, figsize=(6,5))
    axs[0][0].plot(AccData[:,1,1])
    #axs[0][0].plot(XList1[1],XList1[0])
    axs[0][1].plot(YList1[1],YList1[0])
    axs[0][2].plot(ZList1[1],ZList1[0])
    axs[1][0].plot(XList2[1],XList2[0])
    axs[1][1].plot(YList2[1],YList2[0])
    axs[1][2].plot(ZList2[1],ZList2[0])

    # axs[0].set_title('X Axis Acceleration Sensor 1')
    # axs[1].set_title('Y Axis Acceleration Sensor 1')
    # axs[2].set_title('Z Axis Acceleration Sensor 1')
    # axs[3].set_title('X Axis Acceleration Sensor 2')
    # axs[4].set_title('Y Axis Acceleration Sensor 2')
    # axs[5].set_title('Y Axis Acceleration Sensor 2')

    # axs[0].title("X Axis Acceleration")
    # axs[1].title("Y Axis Acceleration")
    # axs[2].title("Z Axis Acceleration")
    plt.show()

 
def socketLoop(): 
    print()
    print("socketLoop")
    global sampleCount                        #Only needed for testing - production code will run continiously
    print(f'sampleCount: {sampleCount}' )
    
    sock = socket.socket()
    sock.connect((host, port))
    print("Connected to server")
    dataTx = struct.pack("=i", 255)
    #try:
    sock.send(dataTx);
    #except:
    #    sock.connect((host, port))
    #    print("Socket Reconnected")
    #    sock.send(255);
    print(f'sockname: {sock.getsockname()}')
    print(f'sockpeer: {sock.getpeername()}')
    y = []
    #time.sleep(0.01)
    #y = sock.recv(18)
    a = 0
    while a < 36:
        #print(f'while loop')
        try:
            y.append(sock.recv(1))
            #print(f'Received 1')
        except ConnectionError:
            print(f"Unable to reach client with socket: Retrying")
            socketLoop()
        # print(f'y[a]: {y[a]}');
        a += 1
    
    #y = bytearray(18)
    #sock.recv_into(y, 18)
    print(f'y: {y}');
    # print(f'y[0]: {y[0]}');
    sock.close()

    if sampleCount < 50:             #Only needed for testing - production code will run continiously
        #TODO ensure that a new thread is created - use ids as args to the threads and check for a free thread to use
        dataThread = Thread(target=processData, args=(y,))
        dataThread.start()
        ##dataThread.join()
        #sampleCount += 1
        time.sleep(0.01)
        socketLoop()
    else:
        #sock.close()
        print("Packet Done")
        plotAcc()
        #sampleCount = 0

def main():
    
    #getHost()
    socketLoop()

    

if __name__ == "__main__": main()