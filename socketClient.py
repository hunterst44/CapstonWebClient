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
 
sock = socket.socket()
port = 80             

AcclData = np.array([ [0,0,0] ])
host = "192.168.1.65"
port = 80

def getHost():
    host = "192.168.1.65"
    #host = input("Enter Server IP: ")
    print("Host IP: {host}")

def socketLoop(): 
    ##ready = struct.pack("=h", 256)
    # try:
    #     sock.send(ready)
    # except:
    #     # recreate the socket and reconnect
    #     #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.connect(host)
    #     sock.send(ready)
        
    dataCount = 0
    dataX = struct.pack("=h", 0)
    dataY = struct.pack("=h", 0)
    dataZ = struct.pack("=h", 0)
    
    #print(f'data: {data}') 
    match dataCount:
        case 0:
            dataX = sock.recv(1) << 4
        case 1:
            dataX = dataX + (sock.recv(1) >> 4)
        case 2:
            dataY = sock.recv(1) << 4
        case 3:
            dataY = dataY + (sock.recv(1) >> 4)
        case 4:
            dataZ = sock.recv(1) << 4
        case 5:
            dataZ = dataZ + (sock.recv(1) >> 4)  
        case _:
            print(f'dataCount Error: {dataCount}')  
            dataCount = 0

    # if dataCount < 5:
    #     dataCount += dataCount
    # else:
    #     dataCount = 0

    # while dataCount < 6:
    #     if dataCount % 2:                    #dataCount is odd, so it is the Hi end of the data
    #         dataByte = sock.recv(1)
    #         data[data/2] = dataByte << 4
    #     else: 
    #         dataByte = sock.recv(1)
    #         data[data/2] = data[data/2] + dataByte
    #     print(data)    
    #     dataCount += 1
        
    AcclData = np.r_[dataX,dataY,dataZ]

    socketLoop()

    sock.close()


def main():
    
    #getHost()
    sock.connect((host, port))
    socketLoop()

    

if __name__ == "__main__": main()