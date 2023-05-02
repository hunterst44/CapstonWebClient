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
 
sock = socket.socket()
port = 80             

AcclData = np.array([ [0,0,0] ])
host = "192.168.1.74"
port = 80

def getHost():
    host = "192.168.1.65"
    #host = input("Enter Server IP: ")
    print("Host IP: {host}")
 
def socketLoop(): 
    print()
    print("socketLoop")
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
    a = 0
    while a < 18:
        y[a] = sock.recv(1)
        #print(f'x: {x}');
        a += 1
    
    #y = bytearray(18)
    #sock.recv_into(y, 18)
    print(f'y: {y}');
    print(f'y[0]: {y[0]}');
    sock.close()
    if y[0] != 0:
        #time.sleep(0.001)
        socketLoop()

def main():
    
    #getHost()
    socketLoop()

    

if __name__ == "__main__": main()