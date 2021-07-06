import numpy as np
import pyaudio
import mido
import xml.etree.ElementTree as ET

from Chromagram import Chromagram
from ChordDetector import ChordDetector

NOTE_ON = [0, 47, 110, 111, 116, 101, 95, 111, 110]
NOTE_OFF = [0, 47, 110, 111, 116, 101, 95, 111, 102, 102, 32, 37, 105]
ALL_NOTES_OFF = [0, 47, 97, 108, 108, 95, 110, 111, 116, 101, 115, 95, 111, 102, 102]
BLINK = [0, 47, 98, 108, 105, 110, 107]
PORT = mido.open_output('Dr Squiggles:Dr Squiggles MIDI 1 20:0')

tree = ET.parse('../.squiggles_notes/squiggles_notes.xml')
root = tree.getroot()
NOTES = [int(root[i].text.strip()) for i in range(1,9)]
PREVIOUS_NOTE = None
print(NOTES)

def convert_note_to_solinoid(note):
    global PREVIOUS_NOTE
    midi_note = (note-4)%12+52
    note_to_play = None
    octaves = [0,1]
    np.random.shuffle(octaves)
    for i in octaves:
        tested_note = midi_note+12*i
        if tested_note in NOTES:
            PREVIOUS_NOTE = tested_note
            note_to_play = NOTES.index(tested_note)
            break
    if note_to_play != None:
        play_solinoid(note_to_play)
        return True
    return False

def play_solinoid(note):
    msg = mido.Message('sysex', data=NOTE_ON)
    msg.data += [32, note+48]
    PORT.send(msg)

def stop_play(note):
    msg = mido.Message('sysex', data=NOTE_OFF)
    msg.data += [32, note]
    PORT.send(msg)

def stop_all():
    msg = mido.Message('sysex', data=ALL_NOTES_OFF)
    PORT.send(msg)

def play_chord(chord):
    global PREVIOUS_NOTE
    notes_in_chord = [i for i, x in enumerate(chord) if x == 1]
    np.random.shuffle(notes_in_chord)
    for note in notes_in_chord:
        if convert_note_to_solinoid(note):
            break

def voice_leading(chord):
    global PREVIOUS_NOTE

    if PREVIOUS_NOTE == None:
        play_chord(chord)

    notes_in_chord = [i for i, x in enumerate(chord) if x == 1]
    possible_notes = []
    for note in notes_in_chord:
        midi_note = (note-4)%12+52
        for i in range(2):
            tested_note = midi_note+12*i
            if tested_note in NOTES:
                possible_notes.append(tested_note)

    if len(possible_notes) == 0:
        PREVIOUS_NOTE = None
        return

    min_distance = 48
    best_note = None
    for note in possible_notes:
        dist = np.abs(PREVIOUS_NOTE - note)
        if dist < min_distance and dist != 0:
            best_note = note

    print(PREVIOUS_NOTE, best_note, NOTES)
    PREVIOUS_NOTE = best_note
    if best_note != None:
        note_to_play = NOTES.index(best_note)
        play_solinoid(note_to_play)



CHUNK = 2**11
RATE = 44100

index_to_note = ["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]
type_of_chord = ["Major", "Minor", "Diminished", "Augmented", "Sus2", "Sus4", "Major 7th", "Minor 7th", "Dominant 7th"]

chroma = Chromagram(CHUNK, RATE, buffer_size=2**12)#, reference_freq=65.41, num_octaves=3)
chord = ChordDetector()
p=pyaudio.PyAudio()
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK)

while True:
    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow = False), dtype=np.int16)
    print(max(np.abs(data)))
    """print(data.shape)
    peak=np.average(np.abs(data))*2
    bars="#"*int(50*peak/2**16)
    print("%04d %05d %s"%(i,peak,bars))"""
    chroma.process_audio_frame(data)
    stop_all()
    if max(np.abs(data)) > 3000:
        if(chroma.chroma_ready):
            pred = chord.classify_chromagram(chroma.chromagram)
            root = index_to_note[pred%12]
            type = type_of_chord[int(pred//12)]
            print(root, type)
            voice_leading(chord.chord_profiles[pred])
stream.stop_stream()
stream.close()
p.terminate()
