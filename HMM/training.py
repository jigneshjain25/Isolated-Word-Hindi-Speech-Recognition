import numpy as np
import scipy.io.wavfile as wav
from features import get_features
import pylab as pl
from hmmlearn.hmm import GaussianHMM
import os
import sys
import math
import pickle
import warnings

warnings.filterwarnings("ignore")
test_folder = sys.argv[1]

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
print 'Words spoken:',spoken

accuracy = float(open('Models/accuracy.txt', 'r').read())

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
		(rate,sig) = wav.read(fpaths[i][j])
		features = get_features(sig)
		arr.append(len(features))
		model.fit([features])

	models.append(model)
	means.append(np.mean(arr))
	std_devs.append(np.std(arr))
	#print("done\n")

correct_answers = []
with open('Test/'+test_folder+'/answer.txt') as answers:
    for entry in answers:
        correct_answers.append(entry.split())

tot_words = len(correct_answers)
right = 0.0
threshold = 1.5

for i in xrange(tot_words):
	try:
		(rate,sig) = wav.read('Test/'+test_folder+"/word" + str(i) + ".wav")
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
		print str(i+1)+". Detected word: "+spoken[ans]
		if spoken[ans] == correct_answers[i][0]:
			right = right + 1
	except:
		break
	    
cur_accuracy = (right/tot_words)*100
print "Accuracy = "+str(cur_accuracy)+"%"

if cur_accuracy > accuracy:
	print "Found better models! Saving these models..."
	with open('Models/models.pkl', 'wb') as output:
		pickle.dump(models, output, 0)
		
	with open('Models/means.pkl', 'wb') as output:
		pickle.dump(means, output, 0)
		
	with open('Models/std_devs.pkl', 'wb') as output:
		pickle.dump(std_devs, output, 0)

	serialized = open('Models/serialized.txt', 'w')
	serialized.write("1")
	
	load_accuracy = open('Models/accuracy.txt', 'w')
	load_accuracy.write(str(cur_accuracy))
	
	print "Done\n"
