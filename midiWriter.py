# Import standard library modules
from re import U
import time
import threading
from threading import Thread
import random

# Import third-party modules
import numpy as np
import rtmidi
from scipy import signal

# Import local modules
from metronome import Metronome
import buildMidi
from midiPlayer import MidiPlayer
from midiArp import MidiArp

BPM = 120
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

    def __init__(self, *, predictions=[], port_name=1, channel=0, cc_num=75, bpm=BPM, rate='w', ToFByte=-1, playControl = []):
        self.midiOut = rtmidi.MidiOut()
        self.midiIn = rtmidi.MidiIn()
        self.midiPortOut = port_name
        self.bpm = bpm
        self.predictions = predictions
        self.ToFEnable = 0
        self.memorySize = 1000 #How many samples to save before purging
        self.memorySizeMin = 100 #How many predictions to keep on purge
        self.ToFByte = ToFByte
        #self.channelCounters = []  #Use this to count each channels loops outside the loop
        self.available_MiDiPortsOut = self.midiOut.get_ports()
        self.controlList = []
        #self.loadChannels() #Load the Channels above - must be defined in loadChannels
        self.available_MiDiPortsIn = self.midiIn.get_ports()
        self.metro = Metronome(bpm = BPM)
        self.play_loop_started = False
        self.playControl = playControl
        self.writerON = 0
        self.writerRate = rate
        self.midi_data_list = []
        self.busy = 0
        # self.midi_player = MidiPlayer()
        # self.midi_player = MidiPlayer()
        self.midiArp = MidiArp(midiIn_port_index = 2) #Need to add this to GUI
        
        #self.midiArp.start_processing_thread()
        
        
        # self.midiBuilder = buildMidi.MidiBuilder()
        

        self.metro = Metronome(bpm = self.bpm)
        # builder1 = buildMidi.MidiBuilder(dataType=self.control00.controllerType, midiMessage=[60], ch=self.control00.channel, velocity=64, rate='w')
        # result1 = builder1.build_midi()
        # midi_data_list = [result1]
        
        
        
        # print(f'self.available_MiDiPortsOut: {self.available_MiDiPortsOut}')
        # #print(f'self.available_MiDiPortsOut[0]: {self.available_MiDiPortsOut[0]}')
        # print(f'self.available_MiDiPortsIn: {self.available_MiDiPortsIn}')
        # #print(f'self.available_MiDiPortsIn[0]: {self.available_MiDiPortsIn[0]}')

        # if len(self.available_MiDiPortsOut) > 1:
            
        #     self.midiOut.open_port(port_name)  #TO DO Start this when the Go button is pressed
        # else:
        #     print(f"Could not find {port_name} in available ports. Opening the first port.")
        #     #self.midiOut.open_port(1)

    def generate_midi_data(self):
        # Logic to generate new MIDI data
        self.refreshMidi()
        
    def start_play_loop(self):
        if not self.play_loop_started:
            # self.refreshMidi()  # Refresh MIDI data before starting the loop
            self.metro.startFlag = True
            self.metro.doneFlag = True
            play_thread = threading.Thread(target=self.play_loop, args=())
            play_thread.start()
            self.play_loop_started = True
            
    def update_playControl(self):
        self.playControl = []
        # for control in self.controlList:
        #     self.playControl.append(control.startFlag)
        # print(self.playControl)   
        
        # Extracting control.startFlag attribute for each object using list comprehension
        self.playControl = [control.startFlag for control in self.controlList]

        # Printing the array of control.startFlag attributes
        print(self.playControl)

    def play_loop(self):
        # non_zero_indices = 0
        # self.playControl = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        while self.metro.startFlag:
            self.refreshMidi()
            # print("Indices where elements are not zero:", non_zero_indices)
            self.metro.startFlag = self.writerON
            if self.writerON:
                self.update_playControl()
                if self.metro.doneFlag == 1:
                    threads = []
                    for i, (midi_player, midi_data) in enumerate(zip(self.midi_players, self.midi_data_list)):
                        threads.append(threading.Thread(target=midi_player.play_beat, args=(midi_data, self.playControl[i])))
                    for thread in threads:
                        thread.start()
                    for thread in threads:
                        thread.join()

                    # for i in range(len(self.playControl)):
                    #     if self.playControl[i] != 0:
                    #         non_zero_indices = i

                    # # print(self.control00.startFlag)
                    # # print(self.control01.startFlag)
                    # # print(self.control02.startFlag)
                
                    # # Update playControl based on conditions
                    # for i, control in enumerate(self.controlList):
                    #     if control.startFlag != 0:
                    #         self.playControl = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                    #         self.playControl[i] = 1
                    #         non_zero_indices = i

                    # print("All elements in the array are 0." if all(element == 0 for element in self.playControl) else "Some elements in the array are not 0.")
                    # print("")

                    # for i in range(len(self.playControl)):
                    #     if self.playControl[i] != 0:
                    #         non_zero_indices = i

    def refreshMidi(self):
        # self.midiArp.update_Midi()  # Update MIDI information from midiArp just once for all controls
        
        time.sleep(0.03)
        self.midiArp.update_Midi()
    
        for control in self.controlList:
            if control.startFlag == 1:
                self.midiArp.order = control.direction
                self.midiArp.octave = control.octave
            arpNote = self.midiArp.update_Midi()  # Update MIDI information from midiArp just once for all controls

            control.changeRate(self.writerRate)
            control.midiBuilder.rate = control.beatLenStr
            control.midiBuilder.rate = control.beatLenStr
            control.midiBuilder.shape = control.waveform
            control.midiBuilder.newTof = control.controlValue

            # Update midiInput for each control from midiArp
            control.midiInput = arpNote
            control.midiBuilder.midiMessage = control.midiInput
            print(f"refreshMidi notes {control.midiInput}")
            

            control.midiResults = control.midiBuilder.build_midi()
    
        self.midi_data_list = [control.midiResults for control in self.controlList]
        self.midi_players = [MidiPlayer(self.midiOut, self.metro.getTimeTick(midi_data), midi_data) for control, midi_data in zip(self.controlList, self.midi_data_list)]

    def reorder_held_notes(self, order):
        if order == 0:
            # Sort notes in ascending order
            self.midiArp.held_notes = set(sorted(self.midiArp.held_notes))
        elif order == 1:
            # Sort notes in descending order
            self.midiArp.held_notes = set(sorted(self.midiArp.held_notes, reverse=True))
        elif order == 2:
            # Shuffle notes randomly
            self.midiArp.held_notes = set(random.sample(self.midiArp.held_notes, len(self.midiArp.held_notes)))
        else:
            print(f"Could not find {self.direction} in available ports. Opening the first port.")
            #self.midiOut.open_port(1)

    # def loadChannels(self):
    #     #1. Define Channels
    #     #Channel 0
    #     #condition type = 0 
    #     # method = modulateDist()
    #     # ToF enable = 1
    #     #conditionData = [[0,3],[1,3]]
    #     #First list is for the ON state, second list is for OFF state
    #     # Gesture -> conditionData[x][0] 
    #     # threshold -> conditionData[x][1])
    #     #self.metro = Metronome(bpm = BPM)
        
    #     #Control demo for midi Tof control
    #     # self.control00 = self.MidiControl(controlLabel="Channel0", midiOut=self.midiOut, channel=0, predictions=self.predictions, conditionType=0, conditionData=[[0,3],[1,3]], bpm = self.bpm, controlNum=0, controllerType=2, waveform=2)
    #     # self.control01 = self.MidiControl(controlLabel="Channel1", midiOut=self.midiOut, channel=1, predictions=self.predictions, conditionType=1, conditionData=[[1,3],[2,3]], bpm = self.bpm, controlNum=1, controllerType=2, waveform=2)
    #     # self.control02 = self.MidiControl(controlLabel="Channel2", midiOut=self.midiOut, channel=2, predictions=self.predictions, conditionType=2, conditionData=[[2,3],[3,3]], bpm = self.bpm, controlNum=2, controllerType=2, waveform=2)
       
    #     #Apregiator Demo
    #     # self.control00 = self.MidiControl(controlLabel="Channel0", midiOut=self.midiOut, channel=0, predictions=self.predictions, conditionType=0, conditionData=[[0,3],[1,3]], bpm = self.bpm, controlNum=0, controllerType=0, waveform=2)
    #     # self.control01 = self.MidiControl(controlLabel="Channel1", midiOut=self.midiOut, channel=1, predictions=self.predictions, conditionType=1, conditionData=[[1,3],[2,3]], bpm = self.bpm, controlNum=1, controllerType=0, waveform=2)
    #     # self.control02 = self.MidiControl(controlLabel="Channel2", midiOut=self.midiOut, channel=2, predictions=self.predictions, conditionType=2, conditionData=[[2,3],[3,3]], bpm = self.bpm, controlNum=2, controllerType=0, waveform=2)
        
    #      #Midi Mod demo
    #     self.control00 = self.MidiControl(controlLabel="Channel0", midiOut=self.midiOut, channel=0, predictions=self.predictions, conditionType=0, conditionData=[[0,3],[1,3]], bpm = self.bpm, controlNum=0, controllerType=1, waveform=0)
    #     self.control01 = self.MidiControl(controlLabel="Channel1", midiOut=self.midiOut, channel=1, predictions=self.predictions, conditionType=1, conditionData=[[1,3],[2,3]], bpm = self.bpm, controlNum=1, controllerType=1, waveform=1)
    #     self.control02 = self.MidiControl(controlLabel="Channel2", midiOut=self.midiOut, channel=2, predictions=self.predictions, conditionType=2, conditionData=[[2,3],[3,3]], bpm = self.bpm, controlNum=2, controllerType=1, waveform=2)
        
    #     self.control00.midiBuilder.rate = 's'
    #     self.controlList = [self.control00, self.control01, self.control02]
                
    #     self.controlList[0].waveform = 0
    #     self.controlList[1].waveform = 1
    #     self.controlList[2].waveform = 2
        
    #     self.control00.order = 0
    #     self.control01.order = 1
    #     self.control02.order = 2

    #     self.control00.order = 1
    #     self.control01.order = 2
    #     self.control02.order = -2

        
    #     self.midi_data_list = [self.control00.midiResults, self.control01.midiResults, self.control02.midiResults]
   
    #     self.midi_players = [MidiPlayer(self.midiOut, self.metro.getTimeTick(midi_data), midi_data) for control, midi_data in zip(self.controlList, self.midi_data_list)] 
                  
    def garbageMan(self):
        length = len(self.predictions)
        if length > self.memorySize:
            self.predictions = [self.predictions[i] for i in range(length - self.memorySizeMin, length)]

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
        
        # self.control00.midiBuilder.midiMessage = [70]
        # self.control01.midiBuilder.midiMessage= [65]
        # self.control02.midiBuilder.midiMessage= [55]

        # self.refreshMidi()
        
        
        
        # midi_data_list = [self.control00.midiResults, self.control01.midiResults, self.control02.midiResults]
        # midi_players = [MidiPlayer(self.midiOut, self.metro.getTimeTick(midi_data), midi_data, onFlag="startFlag") for midi_data in midi_data_list]
        
        # midi_players = [MidiPlayer(self.midiOut, self.metro.getTimeTick(midi_data), midi_data) for control, midi_data in zip(self.controlList, midi_data_list)]
  
        if not self.play_loop_started:  # Check if the play_loop has not started yet
            if self.writerON == True:
                self.refreshMidi()
                self.metro.startFlag = True
                self.metro.doneFlag = True
                play_thread = threading.Thread(target=self.play_loop, args=())
                play_thread.start()
                self.play_loop_started = True  # Set the flag to True after starting play_loop
            
        ##Conducts the process of gathering and sending data
        #Called once per prediction loop
        #Add as many controles as you need to get the effects you want
        # Eventually I will write a control generator so you can create controles and conditions            
       
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
            
                #control.buildMidi()
                # control.changeRate()

        # 4 Start controlThread if it's not going already
            # WriterThread = Thread(target=control00.sendBeat)
                # if control.thread == None:
                #     control.thread = threading.Thread(name=control.controlLabel, target=control.playBeat, args=(control.midiResults, midi_player.timeSlice, self.midiOut))
                #     # control.thread =  threading.Thread(name=control.controlLabel, target=control.play_modulation_loop, args=( control.period, control.max_duration, control.invert))
                #     control.thread.start()
                #     print(f'control name {control.thread.getName()}')
                #     print(f'control is alive {control.thread.is_alive()}')
                #     print(f'Threads (In writer): {threading.enumerate()}')
                # else:
                #     print(f'control is alive? {control.thread.is_alive()}')
                    
            # control.startFlag=False
                
                    #control.thread.start()
        
        # while threading.active_count() > 1:    #wait for the last threads to finish processing
        #     #print(f'threading.active_count(): {threading.active_count()}')
        #     OSCThread.join() 


    ##############################################################################################################
    # ###           MidiControl
    # ############################################################################################################    
    class MidiControl:
        def __init__(self, *, controlLabel='', midiOut=None, ToFEnable=0, updateFlag=0, predictions=[], conditionType=0, conditionData=[[0,3], [1,3]], channel=None, controlNum=None, midiLoopCount = 0, rate=None, waveform=None, minimum=None, maximum=None, direction=None, controlType = 0, bpm=0, controllerType=0, midiMessage=60, startFlag=0, octave=0, midiInput=[]):
            #Removed attributes:  value=-1, 
            
            self.midiLoopCount = midiLoopCount #Precious value fed in each time the loop runs
            self.controlLabel = controlLabel
            self.midiOut = midiOut
            self.bpm = BPM
            self.channel = channel
            self.controlNum = controlNum
            self.controlType = controlType  #0 modulate, 1 arpeggiate, 2 notes
            self.updateFlag = updateFlag
            #attributes provided by GUI
            self.rate = rate
            self.waveform = waveform
            self.mimimum = minimum
            self.maximum = maximum
            self.direction = direction
            ##ConditionType determines what methods will be used to determine when and which attributes to change
            #Parameters for condition checcking methods will be passed in conditionData[]
            ###Condition Type definitions:
             ## 0 - gestureThreshold(gesture, threshold) 
            #       checks for a gesture (conditionData[x][0]) 
            #       held for a threshold (conditionData[x][1])
            ## 1 
            self.conditionType = conditionType 
            self.conditionData = conditionData   ##
            #self.value = value
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
            #self.shape = 0 # 0 = sin; 1 = saw; 2 = square
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
            #self.order = order
            self.midiInput = midiInput
            

      
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
            
            


        # def playBeat(self, midi_data, timeSlice, midiOut):
        #     while True:
        #         startFlag = self.startFlag
        #         if self.startFlag != True:
        #             count = 0
        #             while(count < 3):
        #                 for msg in midi_data:
        #                 # msg = midi_data
        #                     print(f"Playing MIDI from control: {msg}")
        #                     print(self.midiOut.is_port_open)
        #                     midiOut.send_message(msg)
        #                     time.sleep(timeSlice / 1000)
        #                     time.sleep(0.002)
        #             break
                        
        #         while (self.startFlag == True):
        #             for msg in midi_data:
        #                 # msg = midi_data
        #                 print(f"Playing MIDI from control: {msg}")
        #                 print(self.midiOut.is_port_open)
        #                 midiOut.send_message(msg)
        #                 time.sleep(timeSlice / 1000)
        #                 time.sleep(0.002)
                    
     
        #             #self.midiMessage = ([CONTROL_CHANGE | self.channel, self.controlNum, self.controlValue])
        


        # def play_modulation_loop(self, period, max_duration, signal):
        #     if self.getBeatMillis():
        #         modulation = self.modulation_shape(self.shape, self.period, 1, self.invert)
        #         while True:
        #             self.play_modulation(modulation, 8, self.midiOut)
        #             #need to add flag to stop modulation
               
                    
        # def play_modulation(self, y, max_duration,midiOut):
        #     bpm = self.bpm
        #     bps = bpm/60
        #     pause_duration = self.getBeatMillis()/y.size
        #     # pause_duration = max_duration / y.size
        #     for v in y:
        #         # beatStart = int(time() * 1000)
        #         # beatStop = beatStart + pause_duration
        #         v = self.convert_range(v, -1.0, 1.0, 0, 127)
        #         v = self.convert_range(v, 0, 127, self.min_val, self.max_val)
        #         # print(f"Mod: {v}")
        #         mod = ([CONTROL_CHANGE | self.channel, self.cc_num, v])
        #         print(self.midiOut.is_port_open())
        #         midiOut.send_message(mod)
        #         self.midiOut.send_message(mod)
        #         print(time.time())
        #         # time.sleep(0.5)
                
        #         # beatNow = int(time() * 1000)
        #         # while beatNow < beatStop:
        #         time.sleep((self.getBeatMillis()/1000)/10)
        # def sendBeat(self, midiOut):
        #     print("sendBeat")
        #     self.getBeatMillis()
        #     while True:
        #         beatStart = int(time.time() * 1000)
        #         #print(f'beatStart: {beatStart}')
        #         beatStop = beatStart + self.beatMillis
        #         print(self.getBeatMillis)
        #         # print(f'beatStop: {beatStart}')
        #         #Add other commands here...
        #         if self.updateFlag:
        #             try:
        #                 midiOut.send_message(self.midiMessage)   
        #                 print(f'midiOut sent: {self.midiMessage}')
        #             except:
        #                 print('midiOut failure') 
        #         beatNow = int(time.time() * 1000)
        #         # print(f'beatNow: {beatNow}')
        #         # print(f'beatStop - beatNow: {beatStop - beatNow}') 
        #         while beatStop - beatNow > 1:
        #             beatNow = int(time.time() * 1000)
        #             #print(f'beatStop - beatNow: {beatStop - beatNow}') 
        #             time.sleep(0.001)
        #         # if self.threadToggle == 1:
        #         #     self.threadToggle = 0
        #         # else:
        #         #    self.threadToggle = 1 
                
                

                
                
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
            match int(self.conditionType):
                case 0:
                     ## ConditionType 0: Hold
                        # gestureThreshold(gesture, threshold) 
                        # [[ON POSITION, ON THRESHOLD], [OFF POSITION, OFFTHRESHOLD]]
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
                     ## ConditionType 1: Transition
                        # gestureThreshold(gesture, threshold) 
                        # [
                        # [[BEGIN ON POSITION, BEGIN ON THRESHOLD], [END ON POSITION, END ON THRESHOLD]], 
                        # [[BEGIN OFF POSITION, BEGIN OFF THRESHOLD], [END OFF POSITION, END OFF THRESHOLD]
                        # ]
                    if self.onNotOff == 1: #if on check if we need to turn it off
                        self.startFlag = 1
                        #gestureTransition(self, gesture1, threshold1, gesture2, threshold2, startIdx):
                        #When Control is ON it uses the second list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[1][0][0], self.conditionData[1][0][0], self.conditionData[1][1][0], self.conditionData[1][1][0], 0) == 0:
                            
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                            self.startFlag = 1
                        else:
                            self.updateFlag = 0
                            self.startFlag = 0
                    else:
                        self.startFlag = 0
                         #When Control is OFF it uses the first list in conditionData to set gesture and threshold
                        if self.gestureThreshold(self.conditionData[0][0][0], self.conditionData[0][0][0], self.conditionData[0][1][0], self.conditionData[0][1][0], 0) == 0:
                        #self.controlValue = self.conditionData[2]
                            self.updateFlag = 1
                            self.startFlag = 1
                        else:
                            self.updateFlag = 0
                            self.startFlag = 0
                            
                case _:
                    ## ConditionType 0: Hold 
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

        # def buildMidi(self):
        #     match self.controlNumType:
        #         case 0:
        #             print(f'channel:{self.channel}')
        #             print(f'controlNum:{self.controlNum}')
        #             print(f'controlValue:{self.controlValue}')

        #             self.midiMessage = ([CONTROL_CHANGE | int(self.channel), int(self.controlNum), int(self.controlValue)])

        # def changeRate(self):  
        #         newRate = self.controlValue
        #         print(newRate)
        #         if(newRate < 10):
        #             self.beatLenStr = 's'
        #         elif( 10 < newRate and newRate < 20):
        #             self.beatLenStr = 'e'
        #         elif( 20 < newRate and newRate < 30):
        #             self.beatLenStr = 'q'
        #         elif( 30 < newRate and newRate < 50):
        #             self.beatLenStr = 'h'
        #         elif(50 < newRate):
        #             self.beatLenStr = 'w'
               
        #         print(self.beatLenStr)

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

#####################################################################################
##Midi Command builder methods - call these within condition checking methods above  
######################################################################################       
        # def modulateDist(self, gesture, threshold):
        #     print("modulateDist")
        #     self.gestureThreshold(gesture, threshold, 0) 

        #     while self.midiLoopCount < self.modXIdx * 0.01:
        #         self.modulate()
        #         if self.messageType == 0xB:  #This is a control command so send this data...
        #             self.midiMessage = ([CONTROL_CHANGE | self.channel, self.controlNum, self.controlValue])
        #         self.midiLoopCount += 1

        # def modulate(self):
        # #How does self.ToFByte change the modulation?
        #     y = self.modulation_shape(self.period, self.modLenS, self.midiLoopCount)
        #     y = self.convert_range(y, -1.0, 1.0, 0, 127)
        #     y = self.convert_range(y, 0, 127, self.min_val, self.max_val) 
        #     self.controlValue = int((y * self.ToFByte) / 256)


        # #Joel's modulation shape function - uses self.xxx atributes to set shape etc. 
        # # We need these there so they can be exposed to the GUI        
        # def modulation_shape(self, period, x, xArrIdx):
        #     xArr = np.arrange(0, self.modLenS, 0.01)
        #     x = xArr[xArrIdx]
        #     y = 1

        #     if self.shape == 0: #'sine':
        #         y = self.invert * np.sin(2 * np.pi / period * x)
        #     elif self.shape == 1: #'saw':
        #         y = self.invert * signal.sawtooth(2 * np.pi / period * x)
        #     elif self.shape == 2: #'square':
        #         y = self.invert * signal.square(2 * np.pi / period * x)
        #     else:
        #         print("That wave is not supported")

        #     return y   

        # def modulation_shape(self, shape, period, max_duration, signal_invert):
        #     x = np.arange(0, max_duration, 0.01)
        #     y = 1
        #     sig_invert = 1

        #     if signal_invert:
        #         sig_invert = -1

        #     if shape == 'sine':
        #         y = sig_invert * np.sin(2 * np.pi / period * x)
        #     elif shape == 'saw':
        #         y = sig_invert * signal.sawtooth(2 * np.pi / period * x)
        #     elif shape == 'square':
        #         y = sig_invert * signal.square(2 * np.pi / period * x)
        #     else:
        #         print("That wave is not supported")
        #         sys.exit()  #We need to exit 

        #     return y  
                
            # bpm = self.bpm
            # bps = bpm/60
            # pause_duration = self.getBeatMillis()/y.size
            # # pause_duration = max_duration / y.size
            # for v in y:
            #     beatStart = int(time() * 1000)
            #     beatStop = beatStart + pause_duration
            #     v = self.convert_range(v, -1.0, 1.0, 0, 127)
            #     v = self.convert_range(v, 0, 127, self.min_val, self.max_val)
            #     # print(f"Mod: {v}")
            #     mod = ([CONTROL_CHANGE | self.channel, self.cc_num, v])
            #     self.midiout.send_message(mod)
            #     beatNow = int(time() * 1000)
            #     # while beatNow < beatStop:
            #     time.sleep(pause_duration)
                    
        # def convert_range(self, value, in_min, in_max, out_min, out_max):
        #     l_span = in_max - in_min
        #     r_span = out_max - out_min
        #     scaled_value = (value - in_min) / l_span
        #     scaled_value = out_min + (scaled_value * r_span)
        #     return np.round(scaled_value)
    

# def main():

#     #writer = MiDiWriter(predictions=[], port_name=0, channel=0, cc_num=75, bpm=120, rate='w', ToFByte=-1)

# if __name__ == "__main__": main()