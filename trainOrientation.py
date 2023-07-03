import socketClient
import NeuralNetwork
import numpy as np

#Paths
basePath = "data/Orientation00/"

class0 = "baseStationary"   #Class 0 is the reference orientation with no movement

class1 = "baseCW90X_01"         #sensor 1 reference orientation 90 CW on X axis; sensor 2 stationay
class2 = "baseCW90X_02"         #sensor 2 reference orientation 90 CW on X axis; sensor 1 stationay
class3 = "baseCW90X_01baseCW90X_02"         #sensor 1 & 2 reference orientation 90 CW on X axis

class4 = "baseCCW90X_01"         #sensor 1 reference orientation 90 CCW on X axis; sensor 2 stationay
class5 = "baseCCW90X_02"         #sensor 2 reference orientation 90 CCW on X axis; sensor 1 stationay
class6 = "baseCCW90X_01baseCW90X_02"         #sensor 1 & 2 reference orientation 90 CCW on X axis

class7 = "baseCW90Y_01"         #sensor 1 reference orientation 90 CW on Y axis; sensor 2 stationay
class8 = "baseCW90Y_02"         #sensor 2 reference orientation 90 CW on Y axis; sensor 1 stationay
class9 = "baseCW90Y_01baseCW90Y_02"         #sensor 1 & 2 reference orientation 90 CW on Y axis

class10 = "baseCCW90Y_01"         #sensor 1 reference orientation 90 CCW on Y axis; sensor 2 stationay
class11 = "baseCCW90Y_02"         #sensor 2 reference orientation 90 CCW on Y axis; sensor 1 stationay
class12 = "baseCCW90Y_01baseCW90Y_02"         #sensor 1 & 2 reference orientation 90 CCW on Y axis

pathList = [class0, class1, class2, class3, class4, class5, class6, class7, class8, class9, class10, class11, class12]
for item in pathList:
  item = basePath + item

testPathList = pathList
for item in testPathList:
  item = item + "_test"

def main():
## Receives data from 2 sensors and does NN prediction on the data in real time.

  # Get Data for training
  #No movement
  socketClient.createTrainingData(pathPreface=pathList[0], packetLimit=50, label=0, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[0], packetLimit=5, label=0, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[1], packetLimit=50, label=1, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[1], packetLimit=5, label=1, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[2], packetLimit=50, label=2, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[2], packetLimit=5, label=2, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[3], packetLimit=50, label=3, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[3], packetLimit=5, label=3, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[4], packetLimit=50, label=4, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[4], packetLimit=5, label=4, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[5], packetLimit=50, label=5, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[5], packetLimit=5, label=5, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[6], packetLimit=50, label=6, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[6], packetLimit=5, label=6, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[7], packetLimit=50, label=7, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[7], packetLimit=5, label=7, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[8], packetLimit=50, label=8, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[8], packetLimit=5, label=8, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[9], packetLimit=50, label=9, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[9], packetLimit=5, label=9, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[10], packetLimit=50, label=10, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[10], packetLimit=5, label=10, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[11], packetLimit=50, label=11, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[11], packetLimit=5, label=11, packetSize=5, numSensors=2)

  socketClient.createTrainingData(pathPreface=pathList[12], packetLimit=50, label=12, packetSize=5, numSensors=2)
  socketClient.createTrainingData(pathPreface=testPathList[12], packetLimit=5, label=12, packetSize=5, numSensors=2)

  NeuralNetwork.trainOrientation(basePath, pathList)

if __name__ == "__main__": main()