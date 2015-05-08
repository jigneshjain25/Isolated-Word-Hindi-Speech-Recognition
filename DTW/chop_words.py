import numpy as np
import scipy.io.wavfile as wav
from features.sigproc import framesig
import math, sys

winlen = 0.01
winstep = 0.01
sample_rate = 44100

min_signal = 0.0
threshold = 13.0
average_number=1.0
level = 0.0
adjustment = 0.004 #0.003
background = 300.0

# in terms of number of 10 ms frames
start_speech = 10
end_silence = 10
speech_leader = 5
speech_trailer = 5

voiced = []
sig = []
lrms = []

def get_signal(start, end):
    res = np.array([], dtype=np.int16)
    for i in xrange(start, end+1):
        if voiced[i]:
            res = np.append(res, sig[441*i : 441*(i+1)])
    return res

def log_root_mean_square(samples):
    sum_of_squares = sum(1.0*x*x for x in samples)
    root_mean_square = math.sqrt(sum_of_squares*1.0 / len(samples))
    root_mean_square = max(root_mean_square,1)
    return math.log10(root_mean_square) * 20
    
def classify(index):
    global level, background, average_number, threshold
    current = lrms[index]
    #current = log_root_mean_square(audio)
    is_speech = False
    if current >= min_signal:
        level = ((level * average_number) + current) / (average_number + 1)
        if current < background:
            background = current
        else:
            background += (current - background) * adjustment        
        if level < background:
            level = background            
        is_speech = (level - background > threshold)        
    return is_speech

def chop(output_folder = 'chopped-words', audio_file = 'recording.wav'):
    global voiced, sig, lrms, min_signal

    (rate,sig) = wav.read(audio_file)

    frames = framesig(sig, winlen*sample_rate, winstep*sample_rate,lambda x:np.ones((1,x)))

    lrms = [log_root_mean_square(x) for x in frames]
    min_signal = np.mean(lrms) / 2
    # min_signal = 0
    # print min_signal

    # dtype=int16 must for writing to wav file
    # result = np.array([], dtype=np.int16)

    for i in range(0,len(frames)):
        if classify(i):
            #result = np.append(result, sig[441*i : 441*(i+1)])
            voiced.append(True)
        else:
            voiced.append(False)

    started = False
    start_index = 0
    start_cnt = 0
    stop_index = 0
    stop_cnt = 0
    words = 0

    print ">> START_FRAME END_FRAME LENGTH_IN_SECONDS"

    for i in range(0,len(frames)):
        if not started:
            if voiced[i]:
                start_cnt += 1
            else:
                start_cnt = 0
            if start_cnt == start_speech:
                started = True
                start_index = i - start_speech + 1 - speech_leader
                start_index = max(0, start_index)
        else:
            if voiced[i]:
                stop_cnt = 0
            else:
                stop_cnt += 1
            if stop_cnt ==  end_silence:
                stop_index = i - end_silence + 1 + speech_trailer
                stop_index = min(len(frames)-1, stop_index)

                print ">>", start_index, stop_index, (stop_index - start_index + 1 ) * 10
                wav.write(output_folder + "/word" + str(words) + ".wav",rate, sig[441*start_index : 441*(stop_index+1)])
                #wav.write("word" + str(words) + ".wav",rate, get_signal(start_index , stop_index))
                words += 1
                
                started = False
                start_index = start_cnt = 0
                stop_index = stop_cnt = 0
        
    if started:
        stop_index = len(frames)-1
        print ">>", start_index, stop_index, (stop_index - start_index + 1 ) * 10
        wav.write(output_folder + "/word" + str(words) + ".wav",rate, sig[441*start_index : 441*(stop_index+1)])
        #wav.write("word" + str(words) + ".wav",rate, get_signal(start_index , stop_index))
        words += 1

    return words

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: python chop_words.py [AUDIO-FILE]"        
    else:
        print chop('chopped-words', sys.argv[1])
