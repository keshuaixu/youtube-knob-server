import sounddevice as sd
import numpy as np

fs = 48000
duration = 3  # seconds
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=32)
sd.wait()
print(np.sum(np.abs(myrecording)))
# print([x for x in myrecording if x.any != 0])
# print(myrecording)