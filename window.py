import PySimpleGUI as sg

ASSETS_PATH = r"./assets"

def create_window(content_layout, windowname):

    sg.theme("LightGrey1")  # Change the theme to your preferred one
    sg.set_options(font=('Calibri', 12))


    layout = [        
            [sg.Image(filename= ASSETS_PATH +"/image_3.png",pad=(20))],
            [content_layout],
            #  [sg.Frame('Connect to The Conductor.', title_location='n' ,font = ("Calibri", 16, "bold",), pad=(50,0), layout=[
            #  [sg.pin(sg.Column([[sg.Text('Start up The Conductor and connect your PC to the SSID displayed on the screen.', pad=((50),(20,0)), key='-TOPMESSAGE-')]]))],
            #  [sg.pin(sg.Column([[sg.Text('Then enter IP address on the screen and click "Connect."', pad=(50,4), key='-TOPMESSAGE01-')]]))],
            #  [sg.pin(sg.Column([[sg.Input('IP Address', key="-IPIN-", visible=True, pad=(50,4), do_not_clear=True)]]))],
            #  [sg.pin(sg.Column([[sg.Input('IP Address', key="-IPNEW-", visible=False)]]), shrink=False)],
            #  [sg.pin(sg.Column([[sg.Button('Connect', key='-STNCNTEBTN-', visible=False)]], pad=(0,0)), shrink=False)],
            #  [sg.pin(sg.Column([[sg.Input('Password', key="-PSWDIN-", visible=False)]]), shrink=False)],
            #  [sg.pin(sg.Column([[sg.Button('Connect', key='-APCNTEBTN-', visible=True)]], pad=(50,0)), shrink=False)],
            #  [sg.pin(sg.Column([[sg.Button('Continue', key='-CONTBTN-', visible=False)]], pad=(0,0)), shrink=False)],
            #  [sg.pin(sg.Column([[sg.Button('Reconnect', key='-RECNTBTN-', visible=False)]], pad=(0,0)), shrink=True)]])],
            #  [sg.pin(sg.Column([[sg.Text('', visible=True, key='-MESSAGE-'), sg.Text(size=(2,1))]], pad=(0,0)), shrink=False)],
            [sg.Image(filename= ASSETS_PATH +"/image_2.png",pad=(0,0)),sg.Push(),sg.Push(),sg.Image(filename= ASSETS_PATH +"/image_1_s.png",pad=(0,0))]]


    window = sg.Window(windowname, layout,  resizable=True, finalize=True)


    while True:
            event, values = window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'OK':
                break
            
    window.close()
