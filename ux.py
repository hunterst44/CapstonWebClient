import PySimpleGUI as sg
import socketClientUx
import NeuralNetwork
import oscWriter
import os.path
import sys

class UX:

    def __init__(self, *, theme='BluePurple'):
        self.theme = theme
        #self.writer = oscWriter.OSCWriter()
        #self.dataStream = socketClientUx.GetData(packetSize=1, label=0, getTraining=False, numSensors=2, packetLimit=1000, pathPreface="data/Orientation01/", writer=self.writer)
        self.packetLimit = 10
        self.numSensors = 2
        self.pathPreface = "data/Orientation01/"
        self.dataTx = 0xFF
    
    def trainModels(self, numSensors, packetLimit, pathPreface, *, gestureIdx=-1, labelList=[], labelPathList=[]):
        #iterate through all the gestures and collect packetLimit samples of each
        #Called in window 2 and 2.1 where user provides data to set up model and data
        #Switches to window 3 to output data 

        sampleCount = 0
        
        for i in range(gestureIdx):
            dataStream = socketClientUx.GetData(label=labelList[i], labelPath=labelPathList[i], getTraining=True, numSensors=numSensors, packetLimit=packetLimit, pathPreface=pathPreface)
            if sampleCount == 0:
                #dataStream = socketClientUx.GetData(label=label, getTraining=True, numSensors=numSensors, packetLimit=packetLimit, pathPreface=pathPreface)
                print("First Time?")
            else:
                while sampleCount <= packetLimit:
                    dataStream.getSample()
                    dataStream.prepTraining()
                    sampleCount += 1
        
        #CSend all the gestures to neural network
        NeuralNetwork.trainOrientation(pathPreface, labelPathList, 1, numSensors, gestureIdx)
            

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
        layout = [[sg.Text('The Conductor'), sg.Text(size=(2,1), key='-OUTPUT-')],
                [sg.Text('Upload an existing neural network model or create a new one.'), sg.Text(size=(5,1), key='-OUTPUT-')], 
                [sg.Text('Upload a Model'), sg.Text(size=(2,1), key='-OUTPUT-'), sg.Input(), sg.FileBrowse(), sg.Button('Ok', bind_return_key=True)],
                [sg.Text('Create a Model'), sg.Text(size=(2,1), key='-OUTPUT-'), sg.Button('Create')],
                [sg.Text('Not a valid model file. Please try again.'), sg.Text(size=(2,1), key='-invalidModel-')]
                ]

        return sg.Window('THE CONDUCTOR: Step 1', layout, finalize=True)
    

    def makeWindow2(self):
        #Window two Create model
        layout = [[sg.Text('The Conductor'), sg.Text(size=(2,1), key='-OUTPUT-')]
        ]
        return sg.Window('THE CONDUCTOR: Step 2', layout, finalize=True)

    def uxLoop(self):
        sg.theme(self.theme)

        # Set all windows to Noe except window 1 to start
        window2 = None
        window1 = self.makeWindow1()

        while True:  # Event Loop
            window, event, values = sg.read_all_windows()
            print(f'event: {event}')
            print(f'values: {values}')

            #events for window1 (welcome, load / create model)
            if window == window1:
                window['-invalidModel-'].hide_row()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == 'Ok':
                    # Update the "output" text element to be the value of "input" element
                    window['-invalidModel-'].hide_row()
                    print()
                    print(f'Model Path: {values[0]}')
                    # Check that the path has a valid model file
                    try:
                        model = NeuralNetwork.Model.load(values[0])
                    except:
                        window['-invalidModel-'].unhide_row()
                        #TODO toggle invalidModel text

                    # see if there is a model in pathPreface
                    if os.path.exists(self.dataStream.pathPreface + 'model.model'):
                        # figure out a way to elegantly make a new model
                        print('path')
                        
                    # increment the filename to avoid overwriting model (update self.modelFileName)

                    # save the file to pathPreface/model

                    #Go to window2
                if event == 'Create':
                    print()
                    print(f'Value: {values[0]}')
                    window1.hide()
                    window2 = self.makeWindow2()

            if window == window2:
                print("Window 2")
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break


        window.close()

def main():

    testGui = UX()
    testGui.uxLoop()

if __name__ == "__main__": main()