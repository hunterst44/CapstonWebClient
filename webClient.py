
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import requests
import websocket
import _thread
import time
import rel

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")


def main():
    ##Establish web scoket connection
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://192.168.0.67/ws",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()

    
    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])  # Plot some data on the axes.
    plt.show()

if __name__ == "__main__": main()    


