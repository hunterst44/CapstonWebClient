import rtmidi
import threading
import time
import random

class MidiArp:
    def __init__(self, midiIn_port_index = 3, octave = 0, order = 0):
        self.midi_in = rtmidi.MidiIn()
        self.midi_in.open_port(midiIn_port_index)
        self.held_notes = set()
        self.is_running = False
        self.shifted = 0
        self.octave = octave
        self.order = order
        

    def process_messages(self):
        # self.is_running = True
        try:
            while self.is_running:
                msg = self.midi_in.get_message()

                if msg:
                    self._handle_midi_message(msg[0])
                time.sleep(0.001)
                
                print(f"Currently Held Notes: {self.held_notes}")
                print("Hello")
                if self.is_running == False:
                    return

        except KeyboardInterrupt:
            pass

        finally:
            self.midi_in.close_port()
            print("MIDI input port closed.")

    def _handle_midi_message(self, msg):
        note_value = msg[1]
        velocity = msg[2]

        if msg[0] & 0xF0 == 0x90:  # Note-on
            if velocity != 0:  # Only consider note-on events with velocity > 0
                self.held_notes.add(note_value)
        elif msg[0] & 0xF0 == 0x80:  # Note-off
            self.held_notes.discard(note_value)

    def start_processing_thread(self):
        thread = threading.Thread(target=self.process_messages)
        self.is_running = True
        thread.start()

    def stop_processing_thread(self):
        self.is_running = False
        # self.thread.join()
        

    def reorder_held_notes(self):
        if self.order == 0:
            # Sort notes in ascending order
            self.held_notes = set(sorted(self.held_notes))
        elif self.order == 1:
            # Sort notes in descending order
            self.held_notes = set(sorted(self.held_notes, reverse=True))
        elif self.order == 2:
            # Shuffle notes randomly
            self.held_notes = set(random.sample(self.held_notes, len(self.held_notes)))
        else:
            print("Invalid order. Use 0 for ascending, 1 for descending, or 2 for random.")

    def change_octave(self):
        # Shift the octaves of held notes within the specified range
        if self.shifted == 0 and len(self.held_notes) != 0:
            self.held_notes = {note_value + self.shift * 12 for note_value in self.held_notes}
            self.shifted = 1
            
        

# if __name__ == "__main__":
#     # Choose the desired input port index (change this to the appropriate index)
#     midiIn_port_index = 3

#     # Create an instance of MidiArp
#     midi_note_manager = MidiArp(midiIn_port_index)

#     # Start processing MIDI messages in a separate thread
#     midi_note_manager.start_processing_thread()

#     try:
#         while True:
#             # Print the held notes every second in the main thread
            
            
#             # Change order every 5 seconds
            
#             midi_note_manager.reorder_held_notes(2)

#             # Shift the octaves every 7 seconds
           
#             midi_note_manager.change_octave(2)

#             print(f"Currently Held Notes: {midi_note_manager.held_notes}")

#             time.sleep(1)

#     except KeyboardInterrupt:
#         # Stop the processing thread when the main thread is interrupted
#         midi_note_manager.stop_processing_thread()
