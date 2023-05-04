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
host = "192.168.1.74"
port = 80    
packetSize = 0        

Acc1Data = []


def getHost():
    host = "192.168.1.65"
    #host = input("Enter Server IP: ")
    print("Host IP: {host}")

def processData(binaryData):
    print()
    print("processData(binaryData)")
    print(f'binaryData: {binaryData}')
    
    #Parse binary data and recombine into ints
    #X Axis
    XAcc = struct.unpack("=b", binaryData[0])
    #print(f'XAcc Raw: {XAcc}')
    XAcc = XAcc[0] << 4
    #print(f'XAcc Shift: {XAcc}')
    XAcc1 = struct.unpack("=b", binaryData[1])
    XAcc = XAcc + XAcc1[0]
    #print(f'XAcc Final: {XAcc}')

    #Y Axis
    YAcc = struct.unpack("=b", binaryData[3])
    #print(f'XAcc Raw: {XAcc}')
    YAcc = YAcc[0] << 4
    #print(f'YAcc Shift: {YAcc}')
    YAcc1 = struct.unpack("=b", binaryData[2])
    YAcc = YAcc + YAcc1[0]
    #print(f'YAcc Final: {YAcc}')

    #Z Axis
    ZAcc = struct.unpack("=b", binaryData[5])
    #print(f'XAcc Raw: {XAcc}')
    ZAcc = ZAcc[0] << 4
    #print(f'ZAcc Shift: {ZAcc}')
    ZAcc1 = struct.unpack("=b", binaryData[4])
    ZAcc = ZAcc + ZAcc1[0]
    #print(f'ZAcc Final: {ZAcc}')

    #X Time
    XT = struct.unpack("=B", binaryData[9])
    if XT != 0:
        XT = XT[0] << 24
    XT2 = struct.unpack("=B", binaryData[8])
    if XT2 != 0:
        XT = XT + (XT2[0] << 16)
    XT3 = struct.unpack("=B", binaryData[7])
    if XT3 != 0:
        XT = XT + (XT3[0] << 8)
    XT4 = struct.unpack("=B", binaryData[6])
    XT = (XT + XT4[0]) / 8000
    print(f'XT: {XT}')

    #Y Time
    YT = struct.unpack("=B", binaryData[13])
    if YT != 0:
        YT = YT[0] << 24
    YT2 = struct.unpack("=B", binaryData[12])
    if YT2 != 0:
        YT = YT + (YT2[0] << 16)
    YT3 = struct.unpack("=B", binaryData[11])
    if YT3 != 0:
        YT = YT + (YT3[0] << 8)
    YT4 = struct.unpack("=B", binaryData[10])
    YT = (YT + YT4[0]) / 8000
    #print(f'YT: {YT}')

    #Z Time
    ZT = struct.unpack("=B", binaryData[17])
    if ZT != 0:
        ZT = ZT[0] << 24
    ZT2 = struct.unpack("=B", binaryData[16])
    if ZT2 != 0:
        ZT = ZT + (ZT2[0] << 16)
    ZT3 = struct.unpack("=B", binaryData[15])
    if ZT3 != 0:
        ZT = ZT + (ZT3[0] << 8)
    ZT4 = struct.unpack("=B", binaryData[14])
    ZT = (ZT + ZT4[0]) / 8000
    #print(f'ZT: {ZT}')

    Acc1Data.append([])

    Acc1Data[len(Acc1Data) -1].append(XAcc)    #XAcc
    Acc1Data[len(Acc1Data) -1].append(YAcc)    #YAcc
    Acc1Data[len(Acc1Data) -1].append(ZAcc)    #ZAcc
    Acc1Data[len(Acc1Data)-1].append(XT)       #XT
    Acc1Data[len(Acc1Data)-1].append(YT)       #YT
    Acc1Data[len(Acc1Data)-1].append(ZT)       #ZT
    
    print(f'Acc1Data[{len(Acc1Data) -1}]: {Acc1Data[len(Acc1Data) -1]}]')
    print()
    # for i in range(len(Acc1Data)):
    #     for j in range(len(Acc1Data[i])):
    #         print(f'Acc1Data {i},{j}: {Acc1Data[i][j]}')
    #     print()
    
def plotAcc():
    #Arrange the data
    time.sleep(2)
    XList = [[],[]]
    for i in range(len(Acc1Data)):
        XList[0].append(Acc1Data[i][0])
        XList[1].append(Acc1Data[i][3])
    #print(f'XList: {XList}')

    YList = [[],[]]
    for i in range(len(Acc1Data)):
        YList[0].append(Acc1Data[i][1])
        YList[1].append(Acc1Data[i][4])
    #print(f'YList: {YList}')

    ZList = [[],[]]
    for i in range(len(Acc1Data)):
        ZList[0].append(Acc1Data[i][2])
        ZList[1].append(Acc1Data[i][5])
    #print(f'ZList: {ZList}')

    _,axs = plt.subplots(1,3, figsize=(6,5))
    axs[0].plot(XList[1],XList[0])
    axs[1].plot(YList[1],YList[0])
    axs[2].plot(ZList[1],ZList[0])

    # axs[0].title("X Axis Acceleration")
    # axs[1].title("Y Axis Acceleration")
    # axs[2].title("Z Axis Acceleration")
    plt.show()

 
def socketLoop(): 
    print()
    print("socketLoop")
    global packetSize                        #Only needed for testing - production code will run continiously
    print(f'packetSize: {packetSize}' )
    
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
    y = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #time.sleep(0.01)
    #y = sock.recv(18)
    a = 0
    while a < 18:
        #print(f'while loop')
        try:
            y[a] = sock.recv(1)
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

    #TODO ensure that a new thread is created - use ids as args to the threads and check for a free thread to use
    dataThread = Thread(target=processData, args=(y,))
    dataThread.start()
    ##dataThread.join()

    if packetSize < 50:             #Only needed for testing - production code will run continiously
        packetSize += 1
        time.sleep(0.01)
        socketLoop()
    else:
        #sock.close()
        print("Packet Done")
        plotAcc()
        #packetSize = 0

def main():
    
    #getHost()
    socketLoop()

    

if __name__ == "__main__": main()