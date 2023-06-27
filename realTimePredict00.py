import socketClient

## REceives data from 2 sensors and does NN prediction on the data in real time.


dataStream = socketClient.GetData(packetSize=5, label=0, getTraining=False, numSensors=2, packetLimit=1000)
dataStream.socketLoop(0)



#packetSize=packetSize, pathPreface=pathPreface, label=label, getTraining=True, packetLimit=packetLimit, numSensors=numSensors
#pathPreface="data/packet5Avg20/training00_noMove", packetLimit=20, label=0, packetSize=5, numSensors=2