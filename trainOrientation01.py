import socketClient
import NeuralNetwork
import numpy as np

## Receives data from 2 sensors and does NN training and logging on the data in real time.
## WARNING this will start with fresh (random) weights and biases and OVERWRITE current model at pathPreface/model

#Paths
basePath = "data/Orientation01/"

class0 = "baseStationary"   #Class 0 is the reference orientation with no movement

class1 = "baseCW90X_01"         #sensor 1 reference orientation 90 CW on X axis; sensor 2 stationay     Sensor points straight up
class2 = "baseCW90X_02"         #sensor 2 reference orientation 90 CW on X axis; sensor 1 stationay     Sensor points straight up
class3 = "baseCW90X_01baseCW90X_02"         #sensor 1 & 2 reference orientation 90 CW on X axis         Sensor points straight up

class4 = "baseCCW90X_01"         #sensor 1 reference orientation 90 CCW on X axis; sensor 2 stationay   Sensor points straight down
class5 = "baseCCW90X_02"         #sensor 2 reference orientation 90 CCW on X axis; sensor 1 stationay   Sensor points straight down
class6 = "baseCCW90X_01baseCCW90X_02"         #sensor 1 & 2 reference orientation 90 CCW on X axis       Sensor points straight down

class7 = "baseCW90Y_01"         #sensor 1 reference orientation 90 CW on Y axis; sensor 2 stationay     Sensor rotates to right (looking from ESP32)
class8 = "baseCW90Y_02"         #sensor 2 reference orientation 90 CW on Y axis; sensor 1 stationay     Sensor rotates to right (looking from ESP32)
class9 = "baseCW90Y_01baseCW90Y_02"         #sensor 1 & 2 reference orientation 90 CW on Y axis         Sensor rotates to right (looking from ESP32)

class10 = "baseCCW90Y_01"         #sensor 1 reference orientation 90 CCW on Y axis; sensor 2 stationay  Sensor rotates to left (looking from ESP32)
class11 = "baseCCW90Y_02"         #sensor 2 reference orientation 90 CCW on Y axis; sensor 1 stationay  Sensor rotates to left (looking from ESP32)
class12 = "baseCCW90Y_01baseCCW90Y_02"         #sensor 1 & 2 reference orientation 90 CCW on Y axis      Sensor rotates to left (looking from ESP32)

#pathList = [basePath + class0, basePath + class1, basePath + class2, basePath + class3, basePath + class4, basePath + class5, basePath + class6, basePath + class7, basePath + class8, basePath + class9, basePath + class10, basePath + class11, basePath + class12]

pathList = [basePath + class0]

def main():


  # Get Data for training
  #No movement
  socketClient.createTrainingData(pathPreface=basePath, labelPath=class0, packetLimit=30, label=0, packetSize=1, numSensors=2)
  socketClient.createTrainingData(pathPreface=basePath, labelPath=class0 + "_test", packetLimit=3, label=0, packetSize=1, numSensors=2)

  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class1, packetLimit=30, label=1, packetSize=1, numSensors=2)
  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class1 + "_test", packetLimit=3, label=1, packetSize=1, numSensors=2)

  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class2, packetLimit=30, label=2, packetSize=1, numSensors=2)
  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class2 + "_test", packetLimit=3, label=2, packetSize=1, numSensors=2)

  #socketClient.createTrainingData(pathPreface=basePath, labelPath=class3, packetLimit=30, label=3, packetSize=1, numSensors=2)
  #socketClient.createTrainingData(pathPreface=basePath, labelPath=class3 + "_test", packetLimit=3, label=3, packetSize=1, numSensors=2)

  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class4, packetLimit=30, label=4, packetSize=1, numSensors=2)
  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class4 + "_test", packetLimit=3, label=4, packetSize=1, numSensors=2)

  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class5, packetLimit=30, label=5, packetSize=1, numSensors=2)
  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class5 + "_test", packetLimit=3, label=5, packetSize=1, numSensors=2)

#   socketClient.createTrainingData(pathPreface=basePath, labelPath=class6, packetLimit=30, label=6, packetSize=1, numSensors=2)
#   socketClient.createTrainingData(pathPreface=basePath, labelPath=class6 + "_test", packetLimit=3, label=6, packetSize=1, numSensors=2)

  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class7, packetLimit=30, label=7, packetSize=1, numSensors=2)
  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class7 + "_test", packetLimit=3, label=7, packetSize=1, numSensors=2)

  #socketClient.createTrainingData(pathPreface=basePath, labelPath=class8, packetLimit=30, label=8, packetSize=1, numSensors=2)
  #socketClient.createTrainingData(pathPreface=basePath, labelPath=class8 + "_test", packetLimit=3, label=8, packetSize=1, numSensors=2)

  #socketClient.createTrainingData(pathPreface=basePath, labelPath=class9, packetLimit=30, label=9, packetSize=1, numSensors=2)
  #socketClient.createTrainingData(pathPreface=basePath, labelPath=class9 + "_test", packetLimit=3, label=9, packetSize=1, numSensors=2)

  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class10, packetLimit=30, label=10, packetSize=1, numSensors=2)
  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class10 + "_test", packetLimit=3, label=10, packetSize=1, numSensors=2)

  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class11, packetLimit=30, label=11, packetSize=1, numSensors=2)
  # socketClient.createTrainingData(pathPreface=basePath, labelPath=class11 + "_test", packetLimit=3, label=11, packetSize=1, numSensors=2)

#   socketClient.createTrainingData(pathPreface=basePath, labelPath=class12, packetLimit=30, label=12, packetSize=1, numSensors=2)
#   socketClient.createTrainingData(pathPreface=basePath, labelPath=class12 + "_test", packetLimit=3, label=12, packetSize=1, numSensors=2)

  # for i in range(len(pathList)):
  #   #dataArr = np.load(pathList[i] + ".npy", allow_pickle=False)
  #   #print(f'data in file {pathList[i]} shape: {dataArr.shape}')
  #   #print(f'data at basePath: {dataArr}')

  #   truthArr = np.load(pathList[i] + "_truth.npy",allow_pickle=False)
  #   print(f'truth data in {pathList[i]} shape: {truthArr.shape}')
  #   print(f'truth data at basePath: {truthArr}')

  print()
  print()
  print(f'data acquired begin training')

  dataArr = np.load(pathList[0] + ".npy", allow_pickle=False)
  print(f'data in file {pathList[0]} shape: {dataArr.shape}')
  #print(f'data at basePath: {dataArr}')

  tmpArr = np.loadtxt(pathList[0] + ".csv",dtype=float, delimiter=',', ndmin=2)
  print(f'data from csv ({pathList[0] + ".csv"}) shape: {tmpArr.shape}')
  print(f'data from csv: {tmpArr}')

  #np.save(pathList[12] + ".npy", tmpArr, allow_pickle=False)

  #Train network with test data
  NeuralNetwork.trainOrientation(basePath, pathList)

if __name__ == "__main__": main()