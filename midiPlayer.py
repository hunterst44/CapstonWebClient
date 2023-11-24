import time
import rtmidi
import threading
from metronome import Metronome
import buildMidi
import numpy as np



class MidiPlayer:
    def __init__(self, midi_out, time_slice=0, midi_data=None, on_flag=0):
        self.timeSlice = time_slice
        self.midiData = midi_data or []
        self.midiOut = midi_out
        self.onFlag = on_flag

    def play_beat(self, midi_data=None, on_flag=0):
        # on_flag = 1
        a = np.asarray(midi_data)
        if a.size == 0:
            print("Midi array is empty")
        else:
            if on_flag:
                if isinstance(midi_data[0], int):
                    self.midiOut.send_message(midi_data)
                    time.sleep(self.timeSlice / 1000)
                else:
                    for msg in midi_data:
                        print(f"Playing MIDI from control: {msg}")
                        print(self.midiOut.get_ports())
                        self.midiOut.send_message(msg)
                        time.sleep(self.timeSlice / 1000)

    def play_beat_threaded(self):
        threads = []
        for i, control in enumerate(self.midiData):
            thread = threading.Thread(target=self.play_beat, args=(control,))
            threads.append(thread)
            thread.start()
            print(f"Thread {i + 1} started.")

        for thread in threads:
            thread.join()
        print("All threads finished.")

    # ... (other methods remain unchanged)

def initialize_midi_player():
    midi_out = rtmidi.MidiOut()
    available_ports = midi_out.get_ports()

    if available_ports:
        print(f'Available ports: {available_ports}')
        port_index = 1  # Choosing the first available port by default
        if midi_out.is_port_open():
            print(f"The port {available_ports[port_index]} is already open.")
        else:
            midi_out.open_port(port_index)
            print(f"The port {available_ports[port_index]} has been opened.")
    else:
        print(f"No available MIDI ports found. Please check your MIDI setup.")

    return midi_out

def main_loop(midi_players):
    while metronome.startFlag:
        if metronome.doneFlag == 1:
            threads = []
            for midi_player, midi_data in zip(midi_players, midi_data_list):
                threads.append(threading.Thread(target=midi_player.play_beat, args=(midi_data,)))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

if __name__ == "__main__":
    metronome = Metronome(bpm=60)
    midi_out = initialize_midi_player()

    builder1 = buildMidi.MidiBuilder(dataType=0, midiMessage=[60], ch=0, velocity=64, rate='q')
    result1 = builder1.build_midi()

    builder2 = buildMidi.MidiBuilder(dataType=1, shape=1, signal_invert=0, ch=2, min_val=0, rate='h', midiCCNum=2)
    result2 = builder2.build_midi()

    builder3 = buildMidi.MidiBuilder(dataType=2, ch=1, oldTof=60, newTof=80, rate='w', midiCCNum=2)
    result3 = builder3.build_midi()

    midi_data_list = [result1, result2, result3]
    midi_players = [MidiPlayer(midi_out, metronome.getTimeTick(midi_data), midi_data) for midi_data in midi_data_list]
    midi_players[1].onFlag = 1

    metronome.startMetro(True)
    main_loop(midi_players)
