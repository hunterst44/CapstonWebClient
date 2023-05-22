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
 
# sock = socket.socket()
host = "192.168.1.75"
port = 80    
packetStartMS = int(time.time() * 1000)   
packetDone = 0 

Acc1Data = []
AccData = np.zeros([5,4,3])    ##3 dimensional array to hold sensor data [Samples: Sensors : Features]


# def getHost():
#     host = "192.168.1.65"
#     #host = input("Enter Server IP: ")
#     print("Host IP: {host}")

def processData(binaryData, recvCount):
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
    
    if recvCount < 5:
    
        X1Acc, Y1Acc, Z1Acc = formatData(binaryData, 0)
        AccData[recvCount,0,0] = X1Acc
        AccData[recvCount,0,1] = Y1Acc
        AccData[recvCount,0,2] = Z1Acc

        X2Acc, Y2Acc, Z2Acc = formatData(binaryData, 1)
        AccData[recvCount,1,0] = X2Acc
        AccData[recvCount,1,1] = Y2Acc
        AccData[recvCount,1,2] = Z2Acc

        X3Acc, Y3Acc, Z3Acc = formatData(binaryData, 2)
        AccData[recvCount,2,0] = X3Acc
        AccData[recvCount,2,1] = Y3Acc
        AccData[recvCount,2,2] = Z3Acc

        X4Acc, Y4Acc, Z4Acc = formatData(binaryData, 3)
        AccData[recvCount,3,0] = X4Acc
        AccData[recvCount,3,1] = Y4Acc
        AccData[recvCount,3,2] = Z4Acc
    

    #print(f'AccData: {AccData}')
    #print()
    print(f'AccData:')
    for i in range(4):
        for j in range(3):
            print(f'Sample: {recvCount}, Sensor: {i}, Axis: {j}: {AccData[recvCount,i,j]}')
    #     print()
    
def plotAcc():
    #Arrange the data
    #time.sleep(2)

    #Write data to .npy file (binary)
    if os.path.exists('data/data.npy'):
        tmpArr = np.load('data/data.npy',allow_pickle=False)
        print(f'tmpArr: {tmpArr}')
        np.append(tmpArr,AccData, axis=0)
        np.save('data/data.npy', tmpArr, allow_pickle=False)
    else: 
         np.save('data/data.npy', AccData, allow_pickle=False)

     #Write data to .csv file
     #TODO: Flatten to 2D before write; expand to 3D after read numpy.reshape()
    if os.path.exists('data/data.csv'):
        tmpArr = np.loadtxt('data/data.csv')
        np.append(tmpArr,AccData, axis=0)
        np.savetxt('data/data.csv', tmpArr, fmt="%d", delimiter=",")
    else: 
         np.savetxt('data/data.csv', AccData, fmt="%d", delimiter=",")

    #AccData.tofile('data/datafile.csv', sep=',')

    XList1 = [[],[]]
    for i in range(5):
        XList1[0].append(AccData[i,0,0])
        XList1[1].append(i)
    #print(f'XList1: {XList1}')

    XList2 = [[],[]]
    for i in range(5):
        XList2[0].append(AccData[i,1,0])
        XList2[1].append(i)
    #print(f'XList: {XList}')

    XList3 = [[],[]]
    for i in range(5):
        XList3[0].append(AccData[i,2,0])
        XList3[1].append(i)
    #print(f'XList1: {XList1}')

    XList4 = [[],[]]
    for i in range(5):
        XList4[0].append(AccData[i,3,0])
        XList4[1].append(i)
    #print(f'XList: {XList}')

    YList1 = [[],[]]
    for i in range(5):
        YList1[0].append(AccData[i,0,1])
        YList1[1].append(i)
    #print(f'YList: {YList}')

    YList2 = [[],[]]
    for i in range(5):
        YList2[0].append(AccData[i,1,1])
        YList2[1].append(i)
    #print(f'YList: {YList}')

    YList3 = [[],[]]
    for i in range(5):
        YList3[0].append(AccData[i,2,1])
        YList3[1].append(i)
    #print(f'XList1: {XList1}')

    YList4 = [[],[]]
    for i in range(5):
        YList4[0].append(AccData[i,3,1])
        YList4[1].append(i)

    ZList1 = [[],[]]
    for i in range(5):
        ZList1[0].append(AccData[i,0,2])
        ZList1[1].append(i)
    #print(f'ZList: {ZList}')

    ZList2 = [[],[]]
    for i in range(5):
        ZList2[0].append(AccData[i,1,2])
        ZList2[1].append(i)
    #print(f'ZList2: {ZList2}')

    ZList3 = [[],[]]
    for i in range(5):
        ZList3[0].append(AccData[i,2,2])
        ZList3[1].append(i)
    #print(f'XList1: {XList1}')

    ZList4 = [[],[]]
    for i in range(5):
        ZList4[0].append(AccData[i,3,2])
        ZList4[1].append(i)

    _,axs = plt.subplots(4,3, figsize=(6,5))
    #axs[0][0].plot(AccData[:,1,1])
    axs[0][0].plot(XList1[1],XList1[0])
    axs[0][1].plot(YList1[1],YList1[0])
    axs[0][2].plot(ZList1[1],ZList1[0])
    axs[1][0].plot(XList2[1],XList2[0])
    axs[1][1].plot(YList2[1],YList2[0])
    axs[1][2].plot(ZList2[1],ZList2[0])
    axs[2][0].plot(XList3[1],XList3[0])
    axs[2][1].plot(YList3[1],YList3[0])
    axs[2][2].plot(ZList3[1],ZList3[0])
    axs[3][0].plot(XList4[1],XList4[0])
    axs[3][1].plot(YList4[1],YList4[0])
    axs[3][2].plot(ZList4[1],ZList4[0])
   
    plt.show()

 
def socketLoop(recvCount): 
    #recvCount counts how many packets have been received
    #print()
    #print("socketLoop")
    #global processCount
    #print(f'processCount: {processCount}' )
    #print(f'Start socketLoop recvCount: {recvCount}' )
    global packetDone
    global packetStartMS
    if recvCount == 0:
        packetStartMS = int(time.time() * 1000)  
    
    if recvCount < 5:             #Only needed for testing - production code will run continiously
        #time.sleep(0.1)
        sock = socket.socket()
        sock.connect((host, port))
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
                    sock.connect((host, port))
                    a -= 1     #Ask for a resend
                    errorCount += 1
                    sock.send(dataTx);
                else:
                    print(f'Fatal Error: SocketBroken')
                    return -1

                #socketLoop(recvCount)
            # print(f'y[a]: {y[a]}');
            a += 1

            
        #y = bytearray(18)
        #sock.recv_into(y, 18)
        #print(f'y: {y}');
        # print(f'y[0]: {y[0]}');
        sock.close()
        print(f'Start dataThread recvCount: {recvCount}' )
        dataThread = Thread(target=processData, args=(y, recvCount,))
        dataThread.start()
        
        ##dataThread.join()
        #processCount += 1
        #time.sleep(0.01)
        recvCount += 1

        print(f'Recursive call to socketLoop() recvCount: {recvCount}' )
        socketLoop(recvCount)

    elif recvCount == 5:                      # Once we've received 5 packets
        while threading.active_count() > 1:    #wait for the last threads to finish processing
            #print(f'threading.active_count(): {threading.active_count()}')
            pass
        #packetDone = 1

        #sock.close()
        print(f'Packet Done')
        packetStopMS = int(time.time() * 1000)
        packetTimeMS = packetStopMS - packetStartMS
        #print(f'packetStart: {packetStartMS}')
        print(f'processing time in ms: {packetTimeMS}')
        # for thread in threading.enumerate(): 
        #     print(thread.name)
        #print()
        #print(f'data: {AccData}')
        #print()
        plotAcc()
        #print("plot done return 0")
        
        print(f'End recvCount: {recvCount}' )
        #packetDone = 0
        #print(f'Packet Done: {packetDone}')
        time.sleep(2)
        socketLoop(0)
        return 0
    
    else: 
        return 0

def main():
    
    socketLoop(0)

    

if __name__ == "__main__": main()