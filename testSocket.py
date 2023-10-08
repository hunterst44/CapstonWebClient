import socket
import struct
import time
numSensors = 2
y = []

Start = int(time.time())

host = "192.168.1.75"
port = 80
dataTx = struct.pack("=B", 255)

count = 0
skip = 0
while count < 10000:
    sock = socket.socket()
    print("Connecting to Server")
    try:   
        socket.create_connection((host, port), timeout=10)
        #sock.connect((host, port))

    except socket.timeout as err:
        print(err)
        skip = 1
    except socket.error as err:
        skip = 1
        print(err)

    if skip == 0:
        print("Connected to server")
        #print(f'sockname: {sock.getsockname()}')
        #print(f'sockpeer: {sock.getpeername()}')
        
        try:
            sock.send(dataTx)
            print("Sent Data")
        except:
            sock.connect((host, port))
            #print("Socket Reconnected")
            sock.send(dataTx)
    
    #y = []
    #time.sleep(0.01)
    #y = sock.recv(18)
        a = 0
        errorCount = 0
        sampleRxStartMS = int(time.time() * 1000)
        while a < ((numSensors * 3)):                #iterate through the number of sensors * the number of bytes per sample
            print(f'while loop a')
            try:
                y.append(sock.recv(1))
                print(f'Received 1')
            except ConnectionError:
                print(f"Unable to reach client with socket: Retrying")
                #Close and reopen the connection
                if errorCount < 10:      #If you get ten connection errors in a row close and reopen the socket
                    #Close and reopen the connection
                    sock.close()
                    sock = socket.socket()
                    sock.connect((host, port))
                    a -= 1     #Ask for a resend (decrement data index)
                    errorCount += 1
                    sock.send(dataTx)
                else:
                    print(f'Fatal Error: SocketBroken')
            a += 1 
        sock.close()
        dataGot = 1
    count += 1
    skip = 0
