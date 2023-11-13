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
from numpy.core.fromnumeric import shape
import rtmidi
from rtmidi.midiconstants import CONTROL_CHANGE
from scipy import signal
from metronome import Metronome
import buildMidi
from midiPlayer import MidiPlayer
from midiArp import MidiArp

BPM = 30
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

    def __init__(self, *, predictions=[], port_name=1, channel=0, cc_num=75, bpm=BPM, rate='w', ToFByte=-1, playControl = [0,0,0]):
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
        self.metro = Metronome(bpm = BPM)
        self.play_loop_started = False
        self.playControl = playControl
        self.writerON = 0
        self.rate = rate
        self.midi_data_list = []
        # self.midiArp = MidiArp(midiIn_port_index = 3)
        
        # self.midiArp.start_processing_thread()
        
        

        
        
        
        if len(available_ports) > 1:
            print(f'available_ports: {available_ports}')
            print(f'available_ports[0]: {available_ports[0]}')
            self.midiOut.open_port(port_name)
        else:
            print(f"Could not find {port_name} in available ports. Opening the first port.")
            #self.midiOut.open_port(1)

        
    def play_loop(self):
        non_zero_indices = 0
        while self.metro.startFlag == True:
            print("Indices where elements are not zero:", non_zero_indices)
            self.metro.startFlag = self.writerON
            if self.writerON == True:
                
                playIndex = 0
            
                if self.metro.doneFlag == 1:
                    threads = []
                    self.refreshMidi()
                    for midi_player, midi_data in zip(self.midi_players, self.midi_data_list):
                        if self.playControl[playIndex] == 1:
                            # self.refreshMidi()
                        
                            # self.changeRate()
                            # self.metro.getTimeTick
                            # midi_player.timeSlice = self.metro.getTimeTick(midi_data)
                        
                       
                            threads.append(threading.Thread(target=midi_player.playBeat, args=(midi_data, self.playControl[playIndex])))
                            playIndex += 1

                    for thread in threads:
                        thread.start()

                    for thread in threads:
                        thread.join()
                    
                print(self.control00.startFlag)
            
                print(self.control01.startFlag)
                print(self.control02.startFlag)
                self.playControl[0] = self.control00.startFlag
                self.playControl[1] = self.control01.startFlag
                self.playControl[2] = self.control02.startFlag
                if all(element == 0 for element in self.playControl):
                    print("All elements in the array are 0.")
                    self.playControl[non_zero_indices] = 1
                else:
                    print("Some elements in the array are not 0.")
            
                print("")
            
                for i in range(len(self.playControl)):
                    if self.playControl[i] != 0:
                        non_zero_indices = i

                
        
            
    def refreshMidi(self):
        for control in self.controlList:
            control.changeRate(self.rate)
            control.midiBuilder.rate = control.beatLenStr
            control.midiBuilder.rate = control.beatLenStr
            control.midiBuilder.shape = control.shape
            control.midiBuilder.newTof = control.controlValue
            # control.midiIn = self.midiArp.held_notes
            control.midiBuilder.midiMessage = control.midiIn
            print(f"refreshMidi notes {control.midiIn}")
            # control.midiBuilder.rate = 'w'
            print(control.midiBuilder.rate)
            control.midiResults = control.midiBuilder.build_midi()
        self.midi_data_list = [self.control00.midiResults, self.control01.midiResults, self.control02.midiResults]
        self.midi_players = [MidiPlayer(self.midiOut, self.metro.getTimeTick(midi_data), midi_data) for control, midi_data in zip(self.controlList, self.midi_data_list)]
            
            
       
            
        
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
        self.metro = Metronome(bpm = BPM)
        self.control00 = self.MidiControl(controlLabel="Channel0", midiOut=self.midiOut, channel=0, predictions=self.predictions, conditionType=0, conditionData=[[0,3],[1,3]], bpm = self.bpm, controlNum=0, controllerType=1, shape=2)
        self.control01 = self.MidiControl(controlLabel="Channel1", midiOut=self.midiOut, channel=1, predictions=self.predictions, conditionType=1, conditionData=[[1,3],[2,3]], bpm = self.bpm, controlNum=1, controllerType=1, shape=2)
        self.control02 = self.MidiControl(controlLabel="Channel2", midiOut=self.midiOut, channel=2, predictions=self.predictions, conditionType=2, conditionData=[[2,3],[3,3]], bpm = self.bpm, controlNum=2, controllerType=1, shape=2)
        self.controlList = [self.control00, self.control01, self.control02]
                
        self.controlList[0].shape = 0
        self.controlList[1].shape = 1
        self.controlList[2].shape = 2
        self.midi_data_list = [self.control00.midiResults, self.control01.midiResults, self.control02.midiResults]
   
        self.midi_players = [MidiPlayer(self.midiOut, self.metro.getTimeTick(midi_data), midi_data) for control, midi_data in zip(self.controlList, self.midi_data_list)]
        
        
        
                  
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
        
   

        self.refreshMidi()
        
       
        
        
       
        
        if not self.play_loop_started:  # Check if the play_loop has not started yet
            if self.writerON == True:
                self.refreshMidi()
                self.metro.startFlag = True
                self.metro.doneFlag = True
                play_thread = threading.Thread(target=self.play_loop, args=())
                play_thread.start()
                self.play_loop_started = True  # Set the flag to True after starting play_loop
            
        
       
        
        
            
       
        self.ToFEnable = 0
        #print(f'control List: {self.controlList}')
        for control in self.controlList:
            # control.startFlag = True
            # midi_player = MidiPlayer(self.midiOut, time_slice=self.metro.getTimeTick(control.midiResults), midi_data = control.midiResults)
            
            #2 Check conditions
            print(f'threadToggle: {control.threadToggle}')
            control.checkConditions()
            
            print(f'control enabled?: {control.updateFlag}')
            if control.updateFlag:
                
            
                
            # control.controlCounters[control.channel]  += 1 #Check the conditions then update the loop
            
                #3 Toggle ToFEnable / get ToFByte
                self.ToFEnable = control.ToFEnable
                if self.ToFEnable:
                    print(f'ToFByte: {self.ToFByte}')
                    if self.ToFByte > 0 and self.ToFByte < 128:   #Make sure we have a valid ToF value
                        control.controlValue = self.ToFByte    #ToF supplies the control value 
                        # control.midiBuilder.newTof = control.controlValue
    


    ##############################################################################################################
    # ###           MidiControl
    # ############################################################################################################    
    class MidiControl:
        def __init__(self, *, controlLabel='', midiOut=None, ToFEnable=0, updateFlag=0, predictions=[], conditionType=0, conditionData=[[0,3], [1,3]], value=-1, channel=None, controlNum=None, midiLoopCount = 0, bpm=BPM, controllerType=0, startFlag = 0, midiMessage = [60], shape = 0, octave = 0, order = 0, midiIn = []):
            self.midiLoopCount = midiLoopCount #Precious value fed in each time the loop runs
            self.controlLabel = controlLabel
            self.midiOut = midiOut
            self.bpm = BPM
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
            self.midiMessage = midiMessage
            self.invert = 1 #1 or -1 only!
            self.shape = 0 # 0 = sin; 1 = saw; 2 = square
            self.modLenS = 16 #The modulation duration in seconds
            self.min_val = 0
            self.max_val = 127
            self.period = 1
            self.thread = None
            self.controllerType = controllerType
            self.threadToggle = 0 #toggle this within the thread to see what it is doing
            #self.max_duration = max_duration
            self.midiBuilder = buildMidi.MidiBuilder(dataType=self.controllerType, midiMessage=self.midiMessage, ch=self.channel, velocity=self.velocity, rate=self.beatLenStr)
            self.midiResults = self.midiBuilder.build_midi()
            self.startFlag = startFlag
            
            #midiArp Attributes
            self.octave = octave
            self.order = order
            self.midiIn = midiIn
            

      
        def changeRate(self, rate):  
            newRate = self.controlValue
            if newRate == 0:
                self.beatLenStr = rate
                print(newRate)
            elif(newRate < 10):
                self.midiBuilder.rate = 's'
                self.beatLenStr = 's'
            elif( 10 < newRate and newRate < 20):
                self.midiBuilder.rate = 'e'
                self.beatLenStr = 'e'
            elif( 20 < newRate and newRate < 30):
                self.midiBuilder.rate = 'q'
                self.beatLenStr = 'q'
            elif( 30 < newRate and newRate < 40):
                self.midiBuilder.rate = 'h'
                self.beatLenStr = 'h'
            elif(40 < newRate):
                self.midiBuilder.rate = 'w'
                self.beatLenStr = 'w'
               
            print(self.beatLenStr)

   
                
                

                
                
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
                        self.startFlag = 1
                        
                        #When Control is ON it uses the second list in conditionData to set gesture and threshold
                        #Set 
                        if self.gestureThreshold(self.conditionData[1][0], self.conditionData[1][1], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                            self.startFlag = 1
                        else:
                            self.updateFlag = 0
                            self.startFlag = 0
                    else: #When control is not activated...
                        self.startFlag = 0
                         #When Control is OFF it uses the first list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[0][0], self.conditionData[0][1], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                            self.startFlag = 1
                        else:
                            self.updateFlag = 0
                            self.startFlag = 0
                            
                case 1:
                     ## ConditionType 0: Threshold
                        # gestureThreshold(gesture, threshold) 
                        #       checks for a gesture (conditionData[0]) 
                        #       held for a threshold (conditionData[1])
                        #       writes conditionData[3] to self.value
                    if self.onNotOff == 1: #if on check if we need to turn it off
                        self.startFlag = 1
                        
                        #When Control is ON it uses the second list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[1][0], self.conditionData[1][1], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                            self.startFlag = 1
                        else:
                            self.updateFlag = 0
                            self.startFlag = 0
                    else:
                        self.startFlag = 0
                         #When Control is OFF it uses the first list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[0][0], self.conditionData[0][1], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                            self.startFlag = 1
                        else:
                            self.updateFlag = 0
                            self.startFlag = 0
                            
                case 2:
                    ## ConditionType 0: Threshold
                    # gestureThreshold(gesture, threshold) 
                    #       checks for a gesture (conditionData[0]) 
                    #       held for a threshold (conditionData[1])
                    #       writes conditionData[3] to self.value
                    if self.onNotOff == 1: #if on check if we need to turn it off
                        self.startFlag = 1
                        
                        #When Control is ON it uses the second list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[1][0], self.conditionData[1][1], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                            self.startFlag = 1
                        else:
                            self.updateFlag = 0
                            self.startFlag = 0
                    else:
                        self.startFlag = 0
                            #When Control is OFF it uses the first list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[0][0], self.conditionData[0][1], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                            self.startFlag = 1
                        else:
                            self.updateFlag = 0
                            self.startFlag = 0

  

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
                #startIdx = startIdx
                return -1
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

    

def main():

    writer = MiDiWriter(predictions=[], port_name=0, channel=0, cc_num=75, bpm=120, rate='w', ToFByte=-1)

if __name__ == "__main__": main()