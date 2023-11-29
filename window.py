import PySimpleGUI as sg
import os.path

class Window:
    def __init__ (self, ASSETS_PATH = r"./assets"):
        self.ASSETS_PATH = ASSETS_PATH
        self.windowSizeX = 850 #Width of the window
        self.windowSizeY = 670 #Height of the window
        self.font = ("Calibri", 12)
        self.fontB = ("Calibri", 12, 'bold')
        self.colors = ("", "#FFFFFF")
        self.button1 = self.ASSETS_PATH +"/button1.png"
        self.button2 = self.ASSETS_PATH +"/button2.png"

    def button1_properties(self):
        return {
            'button_color': self.colors,
            'border_width': 0,
            'image_source': self.ASSETS_PATH + "/button1.png",
            'font': self.fontB
        }
    def button2_properties(self):
        return {
            'button_color': self.colors,
            'border_width': 0,
            'image_source': self.ASSETS_PATH + "/button2.png",
            'font': self.fontB
        }

    def create_window(self,content_layout, windowtitlemsg):

        #sg.theme("LightGrey1")  # Change the theme to your preferred one
        sg.set_options(font=self.font)


        layout = [        
                [sg.Image(filename= self.ASSETS_PATH +"/image_3.png",pad=(30))],
                [content_layout],
                [sg.Image(filename= self.ASSETS_PATH +"/image_2.png",pad=(0,0)),sg.Push(),sg.VPush(),sg.Image(filename= self.ASSETS_PATH +"/image_1_s.png",pad=(0,0))]
               ]

        windowname = sg.Window(windowtitlemsg, layout, size=(self.windowSizeX,self.windowSizeY), resizable=True, finalize=True)
        return windowname

    def update_top_message(self,window, new_message):
        window['-TOPMESSAGE-'].update(new_message)
        window.refresh()
        return window

    def makeWindow00(self, pathPreface):
        LEFTMARGIN = 50

        windowtitlemsg = 'The Conductor: STEP 00'

        content_layout = [[sg.Push(),sg.Text('Choose a working directory', key='-OUTPUT-',font = ("Calibri", 16, "bold",), pad=((0,0),(0,25))),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([
                    [sg.Text(f"The Conductor will look in\n{os.path.abspath(os.getcwd()) + '/' + pathPreface}\nfor configuration files. Click 'Ok' to use this folder, or 'Browse' to choose a new working folder.", key="-MODELMESSAGE00-", visible=True)],
                    [sg.Button('Ok', key='-CREATEMOEDLBTN-', visible=False)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()], 
                [sg.Push(),sg.pin(sg.Column([
                    [sg.Button('Ok',**self.button2_properties(), key='-USEDEFAULTDIRBTN-', visible=True),
                    sg.Button('Browse',**self.button1_properties(), key='-CHOOSEDIR-', enable_events=True)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()],
                    #sg.FolderBrowse(size=(8,1), visible=True, key='-CHOOSEDIR-', enable_events=True)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([[sg.Button('Ok',**self.button2_properties(), key='-USESELDIRBTN-', visible=False)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()]
                ]
        
        window00 = self.create_window(content_layout, windowtitlemsg)
        return window00
        return sg.Window('THE CONDUCTOR: Step 00', layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)

    def makeWindow0(self, connected, ssidlist, ssid, host):
            
            self.SSIDList = ssidlist  #Get the network list from the air so user can reconnect
            LEFTMARGIN = 50

            if connected:
                topMessage = 'The Conductor is connected on ' + ssid + ' at ' + host
                connectVis = True   #Use to set visibility of an item when The Conductor is connected
                disconnectVis = False  #Use to unset visibility of an item when The Conductor is not connected
                
            else:
                topMessage = 'Start up The Conductor and connect your PC to the SSID displayed on the screen.\n\nThen enter IP address on the screen and click "Connect."'
                connectVis = False
                disconnectVis = True

            windowtitlemsg = 'THE CONDUCTOR: Step 0'
            content_layout = ([sg.Push(),sg.Text(f'Connect to The Conductor.',key='-OUTPUT-',font = ("Calibri", 16, "bold",), pad=((0,0),(0,25))),sg.Push()], 
                    [sg.Push(),sg.pin(sg.Column([[sg.Text(topMessage, pad=(LEFTMARGIN,4), key='-TOPMESSAGE-')]]),shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.Text(f"To use this network click 'Continue.' To connect to another network enter the network info below and click 'Reconnect'. Click 'Don't Connect' to continue without connecting", key='-TOPMESSAGE01-', pad=(LEFTMARGIN,0), visible=connectVis)]]), shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.Input('192.168.XX.XXX', key="-IPIN-", visible=disconnectVis, pad=((5),(0,5)), do_not_clear=True)]], pad=(LEFTMARGIN,0)),shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.Input('192.168.XX.XXX', key="-IPNEW-", visible=False)]]), shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.Btn('Connect',**self.button1_properties(), key='-APCNTEBTN-', visible=disconnectVis, pad=((0,70 ),(5,0)))]]),shrink=True),
                    #[sg.Column([[sg.Btn('Connect',**self.button1_properties(), key='-STNCNTEBTN-', visible=False, pad=((70,70 ),(5,0)))]]),
                     sg.Column([[sg.Btn("Don't Connect",**self.button1_properties(), key='-NOCNTBTN-', visible=disconnectVis )]],pad=((LEFTMARGIN,0),(5,0))),sg.Push()],
                
                    sg.Push(),sg.pin(sg.Column([
                        [sg.Listbox(self.SSIDList, size=(15, 8), key="-SSIDIN-", expand_y=True, enable_events=True, visible=connectVis)],
                        [sg.Button('Refresh', **self.button1_properties(), key='-SSIDLISTRFH-', visible=connectVis)]], pad=(LEFTMARGIN+50, 0),element_justification='c')),
                    sg.Push(),sg.pin(sg.Column([
                        [sg.Input('Password', key="-PSWDIN-", visible=connectVis,size = 15, pad=(0, 0))],
                        [sg.Btn('Reconnect', **self.button1_properties(), key='-RECNTBTN-', visible=connectVis)],
                        [sg.Btn("Don't Connect",**self.button1_properties(), key='-NOCNTBTN2-', visible=False )]], pad=(LEFTMARGIN, 0), element_justification='c')),
                    sg.Push(),[sg.Btn('Continue',**self.button1_properties(), key='-CONTBTN-', visible=connectVis)],sg.Push(),

                    #[sg.pin(sg.Column([[sg.Btn('Connect', key='-APCNTEBTN-', visible=True)]], pad=(LEFTMARGIN,0)), shrink=True)],
                    [sg.Push(),sg.pin(sg.Column([[sg.Btn('Continue',**self.button1_properties(), key='-CONTBTN-', visible=connectVis)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.Text("If your network doesn't show up in the list open Windows network manager before clicking Refresh", visible=True, key='-MESSAGE-')]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()]
                    )
        
            window0=self.create_window(content_layout, windowtitlemsg)
            self.update_top_message(window0, topMessage)
            return window0
        
    def makeWindow1(self, pathPreface):
        LEFTMARGIN = 50
    #Window one welcome, load / create model
        windowtitlemsg = 'THE CONDUCTOR: Step 1'
        content_layout =([sg.Push(),sg.Text('The Conductor: Window 1',key='-OUTPUT-',font = ("Calibri", 16, "bold",), pad=((LEFTMARGIN,0),(0,25))),sg.Push()],
                [sg.pin(sg.Column([[sg.Text(f"The Conductor will look in\n {os.path.abspath(os.getcwd()) + '/' + pathPreface} \nfor Neural Network model files. \nClick 'Ok' to use this folder.", key="-MODELMESSAGE00-", visible=True)],
                    [sg.Button('Ok',**self.button2_properties(), key='-USEDEFAULTBTN-', visible=True)],
                    [sg.Button('Ok',**self.button2_properties(), key='-CREATEMOEDLBTN-', visible=False)]], pad=(LEFTMARGIN,0)), shrink=True)], 
                [sg.pin(sg.Column([[sg.FolderBrowse(size=(8,1), visible=True, key='-CHOOSEDIR-')],[sg.Text(f"Or Browse for a new folder and click 'New Folder.'", key="-MODELMESSAGE01-", visible=True)], 
                    [sg.Button('New Folder',**self.button1_properties(), key='-NEWFOLDER-', visible=True)],
                    [sg.Button('Ok',**self.button1_properties(), key='-ACCPTDEFAULT-', visible=False)]], pad=(LEFTMARGIN,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Input('How many hand positions will you train?', key="-NUMPOS-", visible=False, enable_events=True)]], pad=(LEFTMARGIN,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Input('Position 1 label', key="-POSLABEL-", visible=False)], 
                    [sg.Button('SUBMIT',**self.button1_properties(), key='-SUBLABELBTN-', visible=False)]], pad=(LEFTMARGIN,0)), shrink=True)],
                [sg.pin(sg.Column([[sg.Text('Train Model', key='-TRAIN-', visible=False),sg.Button('Train', key='-TRAINBTN-', visible=False)]]))],
                [sg.pin(sg.Column([[sg.Text('Predict hand positions', key='-PREDICT-', visible=False),
                    sg.Button('Predict',**self.button1_properties(), key='-PREDICTBTN-',visible=False)]]))]
        )
        
        window1=self.create_window(content_layout,windowtitlemsg)
        return window1

    def makeWindow2_1(self):
        #Window3 Training or prediction select
        windowtitlemsg = 'THE CONDUCTOR: Step 2.1'
        content_layout = [[sg.Text('The Conductor: Window 2.1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                    [sg.pin(sg.Column([[sg.Text('Train Model'), sg.Text(size=(2,1), key='-TRAIN-'), sg.Btn('Train', key='-TRAINBTN-')]]))],
                    [sg.pin(sg.Column([[sg.Text('Predict gestures'), sg.Text(size=(2,1), key='-PREDICT-'), sg.Btn('Predict', key='-PREDICTBTN-')]]))],
                    [sg.pin(sg.Column([[sg.Text('', visible=True, key='-WORDS-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=True)],
        ]
        window2_1=self.create_window(content_layout,windowtitlemsg)
        return window2_1
        return sg.Window('THE CONDUCTOR: Step 2.1', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)


    def makeWindow3(self):
        #Window3 Training 
        windowtitlemsg = 'THE CONDUCTOR: Step 3'
        content_layout = [[sg.Text('The Conductor: Window 3'), sg.Text(size=(2,1), key='-OUTPUT-')],
                    [sg.pin(sg.Column([[sg.Text("Hit the 'GO!' Btn to begin training", visible=True, key='-GESTURE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=True)],
                    [sg.pin(sg.Column([[sg.Text('', visible=True, key='-CountDown-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=True)],
                    [sg.Btn('GO!')]
        ]
        window3=self.create_window(content_layout,windowtitlemsg)
        return window3
        return sg.Window('THE CONDUCTOR: Step 3', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)


    def makeWindow3_1(self):
        #Window3_1 Prediction 
        windowtitlemsg = 'THE CONDUCTOR: Step 3_1'
        content_layout = [[sg.Text('The Conductor: Window 3_1'), sg.Text(size=(2,1), key='-OUTPUT-')],
                    [sg.pin(sg.Column([[sg.Text("Hit the 'GO!' Btn to begin prediction", visible=True, key='-GESTURE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=True)],
                    [sg.pin(sg.Column([[sg.Text('', visible=True, key='-CountDown-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=True)],
                    [sg.pin(sg.Column([[sg.Text(''), sg.Text(size=(2,1), key='-GO-'), sg.Btn('GO!', key='-GOBTN-', visible=True)]]), shrink=True)],
                    [sg.pin(sg.Column([[sg.Text(''), sg.Text(size=(2,1), key='-STOP-'), sg.Btn('Stop', key='-STOPBTN-', visible=False)]]), shrink=True)]
        ]
        window3_1=self.create_window(content_layout,windowtitlemsg)
        return window3_1
        return sg.Window('THE CONDUCTOR: Step 3_1', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
