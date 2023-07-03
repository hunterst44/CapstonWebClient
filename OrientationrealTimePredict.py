import socketClient
import NeuralNetwork
import numpy as np

def main():
## Receives data from 2 sensors and does NN prediction on the data in real time.

    dataStream = socketClient.GetData(packetSize=5, label=0, getTraining=False, numSensors=2, packetLimit=1000, pathPreface="data/Orientation00/")
    dataStream.socketLoop(0)


if __name__ == "__main__": main()