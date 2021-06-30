import numpy as np
import scipy.fft as fft
import pyaudio

class Chromagram:
    def __init__(self, frame_size, fs,
            reference_freq = 130.81278265,
            buffer_size = 8192,
            num_harmonics = 2,
            num_octaves = 2,
            num_bins_to_search = 2):

        self.note_frequencies = reference_freq*np.power(2, [i/12 for i in range(12)])

        self.num_harmonics = num_harmonics
        self.num_octaves = num_octaves
        self.num_bins_to_search = num_bins_to_search

        self.buffer = np.zeros(buffer_size)
        self.chromagram = np.zeros(12)
        self.magnitude_spectrum = np.zeros(int(buffer_size/2)+1)

        self.make_hamming_window(buffer_size)

        self.sampling_frequency = fs

        self.input_audio_frame_size = frame_size
        self.downsampled = np.zeros(int(frame_size/4))

        self.num_samples_since_last_calculation = 0

        self.chroma_calculation_interval = 4096

        self.chroma_ready = False

    def process_audio_frame(self, input_audio_frame):
        self.chroma_ready = False

        self.downsample_frame(input_audio_frame)

        self.buffer = np.roll(self.buffer, len(self.downsampled))

        self.buffer[:len(self.downsampled)] = self.downsampled

        self.num_samples_since_last_calculation += len(input_audio_frame)

        if self.num_samples_since_last_calculation > self.chroma_calculation_interval:
            self.calculate_chromagram()
            self.num_samples_since_last_calculation = 0

    def calculate_chromagram(self):
        self.calculate_magnitude_spectrum()

        divisor_ratio = (self.sampling_frequency/4)/len(self.buffer)

        for i in range(12):
            chromasum = 0

            for j in range(self.num_octaves):
                notesum = 0

                for k in range(1,self.num_harmonics+1):
                    #print(self.note_frequencies, j, k, divisor_ratio)
                    center_bin = int(np.around(self.note_frequencies[i]*(2**j)*k/divisor_ratio))
                    min_bin = center_bin - self.num_bins_to_search*k
                    max_bin = center_bin + self.num_bins_to_search*k

                    maxval = 0

                    for l in range(min_bin, max_bin):
                        if self.magnitude_spectrum[l] > maxval:
                            maxval = self.magnitude_spectrum[l]

                    notesum += maxval / k
                chromasum += notesum
            self.chromagram[i] = chromasum
        self.chroma_ready = True

    def downsample_frame(self, input_audio_frame):
        filtered_frame = np.zeros(self.input_audio_frame_size)
        b0 = 0.2929
        b1 = 0.5858
        b2 = 0.2929
        a1 = -0.0000
        a2 = 0.1716

        x_1 = 0
        x_2 = 0
        y_1 = 0
        y_2 = 0

        for i in range(self.input_audio_frame_size):
            filtered_frame[i] = input_audio_frame[i] * b0 + x_1 * b1 + x_2 * b2 - y_1 * a1 - y_2 * a2

            x_2 = x_1
            x_1 = input_audio_frame[i]
            y_2 = y_1
            y_1 = filtered_frame[i]

        for i in range(int(self.input_audio_frame_size/4)):
            self.downsampled[i] = filtered_frame[i*4]

    def calculate_magnitude_spectrum(self):
        self.magnitude_spectrum = np.sqrt(np.abs(fft.rfft(self.buffer)))

    def make_hamming_window(self, buffer_size):
        self.window = np.array([0.54 - 0.46 * np.cos(2 * np.pi * (i /buffer_size)) for i in range(buffer_size)])

if __name__ == "__main__":
    CHUNK = 2**16
    RATE = 44100

    index_to_note = ["C","C#","D","D#","E","F","F#","G","Ab","A","Bb","B"]

    chroma = Chromagram(CHUNK, RATE)#, reference_freq=65.41, num_octaves=3)
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK)

    for i in range(int(60*44100/1024)): #go for a few seconds
        data = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
        """print(data.shape)
        peak=np.average(np.abs(data))*2
        bars="#"*int(50*peak/2**16)
        print("%04d %05d %s"%(i,peak,bars))"""
        chroma.process_audio_frame(data)
        if(chroma.chroma_ready):
            idx = np.argsort(chroma.chromagram)[-3:]
            print(index_to_note[idx[2]],index_to_note[idx[1]],index_to_note[idx[0]])

    stream.stop_stream()
    stream.close()
    p.terminate()
