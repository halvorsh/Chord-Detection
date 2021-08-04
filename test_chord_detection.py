import numpy as np
import pyaudio
import wave
import sys
from os import listdir
from tqdm import tqdm

from Chromagram import Chromagram
from ChordDetector import ChordDetector

OUTPUT_FILE = "Classification.txt"

f = open(OUTPUT_FILE, "w")
f.write("Chord Classification\n")
f.close()

def detect_chord_on_wav_file(file):
    global OUTPUT_FILE
    CHUNK = 2**14
    RATE = 44100
    BUFFERSIZE = CHUNK*2

    index_to_note = ["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]
    type_of_chord = ["Major", "Minor", "Diminished", "Augmented", "Sus2", "Sus4", "Major 7th", "Minor 7th", "Dominant 7th"]
    f = open(OUTPUT_FILE, "a")
    f.write(file + "\n")

    file = "../Wav Dataset/" + file
    chroma = Chromagram(CHUNK, RATE)#, buffer_size = BUFFERSIZE)
    chord = ChordDetector()
    wf = wave.open(file, 'rb')
    while wf.tell() < wf.getnframes():
        data = np.frombuffer(wf.readframes(CHUNK), dtype=np.int16)
        if len(data) < CHUNK:
            break
        chroma.process_audio_frame(data)
        spectrum_dif = chroma.magnitude_spectrum - chroma.previous_spectrum
        pos_values = spectrum_dif[spectrum_dif>0]
        new_energy = np.sum(pos_values)
        root_num = 1
        if new_energy > 100000:
            pred = chord.classify_chromagram(chroma.chromagram)
            root = index_to_note[pred%12]
            type = type_of_chord[int(pred//12)]
            f.write(root+" "+type+"\n")

    f.write("\n")
    f.close()
    wf.close()

all_audio_files = listdir("../Wav Dataset")
#detect_chord_on_wav_file(all_audio_files[40])
for file in tqdm(all_audio_files):
    detect_chord_on_wav_file(file)
