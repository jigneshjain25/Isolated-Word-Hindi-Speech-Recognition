import numpy as np
import scipy.io.wavfile as wav
from features import get_features
import pylab as pl
from hmmlearn.hmm import GaussianHMM
from isolate_words import get_words
import os
import sys
import math
import pickle
import warnings

warnings.filterwarnings("ignore")

test_file = sys.argv[1]
model_folder = 'Models'#sys.argv[2]

fpaths = []
labels = []
spoken = []
for f in os.listdir('dictionary'):
    temp = []
    for w in os.listdir('dictionary/' + f):
        temp.append('dictionary/' + f + '/' + w)
        labels.append(f)
        if f not in spoken:
            spoken.append(f)
    fpaths.append(temp)
    
words = []
with open('meta.txt') as answers:
    for entry in answers:    	
        words.append(entry)

#print 'Words spoken:',words

serialized = open('Models/serialized.txt', 'r')
isSerial = False
if (serialized.read() == '1'):
	isSerial = True

if isSerial == False:
	print "Generating models..."
	n_samples = 20
	###############################################################################
	# Run Gaussian HMM
	models = []
	means = []
	std_devs = []

	for i in range(len(spoken)):
		#print "fitting to HMM and decoding ..."

		n_components = 3
		arr = []

		# make an HMM instance and execute fit
		model = GaussianHMM(n_components, covariance_type="diag", n_iter=1000)

		for j in range(n_samples):
			#print fpaths[i][j]
			(rate,sig) = wav.read(fpaths[i][j])
			features = get_features(sig)
			arr.append(len(features))
			model.fit([features])

		models.append(model)
		means.append(np.mean(arr))
		std_devs.append(np.std(arr))
	
	with open('Models/models.pkl', 'wb') as output:
		pickle.dump(models, output, 0)
		
	with open('Models/means.pkl', 'wb') as output:
		pickle.dump(means, output, 0)
		
	with open('Models/std_devs.pkl', 'wb') as output:
		pickle.dump(std_devs, output, 0)

	serialized = open('Models/serialized.txt', 'w')
	serialized.write("1")
	print "Done\n"
else:
	print "Loading models..."
	with open(model_folder+'/models.pkl', 'rb') as input:
		models = pickle.load(input)
		
	with open(model_folder+'/means.pkl', 'rb') as input:
		means = pickle.load(input)
		
	with open(model_folder+'/std_devs.pkl', 'rb') as input:
		std_devs = pickle.load(input)
	print "Done\n"

tot_words = get_words(test_file)
right = 0.0
threshold = 1.5

print "Detected Words:"

for i in xrange(tot_words):
	try:
		(rate,sig) = wav.read("word" + str(i) + ".wav")
		features = get_features(sig)
		word_len = len(features)
		ans = -1
		j = -1
		max_ans = -1e9
		for model in models:
			j = j+1
			if math.fabs(word_len - means[j]) <= threshold * std_devs[j]:
				temp = model.score(features)
				if temp>max_ans:
					max_ans = temp
					ans = j
	
		#print max_ans
		print words[int(spoken[ans])-1],
	except:
		break	    
