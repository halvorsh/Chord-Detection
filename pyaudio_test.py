import pyaudio
import numpy as np
import time
import queue
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

p = pyaudio.PyAudio()

CHANNELS = 2
RATE = 44100

def callback(in_data, frame_count, time_info, flag):
    # using Numpy to convert to array for processing
    audio_data = np.frombuffer(in_data, dtype=np.float32)
    print(in_data)
    print(max(audio_data))
    return audio_data, pyaudio.paContinue

def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata, fftdata
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data
        fftdata = sp.fft.rfft(plotdata)
    for column, line in enumerate(lines):
        line.set_ydata(fftdata[:, column])
    return lines


length = int(200 * RATE / (1000 * 10))
plotdata = np.zeros((length, 1))

fig, ax = plt.subplots()
lines = ax.plot(plotdata)
ax.axis((0, len(plotdata), -1, 1))
ax.set_yticks([0])
ax.yaxis.grid(True)
ax.tick_params(bottom=False, top=False, labelbottom=False,
               right=False, left=False, labelleft=False)
fig.tight_layout(pad=0)

stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=RATE,
                output=False,
                input=True,
                stream_callback=callback)
ani = FuncAnimation(fig, update_plot, interval=30, blit=True)
with stream:
    plt.show()

"""
stream.start_stream()

while stream.is_active():
    time.sleep(20)
    stream.stop_stream()
    print("Stream is stopped")

stream.close()

p.terminate()
"""
