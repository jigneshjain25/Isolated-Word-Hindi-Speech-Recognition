# prints duration of audio file
import wave
import contextlib
print "enter file name"
fname = raw_input()
with contextlib.closing(wave.open(fname,'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
    print(duration)
