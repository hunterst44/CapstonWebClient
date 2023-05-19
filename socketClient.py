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
 
# sock = socket.socket()
host = "192.168.1.75"
port = 80    
processStartMS = int(time.time() * 1000)   
packetDone = 0 

Acc1Data = []
AccData = np.zeros([50,4,3])    ##3 dimensional array to hold sensor data [Samples: Sensors : Features]


# def getHost():
#     host = "192.168.1.65"
#     #host = input("Enter Server IP: ")
#     print("Host IP: {host}")

def processData(binaryData, recvCount):
    print(f'processData recvCount(): {recvCount}')
    print(f'binaryData: {binaryData}')

    #processStartMS = int(time() * 1000)
    #global processCount

    def formatData(binaryData, sensorIndex):

        #Parse binary data and recombine into ints
        #X Axis
        XAcc = struct.unpack("=b", binaryData[0 + (sensorIndex * 6)])
        #print(f'XAcc Raw: {XAcc}')
        XAcc = XAcc[0] << 4
        #print(f'XAcc Shift: {XAcc}')
        XAcc1 = struct.unpack("=b", binaryData[1 + (sensorIndex * 6)])
        XAcc = XAcc + XAcc1[0]
        #print(f'XAcc Final: {XAcc}')

        #Y Axis
        YAcc = struct.unpack("=b", binaryData[3 + (sensorIndex * 6)])
        #print(f'XAcc Raw: {XAcc}')
        YAcc = YAcc[0] << 4
        #print(f'YAcc Shift: {YAcc}')
        YAcc1 = struct.unpack("=b", binaryData[2 + (sensorIndex * 6)])
        YAcc = YAcc + YAcc1[0]
        #print(f'YAcc Final: {YAcc}')

        #Z Axis
        ZAcc = struct.unpack("=b", binaryData[5 + (sensorIndex * 6)])
        #print(f'XAcc Raw: {XAcc}')
        ZAcc = ZAcc[0] << 4
        #print(f'ZAcc Shift: {ZAcc}')
        ZAcc1 = struct.unpack("=b", binaryData[4 + (sensorIndex * 6)])
        ZAcc = ZAcc + ZAcc1[0]
        #print(f'ZAcc Final: {ZAcc}')

        # #X Time
        # XT = struct.unpack("=B", binaryData[9 + (sensorIndex * 18)])
        # if XT != 0:
        #     XT = XT[0] << 24
        # XT2 = struct.unpack("=B", binaryData[8 + (sensorIndex * 18)])
        # if XT2 != 0:
        #     XT = XT + (XT2[0] << 16)
        # XT3 = struct.unpack("=B", binaryData[7 + (sensorIndex * 18)])
        # if XT3 != 0:
        #     XT = XT + (XT3[0] << 8)
        # XT4 = struct.unpack("=B", binaryData[6 + (sensorIndex * 18)])
        # XT = (XT + XT4[0]) / 1000
        # #print(f'XT: {XT}')

        # #Y Time
        # YT = struct.unpack("=B", binaryData[13 + (sensorIndex * 18)])
        # if YT != 0:
        #     YT = YT[0] << 24
        # YT2 = struct.unpack("=B", binaryData[12 + (sensorIndex * 18)])
        # if YT2 != 0:
        #     YT = YT + (YT2[0] << 16)
        # YT3 = struct.unpack("=B", binaryData[11 + (sensorIndex * 18)])
        # if YT3 != 0:
        #     YT = YT + (YT3[0] << 8)
        # YT4 = struct.unpack("=B", binaryData[10 + (sensorIndex * 18)])
        # YT = (YT + YT4[0]) / 1000
        # #print(f'YT: {YT}')

        # #Z Time
        # ZT = struct.unpack("=B", binaryData[17 + (sensorIndex * 18)])
        # if ZT != 0:
        #     ZT = ZT[0] << 24
        # ZT2 = struct.unpack("=B", binaryData[16 + (sensorIndex * 18)])
        # if ZT2 != 0:
        #     ZT = ZT + (ZT2[0] << 16)
        # ZT3 = struct.unpack("=B", binaryData[15 + (sensorIndex * 18)])
        # if ZT3 != 0:
        #     ZT = ZT + (ZT3[0] << 8)
        # ZT4 = struct.unpack("=B", binaryData[14 + (sensorIndex * 18)])
        # ZT = (ZT + ZT4[0]) / 1000
        # #print(f'ZT: {ZT}')

        return XAcc, YAcc, ZAcc
    
    if recvCount < 50:
    
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
        AccData[recvCount,3,2] = Z2Acc
   

        #processStopMS = int(time() * 1000)

        #processTimeMS = processStopMS - processStartMS
        #print(f'processing time in ms: {processTimeMS}')
        #print(f'Processed packet: {processCount}')
        #processCount += 1


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
    #time.sleep(2)
    XList1 = [[],[]]
    for i in range(50):
        XList1[0].append(AccData[i,0,0])
        XList1[1].append(i)
    #print(f'XList1: {XList1}')

    XList2 = [[],[]]
    for i in range(50):
        XList2[0].append(AccData[i,1,0])
        XList2[1].append(i)
    #print(f'XList: {XList}')

    YList1 = [[],[]]
    for i in range(50):
        YList1[0].append(AccData[i,0,1])
        YList1[1].append(i)
    #print(f'YList: {YList}')

    YList2 = [[],[]]
    for i in range(50):
        YList2[0].append(AccData[i,1,1])
        YList2[1].append(i)
    #print(f'YList: {YList}')

    ZList1 = [[],[]]
    for i in range(50):
        ZList1[0].append(AccData[i,0,2])
        ZList1[1].append(i)
    #print(f'ZList: {ZList}')

    ZList2 = [[],[]]
    for i in range(50):
        ZList2[0].append(AccData[i,1,2])
        ZList2[1].append(i)
    #print(f'ZList2: {ZList2}')

    _,axs = plt.subplots(2,3, figsize=(6,5))
    #axs[0][0].plot(AccData[:,1,1])
    axs[0][0].plot(XList1[1],XList1[0])
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

 
def socketLoop(recvCount): 
    #recvCount counts how many packets have been received
    print()
    print("socketLoop")
    #global processCount
    #print(f'processCount: {processCount}' )
    print(f'Start socketLoop recvCount: {recvCount}' )
    global packetDone
    
    if recvCount < 50:             #Only needed for testing - production code will run continiously
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

    elif recvCount == 50:                      # Once we've received 50 packets
        while threading.active_count() > 1:    #wait for the last threads to finish processing
            #print(f'threading.active_count(): {threading.active_count()}')
            pass
        #packetDone = 1

        #sock.close()
        print(f'Packet Done')
        #processStopMS = int(time.time() * 1000)
        #processTimeMS = processStopMS - processStartMS
        #print(f'processStart: {processStartMS}')
        #print(f'processing time in ms: {processTimeMS}')
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