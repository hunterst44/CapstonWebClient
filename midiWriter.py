# import socketClientUx
# import NeuralNetwork
import numpy as np
# import pythonosc
# import os.path
# import dill
# import socket
import struct
import time
import threading
from threading import Thread
from xml.sax.xmlreader import InputSource
import rtmidi
from rtmidi.midiconstants import CONTROL_CHANGE
from scipy import signal
# import sys

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

    def __init__(self, *, predictions=[], port_name=1, channel=0, cc_num=75, bpm=120, rate='s', ToFByte=-1):
        self.midiOut = rtmidi.MidiOut()
        self.port_name = port_name
        self.bpm = bpm
        self.predictions = predictions
        self.ToFEnable = 0
        self.memorySize = 10000 #How many samples to save before purging
        self.memorySizeMin = 100 #How many predictions to keep on purge
        self.ToFByte = ToFByte
        #self.channelCounters = []  #Use this to count each channels loops outside the loop
        available_ports = self.midiOut.get_ports()
        self.controlList = []
        self.loadChannels() #Load the Channels above - must be defined in loadChannels
        available_ports = self.midiOut.get_ports()
        
        if available_ports:
            print(f'available_ports: {available_ports}')
            print(f'available_ports[0]: {available_ports[0]}')
            self.midiOut.open_port(port_name)
        else:
            print(f"Could not find {port_name} in available ports. Opening the first port.")
            self.midiOut.open_port(1)

    def loadChannels(self):
        #1. Define Channels
        #Channel 0
        #condition type = 0 
        # method = modulateDist()
        # ToF enable = 1
        #conditionData = [[0,3],[1,3]]
        #First list is for the ON state, second list is for OFF state
        # Gesture -> conditionData[x][0] 
        # threshold -> conditionData[x][1])

        self.control00 = self.MidiControl(controlLabel="Channel0", midiOut=self.midiOut, channel=0, predictions=self.predictions, conditionType=0, conditionData=[0,3], bpm = self.bpm, controlNum=0, controllerType=0)
        
        self.controlList = [self.control00]
                  
    def garbageMan(self):
        length = len(self.predictions)
        if length > self.memorySize:
            newPredict = []
            for i in range(length - self.memorySizeMin, length):
                newPredict[i] = self.predictions[i]
            
            self.predictions = newPredict

    def getPredictions(self, prediction):
        print()
        print('getPredictions()')
        # Called in socketClient after prediction has been made 
        # Hands prediction data to the OSCWriter
        self.predictions.append(prediction)
        self.conductor()
        self.garbageMan()      #Reset predictions when it goes above "self.memorySize"


    def conductor(self):
        print()
        print('conductor()')
        ##Conducts the process of gathering and sending data
        #Called once per prediction loop
        #Add as many controles as you need to get the effects you want
        # Eventually I will write a control generator so you can create controles and conditions            
       
        self.ToFEnable = 0
        #print(f'control List: {self.controlList}')
        for control in self.controlList:
            #2 Check conditions
            print(f'threadToggle: {control.threadToggle}')
            control.checkConditions()
            print(f'control enabled?: {control.updateFlag}')
            if control.updateFlag:
            #control.controlCounters[control.channel]  += 1 #Check the conditions then update the loop
            
                #3 Toggle ToFEnable / get ToFByte
                self.ToFEnable = control.ToFEnable
                if self.ToFEnable:
                    print(f'ToFByte: {self.ToFByte}')
                    if self.ToFByte > 0 and self.ToFByte < 128:   #Make sure we have a valid ToF value
                        control.controlValue = self.ToFByte    #ToF supplies the control value 
                control.buildMidi()
        #4 Start controlThread if it's not going already
            #WriterThread = Thread(target=control00.sendBeat)
                if control.thread == None:
                    control.thread = threading.Thread(name=control.controlLabel, target=control.sendBeat, args=(self.midiOut,))
                    control.thread.start()
                    print(f'control name {control.thread.getName()}')
                    print(f'control is alive {control.thread.is_alive()}')
                    print(f'Threads (In writer): {threading.enumerate()}')
                else:
                    print(f'control is alive? {control.thread.is_alive()}')
                #control.thread.start()
        
        # while threading.active_count() > 1:    #wait for the last threads to finish processing
        #     #print(f'threading.active_count(): {threading.active_count()}')
        #     OSCThread.join() 


    ##############################################################################################################
    # ###           MidiControl
    # ############################################################################################################    
    class MidiControl:
        def __init__(self, *, controlLabel='', midiOut=None, ToFEnable=0, updateFlag=0, predictions=[], conditionType=0, conditionData=[[0,3], [1,3]], value=-1, channel=None, controlNum=None, midiLoopCount = 0, bpm=0, controllerType=0):
            self.midiLoopCount = midiLoopCount #Precious value fed in each time the loop runs
            self.controlLabel = controlLabel
            self.midiOut = midiOut
            self.bpm = bpm
            self.channel = channel
            self.controlNum = controlNum
            self.updateFlag = updateFlag
            ##ConditionType determines what methods will be used to determine when and which attributes to change
            #Parameters for condition checcking methods will be passed in conditionData[]
            ###Condition Type definitions:
             ## 0 - gestureThreshold(gesture, threshold) 
            #       checks for a gesture (conditionData[x][0]) 
            #       held for a threshold (conditionData[x][1])
            self.conditionType = conditionType 
            self.conditionData = conditionData   ##
            self.value = value
            self.predictions = predictions
            self.ToFEnable = ToFEnable #IF 1 TOF sensor is enabled when control conditions are met
            self.beatLenStr = 'w'
            self.beatMillis = self.getBeatMillis()
            self.velocity = 64  #default to halfway
            self.controlValue = 0 #default to zero so we can tell if there is a change
            self.note = 60 # default to middle C
            self.onNotOff = 0 #off by default
            self.midiMessage = ([0x80, 60, 0])
            self.invert = 1 #1 or -1 only!
            self.shape = 0 # 0 = sin; 1 = saw; 2 = square
            self.modLenS = 16 #The modulation duration in seconds
            self.min_val = 0
            self.max_val = 127
            self.period = 2
            self.thread = None
            self.controllerType = controllerType
            self.threadToggle = 0 #toggle this within the thread to see what it is doing

            #self.midiMessage = ([CONTROL_CHANGE | self.channel, self.controlNum, self.controlValue])

        def sendBeat(self, midiOut):
            print("sendBeat")
            while True:
                beatStart = int(time.time() * 1000)
                #print(f'beatStart: {beatStart}')
                beatStop = beatStart + self.beatMillis
                # print(f'beatStop: {beatStart}')
                #Add other commands here...
                if self.updateFlag:
                    try:
                        midiOut.send_message(self.midiMessage)   
                        print(f'midiOut sent: {self.midiMessage}')
                    except:
                        print('midiOut failure') 
                beatNow = int(time.time() * 1000)
                # print(f'beatNow: {beatNow}')
                # print(f'beatStop - beatNow: {beatStop - beatNow}') 
                while beatStop - beatNow > 1:
                    beatNow = int(time.time() * 1000)
                    #print(f'beatStop - beatNow: {beatStop - beatNow}') 
                    time.sleep(0.001)
                # if self.threadToggle == 1:
                #     self.threadToggle = 0
                # else:
                #    self.threadToggle = 1 
                
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
            ## Checks the updated predictions list for conditions on each control
            ## Called once for each control in OSCWriter.conductor
            print()
            print('checkConditions(self)')
            match self.conditionType:
                case 0:
                     ## ConditionType 0: Threshold
                        # gestureThreshold(gesture, threshold) 
                        #       checks for a gesture (conditionData[0]) 
                        #       held for a threshold (conditionData[1])
                        #       writes conditionData[3] to self.value
                    if self.onNotOff == 1: #if on check if we need to turn it off
                        
                        #When Control is ON it uses the second list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[1][0], self.conditionData[1][1], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                        else:
                            self.updateFlag = 0
                    else:
                         #When Control is OFF it uses the first list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[0][0], self.conditionData[0][1], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                        else:
                            self.updateFlag = 0

        def buildMidi(self):
            match self.controlNumType:
                case 0:
                    print(f'channel:{self.channel}')
                    print(f'controlNum:{self.controlNum}')
                    print(f'controlValue:{self.controlValue}')

                    self.midiMessage = ([CONTROL_CHANGE | int(self.channel), int(self.controlNum), int(self.controlValue)])


#####################################################################################      
#Condition checking methods - called in checkConditions() based on switch case result
##################################################################################### 

        def gestureThreshold(self, gesture, threshold, startIdx):
            print("gestureThreshold")
            #startIdx counts back from the last element in the list
            # print(f"gesture: {gesture}")
            # print(f"Value: {threshold}")
            # print(f"self.predictions: {self.predictions}")
            ## conditionType = 0
            #       checks for a gesture (conditionData[0]) 
            #       held for a threshold (conditionData[1])
            #       writes conditionData[3] to self.value
            
            
            #Get index of starting point
            lenPred = len(self.predictions)
            #print(f"Predictions Length: {lenPred}")
            if lenPred < threshold:
                startIdx = startIdx
            else:
                loopIdx =  lenPred-(startIdx + threshold)

            #limit noise
            noisebudget = int(threshold/10) #All one in ten errors (for 90% neural network accuracy)
            noiseCount = 0
            for i in range(loopIdx,lenPred):
                #print(f"self.predictions[i]: {self.predictions[i]}")
                if self.predictions[i] != gesture:
                    noiseCount += 1
                    if noiseCount >= noisebudget:
                        return -1
            self.ToFEnable = 1    
            return 0
        
        def gestureTransition(self, gesture1, threshold1, gesture2, threshold2, startIdx):
            if self.gestureThreshold(gesture1, threshold1, startIdx) == 0:
                if self.gestureThreshold(gesture2, threshold2, startIdx + threshold1) == 0:
                    return 0
                else:
                    return -1
            else:
                return -1 

#####################################################################################
##Midi Command builder methods - call these within condition checking methods above  
######################################################################################       
        def modulateDist(self, gesture, threshold):
            print("modulateDist")
            self.gestureThreshold(gesture, threshold, 0) 

            while self.midiLoopCount < self.modXIdx * 0.01:
                self.modulate()
                if self.messageType == 0xB:  #This is a control command so send this data...
                    self.midiMessage = ([CONTROL_CHANGE | self.channel, self.controlNum, self.controlValue])
                self.midiLoopCount += 1

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
    

def main():

    writer = MiDiWriter(predictions=[], port_name=0, channel=0, cc_num=75, bpm=120, rate='s', ToFByte=-1)

if __name__ == "__main__": main()