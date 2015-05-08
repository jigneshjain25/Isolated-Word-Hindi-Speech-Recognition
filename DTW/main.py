import pickle, sys
from chop_words import chop
from record import rec
from dictionary import *

def load_dictionary(path):
    serialized = open(path + '/serialized.txt', 'r')
    is_serial = (serialized.read() == '1')
    serialized.close()

    if is_serial:
        with open(path + '/dictionary.pkl', 'rb') as input:
            dictionary = pickle.load(input)
    else:
        dictionary = Dictionary(path)
        with open(path + '/dictionary.pkl', 'wb') as output:                    
            pickle.dump(dictionary, output, 0)
        serialized = open(path + '/serialized.txt', 'w')
        serialized.write("1")
        serialized.close()
    
    return dictionary


if __name__ == '__main__':
    
    if len(sys.argv) < 3:
        print "Usage: python main.py [DICTIONARY] [AUDIO-FILE]"        
    else:
        dictionary = load_dictionary(sys.argv[1])
        audio_file = sys.argv[2]
        
        word_cnt = chop('chopped-words', audio_file)
        print "querying", word_cnt, "words"

        for i in xrange(word_cnt):    
            w = Word('chopped-words/word' + str(i) + '.wav')
            print dictionary.find_match(w) + ' ',
            sys.stdout.flush()
