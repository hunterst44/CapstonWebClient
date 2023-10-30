import time
import threading
import buildMidi

#Function of this class: To sync midi events to a global clock and calculate the time delays for array type midi commands
#How it works Midi clock is initalized when the play button is pressed, it takes the bpm from the GUI and calculates the milliseconds per beat
# The milliseconds per beat is the total time per a bar of music. We want to be able to divide this chunk of time into smaller chunks so we can modify the following paramiters
    # Be able to play diffrent



class Metronome:
    def __init__(self, bpm=60, startFlag=False, BPM_millis=0, doneFlag = 0):
        self.bpm = bpm
        self.startFlag = startFlag
        self.stopFlag = False
        self.BPM_millis = BPM_millis
        self.doneFlag = doneFlag

    def timer_function(self, interval):
        while not self.stopFlag:
            print(f"Timer: {interval} seconds")
            time.sleep(interval)
            self.doneFlag = 1

    def startMetro(self, offONState):
        self.startFlag = offONState
        self.BPM_millis = (60 / self.bpm) * 1000
        if self.startFlag:
            timer_thread = threading.Thread(target=self.timer_function, args=(self.BPM_millis / 1000,))
            timer_thread.start()
            print("Metronome started.")
        else:
            self.stopFlag = True
            print("Metronome stopped.")

    def getTimeTick(self, midiArray = []):
        midiCount = len(midiArray)
        self.BPM_millis = (60 / self.bpm) * 1000
        timeSlice = self.BPM_millis/midiCount-1
        return timeSlice

    @staticmethod
    def getSubdivisionCount(noteVal):
        if noteVal == 'w':
            return 1
        elif noteVal == 'h':
            return 2
        elif noteVal == 't':
            return 3
        elif noteVal == 'q':
            return 4
        elif noteVal == 'e':
            return 8
        elif noteVal == 's':
            return 16
        else:
            return 1  # Default value for an unknown note value

# # Builder for MIDI note data
# builder1 = buildMidi.MidiBuilder(dataType=0, midiMessage=[60], ch=0, velocity=64, rate = 'q')
# result1 = builder1.buildMidi()

# # Builder for MIDI control change data
# builder2 = buildMidi.MidiBuilder(dataType=1, shape=0, signal_invert=0, midiCC_ch=1, min_val=0, rate = 'q')
# result2 = builder2.buildMidi()

# # Builder for MIDI control Tof data
# builder3 = buildMidi.MidiBuilder(dataType=2, shape=0, signal_invert=0, midiCC_ch=1, oldTof=65, newTof=65, rate = 'w')
# result3 = builder3.buildMidi()

# # Example usage:
# metronome = Metronome()
# print(metronome.getTimeTick(result1))
# print(metronome.getTimeTick(result2))
# print(metronome.getTimeTick(result3))
# metronome.startMetro(True)

# # To stop the thread
# time.sleep(5)
# metronome.startMetro(False)


