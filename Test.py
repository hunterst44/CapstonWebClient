import rtmidi
import threading
import time
import random
from collections import deque

class MidiArp:
    def __init__(self, midiIn_port_index=3, octave=2, order=0):
        self.midi_in = rtmidi.MidiIn()
        self.midi_in.open_port(midiIn_port_index)
        self.held_notes = set()
        self.lock = threading.Lock()
        self.is_running = False
        self.octave = octave
        self.order = order
        self.current_Midi = []
        self.circular_buffer = deque()
        self.buffer_position = 0

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
                    self.update_buffer_position()

        except KeyboardInterrupt:
            pass

        finally:
            self.midi_in.close_port()
            print("MIDI input port closed.")

    def _handle_midi_message(self, msg):
        status_byte = msg[0]  # Status byte is the first element of the message
        note_value = msg[1]
        velocity = msg[2]

        if status_byte >> 4 == 0x9 and velocity != 0:  # Note-on
            self.held_notes.add(note_value)
        elif status_byte >> 4 == 0x8 or (status_byte >> 4 == 0x9 and velocity == 0):  # Note-off or Note-on with velocity 0
            self.held_notes.discard(note_value)

    def start_processing_thread(self):
        if not self.is_running:
            thread = threading.Thread(target=self.process_messages)
            self.is_running = True
            thread.start()

    def stop_processing_thread(self):
        self.is_running = False

    def update_Midi(self):
        if self.held_notes:
            self.current_Midi = sorted(self.held_notes)
            self.reorder_Midi()
            self.change_octave()
        else:
            self.current_Midi = []
            self.circular_buffer.clear()  # Clear buffer if no notes held

    def reorder_Midi(self):
        if self.order == 0 or self.order == 'Up':
            self.current_Midi = sorted(self.current_Midi)
        elif self.order == 1 or self.order == 'Down':
            self.current_Midi = sorted(self.current_Midi, reverse=True)
        elif self.order == 2 or self.order == 'Random':
            random.shuffle(self.current_Midi)
        else:
            print("Invalid order. Use 0 for ascending, 1 for descending, or 2 for random.")

    def change_octave(self):
        if -2 <= self.octave <= 2:
            self.current_Midi = [note_value + self.octave * 12 for note_value in self.current_Midi]

    def update_buffer_position(self):
        if self.current_Midi:
            if len(self.circular_buffer) == 0:
                self.circular_buffer.extend(self.current_Midi)
            self.buffer_position %= len(self.circular_buffer)

    def get_next_note_from_buffer(self):
        with self.lock:
            if self.circular_buffer:
                note = self.circular_buffer[self.buffer_position]
                self.buffer_position = (self.buffer_position + 1) % len(self.circular_buffer)
                return note
            return None

if __name__ == "__main__":
    midiIn_port_index = 3
    midi_note_manager = MidiArp(midiIn_port_index)
    midi_note_manager.start_processing_thread()

    try:
        while True:
            next_note = midi_note_manager.get_next_note_from_buffer()
            if next_note is not None:
                print(f"Next Note to Play: {next_note}")
            time.sleep(1)

    except KeyboardInterrupt:
        midi_note_manager.stop_processing_thread()
