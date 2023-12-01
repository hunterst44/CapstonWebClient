import PySimpleGUI as sg
import os.path
import utils

class Window:
    def __init__ (self, ASSETS_PATH = r"./assets"):
        self.ASSETS_PATH = ASSETS_PATH
        self.windowSizeX = 850 #Width of the window
        self.windowSizeY = 660 #Height of the window
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

        content_layout = [[sg.Push(),sg.T('Choose a working directory', key='-OUTPUT-',font = ("Calibri", 16, "bold",), pad=((0,0),(0,25))),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([
                    [sg.T(f"The Conductor will look in\n{os.path.abspath(os.getcwd()) + '/' + pathPreface}\nfor configuration files. Click 'Ok' to use this folder, or 'Browse' to choose a new working folder.", key="-MODELMESSAGE00-", visible=True)],
                    [sg.Btn('Ok', key='-CREATEMOEDLBTN-', visible=False)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()], 
                [sg.Push(),sg.pin(sg.Column([
                    [sg.Btn('Ok',**self.button2_properties(), key='-USEDEFAULTDIRBTN-', visible=True),
                    sg.Btn('Browse',**self.button1_properties(), key='-CHOOSEDIR-', enable_events=True)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()],
                    #sg.FolderBrowse(size=(8,1), visible=True, key='-CHOOSEDIR-', enable_events=True)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([[sg.Btn('Ok',**self.button2_properties(), key='-USESELDIRBTN-', visible=False)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()]
                ]
        
        window00 = self.create_window(content_layout, windowtitlemsg)
        return window00

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
            content_layout = ([sg.Push(),sg.T(f'Connect to The Conductor.',key='-OUTPUT-',font = ("Calibri", 16, "bold",), pad=((0,0),(0,25))),sg.Push()], 
                    [sg.Push(),sg.pin(sg.Column([[sg.T(topMessage, pad=(LEFTMARGIN,4), key='-TOPMESSAGE-')]]),shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.T(f"To use this network click 'Continue.' To connect to another network enter the network info below and click 'Reconnect'. Click 'Don't Connect' to continue without connecting", key='-TOPMESSAGE01-', pad=(LEFTMARGIN,0), visible=connectVis)]]), shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.Input('192.168.XX.XXX', key="-IPIN-", visible=disconnectVis, pad=((5),(0,5)), do_not_clear=True)]], pad=(LEFTMARGIN,0)),shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.Input('192.168.XX.XXX', key="-IPNEW-", visible=False)]]), shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.Btn('Connect',**self.button1_properties(), key='-APCNTEBTN-', visible=disconnectVis, pad=((0,70 ),(5,0)))]]),shrink=True),
                    #[sg.Column([[sg.Btn('Connect',**self.button1_properties(), key='-STNCNTEBTN-', visible=False, pad=((70,70 ),(5,0)))]]),
                    sg.Column([[sg.Btn("Don't Connect",**self.button1_properties(), key='-NOCNTBTN-', visible=disconnectVis )]],pad=((LEFTMARGIN,0),(5,0))),sg.Push()],                
                    sg.Push(),sg.pin(sg.Column([
                        [sg.Listbox(self.SSIDList, size=(15, 8), key="-SSIDIN-", expand_y=True, enable_events=True, visible=connectVis)],
                        [sg.Btn('Refresh', **self.button1_properties(), key='-SSIDLISTRFH-', visible=connectVis)]], pad=(LEFTMARGIN+50, 0),element_justification='c')),
                    sg.Push(),sg.pin(sg.Column([
                        [sg.Input('Password', key="-PSWDIN-", visible=connectVis,size = 15, pad=(0, 0))],
                        [sg.Btn('Reconnect', **self.button1_properties(), key='-RECNTBTN-', visible=connectVis)],
                        [sg.Btn("Don't Connect",**self.button1_properties(), key='-NOCNTBTN2-', visible=False )]], pad=(LEFTMARGIN, 0), element_justification='c')),
                    sg.Push(),[sg.Btn('Continue',**self.button1_properties(), key='-CONTBTN-', visible=connectVis)],sg.Push(),
                    #[sg.pin(sg.Column([[sg.Btn('Connect', key='-APCNTEBTN-', visible=True)]], pad=(LEFTMARGIN,0)), shrink=True)],
                    [sg.Push(),sg.pin(sg.Column([[sg.Btn('Continue',**self.button1_properties(), key='-CONTBTN-', visible=connectVis)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()],
                    [sg.Push(),sg.pin(sg.Column([[sg.T("If your network doesn't show up in the list open Windows network manager before clicking Refresh", visible=True, key='-MESSAGE-')]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()]
                    )
        
            window0=self.create_window(content_layout, windowtitlemsg)
            self.update_top_message(window0, topMessage)
            return window0
        
    def makeWindow1(self, modelPath,):
        LEFTMARGIN = 50
        modelMessage, existsVis, notVis = utils.makeModelFileMessage(modelPath)
    #Window one welcome, load / create model
        windowtitlemsg = 'THE CONDUCTOR: Step 1'
        content_layout =([sg.Push(),sg.T('The Conductor: Window 1',key='-OUTPUT-',font = ("Calibri", 16, "bold",), pad=((LEFTMARGIN,0),(0,25))),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([
                    [sg.T(modelMessage, key="-MODELMESSAGE00-", visible=True)], 
                    [sg.Btn('Ok',**self.button2_properties(), key='-USEDEFAULTBTN-', visible=existsVis),
                    sg.Btn('Create New',**self.button1_properties(), key='-CREATEMOEDLBTN-', visible=True),
                    sg.Btn('Ok',**self.button2_properties(), key='-ACCPTDEFAULT-', visible=notVis)]], pad=(LEFTMARGIN, 0)), shrink=True),sg.Push()], 
                [sg.Push(),sg.pin(sg.Column([[sg.T(modelMessage, key="-MODELMESSAGE01-", visible=False)]], pad=(LEFTMARGIN, 0)), shrink=True),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([[sg.Input('How many hand positions will you train?', key="-NUMPOS-", visible=False, enable_events=True)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([[sg.Input('Position 1 label', key="-POSLABEL-", visible=False)], 
                    [sg.Btn('SUBMIT',**self.button1_properties(), key='-SUBLABELBTN-', visible=False)]], pad=(LEFTMARGIN,0)), shrink=True),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([[sg.T('Train Model', key='-TRAIN-', visible=False),sg.Btn('Train',**self.button1_properties(), key='-TRAINBTN-', visible=False)]], pad=(LEFTMARGIN, 0)), shrink=True),sg.Push()],
                [sg.Push(),sg.pin(sg.Column([
                    [sg.T('Predict hand positions', key='-PREDICT-', visible=False),
                    sg.Btn('Predict',**self.button1_properties(), key='-PREDICTBTN-',visible=False)]], pad=(LEFTMARGIN, 0)), shrink=True),sg.Push()]
        )
        
        window1=self.create_window(content_layout,windowtitlemsg)
        return window1

    def makeWindow2(self,controlList,waveList,conditionTypeList,currentPositionList,arpegDirList,midiOutList,controlListStr,textHeight,Message00Text,logVisibility,logInvisibility):
        LEFTMARGIN = 50
        windowtitlemsg = 'THE CONDUCTOR: Step 2'
        content_layout = [
            [sg.Push(),sg.T('The Conductor: Window 2', key='-OUTPUT-',font = ("Calibri", 16, "bold",), pad=((LEFTMARGIN,0),(0,25))),sg.Push()
                #[sg.Input('How many hand positions will you train?', key="-NUMPOS-", visible=False, enable_events=True)]
            ],
            [sg.Push(),sg.Column([
                [sg.T(Message00Text, key='-TOPMESSAGE00-', visible=True)], 
                [sg.T(controlListStr, key='-TOPMESSAGE01-', visible=True)]
                ], key='-TOPMESSAGE00COL-', element_justification='left', expand_x = True, vertical_alignment='t', pad=(LEFTMARGIN,0)), sg.Push(),
            sg.Push(),sg.Column([
                [sg.Btn('OK', **self.button2_properties(), key='-USELOGBTN-', visible=logVisibility)], 
                [sg.Btn('Overwrite', **self.button1_properties(), key='-NEWCONTROLBTN-', visible=logVisibility)],
                [sg.Btn('Continue', **self.button1_properties(), key='-CONTUBTN-', visible=False)] 
                ], key='-CNTRLOVERIDECOL-', element_justification='left', expand_x = True, vertical_alignment='t', pad=(LEFTMARGIN,0), visible=logVisibility), sg.Push(),
            sg.Push(), sg.Column([
                [sg.Listbox(midiOutList, size=(50, 8), key="-MIDIPORTOUT-", expand_x=True, expand_y=True,enable_events=True, visible=logInvisibility)], 
                [sg.Btn('Refresh', **self.button1_properties(), key='-MIDIOUTLISTRFH-', visible=logInvisibility)], 
                [sg.Btn('Connect', **self.button1_properties(), key='-MIDIOUTCNTBTN-', visible=logInvisibility)]
                ], key='-MIDIPORTOUTCOL-',  element_justification='left', expand_x = True, vertical_alignment='t', pad=(LEFTMARGIN,0)),sg.Push(),
            ],
            [sg.pin(sg.Column([
                [sg.T("BPM", key='-BPMLABEL-', visible=False)],
                [sg.Slider(range=(30, 300), default_value=120, expand_x=True,orientation='horizontal', key='-BPMSLIDE-', visible=False)],
                [sg.Btn('Ok', **self.button2_properties(), key='-BPMBTN-', visible=False)]
                ], key='-BPMCOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0)), shrink=True),
            sg.Column([
                [sg.Input('Control Name', size=(15,10), key="-CTRLNAME-", visible=False)],
                [sg.Btn('Ok', **self.button2_properties(), key='-CTRLNAMEBTN-', visible=False)]
                ], key='-CTRLNAMECOL-',  vertical_alignment='t', visible=False, pad=(LEFTMARGIN,0)),
            sg.Column([
                [sg.Listbox(conditionTypeList, size=(10, 3), key="-CONDTYPE-", expand_y=True, enable_events=True, visible=False)]
                ], key='-CONDTYPECOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0), visible=False),
            sg.Column([
                [sg.T(f"Position, threshold Control ON.", key='-CURRPOSONLABEL-', size=(15,2), visible=False)],
                [sg.Listbox(currentPositionList, size=(10, 3), key="-CURRPOSLISTON-", expand_y=True, enable_events=True, visible=False)],
                [sg.Slider(range=(1, 25), default_value=3, expand_x=True,orientation='horizontal', key='-CURRPOSONSLIDE-', visible=False)]
                ], key='-CURRPOSLISTONCOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0), visible=False),
            sg.Column([
                [sg.T(f"Position, threshold at END ON.", key='-CURRPOSTRANSONLABEL-', size=(15,2), visible=False)],
                [sg.Listbox(currentPositionList, size=(10, 3), key="-CURRPOSLISTTRANSON-", expand_y=True, enable_events=True, visible=False)],
                [sg.Slider(range=(1, 25), default_value=3, expand_x=True,orientation='horizontal', key='-CURRPOSTRANSONSLIDE-', visible=False)]
                ], key='-CURRPOSLISTTRANSONCOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0), visible=False),
            sg.Column([
                [sg.T(f"Position, threshold control OFF.", key='-CURRPOSOFFLABEL-', size=(15,2), visible=False)],
                [sg.Listbox(currentPositionList, size=(10, 3), key="-CURRPOSLISTOFF-", expand_y=True, enable_events=True, visible=False)],
                [sg.Slider(range=(1, 25), default_value=3, expand_x=True,orientation='horizontal', key='-CURRPOSOFFSLIDE-', visible=False)],
                [sg.Btn('Ok', **self.button2_properties(), key='-CONDBTN-', visible=False)]
                ], key='-CURRPOSLISTOFFCOL-', vertical_alignment='t', pad=(LEFTMARGIN,0), visible=False),
            sg.Column([
                [sg.T(f"Position, threshold at END OFF.", key='-CURRPOSOFFTRANSLABEL-', size=(15,2), visible=False)],
                [sg.Listbox(currentPositionList, size=(10, 3), key="-CURRPOSLISTTRANSOFF-", expand_y=True, enable_events=True, visible=False)],
                [sg.Slider(range=(1, 25), default_value=3, expand_x=True,orientation='horizontal', key='-CURRPOSOFFTRANSSLIDE-', visible=False)],
                [sg.Btn('Ok', key='-CONDTRANSBTN-', visible=False)]
                ], key='-CURRPOSLISTTRANSOFFCOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0), visible=False),
            sg.Column([
                [sg.Listbox(arpegDirList, size=(10, 3), key="-ARPEGDIR-", expand_y=True, enable_events=True, visible=False)],
                [sg.Btn('Ok', **self.button2_properties(), key='-ARPEGBTN-', visible=False)]
                ], key='-ARPEGDIRCOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0), visible=False),
            sg.Column([
                [sg.Listbox(controlList, size=(10, 3), key="-CTRLLIST-", expand_y=True, enable_events=True, visible=False)],
                [sg.Btn('Select', **self.button1_properties(), key='-SELCNTRLTYPEBTN-', visible=False)]
                ], key='-CTRLLISTCOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0)),
            sg.Column([
                [sg.T(f"Rate", key='-RATELABEL-', size=(15,2), visible=False)],
                [sg.Slider(range=(0, 127), default_value=30, expand_x=True,orientation='horizontal',key='-RATESLIDE-', visible=False)]
                ], key='-RATECOL-', vertical_alignment='t', pad=(LEFTMARGIN,0)),
            sg.Column([
                [sg.T(f"Waveform", key='-WAVELABEL-', size=(15,2), visible=False)],
                [sg.Listbox(waveList, size=(50, 3), key="-WAVELIST-", enable_events=True, visible=False)]
                ], key='-WAVECOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0)),
            sg.Column([
                [sg.T(f"Minimum", key='-MINLABEL-', size=(15,2), visible=False)],
                [sg.Slider(range=(0, 127), default_value=30, expand_x=True,orientation='horizontal', key='-MINSLIDE-', visible=False)]
                ], key='-MINCOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0)),
            sg.Column([
                [sg.T(f"Maximum", key='-MAXLABEL-', size=(15,2), visible=False)],
                [sg.Slider(range=(0, 127), default_value=30, expand_x=True,orientation='horizontal', key='-MAXSLIDE-', visible=False)],
                [sg.Btn('Ok', **self.button2_properties(), key='-MODDATABTN-', visible=False)]
                ], key='-MAXCOL-',  vertical_alignment='t', pad=(LEFTMARGIN,0)),
            sg.Column([
                [sg.T(f"Click 'Another' to setup another control, or click 'Done' to continue.", key='-DONELABEL-', size=(15,2), visible=False)],
                [sg.Btn('Another', **self.button1_properties(), key='-ANOTHERBTN-', visible=False)],
                [sg.Btn('Done', **self.button1_properties(), key='-MAPPINGDONEBTN-', visible=False)]
                ], key='-DONECOL-',  vertical_alignment='t', pad=(0,0), visible=False),
            #sg.Column([[sg.T(f"Min / Max", key='-MINMAXLABEL-', size=(15,2), visible=False)], [sg.Listbox(waveList, size=(50, 15), key="-WAVELIST-", expand_y=True, enable_events=True, visible=False)]], key='-MINCOL-',  vertical_alignment='t', pad=(0,0))
            ]
        ]
        window2=self.create_window(content_layout,windowtitlemsg)
        return window2

    def makeWindow3(self):
        #Window3 Training 
        windowtitlemsg = 'THE CONDUCTOR: Step 3'
        content_layout = [[sg.T('The Conductor: Window 3'), sg.T(size=(2,1), key='-OUTPUT-')],
                    [sg.pin(sg.Column([[sg.T("Hit the 'GO!' Btn to begin training", visible=True, key='-GESTURE-'), sg.T(size=(2,1))]], pad=(0,0)), shrink=True)],
                    [sg.pin(sg.Column([[sg.T('', visible=True, key='-CountDown-'), sg.T(size=(2,1))]], pad=(0,0)), shrink=True)],
                    [sg.Btn('GO!')]
        ]
        window3=self.create_window(content_layout,windowtitlemsg)
        return window3
        return sg.Window('THE CONDUCTOR: Step 3', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)


    def makeWindow3_1(self):
        #Window3_1 Prediction 
        windowtitlemsg = 'THE CONDUCTOR: Step 3_1'
        content_layout = [[sg.T('The Conductor: Window 3_1'), sg.T(size=(2,1), key='-OUTPUT-')],
                    [sg.pin(sg.Column([[sg.T("Hit the 'GO!' Btn to begin prediction", visible=True, key='-GESTURE-'), sg.T(size=(2,1))]], pad=(0,0)), shrink=True)],
                    [sg.pin(sg.Column([[sg.T('', visible=True, key='-CountDown-'), sg.T(size=(2,1))]], pad=(0,0)), shrink=True)],
                    [sg.pin(sg.Column([[sg.T(''), sg.T(size=(2,1), key='-GO-'), sg.Btn('GO!', key='-GOBTN-', visible=True)]]), shrink=True)],
                    [sg.pin(sg.Column([[sg.T(''), sg.T(size=(2,1), key='-STOP-'), sg.Btn('Stop', key='-STOPBTN-', visible=False)]]), shrink=True)]
        ]
        window3_1=self.create_window(content_layout,windowtitlemsg)
        return window3_1
        return sg.Window('THE CONDUCTOR: Step 3_1', layout, layout, size=(self.windowSizeX,self.windowSizeY), finalize=True)
