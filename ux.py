import PySimpleGUI as sg
import socketClientUx
import NeuralNetwork
import oscWriter
import os.path
import time
import struct
import socket
import shutil
import sys


class UX:

    def __init__(self, *, theme='BluePurple'):
        self.theme = theme
        self.writer = oscWriter.OSCWriter()
        self.packetLimit = 3
        self.packetSize = 1
        self.numSensors = 2
        self.numGestures = 1   #How many gestures trained by the model
        self.pathPreface = "data/test/"
        self.dataTx = 0xFF
        self.trainCountDown = 0 # Counter for training countdown
        self.sampleCount = 0 #counter for the number of samples collected per gesture while training
        self.gestureCount = 0 #counter for the number of gestures collected while training
        self.goTrain = 0
        self.Test = 0 # A variable to test things
        self.windowSizeX = 750
        self.windowSizeY = 300
        self.stopPredict = 0
        self.dataStream = socketClientUx.GetData(packetSize=self.packetSize, numSensors=self.numSensors, pathPreface=self.pathPreface)
        self.IPAddress = ''


###############################################################################################
##############                  Control Methods                               #################
###############################################################################################

    class ConductorConnector:

        def __init__(self):
            self.SSID = ""
            self.HostIP = ""
            self.PSWD = ""


        def connectAP(self):
            print()
            print(f'UX.connnectDevice')
            dataTx = struct.pack("=B", 0xF0)
            sock = socket.socket()
            sock.connect((self.HostIP, 80))
            print()
            print("Connected to server")
            try:
                sock.send(dataTx)
                #print("Sent Data")
            except:
                sock.connect((self.HostIP, 80))
                #print("Socket Reconnected")
                sock.send(dataTx)
                #TODO Set ESP32 to respond with display when client connects to AP
                recvByte = sock.recv(1)

                if recvByte == 0xFF:
                    return 1
                else:
                    return -1
                
        def sendNetwork(self, newSSID, pswd):
            if newSSID != '' and pswd != '':
                dataTx = newSSID + "__--__" + pswd
                
                sock = socket.socket()
                sock.connect((self.SSID, 80))
                print(f"Connected to server on {self.SSID}")
                try:
                    sock.send(dataTx)
                    #print("Sent Data")
                except:
                    sock.connect((self.SSID, 80))
                    #print("Socket Reconnected")
                    sock.send(dataTx)
                    #TODO Have the ESP32 disconnet and reconnect on the new socket

        # def 
        #         sock.close()
        #         connected = 0
        #         while connected == 0:
        #            time.sleep(5)
        #            sock.connect((newSSID, 80))
        #            connected = 1
                   
        #         print()
        #         print(f"Connected to server on {newSSID}")
        #         self.SSID = newSSID
        #         self.PSWD = pswd

                
                    
            #Connect to ESP32 AP network

            #Get network details from user or file

            #Send network detials to ESP32

            #Reconnect to ESP32 on new network

            #Log network details
    
    
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
        #NeuralNetwork.trainOrientation(pathPreface, labelPathList, 1, numSensors, gestureIdx)        

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
        

    def makeModelFileMessage(self, pathPreface):
        modelPath = pathPreface + 'model.model'
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
        layout = [[sg.Text('The Conductor: Window 0'), sg.Text(size=(2,1), key='-OUTPUT-')],
                [sg.Text('Connect to The Conductor.'), sg.Text(size=(5,1), key='-OUTPUT-')], 
                [sg.pin(sg.Column([[sg.Text('Start up The Conductor and connect your PC to the the SSID and IP Address displayed on the screen.'), sg.Text(size=(2,1), key='-TOPMESSAGE-')]]))],
                [sg.pin(sg.Column([[sg.Text('Enter same IP address below and click "Connect."'), sg.Text(size=(2,1), key='-TOPMESSAGE01-')]]))],
                [sg.pin(sg.Column([[sg.Input('IP Address', key="-IPIN-", visible=True)]]), shrink=False)],
                [sg.pin(sg.Column([[sg.Input('IP Address', key="-IPNEW-", visible=False)]]), shrink=False)],
                [sg.pin(sg.Column([[sg.Input('Network SSID', key="-SSIDIN-", visible=False)]]), shrink=False)],
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
                [sg.pin(sg.Column([[sg.Text('Upload an existing neural network model or create a new one.'), sg.Text(size=(2,1), key='-MODELMESSAGE-'), sg.Button('Ok', key='-MODELMESAGEBTN-')]]))],
                [sg.pin(sg.Column([[sg.Text('Upload a model'), sg.Text(size=(2,1), key='-UPLOADMODEL-'), sg.Input(), sg.FileBrowse(), sg.Button('Ok', key='-UPLOADMODELBTN-')]]))],
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
        ##Methods to collect run time data required for the GUI
        modelMessage = self.makeModelFileMessage(self.pathPreface)

        sg.theme(self.theme)
        connector = self.ConductorConnector()

        # Set all windows to Noe except window 1 to start
        window0 = self.makeWindow0()
        #window1 = self.makeWindow1(modelMessage)
        window1 = 0
        window2_1 = None
        window3 = None
        window3_1 = None

        while True:  # Event Loop
            window, event, values = sg.read_all_windows()
            print(f'event: {event}')
            print(f'values: {values}')


##############     Window0          #################
            #events for window1 (welcome, load / create model)
            if window == window0:
                print()
                print('Window 0')

                if event == "-APCNTEBTN-":
                    print()
                    print(f'Window 0 -APCNTEBTN-')
                    #Get and validate input
                    if values["-IPIN-"] != "IP Address":
                        #TODO better validation
                            #Check pattern for IP, Get list of available networks aand let user check
                        #connector.SSID = values["-SSIDIN-"]
                        connector.HostIP = values["-IPIN-"]
                        #connector.PSWD = "NoneShallPass"
                        print(f'IP: {connector.HostIP}')
                        window['-MESSAGE-'].update(f'Connecting to The Conductor at IP Address {connector.HostIP}...')
                        window.refresh()
                        if connector.connectAP() > 0:
                            #Get Network data from User
                            window['-TOPMESSAGE-'].update(f'Conductor Connected!  IP Address: {connector.HostIP}')
                            window['-TOPMESSAGE01-'].update(f'To use this network click continue. To connect to another network enter the network info below and click OK')
                            #window['-TOPMESSAGE01-'].update(visible=False)
                            window['-SSIDIN-'].update(visible=True)
                            window['-PSWDIN-'].update(visible=True)
                            window['-RECNTBTN-'].update(visible=True)
                            window['-CONTBTN-'].update(visible=True)
                            window['-APCNTEBTN-'].update(visible=False)
                            window.refresh()  

                if event == '-CONTBTN-':
                    print()
                    print(f'Window 0 -CONTBTN-')

                
                if event == '-RECNTBTN-':
                    print()
                    print(f'Window 0 -RECNTBTN-')
                    newSSID = values["-SSIDIN-"]
                    pswd = values["-PSWDIN-"]
                    window['-SSIDIN-'].update(visible=False)
                    window['-PSWDIN-'].update(visible=False)
                    window['-RECNTBTN-'].update(visible=False)
                    window['-CONTBTN-'].update(visible=False)
                    window['-APCNTEBTN-'].update(visible=False)
                    window.refresh()

                    if newSSID != "Network SSID" and pswd != "Password":
                        #TODO better validation
                            #Check pattern for IP, Get list of available networks aand let user check
                        #connector.SSID = values["-SSIDIN-"]
                        newSSID = values["-SSIDIN-"]
                        #connector.PSWD = "NoneShallPass"
                        print(f'IP: {connector.HostIP}')
                        window['-TOPMESSAGE-'].update(f'Connecting Conductor to Network {newSSID}.')
                        window['-TOPMESSAGE01-'].update(f"Check The Conductor's display for connection information, and enter the displayed IP Address below.")
                        window['-IPIN-'].update(visible=True)
                        window.refresh()
                        self.sendNetwork(newSSID, pswd)

                if event == '-IPNEW-':
                    print()
                    print(f'Window 0 -IPNEW-')
                    if window['-IPNEW-'] != 'IP Address':
                        #TODO add better validation
                        self.IPAddress = values['IPNEW']

                 

            
##############     Window0          #################            
            if window == window1:
                print()
                print('Window 1')
                modelPath = self.pathPreface + 'model.model'
                print(f'modelPath: {modelPath}')
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
                print(self.Test)
                
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
                pathList = [class0]

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                
                if event == "GO!":
                    print()
                    print("GO!")
                    #self.goTrain = 1
                    gestureIdx = 5 #hard coded for now, will be provided by user with GUI
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
                        print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for gesture {self.gestureCount + 1} of {gestureIdx} gestures')
                        self.trainModel()
                        sampleCount += 1
                    sampleCount = 0

                    self.dataStream.labelPath = pathList[self.gestureCount] + '_test'  #collect test data to testing the network
                    if self.packetLimit /10 > 1:
                        testIdx = self.packetLimit /10
                    else:
                        testIdx = 1

                    while testCount < testIdx:
                        print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for gesture {self.gestureCount + 1} of {gestureIdx} gestures')
                        self.trainModel()
                        testCount += 1
                    testCount = 0
                    self.gestureCount += 1

                    if self.gestureCount < gestureIdx:
                        #gestureMessage = 'Training Gesture ' + str(self.gestureCount + 1) + ' of ' + str(gestureIdx) +  ' gestures'
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
                    #print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for gesture {self.gestureCount + 1} of {gestureIdx} gestures')
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