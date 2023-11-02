import PySimpleGUI as sg
import socketClientUx
import NeuralNetwork
import midiWriter
import os.path
import time
import struct
import csv
import NeuralNetwork
# import socket
# import subprocess
# import shutil
#import sys
import window


# UX.py use this file for developing data bindings to the GUI. Window difinitions are defined in this file.



class UX:

    def __init__(self, *, theme='BluePurple'):
        self.theme = theme
        self.writer = midiWriter.MiDiWriter()
        self.packetLimit = 30
        #self.packetSize = 1
        #self.numSensors = 4
        self.numHandPositions = 3   #How many handPositions trained by the model
        #self.pathPreface = "data/test/"
        #self.dataTx = 0xFF
        self.trainCountDown = 0 # Counter for training countdown
        self.sampleCount = 0 #counter for the number of samples collected per handPosition while training
        self.handPositionCount = 0 #counter for the number of handPositions collected while training
        self.goTrain = 0
        self.Test = 0 # A variable to test things
        self.windowSizeX = 900
        self.windowSizeY = 700
        self.stopPredict = 0
        self.dataStream = socketClientUx.GetData() # default values: host="192.168.4.1", port=80, packetSize=1, numSensors=4, pathPreface='data/test', labelPath="Test", label=0, getTraining=True
        self.IPAddress = ''
        self.SSIDList = []
        self.positionPathList = []
        self.controlList = [] #a List of controls from GUI or log file
        #define a graph to make the double slider for max / min values
        #self.rateGraph=sg.Graph(canvas_size=(127,10), graph_bottom_left=(0, 0), graph_top_right=(100,10), background_color='blue', enable_events=True, drag_submits=True, key='-RATEGRAPH-', visible=False)


        ports = self.writer.midiOut.get_ports()
        print(f'ports {ports}')
        
        print(f'available_MiDiPortsOut {self.writer.available_MiDiPortsOut}')
        ports = self.writer.midiOut.get_ports()
        print(f'ports {ports}')


###############################################################################################
##############                  Control Methods                               #################
###############################################################################################

    def trainModel(self):
        #iterate through all the handPositions and collect packetLimit samples of each
        #Called in window 2 and 2.1 where user provides data to set up model and data
        #Switches to window 3 to output data 
        print()
        print(f'UX.trainModel')
        # self.dataStream.label = label
        # self.dataStream.labelPath = labelPath 
        # self.dataStream.getTraining = True
        # self.dataStream.numSensors = numSensors
        # self.dataStream.pathPreface = pathPreface
        self.dataStream.getSample()
        self.dataStream.prepTraining()
        
        #CSend all the handPositions to neural network
        NeuralNetwork.trainOrientation(self.dataStream.pathPreface, self.positionPathList, 1, self.dataStream.numSensors, self.numHandPositions)        

    def createNeuralModel(self):
        modelPath = self.dataStream.pathPreface + '\model.model'
        #Add layers
        #Input is 15 features (3 Axis * 5 samples)
        print()
        print('createNeuralModel()')                                 #Or create a new one
        model = NeuralNetwork.Model()   #Instanstiate the model

        model.add(NeuralNetwork.Layer_Dense(3*self.dataStream.packetSize * self.dataStream.numSensors, 300, weight_regularizer_l2=5e-4, bias_regularizer_l2=5e-4))
        model.add(NeuralNetwork.Activation_ReLu())
        model.add(NeuralNetwork.Layer_Dropout(0.1))
        model.add(NeuralNetwork.Layer_Dense(300,self.numHandPositions))
        model.add(NeuralNetwork.Activation_Softmax())
        
        model.set(
            loss=NeuralNetwork.Loss_CategoricalCrossEntropy(),
            optimizer=NeuralNetwork.Optimizer_Adam(learning_rate=0.05, decay=5e-5),
            accuracy=NeuralNetwork.Accuracy_Categorical()
        )
        
        try:
            model.finalize()
            print(f'Model USccessfully created at: {modelPath}') 
        except:
            print('Model file failure.')
            return -1 
        
        model.save(modelPath)
        return 1
            
    def predictSample(self):
        print()
        print('predictSample()')
        #writer = oscWriter.OSCWriter()
        self.dataStream.getSample()
        predictionList = self.dataStream.predictSample()
        print(f'Converting handPosition to midi...') 
        self.writer.getPredictions(predictionList[0])
        if self.writer.ToFEnable:
            #print(f'Enable Time of Flight Sensor...') 
            self.dataStream.dataTx = 0 #Reset dataTx
            self.dataStream.dataTx = struct.pack("=B", 15)   #Enable ToF sensor
            self.dataStream.extraRxByte = 1
        else:
            #print(f'Disable Time of Flight Sensor...') 
            self.dataStream.dataTx = 0 #Reset dataTx
            self.dataStream.dataTx = struct.pack("=B", 255)   #Disable ToF sensor 
            self.dataStream.extraRxByte = 0
        self.dataStream.dataGot = 0   #Reset the dataGot flag for the next sample

        return predictionList[0]
        

    def makeModelFileMessage(self, modelPath):
        if os.path.exists(modelPath):
            # figure out a way to elegantly make a new model
            modelMessage = 'Model file exits at: ' + modelPath + ' Use this model?'
            
        else:
            modelMessage = ''

        return modelMessage   
            
            # window['-MODELOK-'].update(visible=True)
            # window.write_event_value('-MESSAGE-', message)
            # #window['-MESSAGE-'].update(f'message')

###############################################################################################
##############                  Window Definitions                            #################
###############################################################################################

    def makeWindow0(self, connected):

        if connected:
            topMessage = 'The Conductor is connected on ' + self.dataStream.ssid + ' at ' + self.dataStream.host
            connectVis = True   #Use to set visibility of an item when The Conductor is connected
            disconnectVis = False  #Use to unset visibility of an item when The Conductor is not connected
            self.SSIDList = self.dataStream.getNetworks()  #Get the network list from the air so user can reconnect

        else:
            topMessage = 'Start up The Conductor and connect your PC to the SSID displayed on the screen. Then enter IP address on the screen and click "Connect."'
            connectVis = False
            disconnectVis = True

    #Window zero welcome, set up wifi
    #sg row builder... 
                # [
                #     sg.pin(
                #         sg.Column(
                #             [
                #                 [sg.Listbox(self.SSIDList, size=(15, 4), key="-SSIDIN-", expand_y=True, enable_events=True, visible=False)
                #                 ], 
                #                 [sg.Button('Refresh', key='-SSIDLISTRFH-', visible=visibility)
                #                 ]
                #             ], 
                #             pad=(0,0)), 
                #         shrink=True)
                # ],
        layout = [[sg.Text('The Conductor: Window 0: Connect to The Conductor.'), sg.Text(size=(2,1), key='-OUTPUT-')],
                [sg.pin(sg.Column([[sg.Text(topMessage, key='-TOPMESSAGE-', size=(100,2))]]))],
                [sg.pin(sg.Column([[sg.Text(f"To use this network click 'Continue.' To connect to another network enter the network info below and click 'Reconnect'. Click 'Don't Connect' to continue without connecting", key='-TOPMESSAGE01-', size=(100,2), visible=connectVis)]]), shrink=True)],
                [sg.pin(sg.Column([[sg.Input('192.168.XX.XX', key="-IPIN-", visible=disconnectVis)], [sg.Button('Connect', key='-APCNTEBTN-', visible=disconnectVis)]], pad=(0,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Input('192.168.XX.XX', key="-IPNEW-", visible=False)]]), shrink=True)],
                [sg.pin(sg.Column([[sg.Button('Connect', key='-STNCNTEBTN-', visible=False)]], pad=(0,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Button("Don't Connect", key='-NOCNTBTN-', visible=disconnectVis)]], pad=(0,0)), shrink=True)],
                # [sg.pin(sg.Column([[sg.Listbox(self.SSIDList, size=(15, 4), key="-SSIDIN-", expand_y=True, enable_events=True, visible=False)]]), shrink=True)],
                [sg.pin(sg.Column([[sg.Button('Continue', key='-CONTBTN-', visible=connectVis)]], pad=(0,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Listbox(self.SSIDList, size=(15, 8), key="-SSIDIN-", expand_y=True, enable_events=True, visible=connectVis)], [sg.Button('Refresh', key='-SSIDLISTRFH-', visible=connectVis)]], pad=(0,0)), shrink=True)],
                #[sg.pin(sg.Column([[sg.Input('Network SSID', key="-SSIDIN-", visible=False)]]), shrink=False)],
                [sg.pin(sg.Column([[sg.Input('Password', key="-PSWDIN-", visible=connectVis)]]), shrink=True)],
                #[sg.pin(sg.Column([[sg.Button('Connect', key='-APCNTEBTN-', visible=visibility)]], pad=(0,0)), shrink=False)],
                [sg.pin(sg.Column([[sg.Button('Reconnect', key='-RECNTBTN-', visible=connectVis)]], pad=(0,0)), shrink=True)],
                #[sg.pin(sg.Column([[sg.Text('Upload a model'), sg.Text(size=(2,1), key='-UPLOADMODEL-'), sg.Input(), sg.FileBrowse(), sg.Button('Ok', key='-UPLOADMODELBTN-')]]))],
                #[sg.Text(''), sg.Text(size=(2,1), key='-OUTPUT-'), sg.Button('Ok', key='-APCONNECTBTN-')],
                [sg.pin(sg.Column([[sg.Text("If your network doesn't show up in the list open Windows network manager before clicking Refresh", visible=connectVis, key='-MESSAGE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=True)]   
                ]
        return sg.Window('THE CONDUCTOR: Step 0', layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
    

    
    def makeWindow1(self, modelMessage):
    #Window one welcome, load / create model
        layout = [[sg.Text('The Conductor: Window 1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                [sg.pin(sg.Column([[sg.Text(f"The Conductor will look in {os.path.abspath(os.getcwd()) + '/' + self.dataStream.pathPreface} for Neural Network model files\n. Click 'Ok' to use this folder.", key="-MODELMESSAGE00-", visible=True)], [sg.Button('Ok', key='-USEDEFAULTBTN-', visible=True)], [sg.Button('Ok', key='-CREATEMOEDLBTN-', visible=False)]], pad=(0,0)), shrink=True)], 
                [sg.pin(sg.Column([[sg.FolderBrowse(size=(8,1), visible=True, key='-CHOOSEDIR-')],[sg.Text(f"Or Browse for a new folder and click 'New Folder.'", key="-MODELMESSAGE01-", visible=True)], [sg.Button('New Folder', key='-NEWFOLDER-', visible=True)], [sg.Button('Ok', key='-ACCPTDEFAULT-', visible=False)]], pad=(0,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Input('How many hand positions will you train?', key="-NUMPOS-", visible=False, enable_events=True)]], pad=(0,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Input('Position 1 label', key="-POSLABEL-", visible=False)], [sg.Button('SUBMIT', key='-SUBLABELBTN-', visible=False)]], pad=(0,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Text('Train Model', key='-TRAIN-', visible=False), sg.Text(size=(2,1)), sg.Button('Train', key='-TRAINBTN-', visible=False)]]))],
                [sg.pin(sg.Column([[sg.Text('Predict hand positions', key='-PREDICT-', visible=False), sg.Text(size=(2,1)), sg.Button('Predict', key='-PREDICTBTN-',visible=False)]]))]
                  
                #[sg.Text(f'The Conductor will look in {os.path.abspath(os.getcwd()) + self.dataStream.pathPreface} for Neural Network model files.'), sg.Text(size=(5,1), key='-OUTPUT-')],
                # [sg.pin(sg.Column([[sg.Text(modelMessage), sg.Text(size=(2,1), key='-MODELMESSAGE-'), sg.Button('Ok', key='-MODELMESAGEBTN-')]]))],
                # [sg.pin(sg.Column([[sg.Text('Upload a model'), sg.Text(size=(2,1), key='-UPLOADMODEL-'), sg.Input(), sg.FileBrowse(), sg.Button('Upload', key='-UPLOADMODELBTN-')]]))],
                # [sg.Text('Create a New Model'), sg.Text(size=(2,1), key='-OUTPUT-'), sg.Button('Ok', key='-CREATE-')],
                # [sg.pin(sg.Column([[sg.Text('', visible=True, key='-MESSAGE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                #[sg.pin(sg.Column([[sg.Button('-MODELOK-', visible=False)]], pad=(0,0)), shrink=False)]
                        #sg.Text('Not a valid model file. Please try again.', size=(2,1), key='-invalidModel-', visible=True, pad=(0,0)), sg.Text(size=(2,1))]
                ]

        return sg.Window('THE CONDUCTOR: Step 1', layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
    
    def makeWindow2(self):
        self.writer.available_MiDiPortsOut = self.writer.midiOut.get_ports()
        self.writer.available_MiDiPortsIn = self.writer.midiIn.get_ports()
        
        numOutPOrts = len(self.writer.available_MiDiPortsOut)
        midiOutList = [] 
        for i in range(numOutPOrts):
            midiOutList.append(self.writer.available_MiDiPortsOut[i])

        controlList = ['Modulate', 'Arrpegiate', 'Play Note']
        waveList = ['sine', 'square', 'saw']
        conditionTypeList = ['Hold', 'Transition']
        currentPositionList = []

        
        #Window2 Training or prediction select
        #col1=[[sg.Text('Column1', background_color='red', size=sz)]]
        # col2=[[sg.Text('Column2', background_color='green', size=sz)]]
        # col3=[[sg.Text('Column3', background_color='yellow', size=sz)]]
        # col4=[[sg.Text('Column4', background_color='blue', size=sz)]]

        # layout = [[sg.Column(col1, element_justification='c' ), sg.Column(col2, element_justification='c')
        #         , sg.Column(col3, element_justification='c'), sg.Column(col4, element_justification='c')]]

        layout = [[sg.Text('The Conductor: Window 2'), sg.Text(size=(2,1), key='-OUTPUT-')],
                    [
                        sg.Column([[sg.Text(f"Let's map MiDi controls to hand positions.", key='-TOPMESSAGE00-', size=(50,1), visible=True)], [sg.Text(f"First choose a MiDi port to send commands to:", key='-TOPMESSAGE01-', size=(50,1), visible=True)]], key='-TOPMESSAGE00COL-', element_justification='left', background_color='Blue', expand_x = True, vertical_alignment='t', pad=(0,0)), 
                        sg.Column([[sg.Listbox(midiOutList, size=(50, 8), key="-MIDIPORTOUT-", expand_x=True, expand_y=True,enable_events=True, visible=True)], [sg.Button('Refresh', key='-MIDIOUTLISTRFH-', visible=True)], [sg.Button('Connect', key='-MIDIOUTCNTBTN-', visible=True)]], key='-MIDIPORTOUTCOL-', background_color='Green', element_justification='left', expand_x = True, vertical_alignment='t', pad=(0,0))
                    ],
                    [
                        sg.pin(sg.Column([[sg.Text(f"BPM", key='-BPMLABEL-', visible=False)], [sg.Slider(range=(30, 300), default_value=120, expand_x=True,orientation='horizontal', key='-BPMSLIDE-', visible=False)], [sg.Button('Ok', key='-BPMBTN-', visible=False)]], key='-BPMCOL-', background_color = 'Yellow', vertical_alignment='t', pad=(0,0)), shrink=True),
                        sg.Column([[sg.Input('Control Name', key="-CTRLNAME-", visible=False)], [sg.Button('Ok', key='-CTRLNAMEBTN-', visible=False)]], key='-CTRLNAMECOL-', background_color = 'Yellow', vertical_alignment='t', visible=False, pad=(0,0)),
                        sg.Column([[sg.Listbox(conditionTypeList, size=(10, 3), key="-CONDTYPE-", expand_y=True, enable_events=True, visible=False)]], key='-CONDTYPECOL-', background_color = 'Red', vertical_alignment='t', pad=(0,0), visible=False),
                        sg.Column([[sg.Text(f"Choose a position and hold threshold to turn the control on.", key='-CURRPOSONLABEL-', size=(15,2), visible=False)], [sg.Listbox(currentPositionList, size=(10, 3), key="-CURRPOSLISTON-", expand_y=True, enable_events=True, visible=False)], [sg.Slider(range=(1, 25), default_value=3, expand_x=True,orientation='horizontal', key='-CURRPOSONSLIDE-', visible=False)]], key='-CURRPOSLISTONCOL-', background_color = 'Red', vertical_alignment='t', pad=(0,0), visible=False),
                        sg.Column([[sg.Text(f"Choose a position and hold threshold for the end position of the transition when turning the control on.", key='-CURRPOSTRANSONLABEL-', size=(15,2), visible=False)], [sg.Listbox(currentPositionList, size=(10, 3), key="-CURRPOSLISTTRANSON-", expand_y=True, enable_events=True, visible=False)], [sg.Slider(range=(1, 25), default_value=3, expand_x=True,orientation='horizontal', key='-CURRPOSTRANSONSLIDE-', visible=False)]], key='-CURRPOSLISTTRANSONCOL-', background_color = 'Red', vertical_alignment='t', pad=(0,0), visible=False),
                        
                        sg.Column([[sg.Text(f"Choose a position and hold threshold to turn the control off.", key='-CURRPOSOFFLABEL-', size=(15,2), visible=False)], [sg.Listbox(currentPositionList, size=(10, 3), key="-CURRPOSLISTOFF-", expand_y=True, enable_events=True, visible=False)], [sg.Slider(range=(1, 25), default_value=3, expand_x=True,orientation='horizontal', key='-CURRPOSOFFSLIDE-', visible=False)], [sg.Button('Ok', key='-CONDBTN-', visible=False)]], key='-CURRPOSLISTOFFCOL-', background_color = 'Red', vertical_alignment='t', pad=(0,0), visible=False),
                        sg.Column([[sg.Text(f"Choose a position and hold threshold for the end position of the transition when turning the control off.", key='-CURRPOSOFFTRANSLABEL-', size=(15,2), visible=False)], [sg.Listbox(currentPositionList, size=(10, 3), key="-CURRPOSLISTTRANSOFF-", expand_y=True, enable_events=True, visible=False)], [sg.Slider(range=(1, 25), default_value=3, expand_x=True,orientation='horizontal', key='-CURRPOSOFFTRANSSLIDE-', visible=False)], [sg.Button('Ok', key='-CONDTRANSBTN-', visible=False)]], key='-CURRPOSLISTTRANSOFFCOL-', background_color = 'Red', vertical_alignment='t', pad=(0,0), visible=False),
                        
                        sg.Column([[sg.Listbox(controlList, size=(10, 3), key="-CTRLLIST-", expand_y=True, enable_events=True, visible=False)], [sg.Button('Select', key='-SELCNTRLTYPEBTN-', visible=False)]], key='-CTRLLISTCOL-', background_color = 'Red', vertical_alignment='t', pad=(0,0)),
                        sg.Column([[sg.Text(f"Rate", key='-RATELABEL-', size=(15,2), visible=False)], [sg.Slider(range=(0, 127), default_value=30, expand_x=True,orientation='horizontal', key='-RATESLIDE-', visible=False)]], key='-RATECOL-', background_color = 'Red', vertical_alignment='t', pad=(0,0)),
                        sg.Column([[sg.Text(f"Waveform", key='-WAVELABEL-', size=(15,2), visible=False)], [sg.Listbox(waveList, size=(50, 3), key="-WAVELIST-", enable_events=True, visible=False)]], key='-WAVECOL-', background_color = 'Blue', vertical_alignment='t', pad=(0,0)),
                        # sg.Column([[sg.Text(f"Minimum", key='-MINLABEL-', size=(15,2), visible=False)], [sg.Slider(range=(0, 127), default_value=30, expand_x=True,orientation='horizontal', key='-MINSLIDE-', visible=False)]], key='-MINCOL-', background_color = 'Pink', vertical_alignment='t', pad=(0,0)),
                        # sg.Column([[sg.Text(f"Maximum", key='-MAXLABEL-', size=(15,2), visible=False)], [sg.Slider(range=(0, 127), default_value=30, expand_x=True,orientation='horizontal', key='-MAXSLIDE-', visible=False)]], key='-MAXCOL-', background_color = 'Violet', vertical_alignment='t', pad=(0,0)),
                        # #sg.Column([[sg.Text(f"Min / Max", key='-MINMAXLABEL-', size=(15,2), visible=False)], [sg.Listbox(waveList, size=(50, 15), key="-WAVELIST-", expand_y=True, enable_events=True, visible=False)]], key='-MINCOL-', background_color = 'Orange', vertical_alignment='t', pad=(0,0))
                    ],
                    [
                        sg.Column([[sg.Text(f"Minimum", key='-MINLABEL-', size=(15,2), visible=False)], [sg.Slider(range=(0, 127), default_value=30, expand_x=True,orientation='horizontal', key='-MINSLIDE-', visible=False)]], key='-MINCOL-', background_color = 'Pink', vertical_alignment='t', pad=(0,0)),
                        sg.Column([[sg.Text(f"Maximum", key='-MAXLABEL-', size=(15,2), visible=False)], [sg.Slider(range=(0, 127), default_value=30, expand_x=True,orientation='horizontal', key='-MAXSLIDE-', visible=False)], [sg.Button('Ok', key='-MODDATABTN-', visible=False)]], key='-MAXCOL-', background_color = 'Violet', vertical_alignment='t', pad=(0,0)),
                        
                    ]]
      
        # 
        # 
        #         # 
        # 
        #           ,
        #          [[sg.pin(sg.Column([[sg.Text(f"Let's map MiDi controls to hand positions.", key='-TOPMESSAGE00-', size=(100,2), visible=True)]], key='-TOPMESSAGE00COL-', background_color = 'Green'), shrink=True, expand_x = True, expand_y = True)],
        #           [sg.pin(sg.Column([[sg.Text(f"First choose a MiDi port to send commands to:", key='-TOPMESSAGE01-', size=(100,2), visible=True)]], key='-MIDIPORTOUTCOL-', background_color = 'Blue'), shrink=True, expand_x = True, expand_y = True)]],
        #           [sg.pin(sg.Column([[sg.Listbox(midiOutList, size=(50, 8), key="-MIDIPORTOUT-", expand_y=True, expand_x=True, enable_events=True, visible=True)], [sg.Button('Refresh', key='-MIDIOUTLISTRFH-', visible=True)], [sg.Button('Connect', key='-MIDIOUTCNTBTN-', visible=True)]], size=(250,220), expand_x = True, expand_y = True, pad=(0,0), key='-BPMCOL-', background_color = 'Red'), expand_x = True, expand_y = True, shrink=True)],
        #           [sg.pin(sg.Column([[sg.Text(f"BPM", key='-BPMLABEL-', size=(15,2), visible=False)], [sg.Slider(range=(30, 300), default_value=120, expand_x=True,orientation='horizontal', key='-BPMSLIDE-', visible=False)],  [sg.Button('Ok', key='-BPMBTN-', visible=False)]], pad=(0,0), key='-CTRLLISTCOL-', background_color = 'Yellow'), shrink=True, expand_x = True, expand_y = True,)],
                  
                  
        #           #[sg.pin(sg.Column([[sg.Text(f"BPM", key='-BPMLABEL-', size=(15,2), visible=False)], [sg.Slider(range=(30, 300), default_value=120, expand_x=True,orientation='horizontal', key='-BPMSLIDE-', visible=False)],  [sg.Button('Ok', key='-BPMBTN-', visible=True)]], pad=(0,0), visible=False, key='-BPMCOL-'), shrink=True)],
                  
                  
        #           [sg.pin(sg.Column([[sg.Text(f"Waveform", key='-WAVELABEL-', size=(15,2), visible=False)], [sg.Listbox(waveList, size=(50, 15), key="-WAVELIST-", expand_y=True, enable_events=True, visible=False)]], pad=(0,0)), shrink=True)],
        #           [sg.pin(sg.Column([[sg.Text(f"Rate", key='-RATELABEL-', size=(15,2), visible=False)], [rateGraph]], pad=(0,0)), shrink=True)],
        #           [sg.pin(sg.Column([[sg.Listbox(controlList, size=(10, 3), key="-CTRLLIST-", expand_y=True, enable_events=True, visible=False)], [sg.Button('Select', key='-SELCNTRLTYPEBTN-', visible=False)]], pad=(0,0)), shrink=True)],
                  
                 
                 
   #[sg.pin(sg.Column([[sg.Button('Reconnect', key='-RECNTBTN-', visible=True)]], pad=(0,0)), shrink=True)]#[sg.pin(sg.Column([[sg.Text('Train Model'), sg.Text(size=(2,1), key='-TRAIN-'), sg.Button('Train', key='-TRAINBTN-')]]))],
                  #[sg.pin(sg.Column([[sg.Text('Predict hand positions'), sg.Text(size=(2,1), key='-PREDICT-'), sg.Button('Predict', key='-PREDICTBTN-')]]))],
                  #[sg.pin(sg.Column([[sg.Text('', visible=True, key='-WORDS-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
      #  ]
        return sg.Window('THE CONDUCTOR: Step 2 Map positions to controls', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
    

    def makeWindow2_1(self):
        #Window3 Training or prediction select
        layout = [[sg.Text('The Conductor: Window 2.1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                  [sg.pin(sg.Column([[sg.Text('Train Model'), sg.Text(size=(2,1), key='-TRAIN-'), sg.Button('Train', key='-TRAINBTN-')]]))],
                  [sg.pin(sg.Column([[sg.Text('Predict hand positions'), sg.Text(size=(2,1), key='-PREDICT-'), sg.Button('Predict', key='-PREDICTBTN-')]]))],
                  [sg.pin(sg.Column([[sg.Text('', visible=True, key='-WORDS-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
        ]
        return sg.Window('THE CONDUCTOR: Step 2.1', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
    

    def makeWindow3(self):
        #Window3 Training 
        layout = [[sg.Text('The Conductor: Window 3'), sg.Text(size=(2,1), key='-OUTPUT-')],
                  [sg.pin(sg.Column([[sg.Text("Hit the 'GO!' button to begin training", visible=True, key='-GESTURE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                  [sg.pin(sg.Column([[sg.Text('', visible=True, key='-CountDown-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                  [sg.Button('GO!')]
        ]
        return sg.Window('THE CONDUCTOR: Step 3', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)


    def makeWindow3_1(self):
        #Window3_1 Prediction 
        layout = [[sg.Text('The Conductor: Window 3_1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                  [sg.pin(sg.Column([[sg.Text("Hit the 'GO!' button to begin prediction", visible=True, key='-GESTURE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                  [sg.pin(sg.Column([[sg.Text('', visible=True, key='-CountDown-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                  [sg.pin(sg.Column([[sg.Text(''), sg.Text(size=(2,1), key='-GO-'), sg.Button('GO!', key='-GOBTN-', visible=True)]]), shrink=False)],
                  [sg.pin(sg.Column([[sg.Text(''), sg.Text(size=(2,1), key='-STOP-'), sg.Button('Stop', key='-STOPBTN-', visible=False)]]), shrink=False)]
        ]
        return sg.Window('THE CONDUCTOR: Step 3_1', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)

###############################################################################################
##############                  UX LOOP                                       #################
###############################################################################################

    def uxLoop(self):
        print()
        print('uxLoop Start')
        newIP = "192.168.4.1"
        newSSID = "TheConductor"
        newPSWD = "NoneShallPass"
        newControl = [] #Holds data from a new control until it is appended to the list
        usedPositions = [] #indexes of the positions in self.dataStream.

        stopPredict = 0
       
        ##Methods to collect run time data required for the GUI
        modelPath = self.dataStream.pathPreface + 'model.model'
        print(f'modelPath: {modelPath}')
        modelMessage = self.makeModelFileMessage(modelPath)

        sg.theme(self.theme)
        #connector = self.ConductorConnector()
        #connector.getNetworks()

        positionLabelCount = 0
        positionLabelMessage01 = ''
        newPositionLabelList = []

        # Set all windows to Noe except window 1 to start
        #window0 = self.makeWindow0(self.dataStream.sockConnection)
        window0 = None #self.makeWindow0(self.dataStream.sockConnection)
       # window1 = self.makeWindow1(modelMessage)
        window1 = None
        window2 = self.makeWindow2()
        #window2=None
        window2_1 = None
        window3 = None
        window3_1 = None

        while True:  # Event Loop
            window, event, values = sg.read_all_windows()
            print(f'event: {event}')
            print(f'values: {values}')


##############     Window0          #################
            #events for window0 (Create connection)
            #TODO Add option to choose from previous connections
            #Add option to select from detected networks
            if window == window0:

                print()
                print('Window 0')

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == "-APCNTEBTN-":
                    #Connect to the default AP network "TheCondutor"
                    print()
                    print(f'Window 0 -APCNTEBTN-')
                    #Get and validate input
                    if values["-IPIN-"] != "IP Address":
                        #TODO better validation
                            #Check pattern for IP, Get list of available networks aand let user check
                        #connector.SSID = values["-SSIDIN-"]
                        self.dataStream.host = values["-IPIN-"]
                        #connector.PSWD = "NoneShallPass"
                        
                        window['-MESSAGE-'].update(f'Connecting to The Conductor at IP Address {self.dataStream.host}...')
                        window.refresh()
                        connectTries = 0
                        while connectTries < 3:
                            print("Trying to make a socket connection")
                            if self.dataStream.makeSockConnection(self.dataStream.host, self.dataStream.port) == -1:
                                connectTries += 1
                                time.sleep(1)
                            else:
                                print("Connected to The Conductor!")
                                break
        
                    if connectTries == 3:
                        print("Can't connect to the Conductor")
                    
                    if self.dataStream.sockConnection == 1:
                        print(f'IP: {self.dataStream.host}, SSID: {self.dataStream.ssid}')
                
                    #Get Network data from the air
                        self.SSIDList = self.dataStream.getNetworks()
                        window['-TOPMESSAGE-'].update(f'Conductor Connected!  SSID: {self.dataStream.ssid}, IP Address: {self.dataStream.host}')
                        window['-TOPMESSAGE01-'].update(visible=True)
                        window['-TOPMESSAGE01-'].update(f'To use this network click continue. To connect to another network enter the network info below and click Reconnect')
                        window['-MESSAGE-'].update(visible=True)
                        window['-CONTBTN-'].update(visible=True)
                    
                    else:
                        window['-TOPMESSAGE-'].update(f'Conductor Not Connected on  SSID: {self.dataStream.ssid}, IP Address: {self.dataStream.host}')
                        window['-TOPMESSAGE01-'].update(visible=True)
                        window['-TOPMESSAGE01-'].update(f'To connect to another network enter the network info below and click Reconnect')
                        window['-CONTBTN-'].update(visible=False)
                        window['-MESSAGE-'].update(visible=True)
                    
                    self.SSIDList = self.dataStream.getNetworks()
                    window['-IPIN-'].update(visible=False)
                    window['-SSIDIN-'].update(self.SSIDList)
                    window['-SSIDIN-'].update(visible=True)
                    window['-SSIDLISTRFH-'].update(visible=True)
                    window['-PSWDIN-'].update(visible=True)
                    window['-RECNTBTN-'].update(visible=True)
                    window['-APCNTEBTN-'].update(visible=False)
                    window['-MESSAGE-'].update(visible=False)
                    window.refresh()  

                if event == '-SSIDLISTRFH-':
                    #Refresh SSID list button
                    print()
                    print(f'Window 0 -SSIDLISTRFH-')
                    self.SSIDList = self.dataStream.getNetworks()
                    window['-SSIDIN-'].update(self.SSIDList)
                    window['-SSIDIN-'].update(visible=True)
                    window.refresh()

                    
                if event == '-RECNTBTN-':
                    print()
                    print(f'Window 0 -RECNTBTN-')
                    newSSID = values["-SSIDIN-"][0].strip()
                    newPSWD = values["-PSWDIN-"].strip()
                    window['-SSIDIN-'].update(visible=False)
                    window['-PSWDIN-'].update(visible=False)
                    window['-RECNTBTN-'].update(visible=False)
                    window['-CONTBTN-'].update(visible=False)
                    window['-APCNTEBTN-'].update(visible=False)
                    window.refresh()

                    if newSSID != "Network SSID" and newPSWD != "Password":
                        #TODO better validation
                            #Check pattern for IP, Get list of available networks aand let user check
                        #connector.SSID = values["-SSIDIN-"]
                        #connector.PSWD = "NoneShallPass"
                        print(f'New IP: {newSSID}')
                        window['-TOPMESSAGE-'].update(f'Connecting Conductor to Network: {newSSID}. Please reconnect your PC to this network.')
                        window['-TOPMESSAGE01-'].update(f"Check The Conductor's display for connection information, and enter the new IP Address below.")
                        window['-IPNEW-'].update(visible=True)
                        window['-STNCNTEBTN-'].update(visible=True)
                        window.refresh()

                        message = newSSID + "__--__" + newPSWD + "__--__"

                        if self.dataStream.socketSendStr(message):
                            print("Sent network info to Server. Disconnecting from socket.")
                            print("Reconnect PC to the same network and reconnect socket")
                            self.dataStream.sock.close()
                            window['-MESSAGE-'].update(visible=True)
                            window['-SSIDLISTRFH-'].update(visible=False)
                            window['-MESSAGE-'].update(f"Sent Network Information")

                        else:
                            print("Nope Nope Nope. Connection error.")

                if event == '-STNCNTEBTN-':
                    print()
                    print(f'Window 0 -IPNEW-')
                    if window['-IPNEW-'] != 'IP Address':
                        #TODO add better validation
                        newIP = values['-IPNEW-']
                        window['-TOPMESSAGE-'].update(f'Connecting to The Conductor at {newIP} on {newSSID}.')
                        window['-TOPMESSAGE01-'].update(visible=False)
                        self.dataStream.dataTx = self.dataTx = struct.pack("=B", 0x44)
                        if self.dataStream.makeSockConnection(newIP, self.dataStream.port) == 1:
                            self.dataStream.host = newIP
                            self.dataStream.ssid = newSSID
                            self.dataStream.pswd = newPSWD
                            window['-MESSAGE-'].update(f"Connected to server at {self.dataStream.host} on {self.dataStream.ssid}")
                        
                            window.refresh()
                            self.dataStream.logCSVRow('networks.csv', [self.ssid, self.pswd, self.host, self.port])
                            time.sleep(2)
                            window1 = self.makeWindow1(modelMessage)
                            window0.hide()
                        else:
                            print(f"Error Connecting to {newIP} at {newSSID}")
                            window['-MESSAGE-'].update(f"Error Connecting to {newIP} on {newSSID}")
                            window.refresh()

                if event == '-SSIDIN-':
                    pswdInt, pswdStr = self.dataStream.checkPriorConnection(values["-IPIN-"])  
                    if pswdInt == 1:
                        newPSWD = pswdStr
                        window['-MESSAGE-'].update(f"The Conductor remembers your password for {values['-IPIN-']}. Just hit Reconnect")
                        window['-PSWDIN-'].update(f"**********")
 
                if event == '-CONTBTN-':
                    #Continue button - for accepting current connection and moving to window01 - model
                    print()
                    print(f'Window 0 -CONTBTN-')

                    window0.hide()
                    window1 = self.makeWindow1(modelMessage)

                if event == '-NOCNTBTN-':
                    self.dataStream.sock.close()
                    window0.hide()
                    window1 = self.makeWindow1(modelMessage)
           
##############     Window1          #################            
            if window == window1:
                print()
                print('Window 1')
                modelOk = -1

                #window['-invalidModel-'].update(visible=False)
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                
                if event == '-USEDEFAULTBTN-':
                    #Use default path
                    print()
                    print(f'Window 1 -USEDEFAULTBTN-')
                    modelPath = self.dataStream.pathPreface + '/model.model'
                    print(f'modelPath: {modelPath}')
                    modelLogPath = self.dataStream.pathPreface + '/modelLog.csv'
                    print(f'modelLogPath: {modelLogPath}')
                    if os.path.exists(modelPath) and os.path.exists(modelLogPath):
                        positionLabelMessage00 = 'The model at ' + self.dataStream.pathPreface + 'has these positions trained:\n'
                        with open(modelLogPath, 'r') as csvfile:
                            handPositionList = list(csv.reader(csvfile, delimiter=","))
                            print(f'handPositionList: {handPositionList}')
                            for i in range(len(handPositionList[0])):
                                newPositionLabelList.append(handPositionList[0][i])
                                positionLabelMessage00 = positionLabelMessage00 + str(i+1) + '. ' + handPositionList[0][i] + '\n'
                            window['-MODELMESSAGE00-'].update(positionLabelMessage00)
                            window['-MODELMESSAGE01-'].update("Use this model?")
                            window['-MODELMESSAGE00-'].update(visible=True)
                            window['-MODELMESSAGE01-'].update(visible=True)
                            window['-ACCPTDEFAULT-'].update(visible=True)
                            window['-USEDEFAULTBTN-'].update(visible=False)
                            window['-CREATEMOEDLBTN-'].update(visible=False)
                            window['-CHOOSEDIR-'].update(visible=False)
                            window['-NEWFOLDER-'].update(visible=False)
                            window.refresh()

                        #TODO write the positions to the GUI and let the user select
                    else:
                        newPathPreface = self.dataStream.pathPreface
                        print(f"No model at {self.dataStream.pathPreface}. Use this folder and create new model?")
                        window['-MODELMESSAGE00-'].update(f"No model at {self.dataStream.pathPreface}. Use this folder and create new model?")
                        window['-USEDEFAULTBTN-'].update(visible=False)
                        window['-CREATEMOEDLBTN-'].update(visible=True)
                        window['-CHOOSEDIR-'].update(visible=False)
                        window['-MODELMESSAGE01-'].update(visible=False)
                        window['-NEWFOLDER-'].update(visible=False)
                        window.refresh()

                if event == '-ACCPTDEFAULT-':
                    self.positionPathList = newPositionLabelList
                    window['-MODELMESSAGE00-'].update('Model selected')
                    window['-MODELMESSAGE00-'].update(visible=True)
                    window['-MODELMESSAGE01-'].update(visible=False)
                    window['-ACCPTDEFAULT-'].update(visible=False)
                    window1.hide()
                    window2 = self.makeWindow2()
                    # window['-TRAIN-'].update(visible=True)
                    # window['-PREDICT-'].update(visible=True)
                    # window['-TRAINBTN-'].update(visible=True)
                    # window['-PREDICTBTN-'].update(visible=True)


                if event == '-NEWFOLDER-':
                    print()
                    print(f'Window 1 -NEWFOLDER-')
                    print(f'Directory Chosen: {values["-CHOOSEDIR-"]}')
                    newPathPreface = values["-CHOOSEDIR-"]
                    newModelPath = newPathPreface + '/model.model'
                    newModelLogPath = newPathPreface + '/modelLog.csv'

                    if os.path.exists(newModelPath) and os.path.exists(newModelLogPath):
                        positionLabelMessage00 = 'The model at ' + newPathPreface + 'has these positions trained:\n'
                        with open(newModelLogPath, 'r') as csvfile:
                            handPositionList = list(csv.reader(csvfile, delimiter=","))
                            print(f'handPositionList: {handPositionList}')
                            for i in range(len(handPositionList[0])):
                                newPositionLabelList.append(handPositionList[0][i])
                                positionLabelMessage00 = positionLabelMessage00 + str(i+1) + '. ' + handPositionList[0][i] + '\n'
                            window['-MODELMESSAGE00-'].update(positionLabelMessage00)
                            window['-MODELMESSAGE01-'].update("Use this model?")
                            window['-MODELMESSAGE00-'].update(visible=True)
                            window['-MODELMESSAGE01-'].update(visible=True)
                            window['-ACCPTDEFAULT-'].update(visible=True)
                            window['-USEDEFAULTBTN-'].update(visible=False)
                            window['-CREATEMOEDLBTN-'].update(visible=False)
                            window['-CHOOSEDIR-'].update(visible=False)
                            window['-NEWFOLDER-'].update(visible=False)
                            window.refresh()
                    else:
                        print(f"No model at {newPathPreface}. Use this folder and create new model?")
                        window['-MODELMESSAGE00-'].update(f"No model at {newPathPreface}. Use this folder and create new model?")
                        window['-USEDEFAULTBTN-'].update(visible=False)
                        window['-CREATEMOEDLBTN-'].update(visible=True)
                        window['-CHOOSEDIR-'].update(visible=False)
                        window['-MODELMESSAGE01-'].update(visible=False)
                        window['-NEWFOLDER-'].update(visible=False)
                        window.refresh()

                if event == '-CREATEMOEDLBTN-':
                    print()
                    print(f'Window 1 --CREATEMOEDLBTN-')
                    window['-NUMPOS-'].update(visible=True)
                    window['-USEDEFAULTBTN-'].update(visible=False)
                    window['-MODELMESSAGE01-'].update(visible=False)
                    window['-MODELMESSAGE00-'].update(visible=False)
                    window['-CREATEMOEDLBTN-'].update(visible=False)
                    window['-POSLABEL-'].update(visible=False)
                    window['-SUBLABELBTN-'].update(visible=False)
                    window.refresh()

                if event == '-NUMPOS-':
                    print()
                    print(f'Window 1 -NUMPOS-')
                    print(f'positionLabelCount: {positionLabelCount}')
                    print(f'self.positionPathList: {self.positionPathList}')
                    print(f'self.numHandPositions: {self.numHandPositions}')
                    window['-NUMPOS-'].update(visible=False)
                    window['-USEDEFAULTBTN-'].update(visible=False)
                    if positionLabelCount == 0:
                        self.dataStream.pathPreface = newPathPreface
                        
                        window.refresh()
                        numPositions = values['-NUMPOS-']
                        numPositions = int(numPositions)

                        print(f'numPositions: {numPositions}')
                        print(f'type numPositions: {type(numPositions)}')
                        if numPositions < 16:
                            self.numHandPositions = numPositions

                        else: 
                            window.write_event_value("-CREATEMOEDLBTN-", '') #Back to create model option
 
                    if positionLabelCount < self.numHandPositions:
                        window['-MODELMESSAGE00-'].update(f'Add a label for hand position {positionLabelCount + 1}...')
                        window['-MODELMESSAGE00-'].update(visible=True)
                        window['-POSLABEL-'].update(visible=True)
                        window['-SUBLABELBTN-'].update(visible=True)
                        window.refresh()
                    
                    else: #All the labels are in log em...
                        self.dataStream.logCSVRow('modelLog.csv', self.positionPathList, append=False)
                        window['-POSLABEL-'].update(visible=False)
                        window['-SUBLABELBTN-'].update(visible=False)
                        #self.dataStream.logCSVRow('modelLog.csv', self.positionPathList)
                        window['-MODELMESSAGE00-'].update(f'Hand position labels logged to {self.dataStream.pathPreface}/modelLog.csv.')
                        
                        if self.createNeuralModel() == 1:
                            window['-MODELMESSAGE01-'].update(f'A neural network model has been created at {self.dataStream.pathPreface} model.model.\n Now you can train the model or use it to predict hand positions. Note you cannot predict until you have trained the model.')
                        else:
                            window['-MODELMESSAGE01-'].update(f'There is a problem with the neural network model. The network will try to create a new model when you train.\n Now you can train the model or use it to predict hand positions. Note you cannot predict until you have trained the model.')

                        window['-MODELMESSAGE01-'].update(visible=True)
                        window1.hide()
                        window2 = self.makeWindow2()  #model complete go to window two - map positions
                        # window['-TRAIN-'].update(visible=True)
                        # window['-PREDICT-'].update(visible=True)
                        # window['-TRAINBTN-'].update(visible=True)
                        # window['-PREDICTBTN-'].update(visible=True)

                if event == '-SUBLABELBTN-':
                    print()
                    print(f'Window 1 -NUMPOS-')
                    self.positionPathList.append(values['-POSLABEL-'])
                    positionLabelCount += 1
                    positionLabelMessage01 = ''
                    for i in range(len(self.positionPathList)):
                        positionLabelMessage01 = positionLabelMessage01 + str(i+1) + '. ' + self.positionPathList[i] + '\n'
                    window['-MODELMESSAGE01-'].update(positionLabelMessage01)
                    window['-MODELMESSAGE01-'].update(visible=True)
                    window.refresh()
                    window.write_event_value("-NUMPOS-", '')
                
                # if event == "-TRAINBTN-":
                #     print()
                #     print("-TRAINBTN- ")
                #     #setup datastream how we want it for training
                #     #dataStream = socketClientUx.GetData(packetSize=self.packetSize, label=label, labelPath=labelPath, getTraining=True, numSensors=numSensors, pathPreface=pathPreface)
                #     window1.hide()
                #     window3 =self.makeWindow3()
                           
                # if event == "-PREDICTBTN-":  
                #     print() 
                #     print("-PREDICTBTN-")
                #     window1.hide()
                #     window3_1 =self.makeWindow3_1()

##############     Window2          #################
            if window == window2:
                #User chooses training or prediction 
                #Currently used for testing
                print()
                print()
                print("Window 2")

                # self.writer.available_MiDiPortsOut = self.writer.midiOut.get_ports()
                # self.writer.available_MiDiPortsIn = self.writer.midiIn.get_ports()

                # print(f'self.writer.available_MiDiPortsOut: {self.writer.available_MiDiPortsOut}')
                # print(f'self.writer.available_MiDiPortsOut[0]: {self.writer.available_MiDiPortsOut[0]}')

                if event == sg.WIN_CLOSED or event == 'Exit':
                    window2.hide()
                    window1 =self.makeWindow1()   

                #Set up MiDi port
                if event == '-MIDIOUTLISTRFH-':
                    print()
                    print(f'Window 2 -MIDIOUTLISTRFH-')
                    self.writer.available_MiDiPortsOut = self.writer.midiOut.get_ports()
                    self.writer.available_MiDiPortsIn = self.writer.midiIn.get_ports()
        
                    numOutPOrts = len(self.writer.available_MiDiPortsOut)
                    midiOutList = [] 
                    for i in range(numOutPOrts):
                        midiOutList.append(self.writer.available_MiDiPortsOut[i])

                    window['-MIDIPORTOUT-'].update(midiOutList)
                    window.refresh()

                #Set BPM
                if event == '-MIDIOUTCNTBTN-': 
                    print()
                    print(f'Window 2 -MIDIOUTCNTBTN-')
                    
                    newPortlen = len(values["-MIDIPORTOUT-"])
                    if newPortlen >= 1:
                        newPortlen = len(values["-MIDIPORTOUT-"][0])
                        print(f'values["-MIDIPORTOUT-"][0]: {values["-MIDIPORTOUT-"][0]}')
                        newMidiOutPort = values["-MIDIPORTOUT-"][0]
                        self.writer.midiPortOut = int(newMidiOutPort[newPortlen-1])
                        print(f'self.writer.midiPortOut: {self.writer.midiPortOut}')
                        print(f'type(self.writer.midiPortOut): {type(self.writer.midiPortOut)}')

                        if not self.writer.midiOut.is_port_open():
                            try:
                                self.writer.midiOut.open_port(self.writer.midiPortOut) 
                            except:
                                print(f'Unable to connect to port {newMidiOutPort}')  
                        else:
                            print(f'Port already open')
                        print(f'midi port connected') 

                        window['-MIDIPORTOUT-'].hide_row()
                        window['-MIDIPORTOUT-'].set_size(size=(0,0))
                        window['-MIDIPORTOUT-'].update(visible=False)
                        window['-MIDIOUTLISTRFH-'].update(visible=False)
                        window['-MIDIOUTLISTRFH-'].set_size(size=(0,0))
                        window['-MIDIOUTCNTBTN-'].update(visible=False)
                        window['-MIDIOUTCNTBTN-'].set_size(size=(0,0))

                        window['-MIDIPORTOUTCOL-'].set_size(size=(0,0))
                        window['-MIDIPORTOUTCOL-'].update(visible=False)
                        window['-BPMCOL-'].update(visible=True)
                        window['-TOPMESSAGE00-'].update("Set the Beats per minute")
                        window['-TOPMESSAGE01-'].update(visible=False)
                        window['-TOPMESSAGE01-'].set_size(size=(0,0))
                        window['-TOPMESSAGE01-'].hide_row()
                        # window['-MIDIOUTLISTRFH-'].update(visible=False)
                        # window['-MIDIOUTCNTBTN-'].update(visible=False)
                        #window['-MIDIOUTCOL-'].hide_row()

                        window['-BPMLABEL-'].update(visible=True)
                        window['-BPMSLIDE-'].update(visible=True)
                        window['-BPMBTN-'].update(visible=True)
                        #window['-MESSAGE-'].update(visible=False)
                        window.refresh()  
                    else:
                        print(f'No MiDI port selected')
                        window['-MIDIPORTOUT-'].update(visible=True)
                        window['-MIDIOUTLISTRFH-'].update(visible=True)
                        window['-MIDIOUTCNTBTN-'].update(visible=True)
                        window.write_event_value("-MIDIOUTLISTRFH-", '')

                #Set Control Name
                if event == '-BPMBTN-':
                    print()
                    print(f'Window 2 -BPMBTM-')
                    print(f'values["-BPMSLIDE-"][0]: {values["-BPMSLIDE-"]}')
                    
                    self.writer.bpm = values["-BPMSLIDE-"]
                    print(f'self.writer.bpm: {self.writer.bpm}')

                    window['-BPMCOL-'].set_size(size=(0,0))
                    window['-BPMCOL-'].update(visible=False)
                    window['-CTRLLISTCOL-'].update(visible=True)
                    window['-CTRLNAME-'].update(visible=True)
                    window['-CTRLNAMEBTN-'].update(visible=True)
                    window.refresh()

                #Set Conditions
                if event == '-CTRLNAMEBTN-':
                    print()
                    print(f'Window 2 -CTRLNAMEBTN-')
                    print(f'values["-CTRLNAME-"]: {values["-CTRLNAME-"]}')
                    newControl.append(values['-CTRLNAME-'])

                    window['-CTRLLISTCOL-'].set_size(size=(0,0))
                    window['-CTRLLISTCOL-'].update(visible=False)
                    window['-CONDTYPECOL--'].update(visible=True)
                    window['-CONDTYPE-'].update(visible=True)
                    window.refresh()

                
                if event == '-CONDTYPE-':
                    print()
                    print(f'Window 2 -CONDTYPE-')
                    print(f'values["-CONDTYPE-"]: {values["-CONDTYPE-"]}')
                    
                    window['--CONDTYPE-COL-'].set_size(size=(0,0))
                    window['-CONDTYPECOL-'].update(visible=False)
                    window['-CURRPOSLISTONCOL-'].update(visible=True)
                    window['-CURRPOSLISTON-'].update(visible=True)
                    window['-CURRPOSONLABEL-'].update(visible=True)
                    window['-CURRPOSOFFON-'].update(visible=True)
                    window['-CURRPOSLISTOFFCOL-'].update(visible=True)
                    window['-CURRPOSLISTOFF-'].update(visible=True)
                    window['-CURRPOSOFFLABEL-'].update(visible=True)
                    window['-CURRPOSOFFSLIDE-'].update(visible=True)
                    window['-CONDBTN-'].update(visible=True)
                    if values["-CONDTYPE-"] == 'Transition':
                        window['-CURRPOSONLABEL-'].update("Choose a position and threshold for the start position of the transition when turning the control on")
                        window['-CURRPOSLISTTRANSONCOL-'].update(visible=True)
                        window['-CURRPOSTRANSONSLIDE-'].update(visible=True)
                        window['-CURRPOSLISTTRANSON-'].update(visible=True)
                        window['-CURRPOSTRANSONLABEL-'].update(visible=True)
                        window['-CURRPOSONLABEL-'].update("Choose a position and threshold for the start position of the transition when turning the control off")
                        window['-CURRPOSLISTTRANSOFFCOL-'].update(visible=True)
                        window['-CURRPOSOFFTRANSSLIDE-'].update(visible=True)
                        window['-CURRPOSLISTTRANSOFF-'].update(visible=True)
                        window['-CURRPOSOFFTRANSLABEL-'].update(visible=True)
                        window['-CONDTRANSBTN-'].update(visible=True)
                        window['-CONDBTN-'].update(visible=False)
                    window.refresh()

                #Set Control Type    
                if event == 'CONDBTN' or event == '-CONDTRANSBTN-':    
                    #Set Control Type
                    window['-CURRPOSTRANSONSLIDE-'].update(visible=False)
                    window['-CURRPOSLISTTRANSON-'].update(visible=False)
                    window['-CURRPOSTRANSONLABEL-'].update(visible=False)
                    window['-CURRPOSOFFTRANSSLIDE-'].update(visible=False)
                    window['-CURRPOSLISTTRANSOFF-'].update(visible=False)
                    window['-CURRPOSOFFTRANSLABEL-'].update(visible=False)
                    window['-CONDTRANSBTN-'].update(visible=False)
                    window['-CONDBTN-'].update(visible=False)
                    window['-CURRPOSLISTONCOL-'].update(visible=False)
                    window['-CURRPOSLISTON-'].update(visible=False)
                    window['-CURRPOSONLABEL-'].update(visible=False)
                    window['-CURRPOSOFFON-'].update(visible=False)
                    window['-CURRPOSLISTOFFCOL-'].update(visible=False)
                    window['-CURRPOSLISTOFF-'].update(visible=False)
                    window['-CURRPOSOFFLABEL-'].update(visible=False)
                    window['-CURRPOSOFFSLIDE-'].update(visible=False)
                    window['-CURRPOSLISTONCOL-'].set_size(size=(0,0))
                    window['-CURRPOSLISTONCOL-'].update(visible=False)
                    window['-CURRPOSLISTOFFCOL-'].set_size(size=(0,0))
                    window['-CURRPOSLISTOFFCOL-'].update(visible=False)
                    window['-CURRPOSLISTTRANSONCOL-'].set_size(size=(0,0))
                    window['-CURRPOSLISTTRANSONCOL-'].update(visible=False)
                    window['-CURRPOSLISTTRANSOFFCOL-'].set_size(size=(0,0))
                    window['-CURRPOSLISTTRANSOFFCOL-'].update(visible=False)
                    window['-CURRPOSTRANSONSLIDE-'].update(visible=False)
                    window['-CURRPOSLISTTRANSON-'].update(visible=False)
                    window['-CURRPOSTRANSONLABEL-'].update(visible=False)
                    window['-CURRPOSOFFTRANSSLIDE-'].update(visible=False)
                    window['-CURRPOSLISTTRANSOFF-'].update(visible=False)
                    window['-CURRPOSOFFTRANSLABEL-'].update(visible=False)
                    window['-CONDTRANSBTN-'].update(visible=False)
                    window['-CONDBTN-'].update(visible=False)
                    window['-CURRPOSLISTONCOL-'].update(visible=False)
                    window['-CURRPOSLISTON-'].update(visible=False)
                    window['-CURRPOSONLABEL-'].update(visible=False)
                    window['-CURRPOSOFFON-'].update(visible=False)
                    window['-CURRPOSLISTOFFCOL-'].update(visible=False)
                    window['-CURRPOSLISTOFF-'].update(visible=False)
                    window['-CURRPOSOFFLABEL-'].update(visible=False)
                    window['-CURRPOSOFFSLIDE-'].update(visible=False)



                    window['-CTRLLISTCOL-'].update(visible=True)

                    window['-TOPMESSAGE00-'].update("Choose a Control Type.")
                    window['-CTRLLIST-'].update(visible=True)
                    window['-SELCNTRLTYPEBTN-'].update(visible=True)
                    window['-BPMBTN-'].update(visible=False)
                    window['-BPMSLIDE-'].update(visible=False)
                    window['-BPMLABEL-'].update(visible=False)
                    #window['-CTRLLISTCOL-'].hide_row()
                    window.refresh()

                # if event == '-BPMSLIDE-':
                #     print()
                #     print(f'Window 2 -BPMSLIDE-')
                #     print(f'values["-BPMSLIDE-"][0]: {values["-BPMSLIDE-"]}')
                    
                #     self.writer.bpm = values["-BPMSLIDE-"]
                #     print(f'self.writer.bpm: {self.writer.bpm}')

                #     # window['-TOPMESSAGE00-'].update("Choose a Control Type.")
                #     # window['-CTRLLIST-'].update(visible=True)
                #     # window['-SELCNTRLTYPEBTN-'].update(visible=True)
                #     # window.refresh()

                if event == '-SELCNTRLTYPEBTN-':
                    #TODO Figure out how to switch the place of things...
                    #Repopulate columns?
                    print()
                    print(f'Window 2 -SELCNTRLTYPEBTN-')
                    #print(f'')
                    miDIMappath = self.dataStream.pathPreface + '\MiDIMap.csv'

                    if os.path(miDIMappath):
                        print('midiMap exists')
                    
                    else:
                        print('No miDiMap')

                    #TODO set up windows to grab the data that we need
                        #Set conditions and then add values...
                    if values['-CTRLLIST-'][0] == 'Modulate':
                        print(f'Modulate')
                        newControlType = 0
                        window['-CTRLLISTCOL-'].set_size(size=(0,0))
                        window['-CTRLLISTCOL-'].update(visible=False)
                        window['-RATECOL-'].update(visible=True)
                        window['-WAVECOL-'].update(visible=True)
                        window['-MINCOL-'].update(visible=True)
                        window['-MAXCOL-'].update(visible=True)
                        window['-TOPMESSAGE00-'].update("Enter modulation values.")
                        window['-CTRLLIST-'].update(visible=False)
                        window['-SELCNTRLTYPEBTN-'].update(visible=False)
                        window['-WAVELABEL-'].update(visible=True)
                        window['-WAVELIST-'].update(visible=True)
                        window['-RATELABEL-'].update(visible=True)
                        window['-RATESLIDE-'].update(visible=True)
                        window['-MINLABEL-'].update(visible=True)
                        window['-MINSLIDE-'].update(visible=True)
                        window['-MAXLABEL-'].update(visible=True)
                        window['-MAXSLIDE-'].update(visible=True)
                        window['-MODDATABTN-'].update(visible=True)
                        window.refresh()
                    elif values['-CTRLLIST-'][0] == 'Arrpegiate':
                        print(f'Arrpegiate')
                    elif values['-CTRLLIST-'][0] == 'Play Note':
                        print(f'Play Note')

                if event == '-MODDATABTN-':
                    print()
                    print(f'Window 2 -MODDATABTN-')
                    newRate = values['-RATESLIDE-']
                    newWaveForm = values['-WAVELIST-']
                    newMin = values['-MINSLIDE-']
                    newMax = values['-MAXSLIDE-']

                    #TODO do a bunch of error checking here...
                    #Ensure min < max
                    

                    self.controlList.append([newRate, newWaveForm, newMin, newMax])
                    #TODO add conditions...

                    

##############     Window2_1          #################
            if window == window2_1:
                #User chooses training or prediction 
                #Currently used for testing
                print()
                print()
                print("Window 2.1")
                #print(self.Test)
                
                if event == sg.WIN_CLOSED or event == 'Exit':
                    window2_1.hide()
                    window1 =self.makeWindow1()   

                if event == "-TRAINBTN-":
                    print()
                    print("-TRAINBTN- ")
                    #setup datastream how we want it for training
                    #dataStream = socketClientUx.GetData(packetSize=self.packetSize, label=label, labelPath=labelPath, getTraining=True, numSensors=numSensors, pathPreface=pathPreface)
                    window2_1.hide()
                    window3 =self.makeWindow3()
                           
                if event == "-PREDICTBTN-":  
                    print() 
                    print("-PREDICTBTN-")
                    window2_1.hide()
                    window3_1 =self.makeWindow3_1()
                
                if event == "-WORDS-":
                    window["-WORDS-"].update(values['-WORDS-'])

 ##############     Window3          #################           
            if window == window3:
                #Training in progress
                print()
                print()
                print("window 3")
                class0 = "baseStationaryC00"   #Class 0 is the reference orientation with no movement
                self.positionPathList = ["class00", "class01", "class02"]

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                
                if event == "GO!":
                    print()
                    print("GO!")
                    #self.goTrain = 1
                    #handPositionIdx = self.numHandPositions #hard coded for now, will be provided by user with GUI
                    sampleCount = 0
                    testCount = 0

                    #Setup dataStream
                    self.dataStream.label = self.handPositionCount
                    self.dataStream.labelPath = self.positionPathList[self.handPositionCount] 
                    self.dataStream.getTraining = True

                    window['GO!'].hide_row() 
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.handPositionCount} in .....3')
                    window.refresh()
                    time.sleep(2)
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.handPositionCount} in .....2')
                    window.refresh()
                    time.sleep(1)
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.handPositionCount} in .....1')
                    window.refresh()
                    time.sleep(1)
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.handPositionCount} in .....GO!')
                    window.refresh()
                    time.sleep(1)

                    print("Start Training")

                    while sampleCount < self.packetLimit:
                        print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for hand position {self.handPositionCount + 1} of {self.numHandPositions} hand positions')
                        self.trainModel()
                        sampleCount += 1
                    sampleCount = 0

                    self.dataStream.labelPath = self.positionPathList[self.handPositionCount] + '_test'  #collect test data to testing the network
                    if self.packetLimit /10 > 1:
                        testIdx = self.packetLimit /10
                    else:
                        testIdx = 1

                    while testCount < testIdx:
                        print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for hand position {self.handPositionCount + 1} of {self.numHandPositions} hand positions')
                        self.trainModel()
                        testCount += 1
                    testCount = 0
                    self.handPositionCount += 1

                    if self.handPositionCount < self.numHandPositions:
                        #handPositionMessage = 'Training Gesture ' + str(self.handPositionCount + 1) + ' of ' + str(self.numHandPositions) +  ' handPositions'
                        # window['-GESTURE-'].update(handPositionMessage)
                        # window.refresh()
                        window.write_event_value("GO!", '') 
                    else:
                        #trainOrientation(basePath, self.positionPathList, packetSize, numSensors, numClasses):
                        self.handPositionCount = 0
                        NeuralNetwork.trainOrientation(self.pathPreface, self.positionPathList, self.packetSize, self.numSensors, self.numHandPositions)

                        window['-GESTURE-'].update(f'Training Complete')
                        window['-CountDown-'].update('')

##############     Window3_1          #################
            if window == window3_1:
                #Predicting
                print()
                print()
                print("window 3_1")

                #set up dataStream
                self.dataStream.packetSize = 1
                self.dataStream.getTraining = False
                self.dataStream.numSensors = self.numSensors
                self.dataStream.pathPreface = self.pathPreface

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == "-GOBTN-":
                    print()
                    print("-GOBTN-")
                    #print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for hand position {self.handPositionCount + 1} of {self.numHandPositions} hand positions')
                    #if stopPredict < 10:
                    prediction = self.predictSample()
                     #   stopPredict += 1
                    #else:
                     #   stopPredict = 0
                      #  window.write_event_value("-STOPBTN-", '')


                    print(f'prediction: {prediction}')
                    if self.writer.ToFEnable == 1 and self.dataStream.ToFByte > 0 and self.dataStream.ToFByte < 128:   #TOF enabled and Valid ToFData
                        self.writer.ToFByte = self.dataStream.ToFByte     #Pass ToF data to midiWriter
                        PredictMessage = "ToF enabled. Detected Gesture " + str(prediction)
                        #self.writer.getPredictions(prediction)
                    elif self.writer.ToFEnable == 1 and self.dataStream.ToFByte == -1:      #TOF enabled and not valid ToF data
                        print(f"TOFByte not set: {self.writer.ToFByte}")
                        PredictMessage = "ToF enabled, but no data available. Detected Gesture " + str(prediction)
                    else:                                                                   #ToF not enabled
                        PredictMessage = "ToF disabled. Detected Gesture " + str(prediction)
                    
                    #self.writer.getPredictions(prediction)

                    window['-GESTURE-'].update(PredictMessage)
                    window['-STOPBTN-'].update(visible=True)
                    window['-GOBTN-'].update(visible=False)
                    window.refresh()
                    if self.stopPredict == 0:
                        window.write_event_value("-GOBTN-", '') 
                    else:
                        window['-STOPBTN-'].update(visible=False)
                        window['-GOBTN-'].update(visible=True)
                        window.refresh()
                        self.stopPredict = 0

                if event == "-STOPBTN-":
                    print()
                    print("-STOPBTN-")
                    window['-STOPBTN-'].update(visible=False)
                    window['-GOBTN-'].update(visible=True)
                    window['-GESTURE-'].update(f'Prediction paused. Hit "GO!" to resume.')
                    window.refresh()
                    #window.write_event_value("-STOPBTN-", '')
                    self.stopPredict = 1

        window.close()

def main():

    testGui = UX()
    testGui.uxLoop()

if __name__ == "__main__": main()