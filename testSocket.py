import socket
import struct
import time
import numpy as np

numSensors = 2
y = []


# socketClient.GetData.receiveBytes():
# called in thread in socketClient.GetData.getSample()


Start = int(time.time())

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
        self.sock = socket.socket()    # One Socket connection to rule them all
        self.sockRecursionCount = 0
        #self.sock.close()
        #self.socket.create_connection((self.host, self.port), timeout=2)
        try:
            self.sock.connect((self.host, self.port))

        except socket.timeout as err:
            print(f"TCP/IP Socket Timeout Error {self.sockRecursionCount}: {err}")

        except socket.error as err:
            print(f"TCP/IP Socket Error: {err}")
            #self.sock.close()
            #self.socket.create_connection((self.host, self.port), timeout=2)
            #self.sock.connect((host, port), timeout=2)

        except ConnectionError:
            print(f"TCP/IP Socket Error: Connection Error")
    
    def promptServer(self, dataTx, host, port):
        #Check socket connection and send prompt to the server        
        try:   
            self.sock.send(dataTx)    
            
        except socket.timeout as err:
            print(f"TCP/IP Socket Timeout Error {self.sockRecursionCount}: {err}")
            self.sock.close()
            #self.socket.create_connection((self.host, self.port), timeout=2)
            self.sock.connect((host, port), timeout=2)
            #self.sock.send(self.dataTx)
            if self.sockRecursionCount < 5:
                #print(f"TCP/IP Socket Timeout Error: {err}")
                self.sockRecursionCount += 1
                if self.promptServer() == 1:
                    return 1
                else:
                    return -1
            else:
                print(f'Fatal Error: SocketBroken')
                #print(f"TCP/IP Socket Error: {err}")
                print(f"Failed transmission: {self.dataTx}, length: {len(self.dataTx)}")
                self.sockRecursionCount = 0
                return -1
            
        except socket.error as err:
            print(f"TCP/IP Socket Error: {err}")
            self.sock.close()
            #self.socket.create_connection((self.host, self.port), timeout=2)
            self.sock.connect((host, port), timeout=2)
            #//a -= 1     #Ask for a resend (decrement data index)
            #errorCount += 1
            if self.sockRecursionCount < 5:
                #print(f"TCP/IP Socket Timeout Error: {err}")
                self.sockRecursionCount += 1
                if self.promptServer() == 1:
                    return 1
                else:
                    return -1
            else:
                print(f'Fatal Error: SocketBroken')
                #print(f"TCP/IP Socket Error: {err}")
                print(f"Failed transmission: {self.dataTx}, length: {len(self.dataTx)}")
                self.sockRecursionCount = 0
                return -1

        print("Sent Data")
        self.host = host
        self.port = port
        self.sockRecursionCount = 0
        return 1

    def receiveBytes(self, dataTx, host, port):
        #Checks the connection to the servers, sends the prompt and then receives numSensors * 3 bytes
        #Collects one sample and returns the data as a byte array
        count = 0
        #sock = socket.socket()
    
        print("Sending prompt to server")
        if self.promptServer(dataTx, host, port) != 1:
            return -1
        
        #Now receive the response
        #y = self.sock.recv(numSensors * 3)
        #print(f'y received all at once? {y}')
        a = 0
        errorCount = 0
        #sampleRxStartMS = int(time.time() * 1000)
        while a < ((numSensors * 3 + self.extraRxByte)):                #iterate through the number of sensors * the number of bytes per sample
            print(f'while loop a')
            try:
                self.y.append(self.sock.recv(1))
                print(f'Received 1')
            except socket.error as err:
                print(f"TCP/IP Socket RX Error: {err}")
                #print(f"Failed transmission: {self.dataTx}, length: {len(self.dataTx)}")
                print(f"Unable to reach client with socket: Retrying...")
                #Close and reopen the connection
    
                # while errorCount < 2:      #If you get ten connection errors in a row close and reopen the socket
                #     #Close and reopen the connection
                #     # self.sock.close()
                #     # self.sock.connect((self.host, self.port))
                #     a -= 1     #Ask for a resend (decrement data index)
                #     errorCount += 1
                if self.promptServer(self, self.host, self.port) == -1:
                    print(f'Fatal Error: SocketBroken')
                    a -= 1
                    #print(f"TCP/IP Socket Error: {err}")
                    print(f"Failed transmission: {self.dataTx}, length: {len(self.dataTx)}")
                    return -1
            a += 1 
        
        #sock.close()
        self.dataGot = 1
        print(f"self.y returned: {self.y}")
        return self.y
    
    def socketSendStr(self, message):
        print()
        print(f'UX.connnectDevice')
        print(f"Sending connection info {message}")
        response = []

        #Send the prompt to get ESP32 ready to receive text
        self.dataTx = struct.pack("=B", 0x22)
        #self.promptServer(self.dataTx, self.host, self.port)
        
        response0 = self.recieveBytes(self.dataTx, self.host, self.port)

        if response0[0] == 0xFF and response0[1] == 0x0F:
            print(f'Server is ready sending length of the message to server: {len(message)}')
            self.dataTx = struct.pack("=B", message)
            if self.promptServer(self.dataTx, self.host, self.port):
                return 1
            else:
                return -1     
    
def main():
    
    dataStream = GetData(numSensors=4, pathPreface='data/test')

    dataStream.receiveBytes(dataStream.dataTx, dataStream.host, dataStream.port)

    dataStream.dataTx = struct.pack("=B", 0x0F)

    dataStream.receiveBytes(dataStream.dataTx, dataStream.host, dataStream.port)

    i = 0
    while i < 100:
        dataStream.receiveBytes(dataStream.dataTx, dataStream.host, dataStream.port)
        if dataStream.dataTx == 0xFF:
            dataStream.dataTx = struct.pack("=B", 0x0F)
        elif dataStream.dataTx == 0x0F:
            dataStream.dataTx = struct.pack("=B", 0xFF)
        i += 1

    message = "TELUSWiFi6810" + "__--__" + "aMLu4CR7yf" + "__--__"
    
    dataStream.socketSendStr(message, dataStream.host, dataStream.port)


if __name__ == "__main__": main()