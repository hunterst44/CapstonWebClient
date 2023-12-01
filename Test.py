import rtmidi
import threading
import time
import random

class MidiArp:
    class MidiCircularBuffer:
        def __init__(self):
            self.buffer = [None] * 16
            self.current_index = 0
            self.size = 0

        def add_midi_message(self, message):
            
            self.buffer[self.current_index-1] = message
            self.current_index = (self.current_index + 1) % 16
            if self.size < 16:
                self.size += 1

        def get_midi_message(self, index):
            if index < 0 or index >= self.size:
                return None
            actual_index = (self.current_index - self.size + index) % 16
            return self.buffer[actual_index -1]

    def __init__(self, midiIn_port_index=3, octave=2, order=0):
        self.midi_in = rtmidi.MidiIn()
        self.midi_in.open_port(midiIn_port_index)
        self.held_notes = set()
        self.lock = threading.Lock()
        self.is_running = False
        self.octave = octave
        self.order = order
        self.midi_Buffer = self.MidiCircularBuffer()
        self.buffer_index = 0
        self.current_Midi = [0]

    def process_messages(self):
        try:
            while self.is_running:
                msg = self.midi_in.get_message()

                if msg:
                    with self.lock:
                        self._handle_midi_message(msg[0])

                time.sleep(0.001)

                with self.lock:
                    self.update_Midi()

        except KeyboardInterrupt:
            pass

        finally:
            self.midi_in.close_port()
            print("MIDI input port closed.")

    def _handle_midi_message(self, msg):
        status_byte = msg[0]
        note_value = msg[1]
        velocity = msg[2]

        if status_byte >> 4 == 0x9 and velocity != 0:
            self.held_notes.add(note_value)
        elif status_byte >> 4 == 0x8 or (status_byte >> 4 == 0x9 and velocity == 0):
            self.held_notes.discard(note_value)

    def start_processing_thread(self):
        if not self.is_running:
            thread = threading.Thread(target=self.process_messages)
            self.is_running = True
            thread.start()

    def stop_processing_thread(self):
        self.is_running = False

    def update_Midi(self):
        if self.midi_Buffer.buffer[0] != []:
            self.midi_Buffer.size = len(self.held_notes)  # Reset the buffer size
            for notes in self.held_notes:
                self.midi_Buffer.buffer.append(notes)
            self.reorder_Midi()
            self.change_octave()
            self.update_Midi_Buffer()
        else:
            self.midi_Buffer.buffer = []

    def reorder_Midi(self):
        if self.midi_Buffer.buffer[0] != None:
            if self.order == 0 or self.order == 'Up':
                self.midi_Buffer.buffer = sorted(self.midi_Buffer.buffer)
            elif self.order == 1 or self.order == 'Down':
                self.midi_Buffer.buffer = sorted(self.midi_Buffer.buffer, reverse=True)
            elif self.order == 2 or self.order == 'Random':
                random.shuffle(self.midi_Buffer.buffer)
            else:
                print("Invalid order. Use 0 for ascending, 1 for descending, or 2 for random.")

    def change_octave(self):
        if self.midi_Buffer.buffer[0] != None:
            if -2 <= self.octave <= 2:
                self.midi_Buffer.buffer = [note_value + self.octave * 12 for note_value in self.midi_Buffer.buffer]

    def update_Midi_Buffer(self):
        print(self.current_Midi)
        sizeOfBuffer = self.midi_Buffer.size
        if sizeOfBuffer == 0:
            print("MIDI buffer is empty.")
            return

        self.buffer_index = (self.buffer_index) % sizeOfBuffer

        print(f'Current buffer position: {self.buffer_index}')

        self.current_Midi = self.midi_Buffer.get_midi_message(self.buffer_index)

if __name__ == "__main__":
    midiIn_port_index = 3
    midi_note_manager = MidiArp(midiIn_port_index)
    midi_note_manager.start_processing_thread()

    try:
        while True:
            print(f"Currently Held Notes: {midi_note_manager.midi_Buffer.buffer}")
            time.sleep(1)

    except KeyboardInterrupt:
        midi_note_manager.stop_processing_thread()
