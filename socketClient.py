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
    Acc1Data[len(Acc1Data)] = []
    Acc1Data[len(Acc1Data)][0] = (binaryData[0] << 8) + binaryData[1]                                                     #XAcc
    Acc1Data[len(Acc1Data)][1] = (binaryData[2] << 8) + binaryData[3]                                                     #YAcc
    Acc1Data[len(Acc1Data)][4] = (binaryData[2] << 8) + binaryData[5]                                                     #ZACC
    Acc1Data[len(Acc1Data)][5] = (binaryData[6] << 24) + (binaryData[7] << 16) + (binaryData[8] << 8) + binaryData[9]     #XT
    Acc1Data[len(Acc1Data)][6] = (binaryData[10] << 24) + (binaryData[11] << 16) + (binaryData[12] << 8) + binaryData[13] #YT
    Acc1Data[len(Acc1Data)][7] = (binaryData[14] << 24) + (binaryData[15] << 16) + (binaryData[16] << 8) + binaryData[17] #ZT
    
    print(f'Acc1Data: {Acc1Data}')
    
    #Next write to a file or get ready for plotting the data

 
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
        try:
            y[a] = sock.recv(1)
        except ConnectionError:
            print(f"Unable to reach client with socket: Retrying")
            socketLoop()
        print(f'y[a]: {y[a]}');
        a += 1
    
    #y = bytearray(18)
    #sock.recv_into(y, 18)
    print(f'y: {y}');
    # print(f'y[0]: {y[0]}');
    sock.close()

    #TODO ensure that a new thread is created - use ids as args to the threads and check for a free thread to use
    dataThread = Thread(target=processData,args=y)
    dataThread.start()
    ##dataThread.join()

    if packetSize < 5:             #Only needed for testing - production code will run continiously
        packetSize += 1
        time.sleep(2)
        socketLoop()
    else:
        #sock.close()
        print("Packet Done")
        packetSize = 0

def main():
    
    #getHost()
    socketLoop()

    

if __name__ == "__main__": main()