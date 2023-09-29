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
        self.packetLimit = 10
        self.packetSize = 1
        self.numSensors = 2
        self.pathPreface = "data/test/"
        self.dataTx = 0xFF
        self.trainCountDown = 0 # Counter for training countdown
        self.sampleCount = 0 #counter for the number of samples collected per gesture while training
        self.gestureCount = 0 #counter for the number of gestures collected while training
        self.goTrain = 0

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

    def makeWindow1(self):
    #Window one welcome, load / create model
        layout = [[sg.Text('The Conductor: Window 1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                [sg.Text('Upload an existing neural network model or create a new one.'), sg.Text(size=(5,1), key='-OUTPUT-')], 
                [sg.Text('Upload a Model'), sg.Text(size=(2,1), key='-OUTPUT-'), sg.Input(), sg.FileBrowse(), sg.Button('Ok')],
                [sg.Text('Create a Model'), sg.Text(size=(2,1), key='-OUTPUT-'), sg.Button('Create')],
                [sg.pin(sg.Column([[sg.Text('', visible=True, key='-invalidModel-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)]
                    #sg.Text('Not a valid model file. Please try again.', size=(2,1), key='-invalidModel-', visible=True, pad=(0,0)), sg.Text(size=(2,1))]
                ]

        return sg.Window('THE CONDUCTOR: Step 1', layout, finalize=True)
    

    def makeWindow2_1(self):
        #Window3 Training or prediction select
        layout = [[sg.Text('The Conductor: Window 2.1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                  [sg.Text('Train model'), sg.Text(size=(2,1), key='-TRAIN-'), sg.Button('Train')],
                  [sg.Text('Predict gestures with model'), sg.Text(size=(2,1), key='-PREDICT-'), sg.Button('Predict')],
        ]
        return sg.Window('THE CONDUCTOR: Step 2.1', layout, finalize=True)
    

    def makeWindow3(self):
        #Window3 Training 
        layout = [[sg.Text('The Conductor: Window 3'), sg.Text(size=(2,1), key='-OUTPUT-')],
                  [sg.pin(sg.Column([[sg.Text('', visible=True, key='-Gesture-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                  [sg.pin(sg.Column([[sg.Text('', visible=True, key='-CountDown-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
                  [sg.Button('GO!')]
        ]
        return sg.Window('THE CONDUCTOR: Step 3', layout, finalize=True)

    def uxLoop(self):
        sg.theme(self.theme)

        # Set all windows to Noe except window 1 to start
        window1 = self.makeWindow1()
        window2_1 = None
        window3 = None

        while True:  # Event Loop
            window, event, values = sg.read_all_windows()
            print(f'event: {event}')
            print(f'values: {values}')

            #events for window1 (welcome, load / create model)
            if window == window1:
                #window['-invalidModel-'].update(visible=False)
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == 'Ok':
                    model = NeuralNetwork.Model()
                    modelOk = -1
                    #window['-invalidModel-'].hide_row()
                    print()
                    print(f'Model Path: {values[0]}')
                    # Check that the path has a valid model file
                    try:
                        model.load(values[0])
                    except:
                        window['-invalidModel-'].update('Not a valid model file. Please try again.')
                        print(f'Invalid model')
                        modelOk = 0

                    if modelOk == -1:
                        window['-invalidModel-'].update('')

                    modelPath = self.pathPreface + 'model.model'

                    #Save model to pathPreface
                    shutil.copy(values[0], modelPath)
                    try:
                        model.load(modelPath)
                    except:
                        window['-invalidModel-'].update('Bad copy')
                        print(f'BadCopy')

                    # see if there is a model in pathPreface
                    if os.path.exists(self.pathPreface + 'model.model'):
                        # figure out a way to elegantly make a new model
                        print('path')
                        
                    # increment the filename to avoid overwriting model (update self.modelFileName)

                    # save the file to pathPreface/model

                    #Go to window2
                    window1.hide()
                    window2_1 = self.makeWindow2_1()

                if event == 'Create':
                    print()
                    print(f'Value: {values[0]}')
                    window1.hide()
                    window2 = self.makeWindow2_1()

            if window == window2_1:
                print("Window 2.1")
                if event == sg.WIN_CLOSED or event == 'Exit':
                    window2_1.hide()
                    window1 =self.makeWindow1()   

                if event == "Train":
                    window2_1.hide()
                    window3 =self.makeWindow3()
            
            if window == window3:
                print("window 3")
                class0 = "baseStationaryC00"   #Class 0 is the reference orientation with no movement
                pathList = [class0]

                if event == sg.WIN_CLOSED or event == 'Exit':
                    window3.hide()
                    window2_1 =self.makeWindow2_1() 

                if event == "GO!":
                    #self.goTrain = 1
                    gestureIdx = 1 #hard coded for now, will be provided by user with GUI
                    sampleCount = 0
                    testCount = 0
                    window['GO!'].hide_row() 
                    window['-Gesture-'].update(f'Get ready to train Gesture {self.gestureCount}.')
                    time.sleep(1)
                    print("Start Training")

                    for i in range(gestureIdx):
                        while sampleCount < self.packetLimit:
                            print(f'Collected sample {sampleCount} of {self.packetLimit} samples for gesture {i} of {gestureIdx} gestures')
                            self.trainModel(self.numSensors, self.pathPreface, label=0, labelPath=pathList[0])
                            sampleCount += 1
                        sampleCount = 0
                        while testCount < self.packetLimit /10:
                            print(f'Collected sample {sampleCount} of {self.packetLimit} samples for gesture {i} of {gestureIdx} gestures')
                            self.trainModel(self.numSensors, self.pathPreface, label=0, labelPath=(pathList[0] + '_test'))
                            testCount += 1
                        testCount = 0
                        
                    #trainOrientation(basePath, pathList, packetSize, numSensors, numClasses):
                    NeuralNetwork.trainOrientation(self.pathPreface, pathList, 1, self.numSensors, 1)
                    
                    window['-Gesture-'].update(f'Training Complete')
                    window['-CountDown-'].update('')

        window.close()

def main():

    testGui = UX()
    testGui.uxLoop()

if __name__ == "__main__": main()