import PySimpleGUI as sg
import socketClientUx
import NeuralNetwork
import oscWriter
import os.path
import time
import shutil
import sys

class UX:

    def __init__(self, *, theme='BluePurple'):
        self.theme = theme
        #self.writer = oscWriter.OSCWriter()
        #self.dataStream = socketClientUx.GetData(packetSize=1, label=0, getTraining=False, numSensors=2, packetLimit=1000, pathPreface="data/Orientation01/", writer=self.writer)
        self.packetLimit = 3
        self.packetSize = 1
        self.numSensors = 2
        self.pathPreface = "data/test/"
        self.dataTx = 0xFF
        self.trainCountDown = 0 # Counter for training countdown
        self.sampleCount = 0 #counter for the number of samples collected per gesture while training
        self.gestureCount = 0 #counter for the number of gestures collected while training
        self.goTrain = 0
        self.Test = 0 # A variable to test things
        self.windowSizeX = 750
        self.windowSizeY = 300


###############################################################################################
##############                  Control Methods                               #################
###############################################################################################

    def trainModel(self, numSensors, pathPreface, *, label=0, labelPath=''):
        #iterate through all the gestures and collect packetLimit samples of each
        #Called in window 2 and 2.1 where user provides data to set up model and data
        #Switches to window 3 to output data 

            print(f'ux.trainModel')
            dataStream = socketClientUx.GetData(packetSize=self.packetSize, label=label, labelPath=labelPath, getTraining=True, numSensors=numSensors, pathPreface=pathPreface)
            dataStream.getSample()
            dataStream.prepTraining()
        
        #CSend all the gestures to neural network
        #NeuralNetwork.trainOrientation(pathPreface, labelPathList, 1, numSensors, gestureIdx)
            

    def predictSample(self, numSensors, pathPreface):
        dataStream = socketClientUx.GetData(packetSize=1, label=0, getTraining=False, numSensors=numSensors, packetLimit=1000, pathPreface=pathPreface)
        writer = oscWriter.OSCWriter()
        dataStream.getSample()
        predictionList = dataStream.predictSample()
        writer.getPredictions(predictionList[0])

        #Must get dataTx out of this - and write it into getSample()
        #Code from old socketClient below
        # if writer.ToFEnable:
        #     print(f'Enable Time of Flight Sensor...') 
        #     self.dataTx = 0 #Reset dataTx
        #     self.dataTx = struct.pack("=B", 15)   #Enable ToF sensor
        #     self.extraRxByte = 1
        # else:
        #     print(f'Disable Time of Flight Sensor...') 
        #     self.dataTx = 0 #Reset dataTx
        #     self.dataTx = struct.pack("=B", 255)   #Disable ToF sensor 
        #     self.extraRxByte = 0
        # self.dataGot = 0   #Reset the dataGot flag for the next sample

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

    def makeWindow1(self, modelMessage):
    #Window one welcome, load / create model
        layout = [[sg.Text('The Conductor: Window 1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                [sg.Text('Upload an existing neural network model or create a new one.'), sg.Text(size=(5,1), key='-OUTPUT-')], 
                [sg.pin(sg.Column([[sg.Text(modelMessage), sg.Text(size=(2,1), key='-MODELMESSAGE-'), sg.Button('Ok', key='-MODELMESAGEBTN-')]]))],
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
                  [sg.Text('Train model'), sg.Text(size=(2,1), key='-TRAIN-'), sg.Button('Train')],
                  [sg.pin(sg.Column([[sg.Text('Predict gestures with model'), sg.Text(size=(2,1), key='-PREDICT-'), sg.Button('Predict', key='-PREDICTBTN-')]]))],
                  [sg.pin(sg.Column([[sg.Text('', visible=True, key='-WORDS-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
        ]
        return sg.Window('THE CONDUCTOR: Step 2.1', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
    

    def makeWindow3(self):
        #Window3 Training 
        layout = [[sg.Text('The Conductor: Window 3'), sg.Text(size=(2,1), key='-OUTPUT-')],
                  [sg.pin(sg.Column([[sg.Text("Hi I'm GESTURE", visible=True, key='-GESTURE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                  [sg.pin(sg.Column([[sg.Text('', visible=True, key='-CountDown-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                  [sg.Button('GO!')]
        ]
        return sg.Window('THE CONDUCTOR: Step 3', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)

###############################################################################################
##############                  UX LOOP                                       #################
###############################################################################################

    def uxLoop(self):
        ##Methods to collect run time data required for the GUI
        modelMessage = self.makeModelFileMessage(self.pathPreface)

        sg.theme(self.theme)

        # Set all windows to Noe except window 1 to start
        window1 = self.makeWindow1(modelMessage)
        window2_1 = None
        window3 = None

        while True:  # Event Loop
            window, event, values = sg.read_all_windows()
            print(f'event: {event}')
            print(f'values: {values}')

            #events for window1 (welcome, load / create model)
            if window == window1:
                print()
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
                        
                    # increment the filename to avoid overwriting model (update self.modelFileName)

                    # save the file to pathPreface/model

                    #Go to window2

                if event == '-CREATE-':
                    print()
                    print(f'Window 1 -CREATE-')
                    print(f'Value: {values[0]}')
                    window1.hide()
                    window2_1 = self.makeWindow2_1()

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

                if event == "Train":
                    print()
                    window2_1.hide()
                    window3 =self.makeWindow3()
                    print("Train pushed")
                
                if event == "-PREDICTBTN-":  
                    print() 
                    print("Predict Pushed")
        
                    predictSample = 0
                    print(f'values.keys(): {values.keys()}')
                    keys = list(values.keys())
                    print(f'keys: {keys}')
                    if len(keys) > 0 and keys[0] == '-PREDICTBTN-':
                        window['-WORDS-'].update(f'{values["-PREDICTBTN-"]}')
                        print(f'values["-PREDICTBTN-": {values["-PREDICTBTN-"]}')
                        time.sleep(5)
                    while predictSample < 10:
                        print(f"Hi Mom! {predictSample}, from {self.gestureCount}")
                        predictSample += 1
                    
                    if self.gestureCount < 4:
                        gestureMessage = str(self.gestureCount)
                        #window['-WORDS-'].update(f'Completed gesture {self.gestureCount}')
                        window.write_event_value("-PREDICTBTN-", gestureMessage)
                        self.gestureCount += 1

                    else:
                        self.gestureCount = 0
                        window['-WORDS-'].update(f'Completed gestures')
                
                if event == "-WORDS-":
                    window["-WORDS-"].update(values['-WORDS-'])
            
            if window == window3:
                #Training in progress
                print()
                print()
                print("window 3")
                class0 = "baseStationaryC00"   #Class 0 is the reference orientation with no movement
                pathList = [class0]

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

#window.write_event_value("Predict", '')
                
                if event == "GO!":
                    print()
                    print("GO!")
                    #self.goTrain = 1
                    gestureIdx = 5 #hard coded for now, will be provided by user with GUI
                    sampleCount = 0
                    testCount = 0
                    window['GO!'].hide_row() 
                    window['-GESTURE-'].update(f'Get ready to train Gesture {self.gestureCount}.')
                    time.sleep(5)
                    print("Start Training")

                    while sampleCount < self.packetLimit:
                        print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for gesture {self.gestureCount + 1} of {gestureIdx} gestures')
                        self.trainModel(self.numSensors, self.pathPreface, label=0, labelPath=pathList[0])
                        sampleCount += 1
                    sampleCount = 0
                    while testCount < self.packetLimit /10:
                        print(f'Collected sample {sampleCount + 1} of {self.packetLimit} samples for gesture {self.gestureCount + 1} of {gestureIdx} gestures')
                        self.trainModel(self.numSensors, self.pathPreface, label=0, labelPath=(pathList[0] + '_test'))
                        testCount += 1
                    testCount = 0
                    self.gestureCount += 1

                    if self.gestureCount < gestureIdx:
                        gestureMessage = 'Training Gesture ' + str(self.gestureCount + 1) + ' of ' + str(gestureIdx) +  ' gestures'
                        window.write_event_value('-GESTURE-', gestureMessage)
                        window.write_event_value("GO!", '') 
                    else:
                        #trainOrientation(basePath, pathList, packetSize, numSensors, numClasses):
                        self.gestureCount = 0
                        NeuralNetwork.trainOrientation(self.pathPreface, pathList, 1, self.numSensors, 1)

                        window['-GESTURE-'].update(f'Training Complete')
                        window['-CountDown-'].update('')

        window.close()

def main():

    testGui = UX()
    testGui.uxLoop()

if __name__ == "__main__": main()