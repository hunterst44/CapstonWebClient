import rtmidi
import threading
import time
import random

class MidiArp:
    def __init__(self, midiIn_port_index = 3, octave = 2, order = 0, modified_Midi = [], current_Midi = []):
        self.midi_in = rtmidi.MidiIn()
        self.midi_in.open_port(3)
        self.held_notes = set()
        self.is_running = False
        self.shifted = 0
        self.octave = octave
        self.order = order
        self.current_Midi = current_Midi
        self.modified_Midi = modified_Midi
        

    def process_messages(self):
        # self.is_running = True
        # self.reorder_held_notes()
        # self.change_octave()
        try:
            while self.is_running:
                msg = self.midi_in.get_message()

                if msg:
                    self._handle_midi_message(msg[0])
                time.sleep(0.001)
                
                # print(f"Currently Held Notes: {self.held_notes}")
                # print("Hello")
                if self.is_running == False:
                    return
                self.update_Midi()
                self.reorder_Midi()
                self.change_octave
                
                

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
        if self.is_running == False:
            thread = threading.Thread(target=self.process_messages)
            self.is_running = True
            thread.start()
        # thread.join()

    def stop_processing_thread(self):
        self.is_running = False
        # self.thread.join()
        

    def reorder_Midi(self):
        if self.held_notes:
            if self.order == 0 or 'Up':
                # Sort notes in ascending order
                self.current_Midi = sorted(self.modified_Midi)
                # print(self.modified_Midi)
            elif self.order == 1 or 'Down':
                # Sort notes in descending order
                self.current_Midi = sorted(self.modified_Midi, reverse=True)
            elif self.order == 2 or 'Random':
                # Shuffle notes randomly
                self.current_Midi = random.sample(self.modified_Midi, len(self.modified_Midi))
            else:
                print("Invalid order. Use 0 for ascending, 1 for descending, or 2 for random.")

    def change_octave(self, oct):
        # Shift the octaves of held notes within the specified range
        if -2 <= self.octave <= 2 and len(self.modified_Midi) != 0:
            self.current_Midi = {note_value + oct * 12 for note_value in self.modified_Midi}
            # print(self.modified_Midi)
            
    def update_Midi(self):
        self.modified_Midi = self.held_notes
        if not self.held_notes:
            self.current_Midi = []
            
            
        

if __name__ == "__main__":
    # Choose the desired input port index (change this to the appropriate index)
    midiIn_port_index = 3

    # Create an instance of MidiArp
    midi_note_manager = MidiArp(midiIn_port_index)

    # Start processing MIDI messages in a separate thread
    midi_note_manager.start_processing_thread()

    try:
        order_change_interval = 5  # Change order every 5 seconds
        order_counter = 0

        while True:
            #Update the midi from held notes
            
            # Print the held notes every second in the main thread
            print(f"Currently Held Notes: {midi_note_manager.current_Midi}")

            time.sleep(1)

            
            midi_note_manager.reorder_Midi()
            midi_note_manager.change_octave()
            

            print(f"Currently Held Notes MODIFIED: {midi_note_manager.modified_Midi}")

            time.sleep(1)

    except KeyboardInterrupt:
        # Stop the processing thread when the main thread is interrupted
        midi_note_manager.stop_processing_thread()
