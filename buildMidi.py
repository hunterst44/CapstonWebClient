import numpy as np
from scipy import signal
from rtmidi.midiconstants import CONTROL_CHANGE
import matplotlib.pylab as plt
import time

BPM = 30

class Rate:
    whole = 'w'
    half = 'h'
    triplet = 't'
    quarter = 'q'
    eighth = 'e'
    sixteenth = 's'
    
class MidiBuilder:
    def __init__(self, dataType=0, midiMessage=[], ch=0, note=0, velocity=0, shape=0, signal_invert=0, midiCC_ch=0, min_val=0, max_val=127, deltaToF=0, oldTof=0, newTof=0, rate=Rate.whole, midiCCNum=75.):
        self.dataType = dataType
        self.midiMessage = midiMessage
        self.ch = ch
        self.note = note
        self.velocity = velocity
        self.shape = shape
        self.signal_invert = signal_invert
        self.midiCC_ch = midiCC_ch
        self.min_val = min_val
        self.max_val = max_val
        self.deltaToF = deltaToF
        self.oldTof = oldTof
        self.newTof = newTof
        self.rate = rate
        self.midiCCnum = midiCCNum
        self.threshold = 1  # Adjust this threshold as needed


    def modulation_shape(self):
        x = np.arange(0, 1 / self.multiply_rate(self.rate), 0.01)

        y = 1
        sig_invert = 1

        if self.signal_invert:
            sig_invert = -1

        if self.shape == 0:  # 'sine'
            y = sig_invert * np.sin(2 * self.multiply_rate(self.rate) * np.pi * x)
        elif self.shape == 1:  # 'saw'
            y = sig_invert * signal.sawtooth(2 * self.multiply_rate(self.rate) * np.pi * x)
        elif self.shape == 2:  # 'square'
            y = sig_invert * signal.square(2 * self.multiply_rate(self.rate) * np.pi * x)
        else:
            print("That wave is not supported")

        return y

    def convert_range(self, value, in_min, in_max, out_min, out_max):
        l_span = in_max - in_min
        r_span = out_max - out_min
        scaled_value = (value - in_min) / l_span
        scaled_value = out_min + (scaled_value * r_span)
        return np.round(scaled_value)

    def generate_deltaTof_array(self):
            deltaArray = []

            if abs(self.newTof - self.oldTof) > self.threshold:
                if self.newTof > self.oldTof:
                    deltaArray = list(range(self.oldTof, self.newTof + 1))
                elif self.newTof < self.oldTof:
                    deltaArray = list(range(self.oldTof, self.newTof - 1, -1))

            self.oldTof = self.newTof
            return deltaArray

    def multiply_rate(self, rate):
        if rate == Rate.whole:
            return 1
        elif rate == Rate.half:
            return 2
        elif rate == Rate.triplet:
            return 3
        elif rate == Rate.quarter:
            return 4
        elif rate == Rate.eighth:
            return 8
        elif rate == Rate.sixteenth:
            return 16
        else:
            return 1  # Default value for an unknown note value

    def build_midi(self):
        midi_array = []
        if self.dataType == 0:  # for MIDI note data
            if isinstance(self.midiMessage, int):
                note = int(self.midiMessage)
                note_on = self.MIDINoteMessage(ch=self.ch, note=note, velocity=self.velocity)
                midi_array.append(note_on.get_midi())

                    # Add a small delay between note-on and note-off (adjust as needed)
                    # time.sleep(0.1)

                    # Create MIDI note-off message
                note_off = self.MIDINoteMessage(ch=self.ch, note=note, velocity=0)
                midi_array.append(note_off.get_midi())

            return midi_array
            for _ in range(self.multiply_rate(self.rate)):
                for note in set(self.midiMessage):  # Create a copy of the set
                    # Create MIDI note-on message
                    note_on = self.MIDINoteMessage(ch=self.ch, note=note, velocity=self.velocity)
                    midi_array.append(note_on.get_midi())

                    # Add a small delay between note-on and note-off (adjust as needed)
                    # time.sleep(0.1)

                    # Create MIDI note-off message
                    note_off = self.MIDINoteMessage(ch=self.ch, note=note, velocity=0)
                    midi_array.append(note_off.get_midi())

            return midi_array
        elif self.dataType == 1:  # for MIDI control change data
            waveform = self.modulation_shape()
            waveform = self.convert_range(waveform, -1.0, 1.0, 0, 127)
            waveform = self.convert_range(waveform, 0, 127, self.min_val, self.max_val)
            for _ in range(self.multiply_rate(self.rate)):
                for value in waveform:
                    midiCC = self.MIDIControlChange(channel=self.ch, control_number=self.midiCCnum, control_value=value)
                    midi_array.append(midiCC.get_midi_cc())
            return midi_array
        elif self.dataType == 2:  # for MIDI control Tof data
            tof_delta_array = self.generate_deltaTof_array()
            for value in tof_delta_array:
                midiCC = self.MIDIControlChange(control_number=self.midiCCnum, channel=self.ch, control_value=value)
                midi_array.append(midiCC.get_midi_cc())
            return midi_array

    class MIDIControlChange:
        def __init__(self, control_number, control_value, channel=0):
            self.control_number = control_number
            self.control_value = control_value
            self.channel = channel

        def get_midi_cc(self):
            return [CONTROL_CHANGE |  self.channel, self.control_number, self.control_value]

    class MIDINoteMessage:
        def __init__(self, ch=0, note=0, velocity=0):
            self.ch = ch
            self.note = note
            self.velocity = velocity

        def get_midi(self):
            noteON = [int(self.ch) + 0x90, int(self.note), int(self.velocity)]
            noteOFF = [int(self.ch) + 0x80, int(self.note), int(self.velocity)]
            return noteON

# # Builder for MIDI note data
# builder1 = MidiBuilder(dataType=0, midiMessage=[60, 62, 64], ch=0, velocity=64)

# # Builder for MIDI control change data
# builder2 = MidiBuilder(dataType=1, shape=0, signal_invert=0, midiCC_ch=1, min_val=0)

# # Builder for MIDI control Tof data
# builder3 = MidiBuilder(dataType=2, midiCC_ch=2, oldTof=65, newTof=75)

# # Printing the results
# print("Builder 1 - MIDI Note Data:")
# result1 = builder1.build_midi()
# for midi in result1:
#     print(midi)

# print("\nBuilder 2 - MIDI Control Change Data:")
# result2 = builder2.build_midi()
# for midi in result2:
#     print(midi)

# print("\nBuilder 3 - MIDI Control Tof Data:")
# result3 = builder3.build_midi()
# for midi in result3:
#     print(midi)
