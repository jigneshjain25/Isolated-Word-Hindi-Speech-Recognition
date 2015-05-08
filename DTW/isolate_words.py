import numpy, sys
import scipy.io.wavfile as wav
from features.sigproc import framesig
import math

winlen = 0.01
winstep = 0.01
sample_rate = 44100

# in terms of number of 10 ms frames
start_speech = 10
end_silence = 5
speech_leader = 5
speech_trailer = 5

def get_words(audio):
    (rate,sig) = wav.read(audio)
    frames = framesig(sig, winlen*sample_rate, winstep*sample_rate,lambda x:numpy.ones((1,x)))
    word_list = []
    
    #calculate energy per frame and zcr per frame
    frame_energy = []
    zcr = []
    for i in range(0,len(frames)):
        energy = sum(1.0*x*x for x in frames[i])
        zc = 0
        for j in range(1,len(frames[i])):
            if (frames[i][j]<0 and frames[i][j-1]>0) or (frames[i][j]>0 and frames[i][j-1]<0):
                zc = zc + 1
        frame_energy.append(energy)
        zcr.append(zc)
    
    #calculate final noise value
    avg_energy = sum(1.0*x for x in frame_energy[0:9])
    avg_energy = avg_energy/10
    avg_zcr = sum(1.0*x for x in frame_energy[0:9])
    avg_zcr = avg_zcr/10
    
    #calculate threshold
    upper_energy_threshold = 2*avg_energy
    upper_zcr_threshold = 2*avg_zcr
    lower_energy_threshold = 0.75*avg_energy
    lower_zcr_threshold = 0.75*avg_zcr

    print upper_energy_threshold
    print upper_zcr_threshold
    print lower_energy_threshold
    print lower_zcr_threshold
    
    started = False
    start_index = 0
    start_cnt = 0
    stop_index = 0
    stop_cnt = 0
    words = 0

    print ">> START_FRAME END_FRAME LENGTH_IN_SECONDS"

    for i in range(0,len(frames[10:])):
        if not started:
            if frame_energy[i]>upper_energy_threshold or zcr[i]>upper_zcr_threshold:
                start_cnt += 1
            else:
                start_cnt = 0
            if start_cnt == start_speech:
                started = True
                start_index = i - start_speech + 1 - speech_leader
                start_index = max(0, start_index)
        else:
            if frame_energy[i]>upper_energy_threshold or zcr[i]>upper_zcr_threshold:
                stop_cnt = 0
            else:
                stop_cnt += 1
            if stop_cnt ==  end_silence:
                stop_index = i - end_silence + 1 + speech_trailer
                stop_index = min(len(frames)-1, stop_index)

                print ">>", start_index, stop_index, (stop_index - start_index + 1 ) * 10
                wav.write("word" + str(words) + ".wav",rate,sig[441*start_index:441*(stop_index+1)])
                words += 1
                
                started = False
                start_index = start_cnt = 0
                stop_index = stop_cnt = 0
        
    if started:
        stop_index = len(frames)-1
        print ">>", start_index, stop_index, (stop_index - start_index + 1 ) * 10
        wav.write("word" + str(words) + ".wav",rate,sig[441*start_index:441*(stop_index+1)])
        words+=1

    return words
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python isolate_words.py [AUDIO-FILE]"        
    else:
        print get_words(sys.argv[1])
