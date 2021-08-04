from pydub import AudioSegment
from os import listdir
import os
import re

AudioSegment.converter = "../ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe   = "../ffmpeg/bin/ffprobe.exe"
#print(os.path.isfile(AudioSegment.converter))
#print(os.path.isfile(AudioSegment.ffprobe))

all_audio_files = listdir("../Chord Sounds")

current_chord = ""
current_audio = None

for file in all_audio_files:
    chord = re.match(".*?(?=-)", file).group(0)
    if chord != current_chord:
        if current_chord != "":
            current_audio.export("../Chord Dataset/" + current_chord + ".mp3", format="mp3")
        current_chord = chord
        current_audio = AudioSegment.empty()

    audiofile = "..\\Chord Sounds\\" + file

    print(os.path.isfile(audiofile))
    #with open("../Chord Sounds/" + file, 'r'):
        #print("It can be opened" )
    audio = AudioSegment.from_mp3(audiofile)
    current_audio += audio
