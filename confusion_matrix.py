from ChordDetector import ChordDetector
import numpy as np

def get_chord_number(chord):
    note_to_index = {"C":0,"C#":1,"D":2,"Eb":3,"E":4,"F":5,"F#":6,"G":7,"Ab":8,"A":9,"Bb":10,"B":11}
    type_of_chord = {"Major":0, "Minor":1, "Diminished":2, "Augmented":3, "Sus2":4, "Sus4":5, "Major 7th":6, "Minor 7th":7, "Dominant 7th":8}

    split = chord.split(" ")
    root = split[0]
    type = ""
    if len(split) == 3:
        type = split[1] + " " + split[2]
    else:
        type = split[1]

    root_num = note_to_index[root]
    type_num = type_of_chord[type]

    chord_number = type_num*12 + root_num

    return chord_number

def get_chord_from_number(number):
    index_to_note = ["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]
    type_of_chord = ["Major", "Minor", "Diminished", "Augmented", "Sus2", "Sus4", "Major 7th", "Minor 7th", "Dominant 7th"]

    root = index_to_note[number%12]
    type = type_of_chord[int(number//12)]

    chord = root + " " + type
    return chord

def chord_of_wav(wav_name):
    root = wav_name[0].upper()
    if wav_name[1] == '#':
        root += "#"

        if root == "A#":
            root = "Bb"
        elif root == "G#":
            root = "Ab"
        elif root == "D#":
            root = "Eb"

    type = ""
    if "maj7" in wav_name:
        type = "Major 7th"
    elif "min7" in wav_name:
        type = "Minor 7th"
    elif "sus4" in wav_name:
        type = "Sus4"
    elif "sus2" in wav_name:
        type = "Sus2"
    elif "aug" in wav_name:
        type = "Augmented"
    elif "dim" in wav_name:
        type = "Diminished"
    elif "7" in wav_name:
        type = "Dominant 7th"
    elif "maj" in wav_name:
        type = "Major"
    elif "min" in wav_name:
        type = "Minor"
    else:
        print("OH GOD SOMETHING IS WRONG YOU FUCKED UP")

    return root + " " + type

chord = ChordDetector()
profiles = chord.chord_profiles

output = open("Confusion Matrix.csv", 'w')
output.write("Predicted\Actual," + ",".join(map(str,[get_chord_from_number(i) for i in range(len(profiles))])))
output.close()

with open("Classification.txt", 'r') as file:
    confusion_matrix = np.zeros((len(profiles), len(profiles)))
    current_chord = -1

    line = file.readline()
    line = file.readline()

    while line:
        if len(line) != 1:
            line = line.strip()
            if ".wav" in line:

                chord = chord_of_wav(line)
                chord_number = get_chord_number(chord)
                current_chord = chord_number
            else:
                chord_number = get_chord_number(line)
                confusion_matrix[chord_number, current_chord] += 1

        line = file.readline()

    np.set_printoptions(threshold=np.inf)
    output = open("Confusion Matrix.csv", 'a')
    for i in range(len(profiles)):
        chord = get_chord_from_number(i)
        towrite = "\n" + chord + "," + ",".join(map(str, confusion_matrix[i]))
        output.write(towrite)
    output.close()
