import PySimpleGUI as sg
import socketClientUx
import NeuralNetwork
import oscWriter
import os.path
import time
import struct
import socket
import subprocess
import csv
import shutil
import sys


class UX:

    def __init__(self, *, theme='BluePurple'):
        self.theme = theme
        self.writer = oscWriter.OSCWriter()
        self.packetLimit = 30
        self.packetSize = 1
        self.numSensors = 2
        self.numGestures = 3   #How many gestures trained by the model
        self.pathPreface = "data/test/"
        self.dataTx = 0xFF
        self.trainCountDown = 0 # Counter for training countdown
        self.sampleCount = 0 #counter for the number of samples collected per gesture while training
        self.gestureCount = 0 #counter for the number of gestures collected while training
        self.goTrain = 0
        self.Test = 0 # A variable to test things
        self.windowSizeX = 800
        self.windowSizeY = 400
        self.stopPredict = 0
        self.dataStream = socketClientUx.GetData(packetSize=self.packetSize, numSensors=self.numSensors, pathPreface=self.pathPreface)
        self.IPAddress = ''
        self.SSIDList = []


###############################################################################################
##############                  Control Methods                               #################
###############################################################################################

    class ConductorConnector:

        def __init__(self):
            self.SSID = "TheConductor"
            self.HostIP = ""
            self.PSWD = ""
            self.newSSID = ""
            self.newIP = ""
            self.newPSWD = ""

        def getNetworks(self):
            SSIDList = []
            networks = subprocess.check_output(["netsh", "wlan", "show", "network"])
            networks = networks.decode("ascii")
            #networks = networks.replace("\r,","")
            ls = networks.split('\n')
            ls = ls[4:]

            counter = 0
            while counter < (len(ls)):
                if counter % 5 == 0:
                    #print(ls[counter])
                    if len(ls[counter]) > 9:
                        ls[counter] = ls[counter][9:]
                        print(f'Network {counter}: {ls[counter]}')
                        SSIDList.append(ls[counter])
                counter += 1
            return SSIDList

        def socketConnect(self, ip, ssid):
            print()
            print(f'UX.connnectDevice')
            # dataTx = struct.pack("=B", 0xF0)
            sock = socket.socket()
            connection = 0
            while connection == 0:
                # sock = socket.socket()
                # sock.connect((ip, 80))
                print(f"Connected to server at {ip} at {ssid}")
                connection = 1
            #Test the connection
            
            
            # try:
            #     sock.send(dataTx)
            #     #print("Sent Data")
            # except:
            #     sock.connect((ip, 80))
            #     #print("Socket Reconnected")
            #     sock.send(dataTx)
        #     #TODO Set ESP32 to respond with display when client connects to AP
        #     recvByte = sock.recv(1)

            #     if recvByte == 0xFF:

            #        return 1
            #     else:
            #         return -1
            return 1

        def socketSendStr(self, dataTx, ip, ssid):
            print()
            print(f'UX.connnectDevice')
            print(f"Sending connection info {dataTx}")

            #sock = socket.socket()
            #sock.connect((ip, 80))
            print(f"Connected to server at {ip} on {ssid}")
            print(f"Sending connection info {dataTx}")

            # try:
            #     sock.send(dataTx)
            #     #print("Sent Data")
            # except:
            #     sock.connect((ip, 80))
            #     #print("Socket Reconnected")
            #     sock.send(dataTx)
            #     recvByte = sock.recv(1)

            #     if recvByte == 0xF0:
                     #sock.close()
            #         return 1
            #     else:
                      #sock.close()
            #         return -1
                #     #TODO Have the ESP32 disconnet and reconnect on the new socket

            return 1

        def sendNetworkInfo(self, newSSID, pswd):
            print()
            print(f'sendNetworkInfo')
            if newSSID != '' and pswd != '':
                dataTx = newSSID + "__--__" + pswd
                #TODO Connect to AP network
                    #send connection infos
                if self.socketSendStr(dataTx, self.HostIP, self.SSID) == 1:
                    return 1
                else:
                    return -1

        def logNetwork(self):
            print()
            print(f'logNetwork()')
            networkPath = self.pathPreface + "/networks.csv"
            with open(networkPath, 'w') as csvfile:
                csvWrite = csv.writer(csvfile)
                csvWrite.writerow([self.SSID, self.PSWD])

        #Things to log - Network connections
            # model parameters: numSensors, numGestures, pathPreface, pathList

    def trainModel(self):
        #iterate through all the gestures and collect packetLimit samples of each
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
        
        #CSend all the gestures to neural network
        #NeuralNetwork.trainOrientation(pathPreface, labelPathList, 1, numSensors, self.numGestures)        

    def predictSample(self):
        #writer = oscWriter.OSCWriter()
        self.dataStream.getSample()
        predictionList = self.dataStream.predictSample()
        print(f'Converting gesture to OSC...') 
        self.writer.getPredictions(predictionList[0])
        if self.writer.ToFEnable:
            print(f'Enable Time of Flight Sensor...') 
            self.dataStream.dataTx = 0 #Reset dataTx
            self.dataStream.dataTx = struct.pack("=B", 15)   #Enable ToF sensor
            self.dataStream.extraRxByte = 1
        else:
            print(f'Disable Time of Flight Sensor...') 
            self.dataStream.dataTx = 0 #Reset dataTx
            self.dataStream.dataTx = struct.pack("=B", 255)   #Disable ToF sensor 
            self.dataStream.extraRxByte = 0
        self.dataStream.dataGot = 0   #Reset the dataGot flag for the next sample

        return predictionList[0], self.writer.ToFEnable
        

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

    def makeWindow0(self):
    #Window zero welcome, set up wifi
        layout = [[sg.Text('The Conductor: Window 0: Connect to The Conductor.'), sg.Text(size=(2,1), key='-OUTPUT-')],
                #[sg.Text('Connect to The Conductor.'), sg.Text(size=(5,1), key='-OUTPUT-')], 
                [sg.pin(sg.Column([[sg.Text('Start up The Conductor and connect your PC to the SSID displayed on the screen.', key='-TOPMESSAGE-'), sg.Text(size=(2,1))]]))],
                [sg.pin(sg.Column([[sg.Text('Then enter IP address on the screen and click "Connect."', key='-TOPMESSAGE01-'), sg.Text(size=(2,1))]]))],
                [sg.pin(sg.Column([[sg.Input('IP Address', key="-IPIN-", visible=True)]]), shrink=False)],
                [sg.pin(sg.Column([[sg.Input('IP Address', key="-IPNEW-", visible=False)]]), shrink=False)],
                [sg.pin(sg.Column([[sg.Button('Connect', key='-STNCNTEBTN-', visible=False)]], pad=(0,0)), shrink=False)],
                [sg.pin(sg.Column([[sg.Listbox(self.SSIDList, size=(15, 4), key="-SSIDIN-", expand_y=True, enable_events=True, visible=False)]]), shrink=False)],
                #[sg.pin(sg.Column([[sg.Input('Network SSID', key="-SSIDIN-", visible=False)]]), shrink=False)],
                [sg.pin(sg.Column([[sg.Input('Password', key="-PSWDIN-", visible=False)]]), shrink=False)],
                [sg.pin(sg.Column([[sg.Button('Connect', key='-APCNTEBTN-', visible=True)]], pad=(0,0)), shrink=False)],
                [sg.pin(sg.Column([[sg.Button('Continue', key='-CONTBTN-', visible=False)]], pad=(0,0)), shrink=False)],
                [sg.pin(sg.Column([[sg.Button('Reconnect', key='-RECNTBTN-', visible=False)]], pad=(0,0)), shrink=False)],
                #[sg.pin(sg.Column([[sg.Text('Upload a model'), sg.Text(size=(2,1), key='-UPLOADMODEL-'), sg.Input(), sg.FileBrowse(), sg.Button('Ok', key='-UPLOADMODELBTN-')]]))],
                #[sg.Text(''), sg.Text(size=(2,1), key='-OUTPUT-'), sg.Button('Ok', key='-APCONNECTBTN-')],
                [sg.pin(sg.Column([[sg.Text('', visible=True, key='-MESSAGE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)]   
                ]
        return sg.Window('THE CONDUCTOR: Step 0', layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
    

    
    def makeWindow1(self, modelMessage):
    #Window one welcome, load / create model
        layout = [[sg.Text('The Conductor: Window 1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                [sg.Text('Upload an existing neural network model or create a new one.'), sg.Text(size=(5,1), key='-OUTPUT-')], 
                [sg.pin(sg.Column([[sg.Text(modelMessage), sg.Text(size=(2,1), key='-MODELMESSAGE-'), sg.Button('Ok', key='-MODELMESAGEBTN-')]]))],
                [sg.pin(sg.Column([[sg.Text('Upload a model'), sg.Text(size=(2,1), key='-UPLOADMODEL-'), sg.Input(), sg.FileBrowse(), sg.Button('Upload', key='-UPLOADMODELBTN-')]]))],
                [sg.Text('Create a New Model'), sg.Text(size=(2,1), key='-OUTPUT-'), sg.Button('Ok', key='-CREATE-')],
                [sg.pin(sg.Column([[sg.Text('', visible=True, key='-MESSAGE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                #[sg.pin(sg.Column([[sg.Button('-MODELOK-', visible=False)]], pad=(0,0)), shrink=False)]
                        #sg.Text('Not a valid model file. Please try again.', size=(2,1), key='-invalidModel-', visible=True, pad=(0,0)), sg.Text(size=(2,1))]
                ]

        return sg.Window('THE CONDUCTOR: Step 1', layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
    

    def makeWindow2_1(self):
        #Window3 Training or prediction select
        layout = [[sg.Text('The Conductor: Window 2.1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                  [sg.pin(sg.Column([[sg.Text('Train Model'), sg.Text(size=(2,1), key='-TRAIN-'), sg.Button('Train', key='-TRAINBTN-')]]))],
                  [sg.pin(sg.Column([[sg.Text('Predict gestures'), sg.Text(size=(2,1), key='-PREDICT-'), sg.Button('Predict', key='-PREDICTBTN-')]]))],
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
       
        ##Methods to collect run time data required for the GUI
        modelPath = self.pathPreface + 'model.model'
        print(f'modelPath: {modelPath}')
        modelMessage = self.makeModelFileMessage(modelPath)

        sg.theme(self.theme)
        connector = self.ConductorConnector()
        #connector.getNetworks()

        # Set all windows to Noe except window 1 to start
        window0 = self.makeWindow0()
        #window1 = self.makeWindow1(modelMessage)
        window1 = None
        window2_1 = None
        window3 = None
        window3_1 = None

        while True:  # Event Loop
            window, event, values = sg.read_all_windows()
            print(f'event: {event}')
            print(f'values: {values}')


##############     Window0          #################
            #events for window1 (welcome, load / create model)
            #TODO Add option to choose from previous connections
            #Add option to select from detected networks
            if window == window0:

                print()
                print('Window 0')

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == "-APCNTEBTN-":
                    print()
                    print(f'Window 0 -APCNTEBTN-')
                    #Get and validate input
                    if values["-IPIN-"] != "IP Address":
                        #TODO better validation
                            #Check pattern for IP, Get list of available networks aand let user check
                        #connector.SSID = values["-SSIDIN-"]
                        connector.newIP = values["-IPIN-"]
                        #connector.PSWD = "NoneShallPass"
                        
                        window['-MESSAGE-'].update(f'Connecting to The Conductor at IP Address {connector.HostIP}...')
                        window.refresh()
                        if connector.socketConnect(connector.newIP, connector.SSID) == 1:
                            #if self.dataStream.promptServer(connector.newIP, connector.SSID) == 1:   #New version with unified socket connection
                            connector.HostIP = connector.newIP
                            connector.newIP = ''
                            print(f'IP: {connector.HostIP}, SSID: {connector.SSID}')
                            #Get Network data from the air
                            self.SSIDList = connector.getNetworks()
                            window['-TOPMESSAGE-'].update(f'Conductor Connected!  IP Address: {connector.HostIP}')
                            window['-TOPMESSAGE01-'].update(f'To use this network click continue. To connect to another network enter the network info below and click Reconect')
                            #window['-TOPMESSAGE01-'].update(visible=False)
                            window['-IPIN-'].update(visible=False)
                            window['-SSIDIN-'].update(self.SSIDList)
                            window['-SSIDIN-'].update(visible=True)
                            window['-PSWDIN-'].update(visible=True)
                            window['-RECNTBTN-'].update(visible=True)
                            window['-CONTBTN-'].update(visible=True)
                            window['-APCNTEBTN-'].update(visible=False)
                            window['-MESSAGE-'].update(visible=False)
                            window.refresh()  

                if event == '-CONTBTN-':
                    print()
                    print(f'Window 0 -CONTBTN-')
                    window0.hide()
                    window1 = self.makeWindow1(modelMessage)
                    
                if event == '-RECNTBTN-':
                    print()
                    print(f'Window 0 -RECNTBTN-')
                    connector.newSSID = values["-SSIDIN-"][0]
                    connector.newPSWD = values["-PSWDIN-"]
                    window['-SSIDIN-'].update(visible=False)
                    window['-PSWDIN-'].update(visible=False)
                    window['-RECNTBTN-'].update(visible=False)
                    window['-CONTBTN-'].update(visible=False)
                    window['-APCNTEBTN-'].update(visible=False)
                    window.refresh()

                    if connector.newSSID != "Network SSID" and connector.newPSWD != "Password":
                        #TODO better validation
                            #Check pattern for IP, Get list of available networks aand let user check
                        #connector.SSID = values["-SSIDIN-"]
                        #connector.PSWD = "NoneShallPass"
                        print(f'IP: {connector.HostIP}')
                        window['-TOPMESSAGE-'].update(f'Connecting Conductor to Network {connector.newSSID}. Please reconnect your PC to this network.')
                        window['-TOPMESSAGE01-'].update(f"Check The Conductor's display for connection information, and enter the new IP Address below.")
                        window['-IPNEW-'].update(visible=True)
                        window['-STNCNTEBTN-'].update(visible=True)
                        window.refresh()
                        if connector.sendNetworkInfo(connector.newSSID, connector.newPSWD) == 1:
                            window['-MESSAGE-'].update(visible=True)
                            window['-MESSAGE-'].update(f"Sent Network Information")

                if event == '-STNCNTEBTN-':
                    print()
                    print(f'Window 0 -IPNEW-')
                    if window['-IPNEW-'] != 'IP Address':
                        #TODO add better validation
                        connector.newIP = values['-IPNEW-']
                        window['-TOPMESSAGE-'].update(f'Connecting to The Conductor at {connector.newIP} on {connector.newSSID}.')
                        window['-TOPMESSAGE01-'].update(visible=False)
                        if connector.socketConnect(connector.newIP, connector.newSSID) == 1:
                            connector.HostIP = connector.newIP
                            connector.newIP = ''
                            connector.SSID = connector.newSSID
                            connector.newSSID = ''
                            window['-MESSAGE-'].update(f"Connected to server at {connector.HostIP} on {connector.SSID}")
                            
                            connector.logNetwork()
                            
                            time.sleep(5)
                            window1 = self.makeWindow1(modelMessage)
                            window0.hide()
           
##############     Window1          #################            
            if window == window1:
                print()
                print('Window 1')
                modelOk = -1

                #window['-invalidModel-'].update(visible=False)
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == '-UPLOADMODELBTN-':
                    print()
                    print(f'Window 1 -UPLOADMODEL-')
                    window['-MESSAGE-'].update('Sorry feature not enabled yet.')

                    #TODO backup existing model file if it exists and save model to pathPreface/model.model
                    # if modelOk == -1:
                    #     window['-MESSAGE-'].update('')

                    # else:
                    #     modelPath = self.pathPreface + 'model.model'

                    #     #Save model to pathPreface
                    #     shutil.copy(values[0], modelPath)
                    #     try:
                    #         model.load(modelPath)
                    #     except:
                    #         window['-MESSAGE-'].update('Bad copy')
                    #         print(f'BadCopy')

                if event == '-MODELMESAGEBTN-':
                    print()
                    print(f'Window 1 -MODELMESAGEBTN-')
                    # model = NeuralNetwork.Model()                                
                    # try:
                    #     model.load(modelPath)
                    # except:
                    #     window['-MESSAGE-'].update('Not a valid model file. Please try again.')
                    #     print(f'Invalid model')
                    #     modelOk = 0

                    # if modelOk == -1:
                    modelOk = 1
                    window1.hide()
                    window2_1 = self.makeWindow2_1()

                if event == '-CREATE-':
                    print()
                    print(f'Window 1 -CREATE-')
                    print(f'Value: {values[0]}')
                    window1.hide()
                    window2_1 = self.makeWindow2_1()

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
                pathList = ["class00", "class01", "class02"]

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                
                if event == "GO!":
                    print()
                    print("GO!")
                    #self.goTrain = 1
                    #gestureIdx = self.numGestures #hard coded for now, will be provided by user with GUI
                    sampleCount = 0
                    testCount = 0

                    #Setup dataStream
                    self.dataStream.label = self.gestureCount
                    self.dataStream.packetSize = self.packetSize
                    self.dataStream.labelPath = pathList[self.gestureCount] 
                    self.dataStream.getTraining = True
                    self.dataStream.numSensors = self.numSensors
                    self.dataStream.pathPreface = self.pathPreface

                    window['GO!'].hide_row() 
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.gestureCount} in .....3')
                    window.refresh()
                    time.sleep(2)
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.gestureCount} in .....2')
                    window.refresh()
                    time.sleep(1)
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.gestureCount} in .....1')
                    window.refresh()
                    time.sleep(1)
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.gestureCount} in .....GO!')
                    window.refresh()
                    time.sleep(1)

                    print("Start Training")

                    while sampleCount < self.packetLimit:
                        print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for gesture {self.gestureCount + 1} of {self.numGestures} gestures')
                        self.trainModel()
                        sampleCount += 1
                    sampleCount = 0

                    self.dataStream.labelPath = pathList[self.gestureCount] + '_test'  #collect test data to testing the network
                    if self.packetLimit /10 > 1:
                        testIdx = self.packetLimit /10
                    else:
                        testIdx = 1

                    while testCount < testIdx:
                        print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for gesture {self.gestureCount + 1} of {self.numGestures} gestures')
                        self.trainModel()
                        testCount += 1
                    testCount = 0
                    self.gestureCount += 1

                    if self.gestureCount < self.numGestures:
                        #gestureMessage = 'Training Gesture ' + str(self.gestureCount + 1) + ' of ' + str(self.numGestures) +  ' gestures'
                        # window['-GESTURE-'].update(gestureMessage)
                        # window.refresh()
                        window.write_event_value("GO!", '') 
                    else:
                        #trainOrientation(basePath, pathList, packetSize, numSensors, numClasses):
                        self.gestureCount = 0
                        NeuralNetwork.trainOrientation(self.pathPreface, pathList, self.packetSize, self.numSensors, self.numGestures)

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
                    #print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for gesture {self.gestureCount + 1} of {self.numGestures} gestures')
                    prediction, ToFEnable = self.predictSample()
                    if ToFEnable:
                        PredictMessage = "ToF enabled. Detected Gesture " + str(prediction)
                    else:
                        PredictMessage = "ToF disabled. Detected Gesture " + str(prediction)
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