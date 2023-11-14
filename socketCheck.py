import socket
import struct

def socketCheck():
    host="192.168.4.1"
    port = 80
    dataTx = struct.pack("=B", 255)
    print()
    print("makeSockConnection()")
    print(f'dataTx: {0xFF}')
    print(f'host {host}')
    print(f'port: {port}')
    
    sock = socket.socket()
    #self.sock.setblocking(False)
    try:
        sock.connect((host, port))

    except socket.timeout as err:
        print(f"TCP/IP Socket Timeout Error: {err}")
        return -1

    except socket.error as err:
        print(f"TCP/IP Socket Error: {err}")
        return -1
        #self.sock.close()
        #self.socket.create_connection((self.host, self.port), timeout=2)
        #self.sock.connect((host, port), timeout=2)

    print('socket connected.')     
    
    sock.send(dataTx) 

def main():

    socketCheck()
if __name__ == "__main__": main()