import socketClient
import NeuralNetwork
import numpy as np
import pythonosc
import os.path
import dill

def main():
## Receives data from 2 sensors and does NN prediction on the data in real time.

    # path = "data/Orientation01/baseCCW45Y_01C13.csv"

    # with open(path, 'rb') as f:
    #     model = dill.load(f)

    dataStream = socketClient.GetData(packetSize=1, label=0, getTraining=False, numSensors=2, packetLimit=1000, pathPreface="data/Orientation01/")
    dataStream.socketLoop(0)



if __name__ == "__main__": main()