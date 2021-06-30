import numpy as np
import pyaudio

from Chromagram import Chromagram

class ChordDetector:
    def __init__(self):
        self.chord_profiles = np.zeros((108,12))

        v1 = 1
        v2 = 1
        v3 = 1

        j = 0

        #Major
        for i in range(12):
            root = i % 12
            third = (i+4) % 12
            fifth = (i+7) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3

            j+=1

        #Minor
        for i in range(12):
            root = i % 12
            third = (i+3) % 12
            fifth = (i+7) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3

            j+=1

        #Diminished
        for i in range(12):
            root = i % 12
            third = (i+3) % 12
            fifth = (i+6) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3

            j+=1

        #Augmented
        for i in range(12):
            root = i % 12
            third = (i+4) % 12
            fifth = (i+8) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3

            j+=1

        #Sus2
        for i in range(12):
            root = i % 12
            third = (i+2) % 12
            fifth = (i+7) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3

            j+=1

        #Sus4
        for i in range(12):
            root = i % 12
            third = (i+5) % 12
            fifth = (i+7) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3

            j+=1

        #Major 7th
        for i in range(12):
            root = i % 12
            third = (i+4) % 12
            fifth = (i+7) % 12
            seventh = (i+11) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3
            self.chord_profiles[j, seventh] = v3

            j+=1

        #Minor 7th
        for i in range(12):
            root = i % 12
            third = (i+3) % 12
            fifth = (i+7) % 12
            seventh = (i+10) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3
            self.chord_profiles[j, seventh] = v3

            j+=1

        #Dominant 7th
        for i in range(12):
            root = i % 12
            third = (i+4) % 12
            fifth = (i+7) % 12
            seventh = (i+10) % 12

            self.chord_profiles[j, root] = v1
            self.chord_profiles[j, third] = v2
            self.chord_profiles[j, fifth] = v3
            self.chord_profiles[j, seventh] = v3

            j+=1

    def calculate_chord_score(self, chroma, chord_profile, bias_to_use, N):
        sum = 0

        for i in range(12):
            sum += (1-chord_profile[i]) * chroma[i]**2

        delta = np.sqrt(sum)/((12-N)*bias_to_use)

        return delta

    def classify_chromagram(self, chroma):
        chromagram = np.copy(chroma)
        bias = 1.06
        chord = np.zeros(108)

        for i in range(12):
            fifth = (i+7) % 12
            chromagram[fifth] -= (0.1*chromagram[i])

            if chromagram[fifth] < 0:
                chromagram[fifth] = 0

        for j in range(48):
            chord[j] = self.calculate_chord_score(chromagram, self.chord_profiles[j],bias,3)

        for j in range(48,72):
            chord[j] = self.calculate_chord_score(chromagram, self.chord_profiles[j],1,3)

        for j in range(72,84):
            chord[j] = self.calculate_chord_score(chromagram, self.chord_profiles[j],1,4)

        for j in range(84, 108):
            chord[j] = self.calculate_chord_score(chromagram, self.chord_profiles[j],bias,4)

        return np.argmin(chord), chord[np.argmin(chord)], max(chord)

if __name__ == "__main__":
    CHUNK = 2**15
    RATE = 44100

    index_to_note = ["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]
    type_of_chord = ["Major", "Minor", "Diminished", "Augmented", "Sus2", "Sus4", "Major 7th", "Minor 7th", "Dominant 7th"]

    chroma = Chromagram(CHUNK, RATE)#, buffer_size=2**14)#, reference_freq=65.41, num_octaves=3)
    chord = ChordDetector()
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK)

    while True:
        data = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
        print(max(np.abs(data)))
        """print(data.shape)
        peak=np.average(np.abs(data))*2
        bars="#"*int(50*peak/2**16)
        print("%04d %05d %s"%(i,peak,bars))"""
        chroma.process_audio_frame(data)
        if max(np.abs(data)) > 100:
            if(chroma.chroma_ready):
                pred, score, max_score = chord.classify_chromagram(chroma.chromagram)
                root = index_to_note[pred%12]
                type = type_of_chord[int(pred//12)]
                print(root, type, score, max_score - score)

    stream.stop_stream()
    stream.close()
    p.terminate()
