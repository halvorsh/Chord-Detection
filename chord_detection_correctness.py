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

output = open("Classification_eval.txt", 'w')
output.write("Evaluation of Classification")
output.close()

with open("Classification.txt", 'r') as file:
    chord_count = 0
    distance_sum = 0
    correct_identifications = 0
    current_chord = -1

    output = open("Classification_eval.txt", 'a')

    line = file.readline()
    line = file.readline()

    while line:
        if len(line) != 1:
            line = line.strip()
            if ".wav" in line:
                if current_chord >= 0:
                    average_distance = distance_sum/chord_count
                    output.write("\nAverage distance: " + str(average_distance))
                    output.write("\nNumber of identifications: " + str(chord_count))
                    output.write("\nNumber of correct identifications: " + str(correct_identifications))
                    output.write("\nPercentage of correct identifications: " + str(correct_identifications/chord_count))
                    output.write("\n")

                    chord_count = 0
                    distance_sum = 0
                    correct_identifications = 0

                chord = chord_of_wav(line)
                chord_number = get_chord_number(chord)
                current_chord = chord_number
                output.write("\nIdentification for " + chord)
            else:
                chord_number = get_chord_number(line)
                difference = np.sum((profiles[current_chord] - profiles[chord_number])**2)
                if difference == 0:
                    correct_identifications += 1

                chord_count += 1
                distance_sum += difference

        line = file.readline()

    average_distance = distance_sum/chord_count
    output.write("\nAverage distance: " + str(average_distance))
    output.write("\nNumber of identifications: " + str(chord_count))
    output.write("\nNumber of correct identifications: " + str(correct_identifications))
    output.close()
"""
print(get_chord_number("E Augmented"))
print(get_chord_number("Ab Minor 7th"))
"""
