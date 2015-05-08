import numpy as np
import pickle
from dtw import dtw
from features import get_features

# uncomment this to let numpy print everything without truncating
# numpy.set_printoptions(threshold=numpy.nan)

WORD_COMPARE_TR = 300

class Dword:

    def __init__(self, path):
        
        with open(path + '/meta.txt') as meta:
            meta_data = [x for x in meta]

        self.name = meta_data[0].strip()
        self.repeat = int(meta_data[1])
        self.path = path
        self.load()        

    def load(self):
        
        self.features = []
        for i in xrange(self.repeat):
            self.features.append(get_features(self.path + "/" + str(i+1) + ".wav"))

        self.mean = np.mean([len(x) for x in self.features])
        self.std = np.std([len(x) for x in self.features])

    def compare(self, w):
        cost = np.inf
        if abs(w.frame_cnt - self.mean) <= WORD_COMPARE_TR * self.std:
            for f in self.features:
                cost = min(cost, dtw(f, w.features))
        return cost    
 
class Dictionary:

    def __init__(self, path):
        
        with open(path + '/meta.txt') as meta:
            meta_data = [x for x in meta]

        self.path = path
        self.dword_cnt = int(meta_data[0])
        self.load()

    def load(self):
        self.dwords = []
        for i in xrange(self.dword_cnt):
            
            dword_path = self.path + '/' + str(i+1)
            serialized = open(dword_path + '/serialized.txt', 'r')
            is_serial = (serialized.read() == '1')
            serialized.close()
            
            if is_serial:        
    	        with open(dword_path + '/dword.pkl', 'rb') as input:
    		        dword = pickle.load(input)
            else:
                dword = Dword(dword_path)
    	        with open(dword_path + '/dword.pkl', 'wb') as output:                    
        	    	pickle.dump(dword, output, 0)
                serialized = open(dword_path + '/serialized.txt', 'w')
                serialized.write("1")
                serialized.close()

            self.dwords.append(dword)

    def find_match(self, w):
        best = np.inf
        index = 0
        for i in xrange(self.dword_cnt):
            cost = self.dwords[i].compare(w)
            if cost < best:
                best = cost
                index = i
        return self.dwords[index].name


class Word:

    def __init__(self, audio_path):
        self.audio_path = audio_path
        self.load()
    
    def load(self):
        self.features = get_features(self.audio_path)
        self.frame_cnt = len(self.features)

