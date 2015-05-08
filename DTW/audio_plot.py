# plots graph of an audio file
from scipy.io.wavfile import read
import matplotlib.pyplot as plt, sys

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        input_data = read(sys.argv[1])
        audio = input_data[1]
        plt.plot(audio)
        plt.ylabel("Amplitude")
        plt.xlabel("Time")
        plt.title(sys.argv[1])
        plt.show()
