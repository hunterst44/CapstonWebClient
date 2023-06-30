import socketClient
import NeuralNetwork
import numpy as np

def main():
## Receives data from 2 sensors and does NN prediction on the data in real time.

    # print(f'NeuralNetwork: {dir(NeuralNetwork)}') 
    # print(f'socketClientk: {dir(socketClient)}') 
    
    socketClient.createTrainingData(pathPreface="data/test/test", packetLimit=2, label=0, packetSize=2, numSensors=2)

    # dataStream = socketClient.GetData(packetSize=5, label=0, getTraining=False, numSensors=2, packetLimit=1000)
    # dataStream.socketLoop(0)
    # print(f'It\'s {dataStream.predictions}') 

if __name__ == "__main__": main()