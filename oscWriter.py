import socketClient
import NeuralNetwork
import numpy as np
import pythonosc
import os.path
import dill
import socket
import struct
import time
import threading
from threading import Thread
from xml.sax.xmlreader import InputSource
import rtmidi
from rtmidi.midiconstants import CONTROL_CHANGE
from scipy import signal
import sys
import numpy as np
""" 
    'noteon': NOTE_ON,
    'noteoff': NOTE_OFF,
    'programchange': PROGRAM_CHANGE,
    'controllerchange': CONTROLLER_CHANGE,
    'pitchbend': PITCH_BEND,
    'polypressure': POLY_PRESSURE,
    'channelpressure': CHANNEL_PRESSURE """


### Almost there! 
### This module takes the gestures classes predicted by the neural network and associates them with OSC channeles and data.
### Then it sends the data on to the VST to make sweet music.

class MiDiWriter:

    def __init__(self, *, predictions=[], port_name=0, channel=0, cc_num=75, bpm=120, rate='s', ToFByte=-1):
        self.midiout = rtmidi.MidiOut()
        self.port_name = port_name
        self.bpm = bpm
        self.predictions = predictions
        self.ToFEnable = 0
        self.memorySize = 10000 #How many samples to save before purging
        self.memorySizeMin = 100 #How many predictions to keep on purge
        self.ToFByte = ToFByte
        self.channelCounters = []  #Use this to count each channels loops outside the loop
        available_ports = self.midiout.get_ports()
        self.channelList = []
        self.loadChannels() #Load the Channels above - must be defined in loadChannels
        if available_ports:
            self.midiout.open_port(port_name)
        else:
            print(f"Could not find {port_name} in available ports. Opening the first port.")
            self.midiout.open_port(port_name)
        
    class MidiChannel:
        def __init__(self, *, ToFEnable=0, updateFlag=0, predictions=[], conditionType=0, conditionData=[], value=-1, channel=None, controller=None, midiLoopCount = 0):
            self.midiLoopCount = midiLoopCount #Precious value fed in each time the loop runs
            self.channel = channel
            self.controller = controller
            self.updateFlag = updateFlag
            self.conditionType = conditionType 
            ## 0 - checkHoldGesture(gesture, threshold) 
            #       checks for a gesture (conditionData[0]) 
            #       held for a threshold (conditionData[1])
            #       writes conditionData[3] to self.value
            self.conditionData = conditionData   ##
            self.value = value
            self.predictions = predictions
            self.ToFEnable = ToFEnable #IF 1 TOF sensor is enabled when channel conditions are met
            self.beatLenStr = 'w'
            self.beatMillis = self.getBeatMillis()
            self.velocity = 64  #default to halfway
            self.controlValue = 0 #default to zero so we can tell if there is a change
            self.note = 60 # default to middle C
            self.onOffToggle = 0 #off by default
            self.midiMessage = ([0x80, 60, 0])
            self.invert = 1 #1 or -1 only!
            self.shape = 0 # 0 = sin; 1 = saw; 2 = square
            self.modLenS = 16 #The modulation duration in seconds
            self.min_val = 0
            self.max_val = 127
            self.period = 2
            self.thread = threading.Thread(target=self.sendBeat)

            #self.midiMessage = ([CONTROL_CHANGE | self.channel, self.controller, self.controlValue])

        def getBeatMillis(self):
        #beatMillis is 1000 * (noteFactor * bps) 
        # bps = 60 / self.bpm  
            if self.beatLenStr == 'w':
                # 1000 * (4 * 60/self.bpm) = self.beatMillis
                # eg. 1000 * 4 * (60/ 60 bpm) = 4000ms
                beatMillis = 4000 * (60/self.bpm)
            elif self.beatLenStr == 'h':
                # 1000 * (2 * 60/self.bpm) = self.beatMillis
                # eg. 1000 * 2 * (60/ 90 bpm) = 1333 ms
                beatMillis = 2000 * (60/self.bpm)
            elif self.beatLenStr == 'q':
                # 1000 * (1 * 60/self.bpm) = self.beatMillis
                # eg. 1000 * 1 * (60/ 120 bpm) = 500ms
                beatMillis = 1000 * (60/self.bpm)
            elif self.beatLenStr == 'e':
                # 1000 * (1 * 60/self.bpm) = self.beatMillis
                # eg. 1000 * 1 * (60/ 60 bpm) = 2000ms
                beatMillis = 500 * (60/self.bpm)
            elif self.beatLenStr == 's':
                # 1000 * (1 * 60/self.bpm) = self.beatMillis
                # eg. 1000 * 1 * (60/ 60 bpm) = 2000ms
                beatMillis = 250 * (60/self.bpm)
            else:
                beatMillis = 0

            return beatMillis #returns miliseconds / beat
        
        def checkConditions(self):
            ## Checks the updated predictions list for conditions on each channel
            ## Called once for each channel in OSCWriter.conductor
            match self.conditionType:
                case 0:
                    if self.checkHoldGesture(self.conditionData[0], self.conditionData[1]) == 0:
                        self.controlValue = self.conditionData[2]
                        self.updateFlag = 1

            return self.ToFEnable

        ## Methods to check conditions

        def checkHoldGesture(self, gesture, threshold):
            print("checkHoldGesture")
            # print(f"gesture: {gesture}")
            # print(f"Value: {threshold}")
            # print(f"self.predictions: {self.predictions}")
            ## conditionType = 0
            #       checks for a gesture (conditionData[0]) 
            #       held for a threshold (conditionData[1])
            #       writes conditionData[3] to self.value
            if self.value == self.conditionData[2]:
                #No need to update if the value is already set
                return - 1
            lenPred = len(self.predictions)
            #print(f"Predictions Length: {lenPred}")
            if lenPred < threshold:
                startIdx = 0
            else:
                startIdx = lenPred-threshold

            for i in range(startIdx,lenPred):
                print(f"self.predictions[i]: {self.predictions[i]}")
                if self.predictions[i] != gesture:
                    return -1
            self.ToFEnable = 1    
            return 0
    
    def getPredictions(self, prediction):
        # Called in socketClient after prediction has been made 
        # Hands prediction data to the OSCWriter
        self.predictions.append(prediction)
        self.conductor()
        self.garbageMan()      #Reset predictions when it goes above "self.memorySize"


    def sendBeat(self):
        print("sendBeat")
        beatStart = int(time() * 1000)
        beatStop = beatStart + self.beatMillis
        if self.messageType == 0xB:  #This is a control command so send this data...
            self.midiMessage = ([CONTROL_CHANGE | self.channel, self.controller, self.controlValue])
        
        #Add other commands here...
        self.midiout.send_message(self.midiMessage)    
        beatNow = int(time() * 1000)
        while beatNow < beatStop:
            time.sleep(beatStop - beatNow)



 ##Add specialist functions to call on different channels depending on conditions.       

    def modulateDist(self, gesture, threshold):
        print("modulateDist")
            # print(f"gesture: {gesture}")
            # print(f"Value: {threshold}")
            # print(f"self.predictions: {self.predictions}")
            ## conditionType = 0
            #       checks for a gesture (conditionData[0]) 
            #       held for a threshold (conditionData[1])
            #       calls self.modulate() to set self.channelValue
        if self.value == self.conditionData[2]:
            #No need to update if the value is already set
            return - 1
        lenPred = len(self.predictions)
        #print(f"Predictions Length: {lenPred}")
        if lenPred < threshold:
            startIdx = 0
        else:
            startIdx = lenPred-threshold

        for i in range(startIdx,lenPred):
            print(f"self.predictions[i]: {self.predictions[i]}")
            if self.predictions[i] != gesture:
                return -1
        self.ToFEnable = 1    

        while self.channelCounters < self.modXIdx * 0.01:
            self.modulate()
            self.channelCounters += 1

    def modulate(self):
       #How does self.ToFByte change the modulation?
       y = self.modulation_shape(self.period, self.modLenS, self.midiLoopCount)
       y = self.convert_range(y, -1.0, 1.0, 0, 127)
       y = self.convert_range(y, 0, 127, self.min_val, self.max_val) 
       self.controlValue = int((y * self.ToFByte) / 256)
            
    def modulation_shape(self, period, x, xArrIdx):
        xArr = np.arrange(0, self.modLenS, 0.01)
        x = xArr[xArrIdx]
        y = 1

        if self.shape == 0: #'sine':
            y = self.invert * np.sin(2 * np.pi / period * x)
        elif self.shape == 1: #'saw':
            y = self.invert * signal.sawtooth(2 * np.pi / period * x)
        elif self.shape == 2: #'square':
            y = self.invert * signal.square(2 * np.pi / period * x)
        else:
            print("That wave is not supported")

        return y     
                # print(f"value: {value}")
        # print(f"channel: {channel}")
        # print(f"self.host: {self.host}")
        # print(f"self.host: {type(self.host)}")
        # print(f"self.host: {self.port}")
        # print(f"self.host: {type(self.port)}")
        # OSCsock = socket.socket()
        # OscChannel = self.host + channel
        # #OSCsock.connect((OscChannel, self.port))
        # print("Connected to server")
        # print(f"Channel: {OscChannel}")
        # print(f"Value: {value}")
        #print()

        # #try:
        # OSCsock.send(value);
       
        # OSCsock.close()

    def garbageMan(self):
        length = len(self.predictions)
        if length > self.memorySize:
            newPredict = []
            for i in range(length - self.memorySizeMin, length):
                newPredict[i] = self.predictions[i]
            
            self.predictions = newPredict

    ##TODO create makeChannel method

    def loadChannels(self):
        #1. Define Channels
        #Channel 0
        #condition type = 0 
        # method = modulateDist()
        # ToF enable = 1
        #conditionData = [0,3,10]
        # Gesture (conditionData[0]) = 1
        # threshold (conditionData[1]) = 3 
        # Data (self.conditionData[3]) = dist
        self.channel00 = self.MidiChannel(channel=0, predictions=self.predictions, conditionType=0, conditionData=[0,3,10], midiLoopCount=self.channelCounters[0])
        self.channelList.append[self.channel00]

    def conductor(self):
        ##Conducts the process of gathering and sending data
        #Add as many channeles as you need to get the effects you want
        # Eventually I will write a channel generator so you can create channeles and conditions        

        #1. Define Channeles
        #Channel 0
        #condition type = 0 
        # method = modulateDist()
        # ToF enable = 1
        #conditionData = [0,3,10]
        # Gesture (conditionData[0]) = 1
        # threshold (conditionData[1]) = 3 
        # Data (self.conditionData[3]) = dist
       
        self.ToFEnable = 0
        for channel in self.channelList:
            #2 Check conditions
            channel.checkConditions()
            channel.channelCounters[channel.channel]  += 1 #Check the conditions then update the loop
            
            #3 Toggle ToFEnable
            self.ToFEnable = channel.ToFEnable
            if self.ToFEnable:
                channel.controlValue = self.ToFByte    #ToF supplies the the control value 

        #4 Start channelThread if it's not going already
            #WriterThread = Thread(target=channel00.sendBeat)
            if  not channel.thread.is_alive():
                channel.thread.start()
        
        # while threading.active_count() > 1:    #wait for the last threads to finish processing
        #     #print(f'threading.active_count(): {threading.active_count()}')
        #     OSCThread.join()
           

    

def main():

    writer = MiDiWriter(predictions=[], port_name=0, channel=0, cc_num=75, bpm=120, rate='s', ToFByte=-1)

if __name__ == "__main__": main()