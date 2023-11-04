import time
import rtmidi
from metronome import Metronome
import threading
import buildMidi


class MidiPlayer:
    def __init__(self, midi_out, time_slice=0, midi_data=[]):
        self.timeSlice = time_slice
        self.midiData = midi_data
        self.midiOut = midi_out

    def playBeat(self, midi_data):
        for msg in midi_data:
            print(f"Playing MIDI from control: {msg}")
            self.midiOut.send_message(msg)
            time.sleep(self.timeSlice / 1000)
           

    def playBeatThreaded(self):
        threads = []
        for i, control in enumerate(self.midiData):
            thread = threading.Thread(target=self.playBeat, args=())
            threads.append(thread)
            thread.start()
            print(f"Thread {i + 1} started.")

        for thread in threads:
            thread.join()
        print("All threads finished.")
        
    # class Metronome:
    #     def __init__(self, bpm=60, start_flag=False, done_flag=0):
    #         self.bpm = bpm
    #         self.startFlag = start_flag
    #         self.doneFlag = done_flag

    #     def startMetro(self, off_on_state):
    #         self.startFlag = off_on_state

    #     def getTimeTick(self, midi_array):
    #         midi_count = len(midi_array)
    #         bpm_millis = (60 / self.bpm) * 1000
    #         time_slice = bpm_millis / midi_count
    #         return time_slice



# midiOut = rtmidi.MidiOut()
# available_ports = midiOut.get_ports()

# if available_ports:
#     print(f'Available ports: {available_ports}')
#     port_index = 1  # Choosing the first available port by default
#     if midiOut.is_port_open():
#         print(f"The port {available_ports[port_index]} is already open.")
#     else:
#         midiOut.open_port(port_index)
#         print(f"The port {available_ports[port_index]} has been opened.")
# else:
#     print(f"No available MIDI ports found. Please check your MIDI setup.")


# builder1 = buildMidi.MidiBuilder(dataType=0, midiMessage=[60], ch=0, velocity=64, rate='q')
# result1 = builder1.build_midi()

# builder2 = buildMidi.MidiBuilder(dataType=1, shape=1, signal_invert=0, ch=2, min_val=0, rate='h', midiCCNum=2)
# result2 = builder2.build_midi()

# builder3 = buildMidi.MidiBuilder(dataType=2, ch=1, oldTof=60, newTof=80, rate='w', midiCCNum=2)
# result3 = builder3.build_midi()

# metronome = Metronome(bpm=60)
# midi_data_list = [result1, result2, result3]
# midi_players = [MidiPlayer(midiOut, metronome.getTimeTick(midi_data), midi_data) for midi_data in midi_data_list]

# metronome.startMetro(True)

# while metronome.startFlag == True:
    
#     # if(metronome.doneFlag == 1):
#         threads = []
#         for midi_player, midi_data in zip(midi_players, midi_data_list):
#             threads.append(threading.Thread(target=midi_player.playBeat, args=(midi_data,)))

#         for thread in threads:
#             thread.start()

    
#         for thread in threads:
#             thread.join()

       
