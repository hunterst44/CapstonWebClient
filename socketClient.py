
#   Python Socket client
#   Sends query to esp32 to request data
#   Accepts streaming data from esp32
#   Performs data analysis on data received


import socket  
import numpy as np             
 
sock = socket.socket()
port = 80             

AcclData = np.array([ [0,0,0] ])
host = 0

def getHost():
    host = input("Enter Server IP")

def socketLoop(): 
    ready = 0xFF
    try:
        sock.send(ready)
    except:
        # recreate the socket and reconnect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(host, port)
        sock.send(ready)
        
    dataCount = 0
    data = np.array([0,0,0])       
    while dataCount < 6:
        #Receive and build data one byte at a time
        if data % 2:
            dataByte = sock.recv(1)
            data[data/2] = dataByte << 4
        else: 
            dataByte = sock.recv(1)
            data[data/2] = data[data/2] + dataByte
        print(data)    
        dataCount += 1
        
    AcclData = np.r_[AcclData,[data]]

    socketLoop()

    sock.close()


def main():
    
    getHost()
    socketLoop()

    

if __name__ == "__main__": main()